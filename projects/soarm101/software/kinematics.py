#!/usr/bin/env python3
"""Forward kinematics of this arm from upstream's SO-101 URDF, and the servo-count mapping.

Usage:  kinematics.py [--urdf PATH] [--raw 1,2,3,4,5,6 | --live [--port /dev/ttyACM0]]
        prints every joint-frame origin and the gripper frame in the base frame, and whether
        the pose is clear of the bench keep-out plane (docs/hardware.md → Bench).

Model: upstream's `Simulation/SO101/so101_new_calib.urdf` (TheRobotStudio/SO-ARM100,
checked out beside wk-robotics — not vendored, the design authority is upstream). Its zero
pose: pan straight ahead, upper arm vertical, forearm horizontal forward, wrist in line, and
every joint's zero at the middle of its travel. Base frame: +x forward (away from the desk),
+z up, origin at the base plate; the pan axis is at x = PAN_AXIS_X.

Servo counts → URDF radians:  rad = SIGN * (raw - RAW_AT_ZERO) * 2π / 4095.
RAW_AT_ZERO and SIGN per joint live in JOINT_ZERO with their provenance. The 2026-09-14
values are ESTIMATES from the 2026-09-12 hand sweep (docs/test-log.md): the sweep's span
matches the URDF's travel within 3–8° on every pitch joint, so its midpoint is taken as the
URDF zero. Verify against a physically set zero pose before trusting a limit to a few
degrees; wrist_roll and gripper are placeholders. Hand-set zero pose 2026-09-14 agreed
within 9° on the four pitch/pan joints and fixed the pan and wrist_flex signs
(docs/test-log.md). Treat the zero as ±10° until a hard-stop measurement replaces it.
"""
import argparse
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_URDF = Path(os.environ.get(
    "SO101_URDF", HERE.parents[3] / "SO-ARM100" / "Simulation" / "SO101" / "so101_new_calib.urdf"))
CHAIN = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper", "gripper_frame_joint"]
PAN_AXIS_X = 0.0388           # pan axis in base_link, from the URDF's shoulder_pan origin
COUNTS_PER_RAD = 4095 / (2 * np.pi)

# (raw count at URDF zero, sign, provenance)
JOINT_ZERO = {
    "shoulder_pan":  (2046, +1, "sweep midpoint (750+3343)/2, 2026-09-12; hand zero read 2036; sign verified 2026-09-14 (toward the arm's left = raw down = URDF negative)"),
    "shoulder_lift": (1866, +1, "sweep midpoint (736+2997)/2; hand zero read 1918; sign from the rest pose: raw min ↔ URDF lower limit"),
    "elbow_flex":    (2954, +1, "sweep midpoint (1880+4028)/2; hand zero read 3055; sign from the rest pose: raw max ↔ URDF upper limit"),
    "wrist_flex":    (2070, +1, "sweep midpoint (1002+3137)/2; hand zero read 2081; sign verified 2026-09-14 (gripper pitched down = raw up = URDF positive)"),
    "wrist_roll":    (2047, +1, "placeholder: homing mid; unverified"),
    "gripper":       (1328, +1, "placeholder: raw min ↔ closed (URDF 0); unverified"),
}


def _rpy(r, p, y):
    cr, sr, cp, sp, cy, sy = np.cos(r), np.sin(r), np.cos(p), np.sin(p), np.cos(y), np.sin(y)
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def _rot(axis, th):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K


def load_urdf(path=DEFAULT_URDF):
    root = ET.parse(path).getroot(); joints = {}
    for j in root.findall("joint"):
        o, a, l = j.find("origin"), j.find("axis"), j.find("limit")
        joints[j.get("name")] = dict(
            xyz=np.array([float(x) for x in (o.get("xyz") if o is not None else "0 0 0").split()]),
            rpy=np.array([float(x) for x in (o.get("rpy") if o is not None else "0 0 0").split()]),
            axis=(np.array([float(x) for x in a.get("xyz").split()]) if a is not None and any(float(x) for x in a.get("xyz").split()) else None),
            limit=(float(l.get("lower")), float(l.get("upper"))) if l is not None else None)
    return joints


def fk(joints, q):
    """q: {joint: radians}. Returns {frame: 4x4} in base_link for every joint origin in CHAIN."""
    T = np.eye(4); out = {}
    for n in CHAIN:
        j = joints[n]; A = np.eye(4); A[:3, :3] = _rpy(*j["rpy"]); A[:3, 3] = j["xyz"]; T = T @ A
        if j["axis"] is not None:
            Rq = np.eye(4); Rq[:3, :3] = _rot(j["axis"], q.get(n, 0.0)); T = T @ Rq
        out[n] = T.copy()
    return out


def raw_to_rad(raw):
    return {j: JOINT_ZERO[j][1] * (r - JOINT_ZERO[j][0]) / COUNTS_PER_RAD for j, r in raw.items() if j in JOINT_ZERO}


def rad_to_raw(q):
    return {j: int(round(JOINT_ZERO[j][0] + JOINT_ZERO[j][1] * a * COUNTS_PER_RAD)) for j, a in q.items()}


def keepout_clear(frames, plane_x=PAN_AXIS_X, margin=0.0):
    """True if every frame origin lies in front of the vertical plane x = plane_x - margin.
    Frame origins only — link bodies are not modelled yet; a link can cross the plane between
    two clear origins, so this is necessary, not sufficient."""
    worst = min(T[0, 3] for T in frames.values())
    return worst >= plane_x - margin, worst


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--urdf", default=str(DEFAULT_URDF))
    ap.add_argument("--raw", help="six raw counts in ID order 1..6")
    ap.add_argument("--live", action="store_true", help="read the servos (read-only)")
    ap.add_argument("--port", default="/dev/ttyACM0")
    a = ap.parse_args()
    names = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
    if a.live:
        from lerobot.motors import Motor, MotorNormMode
        from lerobot.motors.feetech import FeetechMotorsBus
        b = FeetechMotorsBus(a.port, {n: Motor(i + 1, "sts3215", MotorNormMode.RANGE_M100_100) for i, n in enumerate(names)})
        b.connect(handshake=False)
        try:
            raw = b.sync_read("Present_Position", normalize=False, num_retry=5)
        finally:
            try: b.disconnect(disable_torque=False)
            except Exception: pass
    elif a.raw:
        raw = dict(zip(names, (int(x) for x in a.raw.split(","))))
    else:
        raw = {n: JOINT_ZERO[n][0] for n in names}
    joints = load_urdf(a.urdf); q = raw_to_rad(raw); frames = fk(joints, q)
    print("| Joint | raw | URDF ° | limit ° |\n|---|---|---|---|")
    for n in names:
        lo, hi = np.degrees(joints[n]["limit"])
        print(f"| `{n}` | {raw[n]} | {np.degrees(q[n]):+.1f} | {lo:+.0f} … {hi:+.0f} |")
    print("\n| Frame | x fwd (m) | y left (m) | z up (m) |\n|---|---|---|---|")
    for n, T in frames.items():
        print(f"| `{n}` | {T[0,3]:+.3f} | {T[1,3]:+.3f} | {T[2,3]:+.3f} |")
    ok, worst = keepout_clear(frames)
    print(f"\nkeep-out plane x = {PAN_AXIS_X:.4f}: {'CLEAR' if ok else 'BREACHED'} (rearmost origin x = {worst:+.3f} m)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
