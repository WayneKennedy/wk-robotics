# Test log

What was actually measured, on what date, under what conditions — including "no change
needed" results, which are findings too. Print-job telemetry lives in the private
`3d-printing` repo; only fit and function results are here.

## Format

Each entry: date · what was tested · conditions · result · what changed as a result.

## Entries

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
