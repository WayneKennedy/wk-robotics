# SPDX-License-Identifier: MIT
"""Perception bench node: YOLOv8 objects + SCRFD faces + ArcFace recognition on TensorRT.

Same interface as the HAT half (hailo_perception), all under the node's namespace:
  sub  image            sensor_msgs/Image (the RealSense colour topic remapped)
  sub  enroll           std_msgs/String — name; the next frame's largest face is saved
                        to <gallery_dir>/<name>.txt and added to the gallery
  pub  objects          vision_msgs/Detection2DArray, class_id = COCO label
  pub  faces            vision_msgs/Detection2DArray, class_id = gallery name or "unknown",
                        score = cosine similarity to the best gallery match
  pub  image_annotated  sensor_msgs/Image bgr8, boxes and labels drawn
  pub  stats            std_msgs/String, JSON once a second: fps and per-stage ms (mean, p95)
"""
import json
import time
from collections import deque

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose

from . import arcface, scrfd, yolo
from .gallery import Gallery
from .trt_runtime import TrtRunner


class Stage:
    """Rolling mean/max of a stage's wall time in ms."""
    def __init__(self, n=60):
        self.buf = deque(maxlen=n)

    def add(self, t0):
        self.buf.append((time.perf_counter() - t0) * 1000.0)

    def stats(self):
        if not self.buf:
            return None
        a = np.fromiter(self.buf, float)
        return {'mean_ms': round(float(a.mean()), 2), 'p95_ms': round(float(np.percentile(a, 95)), 2)}


class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')
        self.declare_parameters('', [
            ('models_dir', '~/models'),
            ('yolo_engine', 'yolov8s.engine'),
            ('face_det_engine', 'det_500m.engine'),
            ('face_embed_engine', 'w600k_mbf.engine'),
            ('face_det_size', 640),
            ('embedding_model', 'insightface-buffalo_sc/w600k_mbf'),
            # the following mirror hailo_perception's parameter names
            ('enable_objects', True), ('enable_faces', True),
            ('object_score_threshold', 0.25), ('object_nms_iou', 0.45),
            ('face_score_threshold', 0.5), ('face_nms_iou', 0.4),
            ('face_match_threshold', 0.35),
            ('gallery_dir', '~/orin/gallery'),
            ('publish_annotated', True),
            ('process_every_n', 1),
        ])
        g = lambda k: self.get_parameter(k).value  # noqa: E731
        import os
        md = os.path.expanduser(g('models_dir'))
        self.bridge = CvBridge()
        self.objects_enabled, self.faces_enabled = g('enable_objects'), g('enable_faces')
        self.yolo_conf, self.yolo_iou = g('object_score_threshold'), g('object_nms_iou')
        self.face_size, self.face_thresh, self.face_nms = g('face_det_size'), g('face_score_threshold'), g('face_nms_iou')
        self.match_thresh = g('face_match_threshold')
        self.every_n, self.publish_annotated = g('process_every_n'), g('publish_annotated')
        self.pending_enroll = ''

        t0 = time.perf_counter()
        self.yolo = TrtRunner(os.path.join(md, g('yolo_engine'))) if self.objects_enabled else None
        self.det = TrtRunner(os.path.join(md, g('face_det_engine'))) if self.faces_enabled else None
        self.emb = TrtRunner(os.path.join(md, g('face_embed_engine'))) if self.faces_enabled else None
        self.gallery = Gallery(g('gallery_dir'), g('embedding_model'), self.get_logger().warn) if self.faces_enabled else None
        self.get_logger().info(f'engines loaded in {time.perf_counter() - t0:.1f}s; '
                               f'gallery: {self.gallery.names if self.gallery else "off"}')
        if self.yolo:
            self.yolo_size = self.yolo.input_shape()[-1]
            self.yolo(np.zeros(self.yolo.input_shape(), np.float32))  # warm-up
        if self.det:
            assert self.det.input_shape()[-1] == self.face_size, 'face_det_size must match the engine'
            self.det(np.zeros(self.det.input_shape(), np.float32))
            self.emb(np.zeros(self.emb.input_shape(), np.float32))

        self.st = {k: Stage() for k in ('convert', 'yolo_pre', 'yolo_infer', 'yolo_post',
                                        'face_det', 'face_embed', 'draw_publish', 'total', 'e2e_from_stamp')}
        self.frames_in = self.frames_done = 0
        self.last_report = time.time()
        self.fps_window = deque(maxlen=120)

        # RELIABLE, not SensorDataQoS: realsense2_camera publishes RELIABLE, and a best-effort
        # subscriber to 2.7 MB frames over Fast DDS on this host received 2 fps of the 29
        # published (fragment loss); reliable keep-last-1 receives them all (2026-09-19).
        qos = QoSProfile(reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST, depth=1)
        self.sub = self.create_subscription(Image, 'image', self.on_image, qos)
        self.sub_enroll = self.create_subscription(String, 'enroll', self.on_enroll, 10)
        self.pub_img = self.create_publisher(Image, 'image_annotated', 1)
        self.pub_objects = self.create_publisher(Detection2DArray, 'objects', 10)
        self.pub_faces = self.create_publisher(Detection2DArray, 'faces', 10)
        self.pub_stats = self.create_publisher(String, 'stats', 10)
        self.create_timer(1.0, self.report)
        self.get_logger().info('ready')

    def on_enroll(self, msg: String):
        self.pending_enroll = msg.data.strip()
        self.get_logger().info(f"enroll: waiting for a face to save as '{self.pending_enroll}'")

    # ------------------------------------------------------------------ pipeline
    def on_image(self, msg: Image):
        self.frames_in += 1
        if self.every_n > 1 and self.frames_in % self.every_n:
            return
        T = time.perf_counter()
        t = time.perf_counter()
        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.st['convert'].add(t)

        dets = []
        if self.yolo:
            t = time.perf_counter(); blob, r, pad = yolo.letterbox(img, self.yolo_size); self.st['yolo_pre'].add(t)
            t = time.perf_counter(); out = next(iter(self.yolo(blob).values())); self.st['yolo_infer'].add(t)
            t = time.perf_counter(); dets = yolo.decode(out, r, pad, self.yolo_conf, self.yolo_iou); self.st['yolo_post'].add(t)

        faces = []
        if self.det:
            t = time.perf_counter()
            blob, r = scrfd.preprocess(img, self.face_size)
            fd = scrfd.decode(self.det(blob), self.face_size, r, self.face_thresh, self.face_nms)
            self.st['face_det'].add(t)
            if fd:
                t = time.perf_counter()
                embs = []
                for (x1, y1, x2, y2, sc, kps) in fd:
                    crop = arcface.norm_crop(img, kps)
                    if crop is None:
                        continue
                    e = arcface.normalize(next(iter(self.emb(arcface.preprocess(crop)).values())))
                    name, sim = self.gallery.match(e, self.match_thresh)
                    faces.append((x1, y1, x2, y2, sc, name, sim))
                    embs.append(e)
                self.st['face_embed'].add(t)
                if self.pending_enroll and faces:
                    i = max(range(len(faces)), key=lambda k: (faces[k][2] - faces[k][0]) * (faces[k][3] - faces[k][1]))
                    self.gallery.add(self.pending_enroll, embs[i])
                    self.get_logger().info(f"enrolled '{self.pending_enroll}' ({len(self.gallery)} in gallery)")
                    self.pending_enroll = ''

        t = time.perf_counter()
        self.publish(msg, img, dets, faces)
        self.st['draw_publish'].add(t)
        self.st['total'].add(T)
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        if stamp > 0:
            self.st['e2e_from_stamp'].buf.append((time.time() - stamp) * 1000.0)
        self.frames_done += 1
        self.fps_window.append(time.time())

    def publish(self, msg, img, dets, faces):
        def det2d(x1, y1, x2, y2, class_id, score):
            d = Detection2D(header=msg.header)
            d.bbox.center.position.x, d.bbox.center.position.y = (x1 + x2) / 2, (y1 + y2) / 2
            d.bbox.size_x, d.bbox.size_y = x2 - x1, y2 - y1
            h = ObjectHypothesisWithPose(); h.hypothesis.class_id = class_id; h.hypothesis.score = float(score)
            d.results.append(h)
            return d
        self.pub_objects.publish(Detection2DArray(header=msg.header, detections=[
            det2d(x1, y1, x2, y2, yolo.COCO[c], sc) for (x1, y1, x2, y2, sc, c) in dets]))
        self.pub_faces.publish(Detection2DArray(header=msg.header, detections=[
            det2d(x1, y1, x2, y2, name, sim) for (x1, y1, x2, y2, sc, name, sim) in faces]))
        if not self.publish_annotated:
            return
        for (x1, y1, x2, y2, sc, c) in dets:
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 200, 0), 2)
            cv2.putText(img, f'{yolo.COCO[c]} {sc:.2f}', (int(x1), max(int(y1) - 6, 12)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 2)
        for (x1, y1, x2, y2, sc, name, sim) in faces:
            col = (0, 140, 255) if name == 'unknown' else (255, 120, 0)
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), col, 2)
            cv2.putText(img, f'{name} {sim:.2f}', (int(x1), min(int(y2) + 20, img.shape[0] - 4)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 2)
        tot = self.st['total'].stats()
        cv2.putText(img, f'{self.fps():.1f} fps  {tot["mean_ms"] if tot else 0:.0f} ms', (8, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        out = self.bridge.cv2_to_imgmsg(img, encoding='bgr8')
        out.header = msg.header
        self.pub_img.publish(out)

    # ------------------------------------------------------------------ stats
    def fps(self):
        if len(self.fps_window) < 2:
            return 0.0
        return (len(self.fps_window) - 1) / max(self.fps_window[-1] - self.fps_window[0], 1e-6)

    def report(self):
        s = {'fps_out': round(self.fps(), 2), 'frames_in': self.frames_in, 'frames_done': self.frames_done,
             'stages': {k: v.stats() for k, v in self.st.items() if v.stats()}}
        self.pub_stats.publish(String(data=json.dumps(s)))
        self.get_logger().info(f'{s["fps_out"]:.1f} fps | ' + ' '.join(
            f'{k}={v["mean_ms"]:.1f}' for k, v in s['stages'].items()))


def main():
    rclpy.init()
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()
