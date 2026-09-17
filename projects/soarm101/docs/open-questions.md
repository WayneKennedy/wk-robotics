# Open Questions (pending decisions)

Unresolved. Resolve → move to [`decisions.md`](decisions.md).

A recommendation is *not* a decision — it is one option with an argument attached, offered
and not yet accepted. Do not build against one without the owner deciding.

---

## Servos and power

- **OQ-01 — Where the remaining four STS3215 12 V servos come from.** **Resolved
  2026-09-12 by DEC-09:** taken from koala-bot's RCmall packs, which leaves that robot four
  short. The recommendation here had been a dedicated 6-pack; the owner chose otherwise.

- **OQ-02 — Where demonstrations come from, given no leader arm (DEC-13).** LeRobot's
  record loop wants a teleoperator; the installed 0.6.1 offers, besides leaders:
  **keyboard** (joint or end-effector mode; needs a graphical session for `pynput`, so not
  plain SSH), **gamepad** (pygame or hidapi; whether it works on this headless host is
  untested), and **phone** (iOS or Android pose tracking; the app and its network path are
  unexamined). A fourth route needs no teleoperator: **scripted trajectories recorded as a
  dataset**, which fits DEC-12's aim of proving the control path more than the imitation
  loop does. **Moot since DEC-14 (2026-09-14):** the record-and-train milestone is dropped,
  so no demonstration source is needed. Kept for the record.

- **OQ-03 — The 12 V supply.** Upstream specifies a **12 V, 5 A+** brick for the 12 V
  follower. The family rule for servo robots is a stiff source — a **3S LiPo** with a fuse
  and bulk capacitance — because six STS3215 stall at 16 A in total
  ([wk-robotics `common.md` → Power integrity](../../../docs/common.md#power-integrity)).
  A desk arm on a brick and an arm riding a robot on the robot's pack are different
  answers; both may be right at different times. What powered the bench on 2026-09-09 is
  **unrecorded**; on 2026-09-12 it was a 3S LiPo, not fully charged, 11.7–11.9 V at the
  servos ([`hardware.md`](hardware.md)). The family's 3S ceiling applies (wk-robotics
  `common.md`). **Recommendation for a mains brick, 2026-09-12 (not decided): 12.0 V
  regulated, 10 A**, into the adapter's screw terminals (a 5.5 × 2.1 barrel is typically ~5 A;
  the Waveshare jack's rating is unverified), with a few thousand µF across the servo rail.
  Basis: upstream's 5 A minimum; measured peaks of 2 A on `shoulder_lift` lifting the arm and
  ~0.6 A on the elbow and pan; 16 A all-stalled, which is the fuse's job. The 0.9 V sag seen
  at < 1 A on the 3S pack says the current path (pack lead, terminals) needs checking whatever
  the source. On 2026-09-14 the bench ran from an **Eventek KPS3010D bench supply** (30 V / 10 A
  class, adjustable current limit) at 12.0 V, reading 11.9–12.1 V at all six servos idle and
  **0.72 A peak on its panel through the extents cycle** (one joint moving at a time)
  ([`test-log.md`](test-log.md)) — a stiff bench source, not a decision on the arm's supply.

## Parts

- **OQ-05 — A usable `Wrist_Roll_Pitch`, and inspection of plate 4.** Two copies failed at
  the servo-fork faces (one unsupported, one welded). The third, organic bed-only support,
  finished 2026-09-09 and is **uninspected**, as are `Wrist_Roll_Follower` and
  `Moving_Jaw`. Two questions decide it: did the interface under the fork face release
  cleanly, and did the support trees mark the outer faces.

- **OQ-07 — Fasteners.** Upstream's assembly guide uses **M2×6** and **M3×6** screws
  throughout; the counts have not been tallied from the guide and none are bought. The
  Waveshare servo boxes supplied M2×5 self-tapping and M3 horn screws — whether those
  lengths substitute for the guide's M2×6 is unverified.

## Purpose and control

- **OQ-08 — What the arm is for, ultimately.** Candidates in
  [`concept.md`](concept.md#what-it-is-for): a desk LeRobot arm, the tank's manipulator,
  or both in turn. **Narrowed by DEC-08 (2026-09-09):** the LeRobot use case is explored
  first and the answer is taken afterwards, informed by it. Consequences already visible:
  OQ-02 becomes a demonstration-source question (no leader, DEC-13), OQ-03 is answered "a 12 V brick"
  for the desk phase, and **cameras** join the sourcing list — LeRobot's imitation-learning
  loop needs one or two, and none is owned or specified. **DEC-14 (2026-09-14) ends the
  LeRobot exploration after calibration and bench moves**; the imitation-learning framing
  of the candidates below is no longer the near-term path, the geometry and the Teensy
  runtime are.

  **Stated purpose, 2026-09-12 (owner): a surrogate for big industrial robots, where
  operating ranges are safety issues** — defining and enforcing a box of acceptable
  movement, and more generally geometry awareness that per-joint limits cannot give
  ([wk-robotics `common.md` → Collision awareness](../../../docs/common.md#collision-awareness--open-family-wide)).
  This sits alongside, not instead of, the candidate below.

  **Decided 2026-09-14 (DEC-15): two arms 30 cm apart on the desk edge, coordinated by
  planning against each other's geometry, each broadcasting its pose in ROS 2.** The
  candidate as it stood before that, kept for its detail:
  **Leading candidate (owner, 2026-09-09): two followers cooperating in one workspace.** Motivated by a real problem in large-scale industrial
  machinery — one arm places a pallet of components where a second arm can pick it up and
  load a machine — reproduced at desk scale and solved with current learned-policy
  ("Physical AI") methods rather than scripted coordination. What already exists for it:

  | Need | Exists |
  |---|---|
  | Two-arm robot type | LeRobot 0.6.1 `bi_so_follower` — left and right `SOFollowerConfig`, each on its own USB port, with shared top-level cameras; `bi_so_leader` for teleop |
  | Simulation | Upstream `Simulation/SO101/` — URDF and MuJoCo MJCF with a `scene.xml`, STS3215 motor parameters from Open Duck Mini, mid-range joint zeros matching LeRobot's calibration. Gripper not yet modelled as LeRobot's linear 0–100 joint |
  | Training compute | The family GPU workstation ([wk-robotics `common.md`](../../../docs/common.md#the-gpu-workstation)); no ML stack installed yet |

  **Further candidate (owner, 2026-09-09): two followers as the actual shoulders of a
  humanoid torso.** Prior art and family assets, none committed to:

  - **XLeRobot** — upstream's own sibling project: two SO-101 arms on a body over a Lekiwi
    mobile base, with wrist cameras and a 2-DoF neck ([docs](https://xlerobot.readthedocs.io/en/latest/index.html)).
    Proof that the arm works as a shoulder-mounted pair, and a ready BOM for it.
  - **The family's ~80 %-built InMoov** — head, neck and shoulders already exist
    ([wk-robotics `ideas.md`](../../../docs/ideas.md#inmoov-resurrection)),
    shelved. A candidate torso, if the InMoov shoulder interface can carry the arm's mass
    (OQ-04) and its 12 V bus.
  - **koala-bot** has arms of its own design — 3 DoF each, shoulder pitch + roll + elbow,
    same STS3215 — so it is *not* a candidate torso; it is the alternative answer to
    "what a humanoid arm on this servo looks like".

  Technical notes, all unverified on hardware: the SO-101 is a table arm — `shoulder_pan`'s
  axis is vertical and the `Base` is meant to be clamped down, so a shoulder mount turns
  the base sideways and re-labels the joints; it is 5 DoF plus gripper, ~500 mm reach and
  ~500 g payload (upstream), which is roughly human forearm-and-hand scale; a pair has the
  same servo count, power and teleoperation arithmetic as the two-arm handover candidate
  above, and `bi_so_follower` serves both. The two candidates are therefore the same
  hardware in different frames, and one build can explore both.

  Consequences if either two-arm candidate is taken: a **second follower** (six more 12 V servos, so OQ-01 becomes ten
  servos, not four; a second Waveshare board; a 12 V supply sized for twelve servos, which
  stall at ~32 A in total), and for teleoperation either **two leaders** or one leader
  driving one arm at a time. Whether the handover is learned end to end or the two arms
  run separate single-arm policies with a hand-off protocol is the research question, and
  is not for this document to settle.

- **OQ-09 — What drives the servo bus at runtime.** Commissioning and calibration are
  done from a PC over USB and need nothing else (DEC-04). **Narrowed by DEC-12
  (2026-09-12) and DEC-14 (2026-09-14): the *own reflex MCU* row, a Teensy 4.1 running
  micro-ROS into ROS 2; the PC path stays only for the bench tools until then.** Still
  open: which board (the family's unallocated Teensy 4.1 NE is the candidate —
  [wk-inventory `docs/stock.md`](https://github.com/WayneKennedy/wk-inventory/blob/main/docs/stock.md)), how it connects to the bus (the Waveshare
  board's channel-A UART header, or a separate adapter), which host runs the micro-ROS
  agent and ROS 2 (this workstation, or a Pi 5 from the fleet), which ROS 2 distribution,
  where the geometric check runs (the keep-out and IK in `software/kinematics.py` are
  host-side Python today; the family pattern puts the joint envelope on the MCU and the
  world check on the host), and whether the tank's MCU takes over on mounting. **How the Teensy reaches the bus:** the two front ends and the 3.3 V caveat are in
  [wk-robotics `common.md` → Configuring a servo](../../../docs/common.md#configuring-a-servo--true-for-every-sts-project).
  **Recommendation, not decided (2026-09-14):** the Waveshare board on channel A first — in
  hand, it does the direction switching and power, and flips back to the PC tools — once its
  header's logic level has been metered; the Teensy's own half-duplex UART later, if the arm
  moves onto a robot.

  **Compute budget (2026-09-14: host measured, Teensy estimated).** Host Python, per call:
  forward kinematics 121 µs; self-collision 883 µs (13 link pairs, 75 capsule-pair tests);
  keep-out 106 µs; numeric IK, one seed 1.4 ms; multi-seed solve with all checks 4.5 ms near
  the working pose, ~70 ms averaged over random poses where failing seeds run to their
  iteration cap. **Teensy 4.1 (600 MHz Cortex-M7 with FPU), same work in C — an estimate, not
  measured:** forward kinematics and keep-out a few µs each, self-collision tens of µs, a
  closed-form IK for this arm a few µs (the numeric solver ~0.5 ms), so a full check per
  setpoint well under 0.1 ms. **The ceiling is the servo bus:** at 1 Mbaud each byte takes
  10 µs, so a goal write to six servos is ~0.3 ms and a position read ~0.5–1 ms depending on
  the servos' return delay (unmeasured) — a few hundred Hz position-only, less if current and
  temperature are read every cycle. micro-ROS carries goals in and joint states out at
  10–100 Hz and sits outside the servo loop. To verify: time the C port with the Teensy's
  cycle counter, and time the bus from the Teensy, on the unallocated 4.1 NE.

  The three
  architectures, for the record:

  | Option | How | Fits |
  |---|---|---|
  | **PC over USB** | LeRobot talks to the Waveshare board directly; no MCU | The desk / LeRobot purpose. Upstream's only supported path |
  | **Own reflex MCU** (Teensy, RP2040/Pico, ESP32) | MCU on the board's UART header (jumpers to channel A) runs the bus; joins the family topic contract via micro-ROS | The family two-tier rule ([wk-robotics `common.md`](../../../docs/common.md#compute-the-two-tier-split)); a standalone robot arm |
  | **The tank's MCU** | wk-devastator's reflex tier (Teensy 4.1, its DEC-10) drives the arm bus as more joints; the arm has no compute of its own | The mounted purpose. Cheapest, but the arm then cannot run without the tank |

  **DEC-14 settles the direction:** the MCU row. If the answer
  to OQ-08 is "both", the Waveshare board's A/B jumpers are exactly the switch between the
  PC and an MCU, so the arm can be moved between the two without rewiring.

- **OQ-10 — Upgrade units A and B from firmware 3.9 to 3.10.** **Resolved 2026-09-12 by
  DEC-11:** both upgraded with Feetech FD 1.9.8.3 on Windows; all six read 3.10 and every
  bus check passes ([`test-log.md`](test-log.md)). The pitfalls were the CH343 driver
  (install WCH's VCP driver) and FD's baud, which must be set to 1 000 000 before Search.
- **OQ-12 — Why the shrunk position limits on `wrist_flex` and `gripper` (units D and F)
  do not persist across a power cycle.** **Resolved 2026-09-14: the EEPROM `Lock` register.** A write made
  with `Lock` = 1 reads back correctly and is lost at power-off, and LeRobot's
  `enable_torque()` sets `Lock` = 1. Proven by a canary (written with `Lock` 1, gone after a
  power cycle) against limits written with `Lock` 0 (kept). Rule in [`servos.md`](servos.md)
  rule 4. History: Written 2026-09-12 with matching read-back, gone at
  the next power-up; rewritten with protection flags clear, matching read-back, gone again
  by 2026-09-14. The other four servos keep theirs, and every servo keeps its homing offset.
  `Lock` read 0 on all six that morning. Rewritten again 2026-09-14 with torque off and status 0
  ([`test-log.md`](test-log.md)). **Leading explanation, found later the same day:** LeRobot's
  `enable_torque()` writes `Lock` = 1 (and `disable_torque()` 0), so an EEPROM write made
  while the arm holds lands in RAM only; all six read `Lock` = 1 after `hold_test.py`. The
  new limits were written with `Lock` = 0 explicitly. **Half confirmed 2026-09-14:** limits written with `Lock` = 0 survived a
  power cycle on all six. **Other half confirmed the same evening:** a canary written with
  `Lock` = 1 (`wrist_roll` max 4095 → 4094) read 4095 after the next power cycle ([`test-log.md`](test-log.md)). Candidates, none verified: a `Lock`-register semantics difference for these two
  units; an EEPROM write window the servo needs before power-off; a write made in the
  unlogged 2026-09-13 session. The unlogged session also left `gripper`'s
  `Max_Torque_Limit` at 500 (others 1000) — intended or not is unrecorded.

- **OQ-13 — Who plans for two arms.** DEC-15 needs a move checked against both arms'
  hit boxes along its path before it is commanded. Two shapes: **(a) one planner, one
  planning scene, both arms as one 12-joint system on the host** — every plan sees both
  arms' present and planned motion by construction; this is what MoveIt 2 does with a
  planning group spanning two robots and what an industrial cell controller does; **(b)
  two planners, one per arm, each subscribing to the other's joint states and published
  trajectory** and re-planning on conflict — closer to "each arm knows the other's hit
  box", but two independent planners can each yield to the other or each assume the
  other yields. Either way each arm's reflex tier (Teensy, DEC-12) enforces its *own*
  envelope without the host. Not decided; (a) is the recommendation because the failure
  modes are simpler. Also open: the shared world frame between the two bases (the
  mount spacing is a measurement, 30 cm along the desk edge), and whether the geometry
  is capsules, convex hulls or the URDF meshes at runtime.

## Integration

- **OQ-04 — The arm's real mass.** Upstream and vendor figures give ~330 g of servos plus
  printed parts of unknown total. wk-devastator's OQ-12 (can the chassis carry the arm
  without tipping) is waiting on a weighed arm. **Weigh every part as it is accepted**, and
  the assembled arm when it exists; record in [`test-log.md`](test-log.md).

- **OQ-06 — How the arm mounts to wk-devastator.** No interface exists. Upstream offers an
  optional `4040_Base_Mount` and `Raised_Base`; the devastator's top plate is its own OQ-10.
  Blocked on OQ-04 and on that robot's milestone 1.
