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


def sample_leg(cal, start_raw, goal_raw, deg_per_step, m):
    """Raw samples along a joint-space line, clamped into the servos' saved range less m counts
    (the servo clamps there anyway; a start outside it — e.g. a folded elbow pushed past its limit
    by gravity — is pulled in by the first sample)."""
    steps = max(1, int(np.ceil(max(abs(goal_raw[j] - start_raw[j]) for j in MOVING) / (deg_per_step / 360 * 4095))))
    out = []
    for k in range(steps + 1):
        t = k / steps
        # no clamping: the line runs from where the arm is to a goal inside the limits, so a joint that starts
        # outside them (a droop onto a stop) comes inward gradually; evaluate() refuses any step that goes further out
        raw = {j: int(round(start_raw[j] + (goal_raw[j] - start_raw[j]) * t)) for j in MOVING}
        raw.update({j: start_raw[j] for j in ("wrist_roll", "gripper") if j not in MOVING})
        out.append(raw)
    # the first sample is where the arm IS, unclamped: the step from it into the limits is then checked
    # like every other step (a start outside the limits is pulled in by the next sample)
    out[0] = {**out[0], **{j: start_raw[j] for j in MOVING}}
    return out


ESCAPE_TOL = 0.010   # m: a contact present at the start may get this much deeper than it began — the capsules enclose every
                     # mesh vertex, so they overstate the parts; the real rest pose of 2026-09-14 needs ~5 mm (test-log)
READY_POSE = {"shoulder_pan": 1981, "shoulder_lift": 1925, "elbow_flex": 3031, "wrist_flex": 2070}   # the measured zero pose
ESCAPE_TORQUE = 500  # Torque_Limit while waking: any real contact is gentle on the gears


def evaluate(joints, cal, samples, m, escape=False):
    """Check every sample: servo limits (measured, less m), keep-out, self-collision. With
    escape=True a path may START in contact (an unpowered arm droops into one — owner, 2026-09-15)
    provided that, until the first clear sample, it never makes a NEW contact pair, never takes a
    starting pair more than ESCAPE_TOL deeper than it began, never adds keep-out points, and that it
    ends clear; after the first clear sample it must stay clear. Returns (rows, ok)."""
    rows = []; ok = True; phase = None; prev = None; start_pairs = None
    for k, raw in enumerate(samples):
        frames = K.fk(joints, K.raw_to_rad(raw))
        # limits: every sample inside the 3° planning margin, or — for a joint that started outside it (a droop
        # onto a stop) — no further outside than the sample before; the first sample is where the arm already is
        band = lambda j, x: max(cal[j]["range_min"] + m - x, 0, x - (cal[j]["range_max"] - m))
        cal_ok = k == 0 or all(band(j, raw[j]) == 0 or band(j, raw[j]) <= band(j, samples[k - 1][j]) for j in MOVING)
        clear, rear, nbad = K.keepout_clear(frames); hits = K.self_collisions(frames)
        pairs = {(a, b): c for a, b, c in hits}; nko = 0 if clear else nbad
        fmt = lambda ps: "; ".join(f"{a.split('_')[0]}–{b.split('_')[0]} {c*1000:+.0f} mm" for (a, b), c in ps.items())
        if not pairs and clear:
            good = cal_ok; why = "ok" if cal_ok else "servo-limit"; phase = "clear" if phase != "clear" and cal_ok else phase
            if phase is None: phase = "clear"
        elif escape and phase in (None, "escape"):
            if phase is None:
                good = cal_ok; why = f"start in contact, escape allowed: {fmt(pairs) or 'keep-out'}"; start_pairs = dict(pairs)
            else:
                pp, pn = prev
                new = {p: c for p, c in pairs.items() if p not in start_pairs}
                deeper = {p: c for p, c in pairs.items() if p in start_pairs and c < start_pairs[p] - ESCAPE_TOL}
                good = cal_ok and not new and not deeper and nko <= pn
                why = ("escaping" if good else "servo-limit" if not cal_ok else f"new contact {fmt(new)}" if new
                       else f"contact deepening {fmt(deeper)}" if deeper else f"keep-out worsening ({nko} points)")
            phase = "escape"; prev = (pairs, nko)
        else:
            good = False
            why = "servo-limit" if not cal_ok else f"keep-out {rear:+.3f}" if not clear else "self-collision " + fmt(pairs)
        ok &= good
        rows.append((k, raw, why, rear))
    if escape and phase == "escape":
        ok = False; rows[-1] = (rows[-1][0], rows[-1][1], "path ends still in contact", rows[-1][3])
    return rows, ok


def plan(joints, cal, start_raw, goal_raw, deg_per_step, margin_deg=3.0, escape=False):
    """Sampled joint-space line, checked; returns (samples, report rows, ok). Travel is judged
    against the MEASURED servo limits (stops ∓ 3° since 2026-09-14), not the URDF's; IK still
    chooses goals inside the URDF limits."""
    m = round(margin_deg / 360 * 4095)
    samples = sample_leg(cal, start_raw, goal_raw, deg_per_step, m)
    rows, ok = evaluate(joints, cal, samples, m, escape)
    return samples, rows, ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target"); ap.add_argument("--pitch", type=float)
    ap.add_argument("--raw", help="pan,lift,elbow,wrist raw counts")
    ap.add_argument("--roll", type=int, help="also move wrist_roll to this raw count, planned and checked with the others")
    ap.add_argument("--gripper", type=int, help="also move the gripper to this raw count (jaw capsule checked like every other link)")
    ap.add_argument("--unfold", action="store_true", help="the start may be in contact (e.g. the folded rest pose): allow escaping "
                    "out of contact; if the direct line fails, try moving the joints one at a time in every order")
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
    elif a.unfold:
        goal_raw = dict(READY_POSE); print(f"unfold: no goal given — waking to the ready pose {goal_raw}")
    else:
        print("give --target or --raw (or --unfold for the ready pose)"); return 2

    if a.roll is not None:              # the roll joins the planned, checked, streamed set (MOVING is read by plan() and the executor)
        MOVING.append("wrist_roll"); goal_raw["wrist_roll"] = a.roll
    if a.gripper is not None:
        MOVING.append("gripper"); goal_raw["gripper"] = a.gripper
    if a.unfold:
        import itertools
        m = round(3.0 / 360 * 4095)
        movers = [j for j in MOVING if goal_raw[j] != present[j]]
        cands = [("direct line", [goal_raw])]
        for perm in itertools.permutations(movers):
            seq, cur = [], dict(present)
            for j in perm:
                cur = {**cur, j: goal_raw[j]}; seq.append({jj: cur[jj] for jj in MOVING})
            cands.append(("one joint at a time: " + " → ".join(perm), seq))
        chosen = None; first_fail = None
        for label, seq in cands:
            samples, start = [], dict(present)
            for leg in seq:
                s_ = sample_leg(cal, start, leg, a.deg_per_step, m)
                samples += s_[1:] if samples else s_
                start = {**start, **leg}
            rows, ok = evaluate(joints, cal, samples, m, escape=True)
            if ok:
                chosen = (label, samples, rows); break
            if first_fail is None:
                first_fail = (label, next(r for r in rows if not (r[2] == "ok" or r[2] == "escaping" or r[2].startswith("start in contact"))))
        if chosen is None:
            print(f"unfold: none of {len(cands)} candidate paths escapes cleanly; direct line refused at step {first_fail[1][0]}: {first_fail[1][2]}")
            print("plan refused — nothing moved")
            if b is not None:
                wid = [m for m in NAMES if (b.read("Min_Position_Limit", m, normalize=False, num_retry=5), b.read("Max_Position_Limit", m, normalize=False, num_retry=5)) != (cal[m]["range_min"], cal[m]["range_max"])]
                if wid:
                    print(f"WARNING: servo limits are widened in RAM on {wid} (hold_test.py --wake). Release torque or power-cycle to restore them.")
            return 1
        label, all_samples, rows = chosen
        esc = [r for r in rows if r[2] == "escaping" or r[2].startswith("start in contact")]
        print(f"unfold: {label} — {len(all_samples)-1} steps, OK; in contact for the first {len(esc)} samples, clear after")
        print("| step | pan | lift | elbow | wrist | verdict |\n|---|---|---|---|---|---|")
        for k, raw, verdict, rear in [r for r in rows if r[0] in (0, len(rows) - 1) or r[0] % max(1, len(rows) // 8) == 0 or (r[2] != "ok" and r[0] <= len(esc))][:20]:
            print(f"| {k} | {raw['shoulder_pan']} | {raw['shoulder_lift']} | {raw['elbow_flex']} | {raw['wrist_flex']} | {verdict[:70]} |")
        all_ok = True
        if a.dry_run:
            print("\ndry run — nothing moved"); return 0
        legs = []
    else:
        legs = []
    if a.via_mid and not a.unfold:
        legs.append({j: 2047 for j in MOVING})
    legs.append(goal_raw)
    if not a.unfold:
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
        if a.unfold:
            b.write("Torque_Limit", m, ESCAPE_TORQUE, normalize=False, num_retry=5)
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
        if a.unfold:                            # clear of contact and at the goal: back to full torque
            for m in NAMES:
                b.write("Torque_Limit", m, 1000, normalize=False, num_retry=5)
            time.sleep(0.3)
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
        if a.unfold:                                  # hold_test.py --wake may have widened limits in RAM: put the saved ones back
            for m in NAMES:
                try:
                    b.write("Lock", m, 1, normalize=False, num_retry=5)
                    b.write("Min_Position_Limit", m, cal[m]["range_min"], normalize=False, num_retry=5)
                    b.write("Max_Position_Limit", m, cal[m]["range_max"], normalize=False, num_retry=5)
                except Exception as e:
                    print(m, "limit restore FAILED:", str(e)[-60:])
            print("saved servo limits restored (RAM; EEPROM never changed)")
        log.close()
        try: b.disconnect(disable_torque=False)
        except Exception: pass


if __name__ == "__main__":
    sys.exit(main())
