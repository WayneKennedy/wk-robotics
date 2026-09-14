#!/usr/bin/env python3
"""Grab one frame from the bench webcam, upright and exposed for the garage.

Usage: snap.py [out.jpg] [--dev /dev/video0] [--exposure 40] [--raw]

The camera is mounted in portrait on the arm's left (docs/hardware.md → Bench) and its raw
frame is mirrored, so the default rotates 90° counter-clockwise and then flips horizontally:
upright, desk on the right, the arm's front (free air) on the left. --raw skips both.
Auto-exposure blows out against the garage roof; --exposure sets V4L2 manual absolute
exposure (default 40, usable 2026-09-14).
"""
import sys
import cv2

args = sys.argv[1:]
def opt(name, default):
    return args[args.index(name) + 1] if name in args else default
out = next((a for a in args if not a.startswith("--") and a not in (opt("--dev", ""), opt("--exposure", ""))), "snap.jpg")
dev = opt("--dev", "/dev/video0"); exposure = int(opt("--exposure", 40))
cap = cv2.VideoCapture(dev, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)          # V4L2: 1 = manual
cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
ok = False
for _ in range(12):
    ok, frame = cap.read()
cap.release()
if not ok:
    sys.exit(f"no frame from {dev}")
if "--raw" not in args:
    frame = cv2.flip(cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE), 1)
cv2.imwrite(out, frame); print(out, frame.shape)
