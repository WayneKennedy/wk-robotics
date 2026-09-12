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

## Milestone 2 — Assemble the follower

Per upstream's guide, joint 1 to gripper. Needs milestones 0 and 1, and fasteners (OQ-07).
Ends with the servos daisy-chained, `shoulder_pan` to the control board, and a
`broadcast_ping()` returning IDs 1–6.

## Milestone 3 — Calibrate and move

`lerobot-calibrate` writes homing and travel limits into the servos
([`servos.md` → What calibration adds](servos.md#what-calibration-adds--after-assembly)).
Ends with a scripted move to a pose and back, under a decided 12 V supply (OQ-03), with the
arm clamped to a table.

## Milestone 4 — Teleoperate, record, train, run *(DEC-08: this comes first)*

The LeRobot loop as upstream intends it, entirely on the PC-over-USB path. Needs a leader
or a substitute (OQ-02) and cameras (OQ-08). Ends with a recorded dataset of a simple
pick-and-place, a policy trained from it, and the follower executing it. **If the two-arm
candidate under OQ-08 is taken, a second follower is printed and commissioned in parallel
with this milestone**, and the single-arm result becomes the baseline for the handover.

## Milestone 5 — Decide what it is for, and what drives it

OQ-08 and OQ-09, answered with milestone 4's experience in hand. Nothing below is
scheduled until then.

## Milestone 6 — Mount on wk-devastator *(only if OQ-08 says so)*

Only if that robot's OQ-12 closes in the arm's favour, which needs this arm's mass (OQ-04),
an interface (OQ-06), and a bus driver decision (OQ-09).
