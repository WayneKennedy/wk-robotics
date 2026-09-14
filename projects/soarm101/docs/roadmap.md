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

## Milestone 4 — Geometry: kinematics, keep-out, IK *(DEC-14; in progress since 2026-09-14)*

Replaces the LeRobot teleoperate-record-train milestone, dropped by DEC-14. The arm's own
geometric model, host-side Python in `software/kinematics.py`: forward kinematics from
upstream's `so101_new_calib.urdf`, a servo-count-to-angle mapping good to ±10°
([`servos.md`](servos.md)), a keep-out check of the end-effector against the bench's desk-edge plane
([`hardware.md`](hardware.md) → Bench), and a
damped-least-squares IK for the tool frame with pitch. Done so far: FK validated against the
camera and the rest pose; the mapping checked against a hand-set zero pose; IK round-trips
FK within 2 mm on 47 of 50 random poses ([`test-log.md`](test-log.md) 2026-09-14). Ends
with a **guarded move**: a goal is accepted only if the whole interpolated path from the
present pose stays inside the joint limits and clear of the keep-out, and the arm executes
it under the bench tools' stall, current and temperature guards — **`software/guarded_move.py`,
first run 2026-09-14, an IK target reached within 10 counts** ([`test-log.md`](test-log.md));
the tool position checked with a tape (after correcting a frame error in the first comparison:
2.6 cm short forward, height within ~5 mm, with the measured zeros); and
`software/shapes.py` traced a 20 cm square and a 12 cm cube on a loop the same day. **Self-collision is in** (2026-09-14, later the same day): a capsule hit box per collision
mesh from upstream's URDF, placed by the forward kinematics, every non-adjacent link pair
tested for overlap at IK acceptance and at every sample of a plan — the pose that points the
gripper into the turret is refused before anything moves ([`test-log.md`](test-log.md)).
Capsules were the owner's call: the links are regular enough, and a capsule test is what a
Teensy can run. **Also done 2026-09-14:** mechanical stops measured on five joints and the
servo limits set to stop ∓ 3° (replacing the blanket 10 % shrink); zeros from the stop
midpoints — elbow and pan to about 1°, shoulder and wrist ±5–8° because their travel exceeds
the URDF's; the desk edge measured (25 mm ahead of the pan axis); the extents cycle retired
rather than rewritten. What remains for the milestone: a first live move with the full check
(none made since the self-collision check went in); the shoulder and wrist zeros pinned (a
spirit level on the upper arm; a second tape point); the desk surface modelled so moves can
start from the folded rest pose; the `wrist_roll` and `gripper` mappings, including the jaw
gap in millimetres.

## Milestone 5 — A Teensy 4.1-operated arm on micro-ROS *(DEC-12, DEC-14)*

The servo bus moves from the PC to a Teensy 4.1 running micro-ROS, with a micro-ROS agent
and ROS 2 on a host — the family's two-tier pattern
([wk-robotics `common.md`](../../../docs/common.md#compute-the-two-tier-split)), with the
arm as the proving ground for koala-bot and wk-devastator. Board, bus connection, agent
host and distribution are the open parts of OQ-09. Ends with the arm reproducing milestone
4's guarded move under the MCU, using the calibration LeRobot left in the servos, with the
joint envelope enforced on the Teensy and the keep-out check on the host. What the arm is
ultimately *for* (OQ-08) is decided alongside.

## Milestone 6 — Mount on wk-devastator *(only if OQ-08 says so)*

Only if that robot's OQ-12 closes in the arm's favour, which needs this arm's mass (OQ-04),
an interface (OQ-06), and a bus driver decision (OQ-09).
