#!/usr/bin/env python3
"""First controlled move: hands-off hold, then absolute nudges from the start pose, one joint at a time.

Usage: first_move.py [--port] [--id wk_soarm101] [--delta 3] [--dwell 1.5] [--torque-limit 1000]
                     [--hold 5] [--joints a,b] [--max-drift 3]

Sequence (RAM registers only; nothing here touches EEPROM or toggles torque):
  1. requires torque already ON and holding — run hold_test.py --keep first (the verified
     weak-torque-first sequence, servos.md); refuses if any servo target is off its present position.
  2. confirms the hold is quiet for --hold seconds: abort (keep torque) if any joint drifts > --max-drift °.
  3. for each joint: goal = start ± --delta, then back to start, as ABSOLUTE goals built from
     the start pose — no present-based clamp (servos.md rule 3). After each step read position,
     current, load; abort with torque off if any *other* joint has left start by > --max-drift.
  4. torque is LEFT ON holding the start pose at the end and on every abort, so the arm never
     drops; release with release_torque.py once someone supports it.
"""
import argparse
import sys
import time

from lerobot.robots.so_follower import SOFollower, SOFollowerRobotConfig

ORDER = ["wrist_roll", "gripper", "wrist_flex", "elbow_flex", "shoulder_pan", "shoulder_lift"]


def torque_off(b):
    for m in b.motors:
        try:
            b.write("Torque_Enable", m, 0, normalize=False, num_retry=5)
        except Exception as e:
            print(m, "torque release failed:", str(e)[-40:])


def deg(r, m, raw):
    id_ = r.bus.motors[m].id
    return r.bus._normalize({id_: raw})[id_]


def read_all(b):
    p = b.sync_read("Present_Position", normalize=False, num_retry=5)
    c = b.sync_read("Present_Current", normalize=False, num_retry=5)
    l = b.sync_read("Present_Load", normalize=False, num_retry=5)
    t = b.sync_read("Present_Temperature", normalize=False, num_retry=5)
    return p, c, l, t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", default="/dev/ttyACM0")
    ap.add_argument("--id", default="wk_soarm101")
    ap.add_argument("--delta", type=float, default=3.0, help="degrees; gripper in 0..100 units")
    ap.add_argument("--dwell", type=float, default=1.5)
    ap.add_argument("--hold", type=float, default=5.0)
    ap.add_argument("--torque-limit", type=int, default=1000)
    ap.add_argument("--max-drift", type=float, default=3.0, help="degrees another joint may move before abort")
    ap.add_argument("--joints", default=",".join(ORDER))
    a = ap.parse_args()
    joints = [j for j in a.joints.split(",") if j]

    r = SOFollower(SOFollowerRobotConfig(port=a.port, id=a.id, max_relative_target=None))
    b = r.bus
    b.connect(handshake=False)
    try:
        if not r.is_calibrated:
            print("servos do not match saved calibration — refusing"); return 2
        # Precondition: torque already ON and holding, established by hold_test.py --keep (the only
        # verified torque-on sequence). This tool never toggles torque itself.
        te = {m: b.read("Torque_Enable", m, normalize=False, num_retry=5) for m in b.motors}
        if not all(v == 1 for v in te.values()):
            print(f"torque is not on everywhere {te} — run hold_test.py --keep first"); return 2
        for m in b.motors:
            b.write("Torque_Limit", m, a.torque_limit, normalize=False, num_retry=5)
        start_raw = b.sync_read("Present_Position", normalize=False, num_retry=5)
        goal_now = b.sync_read("Goal_Position", normalize=False, num_retry=5)
        off = {m: goal_now[m] - start_raw[m] for m in b.motors if abs(goal_now[m] - start_raw[m]) > 20}
        if off:
            print(f"servo targets differ from present by > 20 counts {off} — not a settled hold, refusing"); return 2
        start = {m: deg(r, m, start_raw[m]) for m in b.motors}

        # 2. confirm the hold is still quiet for --hold seconds before touching anything
        t0 = time.time(); worst = {m: 0.0 for m in b.motors}
        while time.time() - t0 < a.hold:
            p, c, l, t = read_all(b)
            for m in b.motors:
                worst[m] = max(worst[m], abs(deg(r, m, p[m]) - start[m]))
            if max(worst.values()) > a.max_drift:
                bad = max(worst, key=worst.get)
                print(f"ABORT during hold: {bad} drifted {worst[bad]:.1f}° — torque LEFT ON"); return 1
            time.sleep(0.1)
        p, c, l, t = read_all(b)
        print(f"hold {a.hold:.0f} s OK. | Joint | Start ° | Drift ° | mA | Load | °C |\n|---|---|---|---|---|---|")
        for m in b.motors:
            print(f"| `{m}` | {start[m]:.1f} | {worst[m]:.1f} | {c[m]*6.5:.0f} | {l[m]} | {t[m]} |")

        # 3. absolute nudges
        print("\n| Joint | Command | Reached | Δ | mA | Load | °C | Others max drift ° |\n|---|---|---|---|---|---|---|---|")
        for m in joints:
            for sign in (+1, -1, 0):
                goal = dict(start); goal[m] = start[m] + sign * a.delta
                b.sync_write("Goal_Position", goal)             # normalised → raw, absolute
                time.sleep(a.dwell)
                p, c, l, t = read_all(b)
                reached = deg(r, m, p[m])
                others = max(abs(deg(r, j, p[j]) - start[j]) for j in b.motors if j != m)
                print(f"| `{m}` | {goal[m]:.1f} | {reached:.1f} | {reached-goal[m]:+.1f} | {c[m]*6.5:.0f} | {l[m]} | {t[m]} | {others:.1f} |")
                if others > a.max_drift:
                    b.sync_write("Goal_Position", {m: start_raw[m] for m in b.motors}, normalize=False)
                    print(f"ABORT: another joint moved {others:.1f}° while nudging {m} — re-commanded start, torque LEFT ON"); return 1
        b.sync_write("Goal_Position", {m: start_raw[m] for m in b.motors}, normalize=False)
        print("\ndone → holding start pose, torque LEFT ON (run release_torque.py once the arm is supported)")
        return 0
    except Exception as e:
        print("ABORT on error:", e, "— torque LEFT ON at last goal"); return 1
    finally:
        try:
            b.disconnect(disable_torque=False)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
