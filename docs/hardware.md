# Hardware

What exists for this build, and its state. Print jobs and slicer settings are in the
family's private `3d-printing` repo; only their **results** are recorded here.

## Printed parts — SO-101 follower, 11 parts

All in **white eSUN PLA+** (DEC-05), on the family's Ender-5 S1. Upstream STLs, unmodified.
State as of **2026-09-09**:

| Part | State | Note |
|---|---|---|
| `Base` | **Usable** | Printed 2026-09-07 alone, 87 mm tall, no supports. STS3215 is a solid press fit in the pocket |
| `Base_motor_holder` | **Usable** | Plate 1, 2026-09-07 |
| `Motor_holder_Base` | **Usable** | Clean reprint on plate 1, 2026-09-07. A first copy (2026-09-06, supports everywhere) had support welded in the servo pocket and was superseded; it doubled as the first press-fit gauge |
| `Motor_holder_Wrist` | **Usable** | Plate 1, 2026-09-07 |
| `WaveShare_Mounting_Plate` | **Usable, cosmetic defect** | Plate 1, 2026-09-07. Delaminated at its raised boss; judged cosmetic 2026-09-07 and kept — mates correctly with a servo fitted |
| `Rotation_Pitch` | **Usable** | 2026-09-08, printed rotated 90° about X, which cut support from 5.4 g to 0.1 g |
| `Upper_arm` | **Usable** | Plate 3, 2026-09-08 |
| `Under_arm` | **Usable** | Plate 3, 2026-09-08 |
| `Wrist_Roll_Pitch` | **No usable copy yet** (OQ-05) | Attempt 1 (plate 3, flipped, bed-only support): fork face extruded into air. Attempt 2 (2026-09-08, supports everywhere): support welded to both fork faces. Attempt 3 (2026-09-09, organic support from the bed): **complete, not yet inspected** |
| `Wrist_Roll_Follower` | **Printed, not yet inspected** | Plate 4, 2026-09-09 |
| `Moving_Jaw` | **Printed, not yet inspected** | Plate 4, 2026-09-09, with a 5 mm brim |

The gauges from upstream `STL/Gauges/` (`Gauge_0`, `Gauge_tight_1`) were printed
2026-09-06: the servo is a tight friction fit in `Gauge_0`, the intended press fit. That
and the `Base` result established the family finding that PLA+ at these settings is
dimensionally correct with no elephant-foot compensation
([wk-robotics `common.md`](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#press-fits-and-supports)).

**Nothing is assembled.** No part has been fastened to another; servos have only been
test-fitted into pockets.

## Electronics in hand

| Item | Qty | Since | Note |
|---|---|---|---|
| Waveshare **ST3215 12 V** bus servo (Feetech STS3215 rebadge, 1/345), firmware **3.10** (shipped 3.9, upgraded 2026-09-12, DEC-11) | 2 | 2026-09-07 | Amazon. Bought as koala-bot's test-fit pair; now this arm's `shoulder_pan` and `shoulder_lift` ([`servos.md`](servos.md)). Box contained M3 horn screws and M2×5 self-tapping case screws |
| Feetech **STS3215 12 V** bus servo (1/345), firmware 3.10 | 4 | 2026-09-12 | From koala-bot's RCmall packs (DEC-09); this arm's IDs 3–6 ([`servos.md`](servos.md)). Each box: two metal horns, M3×6 horn screws, M2×6 case screws |
| Waveshare **Bus Servo Adapter (A)** v1.1 | 1 | 2026-09-07 | Upstream's "Motor Control Board" (DEC-03). CH343 USB-C. Both jumpers on **B** for USB |
| Feetech **FE-URT-2** | 1 | 2026-09-08 | Spare / bench bus adapter. Not needed for the arm |

Adapter behaviour, pinouts and power rules are family facts:
[wk-robotics `common.md` → Configuring a servo](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#configuring-a-servo--true-for-every-sts-project).

**Not in hand:** a decided 12 V supply (OQ-03), the
M2×6 and M3×6 fasteners upstream's guide calls for (OQ-07). The 12 V source used on the
bench on 2026-09-09 read 12.3–12.4 V at the servo and is otherwise **unrecorded**; on
2026-09-12 it was a **3S LiPo**, not fully charged, reading 11.7–11.9 V.
