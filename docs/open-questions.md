# Open Questions (pending decisions)

Unresolved. Resolve → move to [`decisions.md`](decisions.md).

A recommendation is *not* a decision — it is one option with an argument attached, offered
and not yet accepted. Do not build against one without the owner deciding.

---

## Servos and power

- **OQ-01 — Where the remaining four STS3215 12 V servos come from.** **Resolved
  2026-09-12 by DEC-09:** taken from koala-bot's RCmall packs, which leaves that robot four
  short. The recommendation here had been a dedicated 6-pack; the owner chose otherwise.

- **OQ-02 — Whether to build the leader arm.** Depends on OQ-08. LeRobot's teleoperation
  and data collection assume an SO-101 leader: 7.4 V servos in three gear ratios, its own control board and
  5 V supply. Alternatives exist (keyboard, gamepad, other leaders) but none is chosen.
  Nothing for a leader has been printed or bought.

- **OQ-03 — The 12 V supply.** Upstream specifies a **12 V, 5 A+** brick for the 12 V
  follower. The family rule for servo robots is a stiff source — a **3S LiPo** with a fuse
  and bulk capacitance — because six STS3215 stall at 16 A in total
  ([wk-robotics `common.md` → Power integrity](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#power-integrity)).
  A desk arm on a brick and an arm riding a robot on the robot's pack are different
  answers; both may be right at different times. What powered the bench on 2026-09-09 is
  **unrecorded**; on 2026-09-12 it was a 3S LiPo, not fully charged, 11.7–11.9 V at the
  servos ([`hardware.md`](hardware.md)). The family's 3S ceiling applies (wk-robotics
  `common.md`).

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
  OQ-02 (a leader) becomes likely rather than optional, OQ-03 is answered "a 12 V brick"
  for the desk phase, and **cameras** join the sourcing list — LeRobot's imitation-learning
  loop needs one or two, and none is owned or specified.

  **Leading candidate, likely but not decided (owner, 2026-09-09): two followers
  cooperating in one workspace.** Motivated by a real problem in large-scale industrial
  machinery — one arm places a pallet of components where a second arm can pick it up and
  load a machine — reproduced at desk scale and solved with current learned-policy
  ("Physical AI") methods rather than scripted coordination. What already exists for it:

  | Need | Exists |
  |---|---|
  | Two-arm robot type | LeRobot 0.6.1 `bi_so_follower` — left and right `SOFollowerConfig`, each on its own USB port, with shared top-level cameras; `bi_so_leader` for teleop |
  | Simulation | Upstream `Simulation/SO101/` — URDF and MuJoCo MJCF with a `scene.xml`, STS3215 motor parameters from Open Duck Mini, mid-range joint zeros matching LeRobot's calibration. Gripper not yet modelled as LeRobot's linear 0–100 joint |
  | Training compute | The family GPU workstation ([wk-robotics `common.md`](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#the-gpu-workstation)); no ML stack installed yet |

  **Further candidate (owner, 2026-09-09): two followers as the actual shoulders of a
  humanoid torso.** Prior art and family assets, none committed to:

  - **XLeRobot** — upstream's own sibling project: two SO-101 arms on a body over a Lekiwi
    mobile base, with wrist cameras and a 2-DoF neck ([docs](https://xlerobot.readthedocs.io/en/latest/index.html)).
    Proof that the arm works as a shoulder-mounted pair, and a ready BOM for it.
  - **The family's ~80 %-built InMoov** — head, neck and shoulders already exist
    ([wk-robotics `ideas.md`](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/ideas.md#inmoov-resurrection)),
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
  (2026-09-12): the PC path for the LeRobot exploration, then the *own reflex MCU* row
  with a Teensy 4.1.** Still open: which board, how it connects to the bus, micro-ROS or
  bare-metal first, and whether the tank's MCU takes over on mounting. The three
  architectures, for the record:

  | Option | How | Fits |
  |---|---|---|
  | **PC over USB** | LeRobot talks to the Waveshare board directly; no MCU | The desk / LeRobot purpose. Upstream's only supported path |
  | **Own reflex MCU** (Teensy, RP2040/Pico, ESP32) | MCU on the board's UART header (jumpers to channel A) runs the bus; joins the family topic contract via micro-ROS | The family two-tier rule ([wk-robotics `common.md`](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#compute-the-two-tier-split)); a standalone robot arm |
  | **The tank's MCU** | wk-devastator's reflex tier (Teensy 4.1, its DEC-10) drives the arm bus as more joints; the arm has no compute of its own | The mounted purpose. Cheapest, but the arm then cannot run without the tank |

  **DEC-08 settles the near term:** the PC-over-USB path is used for the whole LeRobot
  exploration. The MCU options remain open for afterwards. If the answer
  to OQ-08 is "both", the Waveshare board's A/B jumpers are exactly the switch between the
  PC and an MCU, so the arm can be moved between the two without rewiring.

- **OQ-10 — Upgrade units A and B from firmware 3.9 to 3.10.** **Resolved 2026-09-12 by
  DEC-11:** both upgraded with Feetech FD 1.9.8.3 on Windows; all six read 3.10 and every
  bus check passes ([`test-log.md`](test-log.md)). The pitfalls were the CH343 driver
  (install WCH's VCP driver) and FD's baud, which must be set to 1 000 000 before Search.

## Integration

- **OQ-04 — The arm's real mass.** Upstream and vendor figures give ~330 g of servos plus
  printed parts of unknown total. wk-devastator's OQ-12 (can the chassis carry the arm
  without tipping) is waiting on a weighed arm. **Weigh every part as it is accepted**, and
  the assembled arm when it exists; record in [`test-log.md`](test-log.md).

- **OQ-06 — How the arm mounts to wk-devastator.** No interface exists. Upstream offers an
  optional `4040_Base_Mount` and `Raised_Base`; the devastator's top plate is its own OQ-10.
  Blocked on OQ-04 and on that robot's milestone 1.
