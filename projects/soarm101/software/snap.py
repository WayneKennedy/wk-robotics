#!/usr/bin/env python3
"""Grab one frame from the bench webcam. Usage: snap.py [out.jpg] [--dev /dev/video0]"""
import sys
import cv2

out = next((a for a in sys.argv[1:] if not a.startswith("--")), "snap.jpg")
dev = sys.argv[sys.argv.index("--dev") + 1] if "--dev" in sys.argv else "/dev/video0"
cap = cv2.VideoCapture(dev, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
ok = False
for _ in range(10):
    ok, frame = cap.read()
cap.release()
if not ok:
    sys.exit(f"no frame from {dev}")
cv2.imwrite(out, frame); print(out, frame.shape)
