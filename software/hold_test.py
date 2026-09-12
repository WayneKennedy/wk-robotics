#!/usr/bin/env python3
"""Enable torque safely and check the arm holds still.

Usage: hold_test.py [--port] [--id wk_soarm101] [--torque-limit 300] [--seconds 3] [--keep]

Why: LeRobot's connect() re-enables torque while each servo may still hold a stale
Goal_Position from an earlier session, so joints can lurch toward old goals the instant
torque comes on (2026-09-12: the elbow did, twice). This tool reads Goal_Position, sets it
equal to Present_Position with torque still off, caps Torque_Limit (RAM, 0..1000), then
enables torque and streams positions for --seconds, reporting any drift. Torque is released
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
        for m in b.motors:
            b.write("Operating_Mode", m, OperatingMode.POSITION.value, num_retry=3)
            b.write("Goal_Position", m, pres[m], normalize=False, num_retry=5)
            b.write("Torque_Limit", m, a.torque_limit, normalize=False, num_retry=5)
        g2 = b.sync_read("Goal_Position", normalize=False, num_retry=5)
        assert all(g2[m] == pres[m] for m in b.motors), f"goal write mismatch {g2}"
        print(f"\ngoals set to present, Torque_Limit {a.torque_limit}/1000 — enabling torque")
        b.enable_torque()
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
