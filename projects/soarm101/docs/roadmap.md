# Roadmap

**Print, commission, assemble, calibrate, teleoperate, mount** — in that order, because
each step is a precondition of the next and none can be skipped by enthusiasm. Each
milestone ends with something that demonstrably works.

## Milestone 0 — Print every follower part *(nearly done)*

All 11 parts printed at least once by 2026-09-09. Remaining: inspect plate 4 and the third
`Wrist_Roll_Pitch` (OQ-05). Weigh each accepted part (OQ-04).

## Milestone 1 — Commission six servos *(done 2026-09-12)*

Each servo got its ID and baud by script, one at a time, and was labelled
([`servos.md`](servos.md)): two on 2026-09-09, four on 2026-09-12 (DEC-09). All six read
on one bus in LeRobot's order once A and B were upgraded to firmware 3.10 (DEC-11).

## Milestone 2 — Assemble the follower *(done 2026-09-12)*

Per upstream's guide, joint 1 to gripper. Needs milestones 0 and 1, and fasteners (OQ-07).
Ends with the servos daisy-chained, `shoulder_pan` to the control board, and a
`broadcast_ping()` returning IDs 1–6.

## Milestone 3 — Calibrate and move *(done 2026-09-12)*

Homing and travel limits are in the servos, pulled in 10 % at each end
([`test-log.md`](test-log.md) 2026-09-12, `software/calibrate.py` + `shrink_limits.py`).
Every joint nudged ±3° and back within 1° from a hands-off hold, arm clamped, on a 3S pack
(OQ-03 still open). The day's cost was four lurches before the servo behaviours in
[`servos.md`](servos.md) were understood; `hold_test.py --keep` then `first_move.py` is the
proven sequence.

## Milestone 4 — Geometry: kinematics, keep-out, self-collision, IK *(DEC-14; done 2026-09-15)*

Replaces the LeRobot teleoperate-record-train milestone (DEC-14). The arm's own geometric
model and move tools, host-side Python in `software/`:

- **`kinematics.py`** — forward kinematics from upstream's `so101_new_calib.urdf`; count-to-angle
  zeros measured on all six joints ([`servos.md`](servos.md): pan and shoulder ~1°, elbow ±1.5°,
  wrist flex ±2°, roll ±3°); model limits = the measured servo limits; the bench keep-out
  (behind the desk-edge plane, minus a 0.18 m cylinder, floored at the desk top, tested on every
  link — [`hardware.md`](hardware.md) → Bench); capsule self-collision fitted to upstream's
  collision meshes; damped-least-squares IK for the tool frame with pitch.
- **`guarded_move.py`** — a joint or IK goal (roll and gripper optional) is accepted only if every
  sample of the joint-space path passes the measured limits, the keep-out and self-collision;
  streamed at 20 Hz under tracking, current and temperature guards.
- **`shapes.py`** — Cartesian shapes as 1 cm IK waypoints, each checked; a 20 cm square and a
  12 cm cube ran 2026-09-14, on pre-calibration zeros (their real error is in the test log).
- **`find_stops.py`** — mechanical stops by gentle contact; servo limits are the stops ∓ 3° on
  every joint; the roll re-homed so its 335.6° travel sits inside the encoder range; the gripper
  gap calibrated from closed to 37 mm.
- **Validated against the world** — zeros by spirit level and square, tool reach by tape (exact at
  one pose after calibration); everything persisted across power cycles
  ([`test-log.md`](test-log.md) 2026-09-14).

**Closed 2026-09-15.** The last two items: (1) a shape re-run on the calibrated zeros, checked against the world at two or
three points — the validation that closes the milestone — **done: the cube ran clean and two corners taped within 1.5 cm on every axis** ([`test-log.md`](test-log.md)); (2) **wake up from any contact pose** — an
unpowered arm always droops into one, even if parked before torque-off (owner, 2026-09-15), and
every session so far has started from a pose set by hand. Approach: a path may start in contact
provided it only ever gets out of it (no new contact, bounded deepening of the starting ones for
the conservative capsules, ends clear), run at reduced torque until clear, trying the direct line
and every order of single-joint moves to a standard ready pose (`guarded_move.py --unfold`). **Done 2026-09-15: the arm woke
itself from its rest pose** ([`test-log.md`](test-log.md)).

## Milestone 5 — A Teensy 4.1-operated arm on micro-ROS *(DEC-12, DEC-14)*

The servo bus moves from the PC to a Teensy 4.1 running micro-ROS, with a micro-ROS agent
and ROS 2 on a host — the family's two-tier pattern
([wk-robotics `common.md`](../../../docs/common.md#compute-the-two-tier-split)), with the
arm as the proving ground for koala-bot and wk-devastator. Board, bus connection, agent
host and distribution are the open parts of OQ-09. Ends with the arm reproducing milestone
4's guarded move under the MCU, using the calibration now in the servos (homing offsets
and measured limits), with the joint envelope enforced on the Teensy (how the checks split
between tiers is open: OQ-09, and OQ-13 for two arms). What the arm is
ultimately *for* (OQ-08) is decided alongside.

## Milestone 6 — Mount on wk-devastator *(only if OQ-08 says so)*

Only if that robot's OQ-12 closes in the arm's favour, which needs this arm's mass (OQ-04),
an interface (OQ-06), and a bus driver decision (OQ-09).
