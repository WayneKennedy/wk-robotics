#!/usr/bin/env python3
"""Release torque on every servo, one at a time with retries, and print each servo's state."""
import sys
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

names = {1: "shoulder_pan", 2: "shoulder_lift", 3: "elbow_flex", 4: "wrist_flex", 5: "wrist_roll", 6: "gripper"}
port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
b = FeetechMotorsBus(port, {n: Motor(i, "sts3215", MotorNormMode.RANGE_M100_100) for i, n in names.items()})
b.connect(handshake=False)
for n in names.values():
    try:
        b.write("Torque_Enable", n, 0, normalize=False, num_retry=5); state = "off"
    except Exception as e:
        state = f"FAILED {str(e)[-40:]}"
    def rd(reg):
        try: return b.read(reg, n, normalize=False, num_retry=3)
        except Exception: return "?"
    print(f"{n:14s} torque {state:6s} pos {rd('Present_Position')} cur {rd('Present_Current')} temp {rd('Present_Temperature')} status {rd('Status')}")
try:
    b.disconnect(disable_torque=False)
except Exception:
    pass
