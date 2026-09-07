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

**Also in the family, and possibly available:** koala-bot holds a Teensy 4.0 and a
Pololu Dual TB9051FTG. Whether either is spare or committed is **not established here** —
check `koala-bot/docs/sourcing.md` before assuming.

## Needed, once the gating questions close

**Do not order against this table yet.** Every row depends on OQ-01 or OQ-11.

| Part | Depends on | Note |
|---|---|---|
| Replacement gearmotors with encoders | OQ-01, OQ-11 | Voltage undecided; bracket and 4 mm shaft unverified |
| Motor driver | OQ-02 | TB9051FTG recommended, not accepted |
| 32-bit MCU | OQ-03 | Teensy 4.0 owned in-family; 4.1 is the upstream-supported part |
| Battery pack + fuse + connector | OQ-01, OQ-07 | Size for **stall**, not average draw |
| Logic-rail regulator | DEC-07 | Isolated from the motor feed — family power rule |
| Bulk capacitance | — | ~1000–2200 µF across the motor bus, per the family power rules |
| Printed mounts, tray, battery bay | OQ-10 | Off the family printer; PETG default |

## The reference the family already carries

Servo, printer and power findings that apply here are in
[wk-robotics/docs/common.md](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md).
They are not repeated here — link to them.
