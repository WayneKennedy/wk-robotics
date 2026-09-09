# Open Questions (pending decisions)

Unresolved. Resolve → move to [`decisions.md`](decisions.md).

A recommendation is *not* a decision — it is one option with an argument attached, offered
and not yet accepted. Do not build against one without the owner deciding.

---

## Servos and power

- **OQ-01 — Where the remaining four STS3215 12 V servos come from.** Two of six are in
  hand ([`servos.md`](servos.md)). koala-bot's two 6-packs on order are **fully allocated
  to its twelve limb joints with no spare**
  ([koala-bot `bom.md`](https://github.com/WayneKennedy/koala-bot/blob/main/docs/bom.md)),
  so drawing four from them leaves that robot short. **Recommendation, not accepted:** buy
  a dedicated 6-pack for this arm — four for the joints, two spares that also cover
  koala-bot's OQ-16 — from the same source, so the whole family shares one part number.

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
  **unrecorded** and should be written into [`hardware.md`](hardware.md).

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

- **OQ-08 — What the arm is for.** (Owner, 2026-09-09: not yet thought about.) Candidates
  in [`concept.md`](concept.md#what-it-is-for): a desk LeRobot arm, the tank's manipulator,
  or both in turn. This decides OQ-02, OQ-03 and OQ-09, so it is the one to take first.

- **OQ-09 — What drives the servo bus at runtime.** Commissioning and calibration are
  done from a PC over USB and need nothing else (DEC-04). For running the arm, three
  architectures are possible and none is chosen:

  | Option | How | Fits |
  |---|---|---|
  | **PC over USB** | LeRobot talks to the Waveshare board directly; no MCU | The desk / LeRobot purpose. Upstream's only supported path |
  | **Own reflex MCU** (Teensy, RP2040/Pico, ESP32) | MCU on the board's UART header (jumpers to channel A) runs the bus; joins the family topic contract via micro-ROS | The family two-tier rule ([wk-robotics `common.md`](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#compute-the-two-tier-split)); a standalone robot arm |
  | **The tank's MCU** | wk-devastator's reflex tier (Teensy 4.1, its DEC-10) drives the arm bus as more joints; the arm has no compute of its own | The mounted purpose. Cheapest, but the arm then cannot run without the tank |

  **Recommendation, not accepted:** defer until OQ-08 is decided, and commission,
  calibrate and first-move the arm **from the PC over USB** meanwhile, because that path
  is needed in every case and proves the mechanics without buying anything. If the answer
  to OQ-08 is "both", the Waveshare board's A/B jumpers are exactly the switch between the
  PC and an MCU, so the arm can be moved between the two without rewiring.

## Integration

- **OQ-04 — The arm's real mass.** Upstream and vendor figures give ~330 g of servos plus
  printed parts of unknown total. wk-devastator's OQ-12 (can the chassis carry the arm
  without tipping) is waiting on a weighed arm. **Weigh every part as it is accepted**, and
  the assembled arm when it exists; record in [`test-log.md`](test-log.md).

- **OQ-06 — How the arm mounts to wk-devastator.** No interface exists. Upstream offers an
  optional `4040_Base_Mount` and `Raised_Base`; the devastator's top plate is its own OQ-10.
  Blocked on OQ-04 and on that robot's milestone 1.
