#!/usr/bin/env python3
"""Enable torque safely and check the arm holds still.

Usage: hold_test.py [--port] [--id wk_soarm101] [--torque-limit 300] [--seconds 3] [--keep]

Why: servos keep their last motion target across sessions and LeRobot's connect() enables
torque without resetting it; and a Goal_Position written while torque is OFF is stored but
not adopted — the servo resumes the old target when torque comes on (2026-09-12, four
lurches). The only safe order: Torque_Limit very low → Torque_Enable → Goal := Present
(adopted now) → ramp Torque_Limit with drift checks. Then stream positions for --seconds. Torque is released
afterwards unless --keep. Nothing here writes EEPROM.
"""
import argparse
import time

from lerobot.motors.feetech import OperatingMode
from lerobot.robots.so_follower import SOFollower, SOFollowerRobotConfig


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", default="/dev/ttyACM0")
    ap.add_argument("--id", default="wk_soarm101")
    ap.add_argument("--torque-limit", type=int, default=300, help="0..1000, 1000 = full")
    ap.add_argument("--seconds", type=float, default=3.0)
    ap.add_argument("--keep", action="store_true", help="leave torque on at the end")
    ap.add_argument("--weak", type=int, default=30, help="Torque_Limit at the torque-on moment")
    ap.add_argument("--force", action="store_true", help="keep ramping even if a joint drifts")
    a = ap.parse_args()

    r = SOFollower(SOFollowerRobotConfig(port=a.port, id=a.id))
    b = r.bus
    b.connect(handshake=False)
    try:
        b.disable_torque()
        pres = b.sync_read("Present_Position", normalize=False, num_retry=5)
        goal = b.sync_read("Goal_Position", normalize=False, num_retry=5)
        print("| Joint | Present | Stale goal | Δ |\n|---|---|---|---|")
        for m in b.motors:
            print(f"| `{m}` | {pres[m]} | {goal[m]} | {goal[m]-pres[m]:+d} |")
        # A goal written while torque is off is stored but NOT adopted as the motion target: on
        # Torque_Enable the servo resumes its previous target (2026-09-12, elbow +134°). So: torque
        # on at a limit too weak to move anything, THEN write goals (adopted, torque is on), THEN
        # raise the limit in steps, checking drift.
        for m in b.motors:
            b.write("Operating_Mode", m, OperatingMode.POSITION.value, num_retry=3)
            b.write("Torque_Limit", m, a.weak, normalize=False, num_retry=5)
        b.enable_torque()
        time.sleep(0.3)
        p1 = b.sync_read("Present_Position", normalize=False, num_retry=5)
        moved = {m: p1[m] - pres[m] for m in b.motors if abs(p1[m] - pres[m]) > 15}
        print(f"torque on at Torque_Limit {a.weak}: moved > 15 counts: {moved or 'none'}")
        for m in b.motors:
            b.write("Goal_Position", m, p1[m], normalize=False, num_retry=5)
        g2 = b.sync_read("Goal_Position", normalize=False, num_retry=5)
        assert all(g2[m] == p1[m] for m in b.motors), f"goal write mismatch {g2}"
        pres = p1
        lim = a.weak
        for lim in sorted({min(a.torque_limit, x) for x in (150, 300, 600, a.torque_limit)}):
            for m in b.motors:
                b.write("Torque_Limit", m, lim, normalize=False, num_retry=5)
            time.sleep(0.4)
            p2 = b.sync_read("Present_Position", normalize=False, num_retry=5)
            drift = {m: p2[m] - pres[m] for m in b.motors if abs(p2[m] - pres[m]) > 15}
            print(f"Torque_Limit {lim}: drift > 15 counts: {drift or 'none'}")
            if drift and not a.force:
                print("ABORT ramp — leaving torque on at this limit"); break
        print(f"\ngoals = present, Torque_Limit {lim}/1000 — holding, watching {a.seconds:.0f} s")
        t0 = time.time(); worst = {m: 0 for m in b.motors}; last = pres
        while time.time() - t0 < a.seconds:
            try:
                p = b.sync_read("Present_Position", normalize=False, num_retry=3)
            except ConnectionError:
                continue
            for m in b.motors:
                worst[m] = max(worst[m], abs(p[m] - pres[m]))
            last = p
            time.sleep(0.05)
        cur = b.sync_read("Present_Current", normalize=False, num_retry=5)
        load = b.sync_read("Present_Load", normalize=False, num_retry=5)
        print("| Joint | Start | End | Max drift (counts / °) | Current mA | Load |\n|---|---|---|---|---|---|")
        for m in b.motors:
            print(f"| `{m}` | {pres[m]} | {last[m]} | {worst[m]} / {worst[m]*360/4095:.1f} | {cur[m]*6.5:.0f} | {load[m]} |")
    finally:
        if not a.keep:
            for m in b.motors:
                try:
                    b.write("Torque_Enable", m, 0, normalize=False, num_retry=5)
                except Exception as e:
                    print(m, "torque release failed:", str(e)[-40:])
            print("torque released")
        try:
            b.disconnect(disable_torque=False)
        except Exception:
            pass


if __name__ == "__main__":
    main()
