# SPDX-License-Identifier: MIT
"""SCRFD face detector decode (InsightFace det_500m / det_2.5g / det_10g ONNX, with keypoints).

Port of the decode in insightface/model_zoo/scrfd.py: 3 FPN strides (8, 16, 32), 2 anchors
per cell, outputs per stride = scores [A,1], bbox distances [A,4], kps distances [A,10].
"""
import cv2
import numpy as np

STRIDES = (8, 16, 32)
NUM_ANCHORS = 2


def preprocess(img_bgr, size):
    """Fit into (size, size) top-left, pad black. Returns blob [1,3,S,S] float32 ((RGB-127.5)/128), scale."""
    h, w = img_bgr.shape[:2]
    r = min(size / h, size / w)
    nw, nh = int(w * r), int(h * r)
    canvas = np.zeros((size, size, 3), dtype=np.uint8)
    canvas[:nh, :nw] = cv2.resize(img_bgr, (nw, nh))
    blob = cv2.dnn.blobFromImage(canvas, 1.0 / 128, (size, size), (127.5, 127.5, 127.5), swapRB=True)
    return np.ascontiguousarray(blob, dtype=np.float32), r


def group_outputs(outputs: dict, size):
    """Sort engine outputs into [(scores, bbox, kps) per stride] by shape, independent of tensor names."""
    by_stride = {}
    for name, arr in outputs.items():
        a = arr.reshape(arr.shape[-2], arr.shape[-1]) if arr.ndim == 3 else arr
        rows, last = a.shape
        for s in STRIDES:
            if rows == (size // s) * (size // s) * NUM_ANCHORS:
                by_stride.setdefault(s, {})[{1: 'score', 4: 'bbox', 10: 'kps'}[last]] = a
    return [(by_stride[s]['score'], by_stride[s]['bbox'], by_stride[s]['kps']) for s in STRIDES]


def _anchor_centers(size, stride):
    n = size // stride
    ac = np.stack(np.mgrid[:n, :n][::-1], axis=-1).astype(np.float32).reshape(-1, 2) * stride
    return np.stack([ac] * NUM_ANCHORS, axis=1).reshape(-1, 2)


_CENTERS = {}


def decode(outputs: dict, size, r, thresh=0.5, nms=0.4, max_faces=20):
    """Returns list of (x1, y1, x2, y2, score, kps[5,2]) in original image pixels."""
    boxes, scores, kpss = [], [], []
    for stride, (sc, bb, kp) in zip(STRIDES, group_outputs(outputs, size)):
        key = (size, stride)
        if key not in _CENTERS:
            _CENTERS[key] = _anchor_centers(size, stride)
        ac = _CENTERS[key]
        sc = sc.reshape(-1)
        pos = np.where(sc >= thresh)[0]
        if len(pos) == 0:
            continue
        bb = bb[pos] * stride
        kp = kp[pos] * stride
        c = ac[pos]
        x1, y1 = c[:, 0] - bb[:, 0], c[:, 1] - bb[:, 1]
        x2, y2 = c[:, 0] + bb[:, 2], c[:, 1] + bb[:, 3]
        boxes.append(np.stack([x1, y1, x2, y2], 1))
        scores.append(sc[pos])
        k = kp.reshape(-1, 5, 2)
        k[:, :, 0] += c[:, 0:1]
        k[:, :, 1] += c[:, 1:2]
        kpss.append(k)
    if not boxes:
        return []
    boxes = np.concatenate(boxes) / r
    scores = np.concatenate(scores)
    kpss = np.concatenate(kpss) / r
    xywh = np.stack([boxes[:, 0], boxes[:, 1], boxes[:, 2] - boxes[:, 0], boxes[:, 3] - boxes[:, 1]], 1)
    idx = cv2.dnn.NMSBoxes(xywh.tolist(), scores.tolist(), thresh, nms)
    if len(idx) == 0:
        return []
    idx = np.array(idx).reshape(-1)[:max_faces]
    return [(*map(float, boxes[i]), float(scores[i]), kpss[i]) for i in idx]
