# Sourcing

In hand versus still needed, for the follower only (no leader will be built — DEC-13). UK-based, as the
rest of the family is. Upstream's BOM with prices and vendors:
[SO-ARM100 README](https://github.com/TheRobotStudio/SO-ARM100#bill-of-materials-bom).

## In hand

| Part | Qty | Source, date | Note |
|---|---|---|---|
| Waveshare ST3215 12 V servo | 2 | Amazon 204-4694570-7173960, ordered 2026-09-02, delivered 2026-09-04 | Bought for koala-bot's bench, reallocated here 2026-09-09 ([`servos.md`](servos.md)). £31.90 each; the listing names neither Waveshare nor 12 V |
| Feetech STS3215 12 V servo, 1/345 | 4 | RCmall via koala-bot, arrived 2026-09-12 | Four of koala-bot's twelve, reallocated here 2026-09-12 (DEC-09), **permanent since 2026-09-14** (backfill 6-pack ordered for koala-bot); £14.16 each (£84.95 per 6-pack, invoiced; koala-bot `sourcing.md`). Each came with two metal horns, M3×6 horn screws and M2×6 case screws |
| Waveshare Bus Servo Adapter (A) v1.1 | 1 | Amazon 204-4524452-2059566, 2026-09-07, delivered same day | Upstream "Motor Control Board" (DEC-03). Invoiced as "Waveshare Serial Bus Servo Driver Board", £9.99 |
| Feetech FE-URT-2 | 1 | Amazon, 2026-09-08 (as recorded) | Spare bus adapter; not required by the arm. **Invoice conflict:** no FE-URT-2 and no 2026-09-08 order is in the mail; the adapter order above holds a "Stemedu … FE-URT-1" (£15.65). Which board this is, TBC against its silkscreen |
| InnoMaker USB 2.0 UVC cameras: 720P 120° DFOV, and 1080P 130° wide angle | 2 | Amazon 204-2311587-5838765, ordered 2026-09-12; 1080P delivered 2026-09-15, 720P 2026-09-17 (delivery emails) | £13.99 and £16.99. One for the wrist mount, one for a workspace view; **which is which is not decided**, and whether either board matches the 32 × 32 mm hole pattern the upstream mounts assume is **to be checked**. Purpose since DEC-14: the geometry work (a workspace view for the world side of the keep-out, a wrist view for the tool), not LeRobot recording. Upstream's standard is a **32 × 32 mm UVC camera module** (innomaker-type, four corner holes for the servos' M2 screws, manual focus, run at 640 × 480 / 30 fps) — one on the wrist, optionally one overhead; the printed mounts are in upstream `Optional/` ([`hardware.md`](hardware.md)). Upstream's listings: wrist → ASIN **B0CNCSFQC1**; overhead → ASIN **B0CLRJZG8D** |
| All 11 printed parts, PLA+ | — | family printer, 2026-09-06 → 09 | Three still to inspect or reprint ([`hardware.md`](hardware.md)) |

## Still needed

| Part | Qty | Status |
|---|---|---|
| 12 V supply, ≥5 A | 1 | **OQ-03** — upstream brick versus family 3S pack; undecided |
| M2×6 and M3×6 screws | counts per upstream guide | **OQ-07** — not tallied, not bought |
| USB-C cable, table clamps | 1, 2 | Upstream BOM items; whether already owned is unrecorded. Candidate only: 4 × 4" F-clamps, Amazon 204-1157421-6505962, 2026-09-14, £9.99 — nothing ties them to the arm |
| Second follower: 11 printed parts, 6 servos, Waveshare board, clamp | 1 set | **Needed — DEC-15 (2026-09-14): two arms 30 cm apart.** Nothing ordered or printed; servo route as DEC-09's RCmall packs (£84.95 a 6-pack on koala-bot's 2026-09-01 order; £103.15 on its 2026-09-14 backfill) |
