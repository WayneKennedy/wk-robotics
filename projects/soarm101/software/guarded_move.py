#!/usr/bin/env python3
"""Move the arm to a goal only if the whole path is inside the limits and clear of the keep-out.

Usage:  guarded_move.py --target X,Y,Z [--pitch DEG]        tool frame in base metres (+x forward,
                                                            +z up), pitch below horizontal
        guarded_move.py --raw pan,lift,elbow,wrist          joint goal in raw counts
        [--via-mid] [--dry-run] [--deg-per-step 1.5] [--rate 20] [--port /dev/ttyACM0] [--id wk_soarm101]

Not modelled: the arm's own base and the desk surface — do not plan from the folded rest pose,
where the gripper lies against the base (docs/hardware.md → Bench).
Precondition: torque ON and holding (hold_test.py --keep). Never toggles torque; nothing here
writes EEPROM. Plan: straight line in joint space from the present pose to the goal (via the
calibration mid pose first with --via-mid), sampled every --deg-per-step; every sample must be
inside the servos' saved limits (the measured stops ∓ 3°) less a further 3°, clear of the bench
keep-out, and free of self-collision between the capsule hit boxes (kinematics.py). A plan that
fails anywhere is refused before anything moves.
Execution streams the samples as goals at --rate Hz so the servos track the checked line rather
than each racing to the end at its own speed. Guards while moving, as extents_cycle.py: tracking
error, current, temperature — on a trip the goal is rewritten to the present position and the
arm holds there, torque on. wrist_roll and gripper are held at their present positions.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics as K

HERE = Path(__file__).resolve().parent
NAMES = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
MOVING = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex"]


def plan(joints, cal, start_raw, goal_raw, deg_per_step, margin_deg=3.0):
    # keep-out plane and margin: kinematics.keepout_clear defaults (desk edge + link radius)
    """Sampled joint-space line; returns (samples, report rows, ok)."""
    steps = max(1, int(np.ceil(max(abs(goal_raw[j] - start_raw[j]) for j in MOVING) / (deg_per_step / 360 * 4095))))
    rows = []; ok = True; samples = []
    for k in range(steps + 1):
        t = k / steps
        m = round(margin_deg / 360 * 4095)
        # commanded samples are clamped into the servos' saved range: the servo clamps there anyway,
        # and the calibration mid (2047) sits outside the elbow's shrunk range (servos.md)
        raw = {j: int(np.clip(round(start_raw[j] + (goal_raw[j] - start_raw[j]) * t), cal[j]["range_min"] + m, cal[j]["range_max"] - m)) for j in MOVING}
        raw.update({j: start_raw[j] for j in ("wrist_roll", "gripper") if j not in MOVING})
        q = K.raw_to_rad(raw); frames = K.fk(joints, q)
        # travel is judged against the MEASURED servo limits (cal_ok, below; stops ∓ 3° since 2026-09-14),
        # not the URDF's, which are narrower than this arm's real travel (shoulder by 10.5°, wrist 14.9°)
        # and refused a start on the shoulder's own stop. IK still chooses goals inside the URDF limits.
        lim_ok, bad = True, {}
        cal_ok = all(cal[j]["range_min"] + m <= raw[j] <= cal[j]["range_max"] - m for j in MOVING)
        clear, rear, _ = K.keepout_clear(frames); hits = K.self_collisions(frames)
        good = lim_ok and cal_ok and clear and not hits
        ok &= good; samples.append(raw)
        why = ("ok" if good else "urdf-limit " + str({j: round(v) for j, v in bad.items()}) if not lim_ok else "servo-limit" if not cal_ok
               else f"keep-out {rear:+.3f}" if not clear else "self-collision " + "; ".join(f"{a.split('_')[0]}–{b.split('_')[0]} {c*1000:+.0f} mm" for a, b, c in hits))
        rows.append((k, raw, why, rear))
    return samples, rows, ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target"); ap.add_argument("--pitch", type=float)
    ap.add_argument("--raw", help="pan,lift,elbow,wrist raw counts")
    ap.add_argument("--roll", type=int, help="also move wrist_roll to this raw count, planned and checked with the others")
    ap.add_argument("--gripper", type=int, help="also move the gripper to this raw count (jaw capsule checked like every other link)")
    ap.add_argument("--via-mid", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--deg-per-step", type=float, default=1.5); ap.add_argument("--rate", type=float, default=20)
    ap.add_argument("--track", type=int, default=150); ap.add_argument("--max-ma", type=float, default=900); ap.add_argument("--max-temp", type=int, default=60)
    ap.add_argument("--port", default="/dev/ttyACM0"); ap.add_argument("--id", default="wk_soarm101")
    ap.add_argument("--start-raw", help="dry-run only: pretend the arm is at these six raw counts")
    a = ap.parse_args()
    joints = K.load_urdf()
    cal = json.load(open(HERE / "calibration" / f"{a.id}.json"))

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
            if not all(v == 1 for v in te.values()):
                print(f"torque not on everywhere {te} — run hold_test.py --keep first"); return 2
            goal = b.sync_read("Goal_Position", normalize=False, num_retry=5)
            # stale goals from an earlier session differ by hundreds of counts; gravity lag under a horizontal forearm is ~30–40
            off = {m: goal[m] - present[m] for m in NAMES if abs(goal[m] - present[m]) > 60}
            if off:
                print(f"servo targets are not at the present pose {off} — not a verified hold, refusing"); return 2

    # goal
    if a.raw:
        goal_raw = dict(zip(MOVING, (int(x) for x in a.raw.split(","))))
    elif a.target:
        tgt = [float(x) for x in a.target.split(",")]
        q0 = {j: v for j, v in K.raw_to_rad(present).items() if j in MOVING}
        r = K.solve(joints, tgt, pitch=(np.radians(a.pitch) if a.pitch is not None else None), q0=q0)
        if r is None:
            print("IK: no converged solution"); return 3
        print(f"IK: residual {r['err']*1000:.1f} mm, limits {'ok' if r['limits_ok'] else 'VIOLATED'}, keep-out {'clear' if r['clear'] else 'BREACHED'} (rear x {r['rear_x']:+.3f}); "
              f"q° {{{', '.join(f'{j}: {np.degrees(v):+.1f}' for j, v in r['q'].items())}}}")
        if r["self_hits"]:
            print("IK: self-collision at the goal: " + "; ".join(f"{a}–{b} {c*1000:+.0f} mm" for a, b, c in r["self_hits"]))
        if not r["ok"]:
            print("goal itself is not acceptable — refusing"); return 3
        goal_raw = r["raw"]
    else:
        print("give --target or --raw"); return 2

    if a.roll is not None:              # the roll joins the planned, checked, streamed set (MOVING is read by plan() and the executor)
        MOVING.append("wrist_roll"); goal_raw["wrist_roll"] = a.roll
    if a.gripper is not None:
        MOVING.append("gripper"); goal_raw["gripper"] = a.gripper
    legs = []
    if a.via_mid:
        legs.append({j: 2047 for j in MOVING})
    legs.append(goal_raw)
    start = present; all_samples = []; all_ok = True
    for n, leg_goal in enumerate(legs, 1):
        samples, rows, ok = plan(joints, cal, start, leg_goal, a.deg_per_step)
        all_ok &= ok
        print(f"\nleg {n}: {len(samples)-1} steps, {'OK' if ok else 'REFUSED'}")
        print("| step | pan | lift | elbow | wrist | rear x (m) | verdict |\n|---|---|---|---|---|---|---|")
        show = [r for r in rows if r[0] in (0, len(rows) - 1) or r[2] != "ok" or r[0] % max(1, len(rows) // 6) == 0]
        for k, raw, verdict, rear in show:
            print(f"| {k} | {raw['shoulder_pan']} | {raw['shoulder_lift']} | {raw['elbow_flex']} | {raw['wrist_flex']} | {rear:+.3f} | {verdict} |")
        all_samples += samples[1:] if all_samples else samples
        start = {**start, **leg_goal}
    if not all_ok:
        print("\nplan refused — nothing moved"); return 1
    if a.dry_run:
        print("\ndry run — nothing moved"); return 0

    # execute
    for m in NAMES:
        b.write("Acceleration", m, 30, num_retry=5)
        b.write("Goal_Velocity", m, 600, normalize=False, num_retry=5)
    log = open(HERE / "logs" / f"guarded_{time.strftime('%Y%m%d_%H%M%S')}.csv", "w")
    log.write("t,step,pan,lift,elbow,wrist,pan_p,lift_p,elbow_p,wrist_p,max_mA,max_T,min_V\n")
    peak = 0.0; dt = 1.0 / a.rate; t0 = time.time(); over = {"ma": 0, "T": 0}   # two consecutive samples to trip: single bad reads happen

    def tele():
        p = b.sync_read("Present_Position", normalize=False, num_retry=5)
        c = b.sync_read("Present_Current", normalize=False, num_retry=5)
        t = b.sync_read("Present_Temperature", normalize=False, num_retry=5)
        v = b.sync_read("Present_Voltage", normalize=False, num_retry=5)
        return p, max(c.values()) * 6.5, max(t.values()), min(v.values()) / 10

    def hold_here(reason):
        p = b.sync_read("Present_Position", normalize=False, num_retry=5)
        b.sync_write("Goal_Position", p, normalize=False)
        print(f"\n== {reason} → holding at {p}, torque LEFT ON ==")

    try:
        for k, raw in enumerate(all_samples):
            b.sync_write("Goal_Position", {m: raw[m] for m in MOVING}, normalize=False)
            time.sleep(dt)
            p, ma, T, V = tele(); peak = max(peak, ma)
            log.write(f"{time.time()-t0:.2f},{k},{raw['shoulder_pan']},{raw['shoulder_lift']},{raw['elbow_flex']},{raw['wrist_flex']},{p['shoulder_pan']},{p['shoulder_lift']},{p['elbow_flex']},{p['wrist_flex']},{ma:.0f},{T},{V:.1f}\n")
            lag = max(abs(p[m] - raw[m]) for m in MOVING)
            if lag > a.track:
                hold_here(f"TRACKING: lag {lag} counts at step {k}"); return 1
            over["ma"] = over["ma"] + 1 if ma > a.max_ma else 0
            over["T"] = over["T"] + 1 if T > a.max_temp else 0
            if over["ma"] >= 2:
                hold_here(f"CURRENT: {ma:.0f} mA at step {k}"); return 1
            if over["T"] >= 2:
                hold_here(f"TEMPERATURE: {T} °C at step {k}"); return 1
        # settle on the final goal
        t1 = time.time()
        while time.time() - t1 < 2.0:
            p, ma, T, V = tele(); peak = max(peak, ma)
            if all(abs(p[m] - goal_raw[m]) <= 12 for m in MOVING):
                break
            time.sleep(0.05)
        p, ma, T, V = tele()
        q = K.raw_to_rad(p); frames = K.fk(joints, q); clear, rear, _ = K.keepout_clear(frames); tcp = frames["gripper_frame_joint"][:3, 3]
        print("\n| Joint | goal | reached | err |\n|---|---|---|---|")
        for m in MOVING:
            print(f"| `{m}` | {goal_raw[m]} | {p[m]} | {p[m]-goal_raw[m]:+d} |")
        print(f"\nreached in {time.time()-t0:.1f} s; peak {peak:.0f} mA; {T} °C max; {V:.1f} V min; tool at x {tcp[0]:+.3f} y {tcp[1]:+.3f} z {tcp[2]:+.3f} m; keep-out {'clear' if clear else 'BREACHED'} (rear x {rear:+.3f}); holding, torque ON")
        return 0
    except KeyboardInterrupt:
        hold_here("interrupted"); return 1
    finally:
        log.close()
        try: b.disconnect(disable_torque=False)
        except Exception: pass


if __name__ == "__main__":
    sys.exit(main())
