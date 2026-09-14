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
DESK_EDGE_X = PAN_AXIS_X + 0.025   # the desk edge is 25 mm ahead of the pan axis (owner's tape, 2026-09-14); the keep-out plane
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
            parent=j.find("parent").get("link"), child=j.find("child").get("link"),
            xyz=np.array([float(x) for x in (o.get("xyz") if o is not None else "0 0 0").split()]),
            rpy=np.array([float(x) for x in (o.get("rpy") if o is not None else "0 0 0").split()]),
            axis=(np.array([float(x) for x in a.get("xyz").split()]) if a is not None and any(float(x) for x in a.get("xyz").split()) else None),
            limit=(float(l.get("lower")), float(l.get("upper"))) if l is not None else None)
    return joints


def fk(joints, q):
    """q: {joint: radians}. Returns {joint: 4x4} — the frame of each joint's child link in
    base_link, composed along the URDF's parent→child tree (the moving jaw and the tool
    frame `gripper_frame_joint` are siblings under gripper_link, not a chain)."""
    link_T = {"base_link": np.eye(4)}; out = {}
    pending = dict(joints)
    while pending:
        for n in [n for n in pending if pending[n]["parent"] in link_T]:
            j = pending.pop(n); A = np.eye(4); A[:3, :3] = _rpy(*j["rpy"]); A[:3, 3] = j["xyz"]
            T = link_T[j["parent"]] @ A
            if j["axis"] is not None:
                Rq = np.eye(4); Rq[:3, :3] = _rot(j["axis"], q.get(n, 0.0)); T = T @ Rq
            link_T[j["child"]] = T; out[n] = T
    return out


def raw_to_rad(raw):
    return {j: JOINT_ZERO[j][1] * (r - JOINT_ZERO[j][0]) / COUNTS_PER_RAD for j, r in raw.items() if j in JOINT_ZERO}


def rad_to_raw(q):
    return {j: int(round(JOINT_ZERO[j][0] + JOINT_ZERO[j][1] * a * COUNTS_PER_RAD)) for j, a in q.items()}


LINK_RADIUS = 0.03            # m; the printed links are ~40–60 mm across, so a 30 mm capsule radius
GRIPPER_TIP = 0.05            # m beyond gripper_frame_link along the jaw, for the reach of the fingers


def link_points(frames, step=0.01):
    """Points along the arm's skeleton: every joint origin plus samples every `step` metres along
    the segments between consecutive origins, and along the gripper to its tip. A capsule of
    LINK_RADIUS around this polyline is the collision body — a first model, not the meshes."""
    order = ["shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper_frame_joint"]   # the turret (pan) sits on the pan axis by construction
    pts = [frames["gripper"][:3, 3]]                                                              # moving-jaw hinge, a side branch
    for a, b in zip(order, order[1:]):
        pa, pb = frames[a][:3, 3], frames[b][:3, 3]
        n = max(1, int(np.linalg.norm(pb - pa) / step))
        pts += [pa + (pb - pa) * t for t in np.linspace(0, 1, n + 1)]
    tip = frames["gripper_frame_joint"]
    pts += [tip[:3, 3] + tip[:3, 2] * t for t in np.linspace(0, GRIPPER_TIP, 6)]   # tool z = approach axis, out along the jaws
    return np.array(pts)


def tool_points(frames):
    """The end-effector as points: the tool frame origin, samples out to the jaw tip, and the
    moving-jaw hinge. A capsule of LINK_RADIUS around them is the gripper body."""
    tip = frames["gripper_frame_joint"]
    pts = [tip[:3, 3] + tip[:3, 2] * t for t in np.linspace(0, GRIPPER_TIP, 6)]
    pts.append(frames["gripper"][:3, 3])
    return np.array(pts)


def keepout_clear(frames, plane_x=DESK_EDGE_X, margin=LINK_RADIUS):
    """The bench keep-out (docs/hardware.md → Bench, owner's rule as clarified 2026-09-14): the
    END-EFFECTOR does not reach behind the vertical plane at the desk edge. The upper arm and
    forearm may lean behind it. Returns (clear, rearmost x of any tool point); `margin` keeps the
    gripper body, not just its centreline, ahead of the plane."""
    worst = float(tool_points(frames)[:, 0].min())
    return worst >= plane_x + margin, worst


def within_limits(joints, q, margin_rad=np.radians(3)):
    bad = {n: np.degrees(a) for n, a in q.items() if joints[n]["limit"] and not (joints[n]["limit"][0] + margin_rad <= a <= joints[n]["limit"][1] - margin_rad)}
    return not bad, bad


IK_JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex"]


def ik(joints, target_xyz, pitch=None, q0=None, iters=200, damping=0.02, tol=1e-3):
    """Damped-least-squares IK for the gripper frame origin, four joints (pan, lift, elbow,
    wrist_flex; roll and gripper held). `pitch` (radians, optional) additionally asks for the
    gripper's approach axis to make that angle below horizontal — with pan, lift, elbow and
    wrist there are four DOF for the four constraints. Returns (q, err_m, converged)."""
    q = dict(q0 or {n: 0.0 for n in IK_JOINTS})
    target = np.asarray(target_xyz, float)

    def residual(q):
        f = fk(joints, q); p = f["gripper_frame_joint"][:3, 3]
        r = [target - p]
        if pitch is not None:
            z = f["gripper_frame_joint"][:3, 2]          # approach axis
            r.append([np.arcsin(-z[2]) - pitch])         # angle below horizontal
        return np.concatenate(r)

    for _ in range(iters):
        r = residual(q)
        if np.linalg.norm(r[:3]) < tol and (pitch is None or abs(r[3]) < 1e-3):
            return q, float(np.linalg.norm(r[:3])), True
        J = np.zeros((len(r), len(IK_JOINTS))); h = 1e-5
        for i, n in enumerate(IK_JOINTS):
            qh = dict(q); qh[n] += h; J[:, i] = (residual(qh) - r) / h
        dq = -J.T @ np.linalg.solve(J @ J.T + damping ** 2 * np.eye(len(r)), r)   # Newton step on r(q) ≈ r + J dq = 0
        for i, n in enumerate(IK_JOINTS):
            lo, hi = joints[n]["limit"]; q[n] = float(np.clip(q[n] + dq[i], lo, hi))
    r = residual(q)
    return q, float(np.linalg.norm(r[:3])), False


SEEDS = [  # initial guesses for IK: zero, elbow-up ready pose, reaching down, reaching up
    {n: 0.0 for n in IK_JOINTS},
    {"shoulder_pan": 0.0, "shoulder_lift": 0.6, "elbow_flex": -0.9, "wrist_flex": 0.8},
    {"shoulder_pan": 0.0, "shoulder_lift": 1.2, "elbow_flex": -0.3, "wrist_flex": 1.2},
    {"shoulder_pan": 0.0, "shoulder_lift": 0.3, "elbow_flex": -1.4, "wrist_flex": -0.5},
]


def solve(joints, target_xyz, pitch=None, q0=None, plane_x=PAN_AXIS_X, margin=LINK_RADIUS):
    """IK from several seeds (q0 first if given); returns the first converged solution that is
    inside the joint limits and clear of the keep-out plane, else the best converged one with
    its verdicts, else None. Result: dict(q, raw, err, limits_ok, clear, rear_x)."""
    best = None
    for seed in ([q0] if q0 else []) + SEEDS:
        q, err, conv = ik(joints, target_xyz, pitch=pitch, q0=seed)
        if not conv:
            continue
        lim_ok, _ = within_limits(joints, q); clear, rear = keepout_clear(fk(joints, q), plane_x, margin)
        res = dict(q=q, raw=rad_to_raw(q), err=err, limits_ok=lim_ok, clear=clear, rear_x=rear)
        if lim_ok and clear:
            return res
        if best is None or (lim_ok and not best["limits_ok"]) or rear > best["rear_x"]:
            best = res
    return best


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
    print(f"\nkeep-out (tool behind the desk edge, x = {DESK_EDGE_X:.4f} + {LINK_RADIUS} m margin): {'CLEAR' if ok else 'BREACHED'} (rearmost tool point x = {worst:+.3f} m)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
