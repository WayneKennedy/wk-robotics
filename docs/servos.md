# Servos

**The servo map for this arm** — which physical servo carries which ID and joint, how each
was set, and what calibration will add. Every write to a servo is recorded here and in
[`test-log.md`](test-log.md). The procedure and the adapter facts are family knowledge:
[wk-robotics `common.md` → Configuring a servo](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#configuring-a-servo--true-for-every-sts-project).

## The SO-101 follower map

Fixed by LeRobot's `so101_follower` definition; this build follows it exactly (DEC-07).
All six are STS3215 at 1/345, 1 Mbaud, model number 777.

| ID | Joint | This build |
|---|---|---|
| 1 | `shoulder_pan` (base rotation) | **Set 2026-09-09.** Waveshare ST3215 12 V, unit A |
| 2 | `shoulder_lift` | **Set 2026-09-09.** Waveshare ST3215 12 V, unit B |
| 3 | `elbow_flex` | not sourced (OQ-01) |
| 4 | `wrist_flex` | not sourced |
| 5 | `wrist_roll` | not sourced |
| 6 | `gripper` | not sourced |

"Unit A / B" is the label written on the servo case at commissioning. Both units left the
factory as **ID 1, 1 Mbaud**; unit A's write therefore changed nothing and served to prove
the toolchain.

## How an ID is set here

Scripted through LeRobot (DEC-04), one servo on the bus at a time, 12 V on the adapter,
adapter on USB. Exactly what was run on 2026-09-09, with the joint name and ID changed per
servo:

```python
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

bus = FeetechMotorsBus("/dev/ttyACM0",
      {"shoulder_lift": Motor(2, "sts3215", MotorNormMode.RANGE_M100_100)})
bus.connect(handshake=False)
assert bus.broadcast_ping() == {1: 777}      # exactly one factory servo present
bus.setup_motor("shoulder_lift")             # scans, then writes ID and Baud_Rate to EEPROM
assert bus.broadcast_ping() == {2: 777}
print(bus.read("Present_Voltage", "shoulder_lift", normalize=False))   # 0.1 V units
bus.disconnect()
```

The upstream wizard, `lerobot-setup-motors --robot.type=so101_follower`, does the same
writes but insists on gripper-first order across all six; the direct call above is used
because servos arrive in ones and twos. Environment: LeRobot **0.6.1** with the `feetech`
extra, in a `uv` venv; the adapter enumerates as `/dev/ttyACM0` and needs the `dialout`
group.

**Checks after every write:** `broadcast_ping()` shows only the intended IDs;
`Present_Voltage` reads the rail (proves the servo is powered, not merely present); the
servo is labelled before it is unplugged.

## What calibration adds — after assembly

None of the above sets home or travel limits. `lerobot-calibrate --robot.type=so101_follower`
runs once the arm is assembled and writes three more EEPROM registers per servo:

- **`Homing_Offset`** — set with the arm held at mid-range, so that pose reads 2047 and the
  encoder's wrap point sits away from the working range.
- **`Min_Position_Limit` / `Max_Position_Limit`** — recorded from a hand sweep of each
  joint. The servo itself then clamps goals past them. **Stop just short of the hard
  stops during the sweep**, or the recorded limit is the crash point.

`wrist_roll` is treated as a full-turn joint and is not range-swept. The result is also
saved on the host as a calibration JSON keyed by the robot's `--robot.id` and rewritten to
the servos on every connect. Upstream's `Software/WEBUI_CALIBRATION.md` describes a
three-point alternative that also caps torque at 30 % during calibration.

Calibration values, when they exist, are recorded in [`test-log.md`](test-log.md).
