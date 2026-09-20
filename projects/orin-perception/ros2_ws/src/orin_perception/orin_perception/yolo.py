# SPDX-License-Identifier: MIT
"""YOLOv8 (Ultralytics ONNX export, output [1, 4+nc, N]) pre/post-processing."""
import cv2
import numpy as np

COCO = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
        'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
        'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella',
        'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
        'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle',
        'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
        'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant',
        'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
        'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
        'teddy bear', 'hair drier', 'toothbrush']


def letterbox(img_bgr, size, pad_value=114):
    """Resize keeping aspect, pad to (size, size). Returns blob [1,3,S,S] float32 RGB/255, scale, (dx, dy)."""
    h, w = img_bgr.shape[:2]
    r = min(size / h, size / w)
    nw, nh = int(round(w * r)), int(round(h * r))
    dx, dy = (size - nw) // 2, (size - nh) // 2
    canvas = np.full((size, size, 3), pad_value, dtype=np.uint8)
    canvas[dy:dy + nh, dx:dx + nw] = cv2.resize(img_bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)
    blob = canvas[:, :, ::-1].transpose(2, 0, 1)[None].astype(np.float32) / 255.0
    return np.ascontiguousarray(blob), r, (dx, dy)


def decode(out, r, pad, conf=0.25, iou=0.45, max_det=100):
    """out: [1, 4+nc, N] -> list of (x1, y1, x2, y2, score, cls) in original image pixels."""
    pred = out[0].T  # N x (4+nc)
    scores = pred[:, 4:]
    cls = scores.argmax(1)
    conf_v = scores[np.arange(len(cls)), cls]
    keep = conf_v >= conf
    if not keep.any():
        return []
    pred, cls, conf_v = pred[keep], cls[keep], conf_v[keep]
    cx, cy, w, h = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
    dx, dy = pad
    x1 = (cx - w / 2 - dx) / r
    y1 = (cy - h / 2 - dy) / r
    x2 = (cx + w / 2 - dx) / r
    y2 = (cy + h / 2 - dy) / r
    # Class-aware NMS on OpenCV 4.6 (no NMSBoxesBatched): offset each class into its own region.
    off = cls.astype(np.float32) * 8192.0
    boxes_xywh = np.stack([x1 + off, y1 + off, x2 - x1, y2 - y1], 1)
    idx = cv2.dnn.NMSBoxes(boxes_xywh.tolist(), conf_v.tolist(), conf, iou)
    if len(idx) == 0:
        return []
    idx = np.array(idx).reshape(-1)[:max_det]
    return [(float(x1[i]), float(y1[i]), float(x2[i]), float(y2[i]), float(conf_v[i]), int(cls[i])) for i in idx]
