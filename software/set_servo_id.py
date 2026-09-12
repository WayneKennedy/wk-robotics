#!/usr/bin/env python3
"""Set the ID of one factory-state STS3215 for this arm, and print the test-log row.

Usage:  set_servo_id.py <joint> [--port /dev/ttyACM0] [--label "RCmall unit C"]

Preconditions (DEC-04, servos.md "How an ID is set here"):
  - exactly ONE servo on the bus, in factory state (ID 1, 1 Mbaud, model 777);
  - 12 V on the adapter, adapter on USB, user in `dialout`.

Refuses to write if the bus does not show exactly {1: 777}. Every run is recorded in
docs/servos.md and docs/test-log.md by hand from the row this prints.
"""
import argparse
import sys

from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

# LeRobot so101_follower map (DEC-07). Model 777 = STS3215.
SO101_FOLLOWER = {
    "shoulder_pan": 1, "shoulder_lift": 2, "elbow_flex": 3,
    "wrist_flex": 4, "wrist_roll": 5, "gripper": 6,
}
FACTORY = {1: 777}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("joint", choices=sorted(SO101_FOLLOWER, key=SO101_FOLLOWER.get))
    ap.add_argument("--port", default="/dev/ttyACM0")
    ap.add_argument("--label", default="", help="text written on the servo case")
    a = ap.parse_args()
    target = SO101_FOLLOWER[a.joint]

    bus = FeetechMotorsBus(a.port, {a.joint: Motor(target, "sts3215", MotorNormMode.RANGE_M100_100)})
    bus.connect(handshake=False)
    try:
        seen = bus.broadcast_ping()
        if seen != FACTORY:
            print(f"REFUSED: bus shows {seen}, need exactly {FACTORY} (one factory servo).", file=sys.stderr)
            return 2
        bus.setup_motor(a.joint)            # scans baud/ID, writes ID and Baud_Rate to EEPROM
        after = bus.broadcast_ping()
        if after != {target: 777}:
            print(f"FAILED: after write bus shows {after}, expected {{{target}: 777}}", file=sys.stderr)
            return 1
        v = bus.read("Present_Voltage", a.joint, normalize=False) / 10
        pos = bus.read("Present_Position", a.joint, normalize=False)
        temp = bus.read("Present_Temperature", a.joint, normalize=False)
        baud = bus.read("Baud_Rate", a.joint, normalize=False)
        torque = bus.read("Torque_Enable", a.joint, normalize=False)
        print(f"OK  {a.joint}: ID 1 -> {target}, baud code {baud}, {v:.1f} V, position {pos}, "
              f"{temp} °C, torque {'off' if torque == 0 else 'ON'}")
        who = a.label or "(label)"
        print(f"| {who} → `{a.joint}` | ID 1, 1 Mbaud, model 777 | **ID {target}**, baud code {baud} "
              f"| {v:.1f} V, position {pos}, {temp} °C, torque {'off' if torque == 0 else 'on'} |")
        return 0
    finally:
        try:
            bus.disconnect()          # tries to disable torque on the declared ID; absent on REFUSED
        except ConnectionError:
            pass


if __name__ == "__main__":
    sys.exit(main())
