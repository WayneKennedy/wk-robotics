# Servos

**The servo map for this arm** — which physical servo carries which ID and joint, how each
was set, and what calibration will add. Every write to a servo is recorded here and in
[`test-log.md`](test-log.md). The procedure and the adapter facts are family knowledge:
[wk-robotics `common.md` → Configuring a servo](../../../docs/common.md#configuring-a-servo--true-for-every-sts-project).

## The SO-101 follower map

Fixed by LeRobot's `so101_follower` definition; this build follows it exactly (DEC-07).
All six are STS3215 at 1/345, 1 Mbaud, model number 777.

| ID | Joint | This build |
|---|---|---|
| 1 | `shoulder_pan` (base rotation) | **Set 2026-09-09.** Waveshare ST3215 12 V, unit A. Firmware 3.9 → **3.10** on 2026-09-12 |
| 2 | `shoulder_lift` | **Set 2026-09-09.** Waveshare ST3215 12 V, unit B. Firmware 3.9 → **3.10** on 2026-09-12. Held ID 6 for part of 2026-09-12 (DEC-10, reverted) |
| 3 | `elbow_flex` | **Set 2026-09-12.** Feetech STS3215 12 V from koala-bot's RCmall packs (DEC-09), firmware 3.10, unit C |
| 4 | `wrist_flex` | **Set 2026-09-12.** Feetech STS3215 12 V (DEC-09), firmware 3.10, unit D |
| 5 | `wrist_roll` | **Set 2026-09-12.** Feetech STS3215 12 V (DEC-09), firmware 3.10, unit E |
| 6 | `gripper` | **Set 2026-09-12.** Feetech STS3215 12 V (DEC-09), firmware 3.10, unit F. Held ID 2 for part of 2026-09-12 (DEC-10, reverted) |

**Verified on one bus, 2026-09-12, all six on firmware 3.10:** LeRobot's `sync_read` in
this order 30 of 30, every other order tried 30 of 30, `broadcast_ping()` complete 5 of 5
([`test-log.md`](test-log.md)). Milestone 1 is done. The unit letters run A–F in ID order
and in chain order from the base.

The unit letter is the label written on the servo case at commissioning. Every unit left the
factory as **ID 1, 1 Mbaud**; unit A's write therefore changed nothing and served to prove
the toolchain. A and B are Waveshare-branded, C–F Feetech-branded; same part (model 777,
1/345). **All six run firmware 3.10** — A and B shipped with 3.9 and were upgraded on
2026-09-12 because mixed 3.9/3.10 firmware collides on a shared bus (DEC-11; the diagnosis
and the upgrade are in [`test-log.md`](test-log.md); the family rule is in
[wk-robotics `common.md`](../../../docs/common.md#configuring-a-servo--true-for-every-sts-project)).
Any servo joining this bus later is brought to 3.10 first.

## How an ID is set here

Scripted through LeRobot (DEC-04), one servo on the bus at a time, 12 V on the adapter,
adapter on USB. Since 2026-09-12 the write is [`software/set_servo_id.py`](../software/set_servo_id.py)
`<joint> --label "<unit>"`, run from the LeRobot venv: it refuses unless the bus shows exactly
one factory servo, writes, re-pings, reads back voltage/position/temperature and prints the
test-log row. It is this 2026-09-09 sequence, unchanged:

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

**Calibrated 2026-09-12** — homing offsets and limits are in the servos and in
[`test-log.md`](test-log.md); LeRobot's file for robot id `wk_soarm101` is mirrored at
[`software/calibration/wk_soarm101.json`](../software/calibration/wk_soarm101.json). The
stepwise tool is [`software/calibrate.py`](../software/calibrate.py); `status` shows what
the servos hold. Re-running `home` re-centres every joint on the pose held at that moment,
so do not run it casually.

**Three servo facts every tool here obeys (2026-09-12, [`test-log.md`](test-log.md)):**
1. **Writing `Goal_Position` turns torque on**, whatever `Torque_Enable` said a moment
   before. Set `Torque_Limit` first; treat any goal write as energising the arm.
2. **Servos keep their last motion target across sessions, and read `Goal_Position = 0`
   after a power cycle.** LeRobot's `connect()` re-enables torque without touching it — the
   arm lurches toward the stale target (or toward 0). **A goal written while torque is off
   is stored but not adopted.** The only safe order, verified: `Torque_Limit := 30` →
   `Torque_Enable := 1` → `Goal_Position := Present_Position` → ramp `Torque_Limit` with
   drift checks (`hold_test.py`, `first_move.py`).
3. **`max_relative_target` is not a safety net.** It clamps each goal to *present ± step*, so
   a joint already moving is followed, not held. Command absolute goals from a verified
   stationary pose and monitor.

4. **An EEPROM write only persists if the servo's `Lock` register is 0.** LeRobot's
   `enable_torque()` sets `Lock` = 1 and `disable_torque()` sets 0 (0.6.1 source), so any
   EEPROM write made while the arm is holding after `hold_test.py` lands in RAM and is lost
   at power-off — **confirmed 2026-09-14 as the cause of the limits lost on `wrist_flex` and
   `gripper`** (OQ-12, a canary written with `Lock` = 1 was gone after a power cycle). Write `Lock` = 0 first, write, read back, restore `Lock` = 1. **Re-read
   calibration after every power cycle** and rewrite from the JSON before moving.

5. **After a `Homing_Offset` change the servo chases its old goal number.** On 2026-09-14 the
   roll's offset was changed with zero physical shift and the goal rewritten to the new
   present at a 1 % torque limit, yet on raising the limit the roll turned 34° to the old goal's
   number read in the new frame. Change an offset only at a weak torque limit, then re-anchor
   the goal (goal := present, torque on), watch it settle, and only then ramp the limit up.

**One process on the bus at a time.** Two of this repo's tools on `/dev/ttyACM0` together
produce a stream of failed and possibly corrupted reads (2026-09-12); alone, `sync_read` is
100/100. Stop any logger or recorder before running anything else. Every tool here opens
the port itself; none shares it.

## Servo counts to URDF angles — measured 2026-09-14 on four joints

[`software/kinematics.py`](../software/kinematics.py) runs forward kinematics from upstream's
`so101_new_calib.urdf` (zero = pan ahead, upper arm vertical, forearm horizontal forward,
wrist in line; every joint's zero at mid-travel) and maps raw counts to URDF radians as
`sign × (raw − raw_at_zero) × 2π / 4095`. The `raw_at_zero` values are the **midpoints of
the 2026-09-12 hand sweep** (pre-shrink limits above): the sweep spans match the URDF's
travel within 3–8° on every pitch joint, so its midpoint is taken as the URDF zero. Signs
for `shoulder_lift` and `elbow_flex` follow from the folded rest pose reading at the raw
minimum and maximum respectively; pan and wrist_flex signs were fixed by a hand nudge in a
known direction; a hand-set zero pose agreed with the sweep midpoints within 9° on all four
(2026-09-14, [`test-log.md`](test-log.md)). **The zero is good to about ±10°** until each
joint is measured against its hard stops. `wrist_roll`'s zero was set the same evening from the moving jaw (2851, ±3°, [`test-log.md`](test-log.md)); the gripper's zero is its closed stop, and its jaw gap is calibrated in `software/calibration/gripper_gap.json`. The values and their provenance are in the module's
`JOINT_ZERO` table — the one place they live.

The four measured zeros (pan, shoulder, elbow, wrist flex) superseded the sweep-midpoint
estimates later on 2026-09-14 — and a spirit-level check that evening confirmed the shoulder and
moved the elbow 4.8° and the wrist 2.1° off their stop midpoints, so the stop midpoint is a
starting point, not the zero: each is the midpoint of the joint's measured mechanical stops
(below). Their accuracy and the tape check are in the module's docstring and
[`test-log.md`](test-log.md).

## Mechanical stops and servo limits — measured 2026-09-14

`software/find_stops.py` drives one joint gently into each stop and records the raw count;
results in [`software/calibration/stops.json`](../software/calibration/stops.json), method and
table in [`test-log.md`](test-log.md). **The servos' `Min/Max_Position_Limit` are now the
measured stops ∓ 3°**, replacing the 2026-09-12 hand sweep less 10 %. They are the hardware
last resort; configuration-dependent contact (link against link, against the base) and the
bench keep-out are checked in software before every move (`kinematics.py`). `wrist_roll`
stays 0–4095: it has no stop.

