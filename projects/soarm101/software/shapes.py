#!/usr/bin/env python3
"""Trace a shape with the gripper tip, on a loop, under IK and the keep-out.

Usage:  shapes.py --shape square-yz|square-xy|square-xz|cube [--size 0.20] [--centre 0.24,0,0.06]
                  [--pitch 45] [--loops 3 | 0 = until stop file] [--tool-speed 5 (cm/s)] [--dry-run]
                  [--port /dev/ttyACM0] [--id wk_soarm101] [--stop-file software/.stop_shapes]

--centre is relative to the pan axis: metres forward, left, above the base plate. Every 1 cm
along the shape is solved by IK (position + pitch, warm-started from the previous point) and must
converge within 3 mm, sit inside the URDF and servo limits, clear the bench keep-out
(kinematics.keepout_clear: nothing behind the desk edge outside the cylinder), be free of
self-collision between the capsule hit boxes (kinematics.self_collisions) and move no joint
more than 10° from the previous point; one failure anywhere and nothing moves. The arm first
travels from its present pose to the shape's start on a guarded joint-space line (guarded_move.plan),
then streams the loop at --rate Hz with joint-space interpolation between points. Guards as
guarded_move.py; on a trip, or the stop file, or Ctrl-C, the goal is rewritten to the present
position and the arm holds, torque on. Precondition: torque ON and holding (hold_test.py --keep).
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics as K
from guarded_move import plan as joint_plan, NAMES, MOVING

HERE = Path(__file__).resolve().parent


def shape_segments(shape, c, s):
    c = np.asarray(c, float); h = s / 2
    if shape.startswith("square"):
        pl = shape.split("-")[1]
        P = {"yz": [c + [0, -h, -h], c + [0, h, -h], c + [0, h, h], c + [0, -h, h]],
             "xy": [c + [-h, -h, 0], c + [h, -h, 0], c + [h, h, 0], c + [-h, h, 0]],
             "xz": [c + [-h, 0, -h], c + [h, 0, -h], c + [h, 0, h], c + [-h, 0, h]]}[pl]
        return [(P[i], P[(i + 1) % 4]) for i in range(4)]
    if shape == "cube":
        b = [c + [-h, -h, -h], c + [h, -h, -h], c + [h, h, -h], c + [-h, h, -h]]
        t = [p + [0, 0, s] for p in b]
        path = [b[0], b[1], b[2], b[3], b[0], t[0], t[1], b[1], t[1], t[2], b[2], t[2], t[3], b[3], t[3], t[0], b[0]]
        return list(zip(path, path[1:]))
    raise SystemExit(f"unknown shape {shape}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shape", required=True); ap.add_argument("--size", type=float, default=0.20)
    ap.add_argument("--centre", default="0.24,0,0.06"); ap.add_argument("--pitch", type=float, default=45)
    ap.add_argument("--loops", type=int, default=3); ap.add_argument("--tool-speed", type=float, default=5.0)
    ap.add_argument("--rate", type=float, default=20); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--track", type=int, default=150); ap.add_argument("--max-ma", type=float, default=900); ap.add_argument("--max-temp", type=int, default=60)
    ap.add_argument("--port", default="/dev/ttyACM0"); ap.add_argument("--id", default="wk_soarm101")
    ap.add_argument("--stop-file", default=str(HERE / ".stop_shapes"))
    ap.add_argument("--start-raw", help="dry-run only: pretend the arm is at these six raw counts")
    a = ap.parse_args()
    joints = K.load_urdf(); cal = json.load(open(HERE / "calibration" / f"{a.id}.json"))
    dx, dy, dz = (float(v) for v in a.centre.split(","))
    centre = (K.PAN_AXIS_X + dx, dy, dz)
    stop_file = Path(a.stop_file); stop_file.unlink(missing_ok=True)

    # --- solve the shape
    segs = shape_segments(a.shape, centre, a.size); pts = []
    for p0, p1 in segs:
        n = max(1, int(np.ceil(np.linalg.norm(p1 - p0) / 0.01)))
        pts += [p0 + (p1 - p0) * t for t in np.linspace(0, 1, n + 1)[:-1]]
    pts.append(segs[-1][1])
    q0 = None; sols = []; worst = 0.0; rear = 9
    for i, p in enumerate(pts):
        r = K.solve(joints, p, pitch=np.radians(a.pitch), q0=q0)
        if r is None or r["err"] > 0.003 or not r["ok"]:
            print(f"point {i} at {np.round(p, 3)}: " + ("no solution" if r is None else f"err {r['err']*1000:.1f} mm limits {r['limits_ok']} keep-out {r['clear']} self-collision {[(a, b, round(c*1000)) for a, b, c in r['self_hits']]}") + " — refused"); return 1
        m = 3 / 360 * 4095
        if not all(cal[j]["range_min"] + m <= r["raw"][j] <= cal[j]["range_max"] - m for j in MOVING):
            print(f"point {i}: outside the servos' saved limits {r['raw']} — refused"); return 1
        if q0 and max(abs(r["q"][j] - q0[j]) for j in MOVING) > np.radians(10):
            print(f"point {i}: joint jump > 10° from the previous point — refused"); return 1
        q0 = dict(r["q"]); sols.append(r); worst = max(worst, r["err"]); rear = min(rear, r["rear_x"])
    print(f"{a.shape} {a.size*100:.0f} cm, centre {np.round(centre,3)}, pitch {a.pitch}°: {len(pts)} points solved, worst {worst*1000:.1f} mm, rearmost point outside the cylinder x {rear:+.3f} m")
    first = sols[0]["raw"]

    # --- bus
    from lerobot.motors import Motor, MotorNormMode
    from lerobot.motors.feetech import FeetechMotorsBus
    b = None
    if a.start_raw and a.dry_run:
        present = dict(zip(NAMES, (int(x) for x in a.start_raw.split(","))))
    else:
        b = FeetechMotorsBus(a.port, {n: Motor(i + 1, "sts3215", MotorNormMode.RANGE_M100_100) for i, n in enumerate(NAMES)})
        b.connect(handshake=False)
        present = b.sync_read("Present_Position", normalize=False, num_retry=5)
        if not a.dry_run:
            te = {m: b.read("Torque_Enable", m, normalize=False, num_retry=5) for m in NAMES}
            goal = b.sync_read("Goal_Position", normalize=False, num_retry=5)
            off = {m: goal[m] - present[m] for m in NAMES if abs(goal[m] - present[m]) > 30}
            if not all(v == 1 for v in te.values()) or off:
                print(f"torque {te}, targets off present {off} — run hold_test.py --keep first"); return 2
    approach, rows, ok = joint_plan(joints, cal, present, first, 1.5)
    print(f"approach to the start: {len(approach)-1} steps, {'OK' if ok else 'REFUSED'}")
    if not ok:
        for k, raw, verdict, r_ in rows:
            if verdict != "ok": print(f"  step {k}: {verdict}"); break
        return 1
    if a.dry_run:
        print("dry run — nothing moved"); return 0

    # --- execute
    for m in NAMES:
        b.write("Acceleration", m, 30, num_retry=5); b.write("Goal_Velocity", m, 800, normalize=False, num_retry=5)
    log = open(HERE / "logs" / f"shapes_{time.strftime('%Y%m%d_%H%M%S')}.csv", "w", newline=""); w = csv.writer(log)
    w.writerow(["t", "loop", "point", *MOVING, *[m + "_p" for m in MOVING], "max_mA", "max_T", "min_V"])
    dt = 1 / a.rate; t0 = time.time(); peak = 0.0

    def tele():
        p = b.sync_read("Present_Position", normalize=False, num_retry=5)
        c = b.sync_read("Present_Current", normalize=False, num_retry=5)
        t = b.sync_read("Present_Temperature", normalize=False, num_retry=5)
        v = b.sync_read("Present_Voltage", normalize=False, num_retry=5)
        return p, max(c.values()) * 6.5, max(t.values()), min(v.values()) / 10

    def hold_here(reason):
        p = b.sync_read("Present_Position", normalize=False, num_retry=5)
        b.sync_write("Goal_Position", p, normalize=False)
        print(f"\n== {reason} → holding, torque LEFT ON ==")

    over = {"ma": 0, "T": 0}     # a single bad sample is a corrupted read (130 °C after 38 °C, 2026-09-14): trip on two in a row

    def step(raw, loop, i):
        nonlocal peak
        b.sync_write("Goal_Position", {m: raw[m] for m in MOVING}, normalize=False)
        time.sleep(dt)
        p, ma, T, V = tele()
        w.writerow([f"{time.time()-t0:.2f}", loop, i, *[raw[m] for m in MOVING], *[p[m] for m in MOVING], f"{ma:.0f}", T, f"{V:.1f}"])
        lag = max(abs(p[m] - raw[m]) for m in MOVING)
        if lag > a.track: hold_here(f"TRACKING lag {lag} at loop {loop} point {i}"); return False
        over["ma"] = over["ma"] + 1 if ma > a.max_ma else 0
        over["T"] = over["T"] + 1 if T > a.max_temp else 0
        if over["ma"] < 2: peak = max(peak, ma) if ma <= a.max_ma else peak
        if over["ma"] >= 2: hold_here(f"CURRENT {ma:.0f} mA at loop {loop} point {i}"); return False
        if over["T"] >= 2: hold_here(f"TEMPERATURE {T} °C"); return False
        if stop_file.exists(): hold_here("stop file"); return False
        return True

    try:
        for i, raw in enumerate(approach):
            if not step({**present, **raw}, 0, i): return 1
        time.sleep(0.5)
        per_point = max(1, int(round(a.rate / a.tool_speed)))     # 1 cm points at tool-speed cm/s
        loop = 0
        while a.loops == 0 or loop < a.loops:
            loop += 1
            for i in range(len(sols) - 1):
                r0, r1 = sols[i]["raw"], sols[i + 1]["raw"]
                for k in range(1, per_point + 1):
                    t = k / per_point
                    if not step({m: int(round(r0[m] + (r1[m] - r0[m]) * t)) for m in MOVING}, loop, i): return 1
            p, ma, T, V = tele()
            print(f"loop {loop} done  {time.time()-t0:.0f} s  peak {peak:.0f} mA  {T} °C  {V:.1f} V")
        p, ma, T, V = tele(); tcp = K.fk(joints, K.raw_to_rad(p))["gripper_frame_joint"][:3, 3]
        print(f"\ndone: {loop} loops, peak {peak:.0f} mA, {T} °C, {V:.1f} V min; tool at {np.round(tcp,3)}; holding at the shape start, torque ON")
        return 0
    except KeyboardInterrupt:
        hold_here("interrupted"); return 1
    finally:
        log.close()
        try: b.disconnect(disable_torque=False)
        except Exception: pass


if __name__ == "__main__":
    sys.exit(main())
