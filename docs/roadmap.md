# Roadmap

**Print, commission, assemble, calibrate, teleoperate, mount** — in that order, because
each step is a precondition of the next and none can be skipped by enthusiasm. Each
milestone ends with something that demonstrably works.

## Milestone 0 — Print every follower part *(nearly done)*

All 11 parts printed at least once by 2026-09-09. Remaining: inspect plate 4 and the third
`Wrist_Roll_Pitch` (OQ-05). Weigh each accepted part (OQ-04).

## Milestone 1 — Commission six servos *(2 of 6)*

Each servo gets its ID and baud by script, one at a time, and is labelled
([`servos.md`](servos.md)). `shoulder_pan` and `shoulder_lift` done 2026-09-09 and verified
together on one bus. **Blocked on OQ-01** for the other four.

## Milestone 2 — Assemble the follower

Per upstream's guide, joint 1 to gripper. Needs milestones 0 and 1, and fasteners (OQ-07).
Ends with the servos daisy-chained, `shoulder_pan` to the control board, and a
`broadcast_ping()` returning IDs 1–6.

## Milestone 3 — Calibrate and move

`lerobot-calibrate` writes homing and travel limits into the servos
([`servos.md` → What calibration adds](servos.md#what-calibration-adds--after-assembly)).
Ends with a scripted move to a pose and back, under a decided 12 V supply (OQ-03), with the
arm clamped to a table.

## Milestone 4 — Decide what it is for, and what drives it

OQ-08 and OQ-09. Nothing below this line is scheduled until they are decided. Milestone 3
deliberately uses the PC-over-USB path, which every candidate answer needs anyway.

## Milestone 5a — Teleoperate and record *(if a LeRobot arm)*

Needs a leader or a substitute (OQ-02). Ends with a recorded LeRobot dataset of a simple
pick-and-place, replayed on the arm.

## Milestone 5b — Mount on wk-devastator *(if the tank's manipulator)*

Only if that robot's OQ-12 closes in the arm's favour, which needs this arm's mass (OQ-04),
an interface (OQ-06), and a bus driver decision (OQ-09).
