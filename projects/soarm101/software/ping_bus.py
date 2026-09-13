#!/usr/bin/env python3
"""Ping the arm's bus and read voltage, position and temperature from every servo present.

Usage:  ping_bus.py [--port /dev/ttyACM0] [--expect 1,2,3,4,5,6]

Read-only. Exits 1 if --expect is given and the set of IDs seen differs. Used for the
"all six on one bus" milestone-1 check (docs/roadmap.md) and for any later bus sanity check.
"""
import argparse
import sys

from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

SO101_FOLLOWER = {1: "shoulder_pan", 2: "shoulder_lift", 3: "elbow_flex",
                  4: "wrist_flex", 5: "wrist_roll", 6: "gripper"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", default="/dev/ttyACM0")
    ap.add_argument("--expect", default="", help="comma-separated IDs that must be exactly the set present")
    a = ap.parse_args()

    probe = FeetechMotorsBus(a.port, {"probe": Motor(1, "sts3215", MotorNormMode.RANGE_M100_100)})
    probe.connect(handshake=False)
    seen = probe.broadcast_ping()
    try:
        probe.disconnect()
    except ConnectionError:
        pass
    print("broadcast ping:", dict(sorted(seen.items())))
    # Broadcast ping dropped replies while the bus mixed firmware 3.9 and 3.10 (2026-09-12,
    # docs/test-log.md); complete since all six run 3.10. Kept as a fallback: fill in with
    # addressed pings of the expected IDs, then sync_read — LeRobot's runtime path — decides.
    if a.expect:
        want = {int(x) for x in a.expect.split(",") if x}
        if set(seen) != want:
            probe = FeetechMotorsBus(a.port, {"probe": Motor(1, "sts3215", MotorNormMode.RANGE_M100_100)})
            probe.connect(handshake=False)
            for i in sorted(want - set(seen)):
                model = probe.ping(i, raise_on_error=False)
                if model is not None:
                    seen[i] = model
            try:
                probe.disconnect()
            except ConnectionError:
                pass
            print("after addressed pings:", dict(sorted(seen.items())))
    if not seen:
        return 1

    # ID order = LeRobot's read order; the order matters on a mixed-firmware bus (DEC-10).
    motors = {SO101_FOLLOWER.get(i, f"id{i}"): Motor(i, "sts3215", MotorNormMode.RANGE_M100_100) for i in sorted(seen)}
    bus = FeetechMotorsBus(a.port, motors)
    bus.connect(handshake=False)
    try:
        v = bus.sync_read("Present_Voltage", normalize=False, num_retry=3)
        p = bus.sync_read("Present_Position", normalize=False, num_retry=3)
        t = bus.sync_read("Present_Temperature", normalize=False, num_retry=3)
        print("| ID | Joint | Model | V | Position (raw) | °C |\n|---|---|---|---|---|---|")
        for name, m in sorted(motors.items(), key=lambda kv: kv[1].id):
            print(f"| {m.id} | `{name}` | {seen[m.id]} | {v[name]/10:.1f} | {p[name]} | {t[name]} |")
    finally:
        try:
            bus.disconnect()
        except ConnectionError:
            pass

    if a.expect:
        want = {int(x) for x in a.expect.split(",") if x}
        if set(seen) != want:
            print(f"MISMATCH: expected {sorted(want)}, saw {sorted(seen)}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
