# Test log

What was actually measured, on what date, under what conditions — including "no change
needed" results, which are findings too. Print-job telemetry lives in the private
`3d-printing` repo; only fit and function results are here.

## Format

Each entry: date · what was tested · conditions · result · what changed as a result.

## Entries

### 2026-09-12 · Assembled; calibrated with LeRobot's routine, stepwise

**Conditions:** arm assembled per upstream's guide the same day (milestone 2), no camera,
at rest on the bench. Waveshare Bus Servo Adapter (A) on this host, **second 3S LiPo, more
charge than the morning's, 12.2–12.4 V at the servos.** LeRobot 0.6.1. Written by
`software/calibrate.py`, which runs `SOFollower.calibrate()`'s writes as separate steps
(`home` → `sweep-start` → `sweep-stop`) because the arm is moved by hand between them.
Robot id **`wk_soarm101`**; the calibration JSON LeRobot will load is
`~/.cache/huggingface/lerobot/calibration/robots/so_follower/wk_soarm101.json`, copied to
[`software/calibration/wk_soarm101.json`](../software/calibration/wk_soarm101.json).

**Before:** every servo at factory calibration — `Homing_Offset` 85, limits 0–4095.

**Homing** — owner held all six at approximate mid-range; `set_half_turn_homings()` wrote
an offset so that pose reads 2047:

| Joint | Raw at mid-range | `Homing_Offset` written |
|---|---|---|
| `shoulder_pan` | 1168 | −793 |
| `shoulder_lift` | 2831 | 870 |
| `elbow_flex` | 3517 | 1555 |
| `wrist_flex` | 3793 | 1831 |
| `wrist_roll` | 2002 | 40 |
| `gripper` | 423 | −1539 |

**Range sweep** — 7 489 samples at ~50 Hz while the owner moved each joint to just short of
both stops; `wrist_roll` is LeRobot's full-turn joint and gets 0–4095 unswept:

| Joint | `Min_Position_Limit` | `Max_Position_Limit` | Span (counts / °) |
|---|---|---|---|
| `shoulder_pan` | 750 | 3343 | 2593 / 228 |
| `shoulder_lift` | 736 | 2997 | 2261 / 199 |
| `elbow_flex` | 1880 | 4028 | 2148 / 189 |
| `wrist_flex` | 1002 | 3137 | 2135 / 188 |
| `wrist_roll` | 0 | 4095 | full turn |
| `gripper` | 1328 | 2737 | 1409 / 124 |

Read back from the servos after the write and matching the JSON. The mid-range pose sits
well inside every range except `elbow_flex`, where it is 167 counts (15°) from the recorded
minimum — the "middle" was held near one end of the elbow's travel. Harmless for LeRobot,
which normalises on the range; noted in case the elbow's usable range looks lopsided later.
Limits are a hand sweep and stop short of the hard stops by an unmeasured margin.

**Not yet done:** a scripted move under torque (milestone 3's exit) — the arm must be
clamped first.

**Changed as a result:** servos hold homing and limits; `servos.md` points here; roadmap
milestone 3 half done; OQ-03 gains the second pack.

### 2026-09-12 · Servos 3–6 commissioned from koala-bot's RCmall packs

**Conditions:** as 2026-09-09 — Waveshare Bus Servo Adapter (A), jumpers on B, USB to
this Linux host, 12 V on the adapter (source unrecorded, OQ-03), LeRobot 0.6.1. Written
by `software/set_servo_id.py`, one servo on the bus at a time. All four are Feetech-branded
STS3215 from the packs koala-bot bought 2026-09-01 (DEC-09).

| Servo | Factory state | Written | Read back after write |
|---|---|---|---|
| Unit C → `elbow_flex` | ID 1, 1 Mbaud, model 777 | **ID 3**, baud code 0 | 11.8 V, position 4092, 31 °C, torque off |
| Unit D → `wrist_flex` | ID 1, 1 Mbaud, model 777 | **ID 4**, baud code 0 | 11.8 V, position 2, 26 °C, torque off |
| Unit E → `wrist_roll` | ID 1, 1 Mbaud, model 777 | **ID 5**, baud code 0 | 11.9 V, position 2, 25 °C, torque off |
| Unit F → `gripper` | ID 1, 1 Mbaud, model 777 | **ID 6**, baud code 0 | 11.8 V, position 4094, 25 °C, torque off |

The rail read 11.7–11.9 V throughout: the bench supply this day was a **3S LiPo, not fully
charged** (owner) — which also explains the 12.3–12.4 V of 2026-09-09 being different
(OQ-03). Positions are raw, pre-homing.

**Six on one bus — failed, diagnosed, fixed the same day.** Chained A–F, 12 V from the pack.

| Step | Result |
|---|---|
| `broadcast_ping()` | `{1, 4, 5, 6}` every time; IDs 2 and 3 missing; one reply flagged `Angle sen error` |
| Addressed `ping(i)`, each ID ×3 | all six answer 777, every time |
| Addressed reads by ID — voltage, position, temperature, `Status`, `Baud_Rate`, firmware | all six: status 0, baud code 0, model 777; **A and B firmware 3.9, C–F firmware 3.10** |
| `sync_read` of all six in LeRobot order (1…6) | **0 of 5**, `Incorrect status packet` |
| `sync_read` of every pair | 15 of 15 pass |
| `sync_read` of every triple | pass except `(1,2,3)`, `(1,2,4)`, `(1,2,5)`, `(1,2,6)` — 0 of 3 each |
| Orderings of 1,2,3 | `(1,2,3)` and `(2,1,3)` fail; `(1,3,2)`, `(2,3,1)`, `(3,1,2)`, `(3,2,1)` pass |
| Raw bytes of `(1,2,3)` | `ff ff 01 04 00 76 04 80` · `ff ff 02 04 00 bb f7` · `ff ff 03 04 00 fc 0f ed` — ID 3's header overwrites ID 2's checksum byte. A **bus collision**, not host parsing |
| `Return_Delay_Time` 50 then 250 on IDs 1–2; then on 3–6 (EEPROM writes) | no effect on any combination; broadcast ping goes empty at 250. **All reset to 0** and read back 0 |
| Swap IDs of B and C (2 ↔ 3, via temp ID 7) | still 0 of 5; **reverted** |
| Rule: a 3.10 unit starting after a 3.9 unit that was not first responder collides | predicted 10 of 10 test orders, e.g. `(3,4,5,6,1,2)` and `(1,3,4,5,6,2)` pass 5/5, `(4,5,6,1,2,3)` and `(3,1,4,5,6,2)` fail 0/5 |
| **Fix: B 2 → 6, F 6 → 2** (via temp ID 7; DEC-10) | `sync_read` 1…6 **10 of 10**. Broadcast ping still drops ID 1 on some calls — not the runtime path |

Final state, all six on one bus, 3S pack:

| ID | Joint | Unit | Firmware | V | Position (raw) | °C | Status |
|---|---|---|---|---|---|---|---|
| 1 | `shoulder_pan` | A | 3.9 | 11.7 | 1142 | 31 | 0 |
| 2 | `shoulder_lift` | F | 3.10 | 11.7 | 4094 | 33 | 0 |
| 3 | `elbow_flex` | C | 3.10 | 11.7 | 4092 | 31 | 0 |
| 4 | `wrist_flex` | D | 3.10 | 11.8 | 2 | 32 | 0 |
| 5 | `wrist_roll` | E | 3.10 | 11.7 | 0 | 31 | 0 |
| 6 | `gripper` | B | 3.9 | 11.7 | 1979 | 32 | 0 |

**Reliability after the fix, 30 trials each:** LeRobot order 1…6 — **30/30** on
`Present_Position` and 30/30 on `Present_Voltage`; `(1,2)` 30/30; `(2,3,4,5,6)` 30/30;
`(6,1)` 30/30; `(3,6,1)` 30/30; `(3,4,5,6,1,2)` **0/30** — which the rule predicts, because
F (3.10, now ID 2) follows A (3.9, now non-first). The same order passed 5/5 before the
swap, when ID 2 was B (3.9). The rule has held for every order tried, before and after.

Also observed: a first EEPROM write on the full bus once returned no status packet and did
not apply; with `num_retry=4` every write applied and read back.

**Firmware upgrade of A and B, 3.9 → 3.10 — same afternoon, root fix.** Owner's call:
upgrade rather than live with the ID workaround. On the Windows host: **FT SCServo Debug
(FD) 1.9.8.3**, WCH **CH343SER** VCP driver installed for the Waveshare board (Windows had
bound it to a generic CDC driver). FD then listed no servo until **BaudR was set to
1000000** — the screenshot showed 115200, and the port was not open; that setting, not the
driver, is the confirmed cause of "port but no servo" (whether CDC would also have worked
at 1 Mbaud is untested). With A alone on the board FD found ID 1; *Upgrade → Online →
Upgrade* reported success; B was done seated in the arm with A on the bus. Supply: the
same 3S pack, ~11.6 V.

Back on this host: all six read **firmware 3.10**, status 0, baud code 0. The DEC-10 swap
was reverted (B → 2, F → 6, via temp ID 7) so IDs follow the seated units.

| Check, all six chained A–F, 3S pack | Result |
|---|---|
| `sync_read` 1…6, `Present_Position` / `Present_Voltage` | **30/30 · 30/30** |
| `(1,2,3)`, `(2,1,3)` — failed 0/n before | **30/30 · 30/30** |
| `(3,4,5,6,1,2)`, `(4,5,6,1,2,3)` — failed 0/30 before | **30/30 · 30/30** |
| `broadcast_ping()` ×5 | `{1,2,3,4,5,6}` every time — first complete broadcast of the day |

| ID | Joint | Unit | Firmware | V | Position (raw) | °C | Status |
|---|---|---|---|---|---|---|---|
| 1 | `shoulder_pan` | A | 3.10 | 11.6 | 1139 | 34 | 0 |
| 2 | `shoulder_lift` | B | 3.10 | 11.7 | 3161 | 33 | 0 |
| 3 | `elbow_flex` | C | 3.10 | 11.6 | 4092 | 32 | 0 |
| 4 | `wrist_flex` | D | 3.10 | 11.7 | 2 | 34 | 0 |
| 5 | `wrist_roll` | E | 3.10 | 11.6 | 0 | 34 | 0 |
| 6 | `gripper` | F | 3.10 | 11.6 | 4094 | 33 | 0 |

**Changed as a result:** `servos.md` map back to A–F = 1–6, all 3.10; DEC-10 superseded
by DEC-11 (one firmware on the bus); OQ-10 resolved; the family rule in wk-robotics
`common.md` now says *upgrade*, with the FD procedure that worked; OQ-03 gains the supply
fact. Milestone 1 closed.

### 2026-09-09 · Two servos commissioned and verified on one bus

**Conditions:** Waveshare Bus Servo Adapter (A), jumpers on B, USB to a Linux host,
12 V on the adapter (source unrecorded, OQ-03). LeRobot 0.6.1 `FeetechMotorsBus`.
One servo on the bus at a time for the writes; both daisy-chained for the final check.

| Servo | Factory state | Written | Read back after write |
|---|---|---|---|
| Unit A → `shoulder_pan` | ID 1, 1 Mbaud, model 777 | ID 1, baud code 0 (1 M) — no change | 12.3 V, position 599, 27–30 °C, torque off |
| Unit B → `shoulder_lift` | ID 1, 1 Mbaud, model 777 | **ID 2**, baud code 0 | 12.4 V, position 2446, 28 °C, torque off |

**Pair on one bus:** `broadcast_ping()` → `{1: 777, 2: 777}`; `sync_read` of voltage,
position and temperature answered for both. Positions are raw, pre-homing, and carry no
meaning until calibration.

**Also established:** the adapter is a CH343 (`1a86:55d3`, `/dev/ttyACM0`) and does not
echo transmitted bytes — banked in wk-robotics. Feetech's FD GUI on a Windows host saw the
COM port but found no servo; cause not diagnosed (the same board and servo answered
immediately from Linux), so treat FD as unverified on this hardware.

**Changed as a result:** `servos.md` map filled for IDs 1 and 2; both units labelled.

### 2026-09-07 · Press fit on a production part

**Conditions:** `Base`, white PLA+, no supports, no elephant-foot compensation; Waveshare
ST3215 pushed into the pocket by hand.

**Result:** solid press fit — the intended interface. Confirms on a real part what the
gauges showed the day before. **Changed as a result:** nothing; the profile stands (DEC-05).

### 2026-09-06 · Upstream gauges

**Conditions:** `Gauge_0` and `Gauge_tight_1` from upstream `STL/Gauges/`, white PLA+, no
supports, printed to separate support residue from dimensional error after a servo would
not seat in the first `Motor_holder_Base`.

**Result:** tight friction fit in `Gauge_0`, the intended press fit; the machine is
dimensionally correct and the tight holder was support residue. **Changed as a result:**
the part was reprinted without supports; the finding generalised into wk-robotics.
