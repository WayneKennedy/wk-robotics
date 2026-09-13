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
  ([wk-robotics `common.md`](../../../docs/common.md#configuring-a-servo--true-for-every-sts-project)).
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

- **DEC-09 — The remaining four servos come from koala-bot's RCmall STS3215 packs.**
  (Owner, 2026-09-12; resolves OQ-01.) Four of the twelve Feetech STS3215 12 V that arrived
  for koala-bot that day become this arm's `elbow_flex`, `wrist_flex`, `wrist_roll` and
  `gripper`, commissioned the same day ([`servos.md`](servos.md)). Same part number as the
  two Waveshare units (model 777, 1/345), so the arm stays one uniform servo. The cost lands
  on koala-bot: it now holds **eight of the twelve** its V1 limbs need and must re-order
  ([koala-bot `bom.md`](https://github.com/WayneKennedy/koala-bot/blob/main/docs/bom.md),
  OQ-16). Chosen over the OQ-01 recommendation (a dedicated 6-pack) because the arm can be
  finished now and the re-order is koala-bot's, whose limbs are months from assembly.

- **DEC-10 — The two firmware-3.9 units (Waveshare A and B) hold IDs 1 and 6.**
  *Superseded the same day by DEC-11 and reverted: B is ID 2, F is ID 6 again.*
  (2026-09-12; from the six-on-one-bus diagnosis in [`test-log.md`](test-log.md).) Mixed
  3.9/3.10 firmware collides on a sync read whenever a 3.10 unit answers after a 3.9 unit
  that was not the first responder. LeRobot reads IDs 1–6 in fixed order, so the 3.9 units
  go first and last: unit B moves from `shoulder_lift` (2) to `gripper` (6), unit F takes
  `shoulder_lift`. Chosen over a firmware upgrade because it worked immediately with no
  new tooling; the upgrade stays open as OQ-10 and would make this decision unnecessary.
  Reply-delay tuning was tried first and does not help.

- **DEC-11 — One firmware on the bus: every servo runs 3.10, and any servo joining later
  is upgraded before it is chained.** (Owner, 2026-09-12, resolves OQ-10; supersedes
  DEC-10.) A and B were upgraded from 3.9 with Feetech FD 1.9.8.3 on Windows
  ([`test-log.md`](test-log.md) has the procedure and the pitfalls — VCP driver, and FD
  must be set to 1 000 000 baud). Afterwards every read order passes 30/30 and broadcast
  ping is complete, so the ID placement of DEC-10 was reverted and IDs follow the seated
  units. Chosen over the workaround because it removes the constraint instead of routing
  around it — "if a firmware update is possible, let's do that".

- **DEC-12 — After the LeRobot exploration, the arm becomes a Teensy 4.1-operated arm:
  the family's reflex-tier proving ground.** (Owner, 2026-09-12.) The LeRobot loop is run
  first and in full "for completeness" (DEC-08 stands), then the servo bus moves from the
  PC to a **Teensy 4.1** — the family's reflex-tier MCU pattern
  ([wk-robotics `common.md`](../../../docs/common.md#compute-the-two-tier-split))
  — "to develop and prove our approach for other bots". This picks the *own reflex MCU* row
  of OQ-09 and adds a purpose to OQ-08: the arm is the testbed where the MCU-drives-the-bus
  approach is developed before koala-bot and wk-devastator depend on it. Not decided:
  which Teensy 4.1 (the family holds an unallocated 4.1 NE), whether the Waveshare board's
  channel-A UART header or a separate adapter carries the bus, the firmware stack
  (micro-ROS per the family rule, or bare-metal first), and whether the tank's MCU later
  absorbs the role. Calibration written by LeRobot lives in the servos' EEPROM (homing
  offset and limits), so it carries over to the Teensy unchanged.

- **DEC-13 — No leader arm.** (Owner, 2026-09-12; resolves OQ-02 as "no".) "Not a useful
  use case for me." The LeRobot exploration (DEC-08) therefore runs without upstream's
  intended teleoperator; demonstrations come from one of the substitutes in OQ-02, or are
  scripted. Nothing for a leader is printed or bought, and the two-follower candidate under
  OQ-08 loses its "two leaders" line.
