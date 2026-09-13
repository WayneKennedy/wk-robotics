# Sourcing

UK-focused, as the rest of the family is. **Ordered so far:** the drive motors (DEC-11,
**due end of October 2026**, revised 2026-09-09) and a Teensy 4.1 (DEC-10), both bought for this robot. The
driver (DEC-13) is in hand since 2026-09-11 — supplied by koala-bot's over-order for a
cancelled four-wheel V1, not bought by this project. Nothing else.

UK import: **VAT 20 %** applies; the **£135 threshold** (goods value, excluding
shipping) decides how — under it the seller charges VAT at checkout, over it the courier
collects VAT plus a ~£8–12 handling fee.

## Already owned

| Part | Note |
|---|---|
| DFRobot Devastator chassis (ROB0128) | With original 6 V motors — see [`hardware.md`](hardware.md) |
| Raspberry Pi 4 | Fitted to the first build (OQ-06) |
| 2 × Intel RealSense cameras | Models **unrecorded** (OQ-09) |
| Arduino Nano, L298N, DC-DC module | Retired by DEC-03; not part of the new build |

**What the family holds, checked 2026-09-11.** The Pololu Dual TB9051FTG this robot uses
was koala-bot's single board, borrowed on 2026-09-07; koala-bot's later order delivered
two more, so this robot now has one of its own and the loan is dissolved (DEC-13,
amended; koala-bot DEC-51). Family drive-hardware holdings are tabulated in
[wk-robotics `common.md`](../../../docs/common.md#drive-motors-drivers-and-mcus-in-hand). koala-bot's Teensy 4.0 was never borrowed and is
moot regardless — DEC-10 buys a 4.1, and one has been ordered.

## Needed, once the gating questions close

**Motors and MCU are ordered and the driver is in hand; the rest still waits on the
power budget** (DEC-07) — purchases follow a budget rather than produce one.

| Part | Depends on | Note |
|---|---|---|
| 2 × Pololu #4865 — 25D 47:1 MP 12V, 48 CPR encoder | — | **DEC-11. Ordered; back order, due end of October 2026 (revised 2026-09-09; was ~26 Sept).** ~£50 each, RobotShop UK. Remove the end caps on fitting — 67 mm each does not fit, 64.5 mm does |
| Pololu Dual TB9051FTG | — | **DEC-13. In hand** — this robot's own since 2026-09-11, from koala-bot's over-order; not bought by this project. 2.6 A cont. / 5 A peak per channel; one board drives both tracks |
| Teensy 4.1 | — | **DEC-10. Ordered** for this robot — the upstream-**Supported** board, not the "Not tested" 4.0 |
| 3S LiPo + fuse + connector | OQ-07 | **12 V / 3S settled by DEC-12**; capacity and fuse rating open. Size for **stall**, not average draw |
| Logic-rail regulator | DEC-07 | Isolated from the motor feed — family power rule |
| Bulk capacitance | — | ~1000–2200 µF across the motor bus, per the family power rules — **and again on the arm bus** if OQ-12 resolves yes |
| Printed mounts, tray, battery bay | OQ-10 | Off the family printer; PETG default |

## The reference the family already carries

Servo, printer and power findings that apply here are in
[wk-robotics/docs/common.md](../../../docs/common.md).
They are not repeated here — link to them.
