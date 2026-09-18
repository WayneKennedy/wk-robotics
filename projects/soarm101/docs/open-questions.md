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

  **2026-09-18 — THE SAG DOES NOT EXIST. Closed.** Logging all six servos' voltage instead of
  `min()` showed that **no moving servo ever reads below 11.4 V**, while the only low samples are
  **isolated single frames on the two joints that are not moving** ([`test-log.md`](test-log.md)).
  The logged "rail minimum" was `min()` across six servos — ~6000 chances a run to catch a corrupt
  frame at OQ-18's rate — so it measured **the bus's corruption rate, not the supply**, which is
  why every supply from 2 A to 10 A "sagged" identically. **True rail under load: 11.9–12.1 V.**
  **No bulk capacitance is indicated, and there is nothing for a multimeter or a logger to find
  here.** The guard now uses the median of the six. Everything below is kept as the record of how
  a phantom survived four days.

  **2026-09-17 — the sag is not the supply. Where it *is* remains open.** The
  owner ran the arm from a hobby **2 A** brick on the barrel jack to test for brownouts. Across
  the same cube at 5 cm/s, the rail minima were **10.9 V and 10.4 V on the 10 A bench supply**
  against **10.8 V on the 2 A brick** — a bench supply with five times the headroom sags as deep
  or deeper, so the transient is **not the source's current capability**. That much is settled.

  **What is not settled is where the sag happens, and a first pass here overstated it** (corrected
  2026-09-18, owner's challenge). The rail is read by each **servo's own internal ADC, downstream
  of the connector**, so the measurement cannot separate (a) drop in the leads and connectors,
  which bulk capacitance at the bus head would fix, from (b) a dip inside the servo during its own
  commutation, or an artefact of when its ADC samples — which **no external capacitor can touch**.
  Three supplies look identical under either explanation. Sampling at 20 Hz, on a separate
  round-trip from current, cannot tell them apart either.

  **The test that settles it costs nothing: a multimeter across the board's power input during a
  cube run.** Steady 12 V there while the servos report 10.5 V means (b), and the question closes
  with nothing bought. Until that is done, **do not fit capacitance on the strength of this
  evidence** — see the standing recommendation's caveat below. **Earlier entries understated the
  sag itself**: the "11.8–12.0 V" figures were a mislabelled closing sample, corrected in
  [`test-log.md`](test-log.md).

  **The 2 A brick is not cleared.** It provoked no brownout, but sampled sum current peaked at
  **377 mA** — 19 % of its rating — because the cube is a low-load path. Against the 2 A peak
  measured on `shoulder_lift` *lifting the arm*, a 2 A supply is at or below a single joint's
  demand, and it feeds through a barrel jack whose rating on the Waveshare board is unverified.
  **Do not run fast or loaded moves from it.** The recommendation above is unchanged on the
  supply: 12.0 V regulated, 10 A, into the screw terminals.

  **On the bulk capacitance: no longer indicated at all (2026-09-18, after the sag was disproved).**
  What follows was written when the sag was still believed real, and already argued the case was
  weak; it is now moot for this arm. Kept because the reasoning about provenance still applies.

  **The recommendation is weaker than it was written.**
  **Upstream asks for none.** `SO-ARM100`'s README specifies only "a 12V 5A+ power supply" for
  this exact variant — a barrel-jack brick — and the repo mentions no capacitor, fuse or brownout
  anywhere. The family rule comes from
  [`common.md` → Power integrity](../../../docs/common.md#power-integrity), which states its own
  provenance: *"banked from an earlier InMoov build"* — dozens of **PWM hobby servos** on a shared
  rail. That page already records that **one InMoov failure mode does not transfer** to
  closed-loop STS bus servos; this may be a second. Against it: this arm peaks at 377 mA summed,
  and across three supplies and a dozen runs has never dropped a packet, reset a servo or
  reported anything but status 0. **Settle the multimeter test first.** If capacitance is ever
  wanted, it does **not** mean breaking into the servo loom — the board is a pass-through, so V+
  at its power input is the same node as the servo sockets, and a capacitor goes into the same
  screw terminals as the supply leads (owner raised the loom concern, 2026-09-18).

- **OQ-17 — Whether to tune the servos' position loop, and how far.** **Raised 2026-09-17.**
  The arm's speed is capped by proportional following error, not by torque, heat, slew or
  acceleration — all four ruled out by experiment ([`test-log.md`](test-log.md)). All six servos
  run the Feetech defaults **`P_Coefficient` 16, `I_Coefficient` 0, `D_Coefficient` 32**, never
  written by any script here ([`servos.md`](servos.md)). With no integral term the error cannot
  be driven out, and the cube trips the 150-count tracking guard at 10 cm/s — about twice the
  validated speed — with the elbow at 152 counts while no other joint exceeds 50.

  **What makes it a question rather than a fix:** `P_Coefficient` is register 21, **EEPROM**, so
  it is a durable change to the hardware, not a run-time flag, and by this repo's conventions a
  logged, owner-approved write. Raising P stiffens the loop and risks oscillation or buzz —
  the real hazard with I = 0 — and makes current draw spikier, which bears directly on
  OQ-03. It is reversible: 16 goes back the same way.

  **Recommendation, not decided (2026-09-17): raise P on `elbow_flex` alone first**, 16 → 32,
  and measure. It is the only joint at the wall, so one servo isolates the oscillation risk
  before the other five are touched, and halving the following error should bring 20 cm/s inside
  the existing guard without loosening it. **Do it from a proper 12 V supply, not the 2 A brick**
  (OQ-03). The alternative — raising `--track` and accepting the lag — trades away the accuracy
  milestone 4 just bought: 152 counts is 13.4° of elbow, several cm at the tool.

  **Partly answered 2026-09-18 (owner approved; done).** `P_Coefficient` 16 -> **32 on all four
  arm joints**, `wrist_roll` and `gripper` left at 16 ([`servos.md`](servos.md),
  [`test-log.md`](test-log.md)). **No oscillation, buzz or hunting appeared at 32**, which was the
  feared failure mode. It bought **~20% less following error, not the 50%** a proportional model
  predicts — the coefficient does not map linearly onto loop gain. Combined with corner easing and
  a new joint-speed cap, the cube went from **4.6 to 7.5 cm/s real, a 63% gain**, at
  `--tool-speed 8 --corner-speed 4 --max-joint-speed 600` with max lag 86 of 150.

  **What the tuning revealed, and what is still open.** Above ~8 cm/s the limit is no longer
  steady-state following error but a **joint reversal at a path corner**: the servo's turnaround
  time lets error integrate while the command advances, and tool-space easing cannot see it
  because the Jacobian makes the joint reversal sharp where the tool corner is gentle. Still open:
  whether P above 32 helps or starts to ring; whether `wrist_roll` and `gripper` should follow
  (the gripper reached lag 116 of 150 under `--jaw-cycle`, the closest any joint has come);
  whether a small non-zero `I` is worth the wind-up risk; whether a joint-space *acceleration*
  limit beats the velocity cap for reversals; and whether any of it survives the move to the
  Teensy (OQ-09), which will run its own loop above the servos' and may prefer them soft.

- **OQ-18 — Why 1.3-2.4% of telemetry reads come back corrupted, and whether to chase it.**
  **Raised and largely ANSWERED 2026-09-18: it is not the bus.** `Present_Position` is
  encoder-derived and has **0 impossible values in 82,260 readings**, while ADC-derived temperature
  corrupts at 1.58% — over the same bus, the same transactions, the same checksum. Corruption is
  0.00% with torque off, 0.25% holding still, 1.3-6% moving. **The STS3215's internal ADC is
  disturbed by its own motor drive**; the servo reports a wrong value faithfully, and the frame is
  valid ([`test-log.md`](test-log.md)). **Nothing on the bus is broken and nothing external fixes
  it** — not baud, not `Return_Delay_Time` (0 on all six), not wiring, not capacitance.

  **What remains open** is only the engineering response: whether to sample ADC channels only when
  a joint is still, whether a median across servos is enough for every guard (`--max-ma` still
  takes the worst single servo, the weakest guard left), and what the Teensy should do at
  reflex-tier rates, where a raw ADC reading at 200-1000 Hz would trip constantly (OQ-09).
  **Position is trustworthy and the control loop rests on it**, which is why the OQ-17 tuning
  stands. Original framing below.

  **Original framing.** Counted across every `shapes.py` log since 2026-09-14: **1.35-1.55% on
  the bench PSU and the 2 A brick, 2.35% on the Maplin** — a persistent background on every
  supply, not the occasional freak the earlier entries describe. A plausibility filter measuring
  it directly puts the true rate nearer **6%**. It has caused at least two false guard trips
  (130 C in 2026-09-14, **63 C on 2026-09-18 with every servo at 37 C**), and at that rate two bad
  samples in a row is near-certain over a long run, so **the two-sample debounce never protected
  anything**. A corrupted sample carried the same value, 78, in both the temperature and current
  columns, so **frames are being mis-parsed, not servos misreporting**.

  **It silently produced a four-day phantom.** The "rail sags to 10.5 V" finding that OQ-03 carried
  from 2026-09-14, and the bulk-capacitance case built on it, were **entirely this corruption**
  read through a `min()` across six servos (2026-09-18). That is the strongest argument for
  chasing it: it does not merely trip guards, it **manufactures findings**, and it did so across
  three supplies without once looking like noise.

  **Mitigated, not fixed:** `shapes.py` now rejects physically impossible temperature jumps
  (> 5 C in one 50 ms step) and reports the count. Candidate causes, none tested: electrical noise
  from the servo rail onto the bus under load (the mechanism
  [`common.md` → Power integrity](../../../docs/common.md#power-integrity) describes, and a far
  more credible symptom than the voltage sag chased under OQ-03); `Return_Delay_Time`; the
  half-duplex turnaround on the Waveshare adapter; `num_retry` masking hard failures as soft ones.
  Worth doing before the Teensy takes the bus (OQ-09), since a reflex tier reading corrupt
  telemetry at 200-1000 Hz is a different proposition from a 20 Hz host loop that can shrug.

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
  open: which board (**the family's unallocated Teensy 4.1 NE, and since 2026-09-18 this project
  is its sole claimant** — koala-bot's competing fallback claim went when its OQ-14 was closed by
  buying a third NE rather than testing its Teensy 4.0, koala-bot DEC-18 as amended; **the family
  now standardises on the 4.1 NE for every reflex tier**, and the 4.0 is off load-bearing paths
  because upstream lists it "Not tested" —
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

- **OQ-04 — The arm's real mass.** **Answered 2026-09-17: 810 g** — fully assembled, serial bus
  driver attached, no external wiring connections; weighed by the owner, instrument not recorded
  ([`test-log.md`](test-log.md)). Against upstream's ~330 g of servos, the printed parts and
  fasteners come to ~480 g. **wk-devastator's OQ-12** (can the chassis carry the arm without
  tipping) was waiting on this and is now unblocked, as is OQ-06 behind it. Still to add
  when it matters: the loom from the arm to whatever drives the bus, which 810 g excludes.

- **OQ-06 — How the arm mounts to wk-devastator.** No interface exists. Upstream offers an
  optional `4040_Base_Mount` and `Raised_Base`; the devastator's top plate is its own OQ-10.
  Blocked on OQ-04 and on that robot's milestone 1.
