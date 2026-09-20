# SPDX-License-Identifier: MIT
"""ArcFace-style embedder (InsightFace w600k_mbf / w600k_r50 ONNX): 5-point alignment to 112x112, L2-normalised 512-d."""
import cv2
import numpy as np

# Canonical landmark positions for a 112x112 crop (insightface.utils.face_align.arcface_dst).
ARCFACE_DST = np.array([[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366],
                        [41.5493, 92.3655], [70.7299, 92.2041]], dtype=np.float32)


def norm_crop(img_bgr, kps, size=112):
    """Similarity-transform the face so its 5 landmarks land on ARCFACE_DST."""
    M, _ = cv2.estimateAffinePartial2D(np.asarray(kps, dtype=np.float32), ARCFACE_DST, method=cv2.LMEDS)
    if M is None:
        return None
    return cv2.warpAffine(img_bgr, M, (size, size), borderValue=0.0)


def preprocess(crop_bgr):
    return np.ascontiguousarray(
        cv2.dnn.blobFromImage(crop_bgr, 1.0 / 127.5, (112, 112), (127.5, 127.5, 127.5), swapRB=True),
        dtype=np.float32)


def normalize(emb):
    emb = np.asarray(emb, dtype=np.float32).reshape(-1)
    return emb / max(np.linalg.norm(emb), 1e-6)
