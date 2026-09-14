#!/usr/bin/env python3
"""Find one joint's mechanical stops by gentle contact, and derive its zero and travel.

Usage:  find_stops.py JOINT [--dir min|max|both] [--torque 180] [--step-deg 1.0] [--dwell 0.25]
                      [--stall 40] [--stall-steps 3] [--max-ma 500] [--beyond-deg 20] [--dry-run]
                      [--port /dev/ttyACM0] [--id wk_soarm101] [--out calibration/stops.json]

Why: the servo limits were a hand sweep pulled in 10 % at each end, and the count-to-angle zero
is only good to ±10° (servos.md). Measuring where each joint actually stops, in raw counts,
gives the limit directly and — because upstream's URDF puts every joint's zero at the middle
of its travel — the zero as the midpoint of the two stops.

How: precondition torque ON and holding (hold_test.py --keep). Only JOINT moves; the others
hold at full torque. JOINT's Torque_Limit is dropped to --torque (too weak to damage a printed
stop; 150 moved nothing it should not on 2026-09-14), then its goal is stepped --step-deg at a
time toward the stop. Contact = the servo falls --stall counts behind its goal for --stall-steps
consecutive steps, or reads over --max-ma twice in a row. The present position at contact is
the stop. The goal is then pulled back 5° and the joint returns to where it started at the
weak torque before the limit is restored to 1000. Ceilings: the sweep never goes beyond the
URDF's limit for that joint plus --beyond-deg (mapped through the current zero estimate), and
every step is checked against the world keep-out (kinematics.keepout_clear). Link-on-link
self-collision is NOT a veto — that contact is one of the things being measured — but a
predicted capsule touch against the base stops the sweep, as does the world keep-out; other
overlaps are printed as the stop forms. Still set the other joints first so that JOINT's sweep is sensible (docs/servos.md).
Results are appended to --out as {joint: {min, max, zero, span_deg, date}} and printed with
the suggested limits (stop ∓ 3°); nothing is written to a servo's EEPROM here.
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
CPD = 4095 / 360.0   # counts per degree


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("joint", choices=NAMES[:4] + ["gripper"])
    ap.add_argument("--dir", choices=["min", "max", "both"], default="both")
    ap.add_argument("--torque", type=int, default=180); ap.add_argument("--step-deg", type=float, default=1.0)
    ap.add_argument("--dwell", type=float, default=0.25); ap.add_argument("--stall", type=int, default=40)
    ap.add_argument("--stall-steps", type=int, default=3); ap.add_argument("--max-ma", type=float, default=500)
    ap.add_argument("--beyond-deg", type=float, default=20); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-base-veto", action="store_true", help="let stall detection judge contact with the base: the fitted capsules are "
                    "conservative (they enclose horn bulges) and stop some sweeps before the real contact; keep-out still applies")
    ap.add_argument("--port", default="/dev/ttyACM0"); ap.add_argument("--id", default="wk_soarm101")
    ap.add_argument("--out", default=str(HERE / "calibration" / "stops.json"))
    a = ap.parse_args()
    J = K.load_urdf(); j = a.joint
    zero_raw, sign, _ = K.JOINT_ZERO[j]
    lo_urdf, hi_urdf = np.degrees(J[j]["limit"])
    ceil = {"min": int(zero_raw + sign * (lo_urdf - a.beyond_deg) * CPD), "max": int(zero_raw + sign * (hi_urdf + a.beyond_deg) * CPD)}
    if sign < 0: ceil = {"min": ceil["max"], "max": ceil["min"]}
    print(f"{j}: current zero estimate raw {zero_raw}, URDF travel {lo_urdf:+.0f}…{hi_urdf:+.0f}°, sweep ceilings raw {ceil['min']}…{ceil['max']}")

    from lerobot.motors import Motor, MotorNormMode
    from lerobot.motors.feetech import FeetechMotorsBus
    b = FeetechMotorsBus(a.port, {n: Motor(i + 1, "sts3215", MotorNormMode.RANGE_M100_100) for i, n in enumerate(NAMES)})
    b.connect(handshake=False)
    present = b.sync_read("Present_Position", normalize=False, num_retry=5)
    te = {m: b.read("Torque_Enable", m, normalize=False, num_retry=5) for m in NAMES}
    goal = b.sync_read("Goal_Position", normalize=False, num_retry=5)
    off = {m: goal[m] - present[m] for m in NAMES if abs(goal[m] - present[m]) > 30}
    if not all(v == 1 for v in te.values()) or off:
        print(f"torque {te}, targets off present {off} — run hold_test.py --keep first"); return 2
    start = present[j]
    print(f"start raw {start} = {sign*(start-zero_raw)/CPD:+.1f}° (current estimate); others hold at {{{', '.join(f'{m}: {present[m]}' for m in NAMES if m != j)}}}")
    if a.dry_run:
        print("dry run — nothing moved"); return 0

    # servo EEPROM limits would clamp the sweep short of the stop: read them, widen to the ceilings for
    # the run (RAM write of an EEPROM register — restored afterwards, and re-verified by the tools anyway)
    lim0 = (b.read("Min_Position_Limit", j, normalize=False, num_retry=5), b.read("Max_Position_Limit", j, normalize=False, num_retry=5))
    print(f"servo limits {lim0} → widened to ({max(0, ceil['min'])}, {min(4095, ceil['max'])}) for the sweep")
    b.write("Min_Position_Limit", j, max(0, ceil["min"]), normalize=False, num_retry=5)
    b.write("Max_Position_Limit", j, min(4095, ceil["max"]), normalize=False, num_retry=5)
    b.write("Torque_Limit", j, a.torque, normalize=False, num_retry=5)
    b.write("Acceleration", j, 20, num_retry=5); b.write("Goal_Velocity", j, 300, normalize=False, num_retry=5)
    found = {}

    def read():
        p = b.read("Present_Position", j, normalize=False, num_retry=5)
        c = b.read("Present_Current", j, normalize=False, num_retry=5) * 6.5
        return p, c

    def go_to(target, speed_deg_s=8):
        cur = read()[0]; steps = max(1, int(abs(target - cur) / (a.step_deg * CPD)))
        for k in range(1, steps + 1):
            b.write("Goal_Position", j, int(cur + (target - cur) * k / steps), normalize=False, num_retry=5)
            time.sleep(a.step_deg / speed_deg_s)
        time.sleep(0.5)

    try:
        for d in (["min", "max"] if a.dir == "both" else [a.dir]):
            sgn = -1 if d == "min" else +1
            g = start; stalled = 0; over = 0; stop = None
            print(f"\n→ towards {d} (raw {'decreasing' if sgn < 0 else 'increasing'}), torque {a.torque}, {a.step_deg}° per {a.dwell}s")
            while True:
                g = int(g + sgn * a.step_deg * CPD)
                if not 0 <= g <= 4095:
                    print(f"   reached the encoder wrap (goal {g}) without contact — no stop found; re-home this joint so its travel sits inside 0…4095"); break
                if (sgn < 0 and g < ceil["min"]) or (sgn > 0 and g > ceil["max"]):
                    print(f"   reached the sweep ceiling {g} without contact — no stop found (the joint travels further than the URDF says: raise --beyond-deg)"); break
                # world keep-out on the pose this step would make
                raw_pose = dict(present); raw_pose[j] = g
                fr = K.fk(J, K.raw_to_rad(raw_pose)); clear, rear, nbad = K.keepout_clear(fr)
                if not clear:
                    print(f"   keep-out would be breached at raw {g} ({nbad} points, rear x {rear:+.3f}) — stopping the sweep here, no stop found"); break
                # link-on-link contact is what a stop is, so self-collision is not a veto — except against the
                # base and shoulder, which are the world as far as a moving joint is concerned
                hits = K.self_collisions(fr)
                base_hits = [(x, y, c) for x, y, c in hits if "base_link" in (x, y)]
                other = [(x, y, c) for x, y, c in hits if "base_link" not in (x, y)]
                if base_hits and j != "shoulder_pan" and not a.no_base_veto:
                    print(f"   capsules would touch the base at raw {g}: " + "; ".join(f"{x.split('_')[0]}–{y.split('_')[0]} {c*1000:+.0f} mm" for x, y, c in base_hits) + " — stopping the sweep here, no stop found"); break
                if base_hits and a.no_base_veto:
                    other = base_hits + other
                if other:
                    print(f"   (capsules overlapping — may be the stop forming: " + "; ".join(f"{x.split('_')[0]}–{y.split('_')[0]} {c*1000:+.0f} mm" for x, y, c in other) + ")")
                b.write("Goal_Position", j, g, normalize=False, num_retry=5)
                time.sleep(a.dwell)
                p, c = read(); lag = abs(p - g)
                stalled = stalled + 1 if lag > a.stall else 0
                over = over + 1 if c > a.max_ma else 0
                print(f"   goal {g:4d}  present {p:4d}  lag {lag:3d}  {c:4.0f} mA", flush=True)
                if stalled >= a.stall_steps or over >= 2:
                    stop = p; print(f"   CONTACT: {'stalled' if stalled >= a.stall_steps else 'current'} — stop at raw {stop} ({sign*(stop-zero_raw)/CPD:+.1f}° by the current zero)"); break
            back = int((stop if stop is not None else read()[0]) - sgn * 5 * CPD)
            b.write("Goal_Position", j, back, normalize=False, num_retry=5); time.sleep(0.6)
            found[d] = stop
            if stop is not None:
                res = json.load(open(a.out)) if Path(a.out).exists() else {}
                rec = res.get(j, {}); rec[d] = stop; rec["date"] = time.strftime("%Y-%m-%d"); rec.pop("note", None)
                res[j] = rec; Path(a.out).parent.mkdir(exist_ok=True); json.dump(res, open(a.out, "w"), indent=2)
            go_to(start)
            print(f"   back at {read()[0]} (start {start})")
        # report
        res = json.load(open(a.out)) if Path(a.out).exists() else {}
        rec = res.get(j, {})
        rec.update({k: v for k, v in found.items() if v is not None}); rec["date"] = time.strftime("%Y-%m-%d"); rec.pop("note", None)
        if "min" in rec and "max" in rec:
            rec["span_deg"] = round((rec["max"] - rec["min"]) / CPD, 1)
            if j != "gripper":      # URDF zero = mid-travel for the arm joints; the gripper's URDF travel (−10…+100°) is not symmetric
                rec["zero"] = int(round((rec["min"] + rec["max"]) / 2))
        res[j] = rec; Path(a.out).parent.mkdir(exist_ok=True); json.dump(res, open(a.out, "w"), indent=2)
        print(f"\n{j}: " + ", ".join(f"{k} {v}" for k, v in rec.items()))
        if "span_deg" in rec:
            if "zero" in rec:
                print(f"   zero {rec['zero']} vs estimate {zero_raw} ({(rec['zero']-zero_raw)/CPD:+.1f}°); span {rec['span_deg']}° vs URDF {hi_urdf-lo_urdf:.1f}°")
            else:
                print(f"   span {rec['span_deg']}° vs URDF {hi_urdf-lo_urdf:.1f}° (no zero derived: travel not symmetric about the URDF zero)")
            print(f"   suggested servo limits (stop ∓ 3°): {int(rec['min'] + 3*CPD)} … {int(rec['max'] - 3*CPD)}   (were {lim0})")
        print(f"saved to {a.out}")
        return 0
    except KeyboardInterrupt:
        print("interrupted — returning to start"); go_to(start); return 1
    finally:
        try:
            b.write("Torque_Limit", j, 1000, normalize=False, num_retry=5)
            b.write("Min_Position_Limit", j, lim0[0], normalize=False, num_retry=5)
            b.write("Max_Position_Limit", j, lim0[1], normalize=False, num_retry=5)
            print(f"torque limit 1000 and servo limits {lim0} restored on {j}; still holding")
        except Exception as e:
            print("restore failed:", e)
        try: b.disconnect(disable_torque=False)
        except Exception: pass


if __name__ == "__main__":
    sys.exit(main())
