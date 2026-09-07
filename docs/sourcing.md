# Sourcing

UK-focused, as the rest of the family is. **Nothing has been ordered.**

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

**Nothing is borrowable from the family — checked 2026-09-07.** koala-bot's Teensy 4.0 and
Pololu Dual TB9051FTG are **qty 1 each in its confirmed order, purchased 2026-09-01**
(`koala-bot/docs/sourcing.md`): committed to that build, not spare. This robot buys its own
of both. (The 4.0 is moot here regardless — DEC-10 buys a 4.1.)

## Needed, once the gating questions close

**Do not order against this table yet** — milestone 0 buys nothing. Every row but the MCU
depends on OQ-01 or OQ-11.

| Part | Depends on | Note |
|---|---|---|
| Replacement gearmotors with encoders | OQ-01, OQ-11 | Voltage undecided; bracket and 4 mm shaft unverified |
| Motor driver | OQ-02 | TB9051FTG recommended, not accepted |
| Teensy 4.1 | — | Settled by DEC-10 — the upstream-**Supported** board, not the "Not tested" 4.0 |
| Battery pack + fuse + connector | OQ-01, OQ-07 | Size for **stall**, not average draw |
| Logic-rail regulator | DEC-07 | Isolated from the motor feed — family power rule |
| Bulk capacitance | — | ~1000–2200 µF across the motor bus, per the family power rules — **and again on the arm bus** if OQ-12 resolves yes |
| Printed mounts, tray, battery bay | OQ-10 | Off the family printer; PETG default |

## The reference the family already carries

Servo, printer and power findings that apply here are in
[wk-robotics/docs/common.md](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md).
They are not repeated here — link to them.
