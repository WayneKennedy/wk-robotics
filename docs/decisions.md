# Banked Decisions

Committed decisions with rationale. Unresolved items live in
[`open-questions.md`](open-questions.md). Format: `DEC-nn — decision — why`.

A decision appears here only if the owner made it, or if it follows necessarily from one
that was made. Recommendations offered and not accepted are open questions.

---

- **DEC-01 — Build the SO-101 follower from upstream, unmodified; clone upstream, do not
  fork it.** (Owner; printing began 2026-09-06, repo created 2026-09-09.) The design is
  mature, LeRobot-native and maintained. A fork would invite drift for no gain; a build
  record beside a read-only clone keeps the two roles separate.

- **DEC-02 — The 12 V servo variant.** (Owner, by allocation 2026-09-09: the two 12 V
  units in hand were assigned to `shoulder_pan` and `shoulder_lift`.) Upstream offers the
  12 V STS3215 (~30 kg·cm) as the stronger option over the standard 7.4 V (16.5 kg·cm), and
  the family already standardises on the 12 V part. Consequences: a 12 V rail (OQ-03), and
  **all six follower servos must be 12 V** — mixing rails on one bus is not possible.

- **DEC-03 — The Waveshare Bus Servo Adapter (A) is the arm's control board.** (Owner,
  2026-09-07, purchase.) It is the upstream BOM part, the part upstream's mounting plate is
  designed for, and the one LeRobot's docs are written against.

- **DEC-04 — LeRobot is the path for commissioning and calibration, and every servo write
  is scripted and logged.** (What drives the bus at *runtime* is open — OQ-09.) Follows
  from DEC-01 and the family rule
  ([wk-robotics `common.md`](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#configuring-a-servo--true-for-every-sts-project)).
  Feetech's GUI works but leaves no record; a build that cannot say which servo is ID 3 is
  not a build record. Applied 2026-09-09 for the first two servos ([`servos.md`](servos.md)).

- **DEC-05 — All parts in white eSUN PLA+.** (Owner, 2026-09-06.) Upstream's recommended
  material; validated on this build's parts — the servo press fit is correct with no
  elephant-foot compensation, and an 87 mm part crossed a garage hot/cold cycle without
  lift. Findings banked in wk-robotics.

- **DEC-06 — This repository is the build record; print jobs stay in `3d-printing`;
  facts shared with other robots stay in wk-robotics.** (Owner, 2026-09-09.) Upstream
  cannot hold build-specific facts and the private print log should not have to; the
  family placement rule puts one-project facts in the project's repo.

- **DEC-07 — Servo IDs follow LeRobot's `so101_follower` map exactly.** Follows from
  DEC-04: any other numbering would need a custom robot definition for no benefit.

- **DEC-08 — Learn the arm as LeRobot intends it before repurposing it.** (Owner,
  2026-09-09.) The SO-101 was designed for imitation learning — teleoperate a follower
  from a leader, record demonstrations, train a policy, run it. That use case is explored
  **first**, on the PC-over-USB path upstream supports, before any micro-ROS driver or
  tank mounting is attempted. This sequences the work; it does not close OQ-08 (what the
  arm is ultimately for) or OQ-09 (what drives it at runtime), which stay open until the
  exploration has taught something.
