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
pan, shoulder, elbow and wrist-flex values are MEASURED (2026-09-14): the midpoint of each
joint's mechanical stops found by find_stops.py, taken as the URDF zero by upstream's
new-calibration convention (zero at mid-travel) — then CHECKED with a spirit level at the zero
pose the same evening. Equal span does not make the midpoint the zero: the elbow's travel
matches the URDF's span yet its zero is 4.8° off its stop midpoint (level + tape agree). Now:
pan ±1.3° (midpoint, span 2.6° over the URDF), shoulder ~1° (level), elbow ±1.5° (level +
tape), wrist ±2° (level on the gripper + tape). Tape check at one pose after the corrections:
reach 24.9 cm, exact; height within the jaw-point ambiguity. Verify against a physically set zero pose before trusting a limit to a few
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
DESK_TOP_Z = 0.0              # the desk top in the base frame: the base plate sits on it (its underside is z = 0 in the URDF).
                              # Behind the plane and below this is desk, whatever the cylinder says — the forearm found the
                              # underside on 2026-09-14 (docs/test-log.md)
UPPER_ARM_RADIUS = 0.18       # m; the upper arm's sweep about the pan axis: elbow axis at most 0.15 m from it (URDF: shoulder
                              # axis 0.035 m off the pan axis, shoulder→elbow 0.116 m) plus the link body — the keep-out cylinder
COUNTS_PER_RAD = 4095 / (2 * np.pi)

# (raw count at URDF zero, sign, provenance)
JOINT_ZERO = {
    "shoulder_pan":  (1981, +1, "MEASURED 2026-09-14: midpoint of the mechanical stops 715 / 3247 (find_stops.py; span 222.6° vs URDF 220°). Was the sweep midpoint 2046; the owner's by-eye straight-ahead read 2036 — 4.8° from this, unresolved; sign verified 2026-09-14"),
    "shoulder_lift": (1925, +1, "MEASURED 2026-09-14: stop midpoint 1920 (stops 723 / 3118), refined by a spirit level on the upper arm at the zero pose — 3.0° forward where 1920 predicted 3.4°. ~1° (iPhone level); sign from the rest pose"),
    "elbow_flex":    (3031, +1, "MEASURED 2026-09-14: NOT the stop midpoint 2976 — a spirit level on the forearm (+2° front up at the zero pose) and the tape reach (24.9 cm at the first target) both put the zero 3.4–6.2° above it; 3031 (+4.8°) is the middle of that band, ±1.5°. So the stops 1879 / 4074 sit at −101° / +92°: the travel has the URDF's span but is not centred on its zero"),
    "wrist_flex":    (2070, +1, "MEASURED 2026-09-14: NOT the stop midpoint 2046 (stops 881 / 3212) — a spirit level on the gripper's fixed jaw (+4° front up at the zero pose) and the tape reach (24.9 cm exactly) both want 2070 (+2.1°), ±2° (whether the jaw edge runs along the approach axis is unverified; the tape bounds it). Coincides with the 2026-09-12 sweep midpoint"),
    "wrist_roll":    (2047, +1, "placeholder: homing mid; unverified"),
    "gripper":       (1289, +1, "closed stop MEASURED 2026-09-14 (open stop 2741, span 127.6°); taken as URDF 0 — whether URDF 0 or −10° is the closed jaw is unverified; jaw GAP not calibrated"),
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
    return apply_measured_limits(joints)


CALIBRATION_JSON = HERE / "calibration" / "wk_soarm101.json"
LIMIT_JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex"]


def apply_measured_limits(joints, cal_path=CALIBRATION_JSON):
    """Replace the URDF's limits on the four arm joints with the servos' saved limits (the measured
    stops ∓ 3° since 2026-09-14), mapped through JOINT_ZERO. The URDF's are symmetric CAD numbers;
    this arm's travel is wider and, on the elbow, not centred on the URDF zero. URDF values kept
    as joints[j]["urdf_limit"]."""
    if not Path(cal_path).exists():
        return joints
    import json
    cal = json.load(open(cal_path))
    for j in LIMIT_JOINTS:
        z, sgn, _ = JOINT_ZERO[j]
        a, b = sorted(sgn * (cal[j][k] - z) / COUNTS_PER_RAD for k in ("range_min", "range_max"))
        joints[j]["urdf_limit"] = joints[j]["limit"]; joints[j]["limit"] = (a, b)
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


def keepout_clear(frames, plane_x=DESK_EDGE_X, margin=LINK_RADIUS, cyl_r=UPPER_ARM_RADIUS):
    """The bench keep-out (docs/hardware.md → Bench, owner's rule as settled 2026-09-14): the
    forbidden region is the half-space BEHIND the desk-edge plane MINUS a vertical cylinder about
    the pan axis of the upper arm's sweep radius — the cylinder exemption only ABOVE the desk top,
    since below it the space behind the plane is the desk. Every part of the arm is tested —
    inside the cylinder and above the desk (the installer's clearance zone) a part may be
    anywhere; otherwise it must be ahead of the plane. `margin` is the link body radius. Returns
    (clear, rearmost x of any offending-or-not point outside the cylinder, count of violating points)."""
    pts = np.vstack([link_points(frames), tool_points(frames)])
    r = np.hypot(pts[:, 0] - PAN_AXIS_X, pts[:, 1])
    outside = r + margin > cyl_r
    behind = pts[:, 0] - margin < plane_x
    under_desk = pts[:, 2] - margin < DESK_TOP_Z          # the cylinder exemption has a floor: the desk itself is behind the plane below its top
    bad = behind & (outside | under_desk)
    rear = float(pts[outside, 0].min()) if outside.any() else float("nan")
    return not bad.any(), rear, int(bad.sum())


def within_limits(joints, q, margin_rad=np.radians(3)):
    bad = {n: np.degrees(a) for n, a in q.items() if joints[n]["limit"] and not (joints[n]["limit"][0] + margin_rad <= a <= joints[n]["limit"][1] - margin_rad)}
    return not bad, bad


# ---- self-collision: capsule hit boxes per link, in the link's own frame ------------------------
# Fitted 2026-09-14 to upstream's collision meshes (Simulation/SO101/assets/*.stl, placed by each
# <collision><origin>): PCA axis, radius = largest perpendicular vertex distance, ends pulled in as far
# as the caps still cover every vertex. Conservative by construction. (p0, p1, r) in metres.
CAPSULES = {
    "base_link": [
        ((-0.0191, -0.0061, 0.0549), (0.0332, 0.0203, 0.0487), 0.0417),   # base_motor_holder
        ((0.0115, -0.0006, 0.0220), (0.0206, 0.0008, 0.0175), 0.0598),     # base plate
        ((0.0256, 0.0, 0.0470), (0.0301, 0.0, 0.0420), 0.0308),            # pan servo
        ((-0.0289, 0.0181, 0.0478), (-0.0289, -0.0185, 0.0478), 0.0215),   # Waveshare plate
    ],
    "shoulder_link": [
        ((-0.0304, 0.0021, -0.0454), (-0.0304, -0.0028, -0.0410), 0.0308),  # lift servo
        ((-0.0338, -0.0111, -0.0242), (-0.0253, 0.0100, -0.0262), 0.0316),  # motor_holder_base
        ((-0.0240, -0.0027, -0.0127), (-0.0102, 0.0001, 0.0191), 0.0439),   # rotation_pitch
    ],
    "upper_arm_link": [
        ((-0.1126, -0.0148, 0.0154), (-0.1126, -0.0192, 0.0204), 0.0308),   # elbow servo
        ((-0.1191, 0.0015, 0.0150), (-0.0005, -0.0006, 0.0333), 0.0475),    # upper arm
    ],
    "lower_arm_link": [
        ((-0.1015, -0.0013, 0.0069), (-0.0091, 0.0001, 0.0389), 0.0536),    # under arm
        ((-0.1043, 0.0014, 0.0024), (-0.1082, -0.0004, 0.0365), 0.0275),    # wrist motor holder
        ((-0.1261, 0.0052, 0.0204), (-0.1217, 0.0052, 0.0154), 0.0308),     # wrist-flex servo
    ],
    "wrist_link": [
        ((0.0, -0.0518, 0.0220), (0.0, -0.0505, 0.0403), 0.0293),           # roll servo
        ((0.0018, -0.0186, 0.0339), (-0.0035, -0.0324, 0.0250), 0.0507),    # wrist_roll_pitch
    ],
    "gripper_link": [
        ((0.0070, 0.0034, -0.0234), (0.0114, -0.0016, -0.0234), 0.0308),    # gripper servo
        ((-0.0160, 0.0, -0.0960), (-0.0069, 0.0001, -0.0050), 0.0405),      # fixed jaw body
    ],
    "moving_jaw_so101_v1_link": [
        ((0.0038, -0.0009, 0.0179), (-0.0069, -0.0719, 0.0192), 0.0282),    # moving jaw
    ],
}
LINK_OF_JOINT = {"shoulder_pan": "shoulder_link", "shoulder_lift": "upper_arm_link", "elbow_flex": "lower_arm_link",
                 "wrist_flex": "wrist_link", "wrist_roll": "gripper_link", "gripper": "moving_jaw_so101_v1_link"}
LINK_ORDER = ["base_link", "shoulder_link", "upper_arm_link", "lower_arm_link", "wrist_link", "gripper_link", "moving_jaw_so101_v1_link"]
# pairs that touch by design are never tested: joint-joined neighbours, plus two pairs whose fat
# joint-end capsules overlap in every pose (base–upper arm −8…−12 mm, wrist–jaw −18 mm, 2026-09-14)
ADJACENT = {frozenset(p) for p in zip(LINK_ORDER, LINK_ORDER[1:])} | {
    frozenset(("gripper_link", "moving_jaw_so101_v1_link")),
    frozenset(("base_link", "upper_arm_link")), frozenset(("wrist_link", "moving_jaw_so101_v1_link"))}
SELF_MARGIN = 0.0             # the capsules already cover every mesh vertex, so overlap is the test; no extra margin …
# … except these, whose capsules overlap slightly at poses the arm ran through contact-free on
# 2026-09-14 (minimum along the square and cube paths: lower arm–gripper −14 mm, shoulder–lower
# arm −17 mm, upper arm–wrist −1 mm; the folded rest pose, a real contact, reads −17 / −59 / −75)
SELF_ALLOW = {frozenset(("lower_arm_link", "gripper_link")): -0.015, frozenset(("shoulder_link", "lower_arm_link")): -0.020,
              frozenset(("upper_arm_link", "wrist_link")): -0.010}


def link_frames(frames):
    T = {"base_link": np.eye(4)}
    T.update({LINK_OF_JOINT[j]: frames[j] for j in LINK_OF_JOINT if j in frames})
    return T


def world_capsules(frames):
    out = {}
    for link, T in link_frames(frames).items():
        R, t = T[:3, :3], T[:3, 3]
        out[link] = [(R @ np.asarray(p0) + t, R @ np.asarray(p1) + t, r) for p0, p1, r in CAPSULES.get(link, [])]
    return out


def segment_distance(p0, p1, q0, q1):
    """Closest distance between segments p0p1 and q0q1 (Ericson, Real-Time Collision Detection 5.1.9)."""
    d1, d2, r = p1 - p0, q1 - q0, p0 - q0
    a, e, f = d1 @ d1, d2 @ d2, d2 @ r
    if a <= 1e-12 and e <= 1e-12:
        return float(np.linalg.norm(r))
    if a <= 1e-12:
        s, t = 0.0, np.clip(f / e, 0, 1)
    else:
        c = d1 @ r
        if e <= 1e-12:
            t, s = 0.0, np.clip(-c / a, 0, 1)
        else:
            b = d1 @ d2; den = a * e - b * b
            s = np.clip((b * f - c * e) / den, 0, 1) if den > 1e-12 else 0.0
            t = (b * s + f) / e
            if t < 0: t, s = 0.0, np.clip(-c / a, 0, 1)
            elif t > 1: t, s = 1.0, np.clip((b - c) / a, 0, 1)
    return float(np.linalg.norm((p0 + d1 * s) - (q0 + d2 * t)))


def pair_clearances(frames):
    """{(linkA, linkB): clearance} for every non-adjacent link pair — the smallest surface gap
    between any capsule of A and any of B (negative = overlapping)."""
    W = world_capsules(frames); out = {}
    for i, A in enumerate(LINK_ORDER):
        for B in LINK_ORDER[i + 1:]:
            if frozenset((A, B)) in ADJACENT or not W[A] or not W[B]:
                continue
            out[(A, B)] = min(segment_distance(a0, a1, b0, b1) - ra - rb for a0, a1, ra in W[A] for b0, b1, rb in W[B])
    return out


def self_collisions(frames, margin=SELF_MARGIN):
    """[(linkA, linkB, clearance)] for every tested pair closer than its allowed minimum
    (`margin`, or SELF_ALLOW for the two joint-crowded pairs). Empty = clear."""
    return [(a, b, c) for (a, b), c in pair_clearances(frames).items() if c < SELF_ALLOW.get(frozenset((a, b)), margin)]


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
        f = fk(joints, q)
        lim_ok, _ = within_limits(joints, q); clear, rear, nbad = keepout_clear(f, plane_x, margin); hits = self_collisions(f)
        res = dict(q=q, raw=rad_to_raw(q), err=err, limits_ok=lim_ok, clear=clear, rear_x=rear, violations=nbad, self_hits=hits,
                   ok=lim_ok and clear and not hits)
        if res["ok"]:
            return res
        if best is None or (res["limits_ok"] + res["clear"] + (not hits)) > (best["limits_ok"] + best["clear"] + (not best["self_hits"])):
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
    hits = self_collisions(frames)
    print("\nself-collision: " + ("none" if not hits else "; ".join(f"{a}–{b} {c*1000:+.0f} mm" for a, b, c in hits)))
    ok, worst, nbad = keepout_clear(frames)
    print(f"\nkeep-out (behind the desk edge x = {DESK_EDGE_X:.4f} and outside the {UPPER_ARM_RADIUS} m cylinder, every part, {LINK_RADIUS} m body): {'CLEAR' if ok else f'BREACHED ({nbad} points)'} (rearmost point outside the cylinder x = {worst:+.3f} m)")
    return 0 if ok and not hits else 1


if __name__ == "__main__":
    sys.exit(main())
