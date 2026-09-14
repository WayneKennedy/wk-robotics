# Test log

What was actually measured, on what date, under what conditions — including "no change
needed" results, which are findings too. Print-job telemetry lives in the private
`3d-printing` repo; only fit and function results are here.

## Format

Each entry: date · what was tested · conditions · result · what changed as a result.

## Entries

### 2026-09-14 · First guarded move: IK target reached under path checking

**Conditions:** arm set to roughly mid by hand (owner), Eventek bench supply 12.0 V,
`hold_test.py --keep` (two passes — the first aborted its ramp at `Torque_Limit` 150 when
the gripper and elbow, sitting just below their minimum limits, stepped up to them; the
second ramped to 1000 with zero drift). Then `software/guarded_move.py --target
0.239,0,-0.05 --pitch 90`: the tool frame 20 cm ahead of the pan axis, 5 cm below the base
plate, approach axis straight down.

**Plan:** IK residual 0.3 mm, solution in limits and clear; joint-space line from the
present pose in 62 samples of ≤1.5°, every sample inside the URDF limits, inside the servos'
shrunk limits less 3°, and clear of the keep-out plane (rearmost skeleton point +0.069 m
throughout). Streamed at 20 Hz, `Goal_Velocity` 600, `Acceleration` 30.

| Joint | Goal (raw) | Reached | Error |
|---|---|---|---|
| `shoulder_pan` | 2046 | 2047 | +1 |
| `shoulder_lift` | 2195 | 2199 | +4 |
| `elbow_flex` | 3142 | 3132 | −10 |
| `wrist_flex` | 2578 | 2572 | −6 |

Reached in 3.5 s, peak 13 mA sampled at 20 Hz, 36 °C, rail 12.0 V. Model's tool position
from the reached counts: x +0.247, y +0.006, z −0.050 m. No guard tripped. Arm left holding
there under torque. **Measured with a tape (owner): 24.9 cm forward of the pan axis, ~3 cm
below the top of the base plate** — forward within 2 mm, height 2 cm high in the model. At
this reach 2 cm is ~5° of pitch across the chain, the size of the elbow residual at the
hand-set zero; the count-to-angle zero (±10°) is the limiting error, not the URDF. **Also
measured: the desk edge is 25 mm ahead of the pan axis**, which moves the keep-out plane to
x = 0.0638 m in `kinematics.py` and brings the rule's meaning to a head: with link bodies
kept ahead of the edge (30 mm margin) the URDF zero pose is refused (its vertical upper arm
overhangs the edge by ~13 mm) and the upper arm must lean ≥14° forward; with centrelines
only, it passes. The calibration mid and today's target pass either way; the rest pose
fails either way. Open, owner to say ([`hardware.md`](hardware.md) → Bench).

**Also corrected:** the elbow's "gravity lag" on every return to mid in the extents cycles
(err +59) is the servo clamping at its shrunk minimum limit 2095: the calibration mid, 2047,
lies outside the elbow's shrunk range (noted 2026-09-12, not connected until today). The
hold-test "drift" of the gripper (1324 → 1464) and elbow (2077 → 2095) at the first ramp
step is the same clamp. Neither is a fault.

**Changed as a result:** milestone 4's guarded move exists and has run once;
`guarded_move.py` clamps planned samples into the servo range so a start at the calibration
mid is accepted.

### 2026-09-14 · Kinematics module validated offline

**Conditions:** no servo touched. `software/kinematics.py` against upstream
`so101_new_calib.urdf`, numpy only, on this host.

**Forward kinematics.** First version composed the tool frame onto the moving jaw; the URDF
has the jaw and the tool frame as siblings under `gripper_link`, which put the tool centre
0.116 m off to the side. Rebuilt as a parent→child tree: at the URDF zero the tool frame is
now 0.098 m along the wrist-roll axis from the roll origin, coaxial, approach axis +x.

**Keep-out check** (capsule skeleton from the shoulder-lift origin outward, 30 mm radius,
turret excluded because it sits on the pan axis by construction): rest pose **breached**
(rearmost point x = −0.046 m), calibrated mid pose and URDF zero **clear** (+0.069 m).

**Inverse kinematics** (damped least squares, four joints, tool position + pitch, four
seeds): FK → IK round trip on 50 random in-limit poses, **47 of 50 within 2 mm**. Sample
targets from the pan axis: 20 cm ahead, 5 cm below the base plate, straight down — solved
0.3 mm, in limits, clear. 25 cm ahead, 10 cm up, 45° down — solved 0.7 mm, in limits, but
**not clear**: every seed leans the upper arm back over the desk to get there; whether an
elbow-up solution exists for it is unexplored (the solver does not search the null space
for clearance). 30 cm ahead, 5 cm up, straight down — no converged solution from any seed.

**Changed as a result:** milestone 4 redefined (DEC-14); `servos.md` mapping section.
Nothing here has moved the arm; the first guarded move is the next step.

### 2026-09-14 · URDF zero pose set by hand; count-to-angle mapping checked

**Conditions:** torque off, owner holding the arm against droop, bench camera side-on from
the arm's left (`software/snap.py`, rotation only). Reads by `software/kinematics.py --live`,
which maps raw counts to upstream `so101_new_calib.urdf` angles using the sweep-midpoint
zeros in its `JOINT_ZERO` table.

**Pose 1 — URDF zero as described** (pan ahead, upper arm vertical, forearm horizontal
forward, wrist in line). **Pose 2 — from pose 1, gripper pitched down ~30° and the arm
swung ~30° toward the camera** (the arm's left), both by eye.

| Joint | Pose 1 raw | Pose 1 mapped ° | Pose 2 raw | Pose 2 mapped ° |
|---|---|---|---|---|
| `shoulder_pan` | 2036 | −0.9 | 1659 | −34.0 |
| `shoulder_lift` | 1918 | +4.6 | 1973 | +9.4 |
| `elbow_flex` | 3055 | +8.9 | 3065 | +9.8 |
| `wrist_flex` | 2081 | +1.0 | 2568 | +43.8 |

**Result:** the sweep-midpoint zeros put the hand-set zero pose within 9° on every joint.
In the frame the upper arm leans a little toward the holding hand and the forearm rises a
little toward it, so part of the shoulder and elbow residual is the hold, and the camera is
not level; the residual is inside by-eye accuracy and was not chased. **Signs:** URDF pan is
positive about −z (swings the arm to its right), so toward the camera is negative — raw fell,
sign +1 confirmed. URDF `wrist_flex` is positive about +y (pitches the gripper down) — raw
rose, sign +1 confirmed. `shoulder_lift` and `elbow_flex` signs had already followed from the
rest pose (raw min ↔ URDF −100°, raw max ↔ +97°). Also read at rest, earlier the same day:
2026 / 736 / 4085 / 2922 / 1363 / 1324, which the model places at the shoulder and elbow
travel limits, and with the elbow 46 mm behind the pan axis — the folded rest pose breaches
the keep-out plane.

**Changed as a result:** `kinematics.py` `JOINT_ZERO` provenance updated; `servos.md` gains
the mapping section. The zero is carried as ±10° (an unmeasured stop margin at each end of
the sweep, plus the hand pose); a hard-stop measurement per joint would tighten it.
`wrist_roll` and `gripper` remain unmapped.

### 2026-09-14 · Health check after relocating to a desk-edge mount

**Conditions:** arm clamped to a desk edge with free air in front and below (owner), set
by hand to roughly mid-throw on every joint before torque. Eventek KPS3010D bench supply at
12.0 V (current limit setting not recorded). Bench webcam absent from this host (no
`/dev/video*`). One process on the bus at a time. Full sequence, in order:
`ping_bus.py` → register dump (read-only) → limits rewrite (below) → `hold_test.py --keep`
twice → `extents_cycle.py --cycles 2` → register read-back.

**Found before moving, from the register dump:**

- **Homing offsets intact** on all six (−793, 870, 1555, 1831, 40, −1539), matching the JSON.
- **`wrist_flex` and `gripper` limits had reverted again** to the pre-shrink values
  (1002/3137 and 1328/2737) while the other four held their shrunk limits. This is the same
  pair as 2026-09-12, after a rewrite made with their protection flags clear and a matching
  read-back. The "flagged servo → RAM only" hypothesis therefore does not explain it
  (OQ-12). `Lock` reads 0 on all six. Rewritten from the JSON with torque off and status 0,
  read back matching — see the table at the end for the state after the run.
- **`gripper` `Max_Torque_Limit` (EEPROM) reads 500**; the other five read 1000. No entry
  here records that write; the 2026-09-13 driving session is unlogged. Left as found. The
  servo's effective limit is therefore 500 whatever `Torque_Limit` (RAM) is set to.
- Every `Goal_Position` read 0 and every `Torque_Enable` 0: the servos had been power
  cycled since last use, as the 2026-09-12 finding predicts.

**Torque-on and hold** (`hold_test.py`, verified weak-torque-first sequence): first pass
aborted its ramp at `Torque_Limit` 150 because the gripper, sitting at 1354 — below its
freshly restored minimum of 1469 — was clamped by the servo to the limit and moved 110
counts to 1464. Not a drift: the limit doing its job. Second pass with all joints inside
limits: no motion at 30, no drift at 150 / 300 / 600 / 1000, then 8 s hands-off hold at
1000 with **0–1 counts drift, 0 mA on all six**.

**Extents cycle, 2 cycles, 37 moves, ~1.3 min, self-parked at mid, torque left on.**
`Goal_Velocity` 600, `Acceleration` 30, shrunk limits −3°, `wrist_roll` ±123°. No stall,
no current or temperature guard trip.

| Joint | Max tracking error (counts) | Peak mA (this run) | Peak mA (2026-09-12, 260-move run) |
|---|---|---|---|
| `shoulder_pan` | 6 | 156 | 592 |
| `shoulder_lift` | 21 | 578 | 630 |
| `elbow_flex` | 59 (return to mid — the servo clamping at its shrunk minimum 2095, not gravity; see the guarded-move entry) | 384 | 592 |
| `wrist_flex` | 4 | 416 | 169 |
| `wrist_roll` | 7 | 176 | 52 |
| `gripper` | 4 | 39 | 32 |

Temperatures 33–35 °C throughout (43 °C peak on 2026-09-12's longer run). Rail at the
servos 11.5–12.0 V across every move, versus 10.8 V minimum on the LiPo — the bench supply
holds up under the shoulder's lift, the pack did not. **Whole-arm draw on the supply's
panel: 0.72 A peak** (owner, watching the Eventek's ammeter through these first moves; the
panel samples a few times a second, so shorter spikes are not captured). Against the
servos' own readings the same moves peaked at 578 mA on `shoulder_lift` alone, so the total
is consistent with one joint working while the other five idle. Per-move CSV:
`software/logs/extents_20260914_154116.csv`. The per-joint peak differences from
2026-09-12 are recorded, not explained: the mount, the start pose and the run length all
differ.

**Verdict: the arm is healthy after the relocation.** Sensing, calibration offsets, the
safe torque-on sequence, tracking, thermal and rail behaviour all match or better the
2026-09-12 run.

**State left:** parked at mid (all joints ~2047), `Torque_Enable` 1, `Torque_Limit` 1000,
status 0, 0–1 mA. Limits in the servos match the JSON on all six. **Whether the
`wrist_flex` / `gripper` limits survive the next power cycle is the open test** (OQ-12):
re-run the register read-back after the supply has been off.

**Changed as a result:** OQ-12 opened; `servos.md` rule 4 reworded; the 2026-09-12
hypothesis marked not confirmed.

### 2026-09-14 · Reconnect on a bench power supply

**Conditions:** arm at rest, torque off, Waveshare Bus Servo Adapter (A) on this host,
`/dev/ttyACM0`. **First run on a mains bench supply**: Eventek KPS3010D (30 V / 10 A class)
set to 12.0 V with the current limit turned down for a first look at the draw. LeRobot 0.6.1,
`software/ping_bus.py --expect 1,2,3,4,5,6`. Read-only; no servo written.

**Result:** `broadcast_ping()` complete, `{1..6: 777}`; `sync_read` answered for all six.

| ID | Joint | V | Position (raw) | °C |
|---|---|---|---|---|
| 1 | `shoulder_pan` | 11.9 | 1880 | 31 |
| 2 | `shoulder_lift` | 12.0 | 734 | 31 |
| 3 | `elbow_flex` | 12.0 | 4074 | 31 |
| 4 | `wrist_flex` | 12.1 | 2780 | 31 |
| 5 | `wrist_roll` | 12.0 | 1397 | 31 |
| 6 | `gripper` | 12.0 | 1354 | 32 |

The rail at the servos matches the set point to within the register's 0.1 V resolution, so
the supply was in constant-voltage mode at idle — the idle draw sits under the current limit
set. Positions are pre-move rest positions and carry no meaning beyond "the arm is where it
was left". The supply's own current readout was not recorded.

**Changed as a result:** OQ-03 and `hardware.md` gain the bench-supply fact; nothing decided.

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

**Limits pulled in 10 % of span at each end (owner, same day)** after the first move below —
`software/shrink_limits.py`, servos read back matching, JSON re-saved and mirrored:

| Joint | Limits now | Span |
|---|---|---|
| `shoulder_pan` | 1009 – 3084 | 2075 |
| `shoulder_lift` | 962 – 2771 | 1809 |
| `elbow_flex` | 2095 – 3813 | 1718 |
| `wrist_flex` | 1216 – 2924 | 1708 |
| `wrist_roll` | 0 – 4095 | full turn |
| `gripper` | 1469 – 2596 | 1127 |

**First move under torque — aborted by an elbow overload; no damage reported.** Arm clamped,
started from the folded rest pose (in which the gripper body rests against the base — owner).
`software/first_move.py` (first version): LeRobot `so101_follower` connect (torque on), hold,
then ±10° per joint with `max_relative_target = 10`. Observed:

| Joint | What happened |
|---|---|
| `wrist_roll` | ±10° reached within 5–6°, current 13–26 mA. Fine |
| `wrist_flex` | did not move in either direction, load −200 (full), 136–156 mA — blocked by the pose |
| `gripper` | did not move, load +200, 117–156 mA — jaw against its stop; **Overload error** flagged afterwards |
| `elbow_flex` | the present-position read used by LeRobot's step clamp returned **−259°** (a true 101° minus a full turn) while the observation a moment earlier read 99.3°; the clamp then commanded a goal past the wrap, the servo took the short way round through its recorded maximum into the hard stop, **Overload error**, position 4087 afterwards (max limit was 4028). `Min/Max_Position_Limit` did not stop it |
| `shoulder_lift` | +10° reached 1.3°, 507 mA, load −376 — lifting the folded arm; steady-state error with LeRobot's P = 16 |
| `shoulder_pan` | ±10° fine, 0 mA |

`disconnect()` failed on the overloaded servos; torque was released servo by servo
(`software/release_torque.py`). All six then read status 0, 0 mA, 35–40 °C. Swept by hand
with torque off, the elbow's position is **continuous, never negative, from 4087 down to
2380** (1 765 samples) — the sensing is fine; the −259° read is unexplained. Read errors
seen during that sweep were **port contention: two of this session's processes on
`/dev/ttyACM0` at once**. Alone on the port, `sync_read` is 100/100. **One process on the
bus at a time** — recorded as a rule in `servos.md`.

Two more attempts, both aborted by the read guards, and the diagnosis that followed:

| Run | What happened |
|---|---|
| 2 — open pose, held by owner, LeRobot `connect()`, step 5° | Guard tripped before the first nudge: elbow read −57° then +54° a second later. Afterwards the servos' `Goal_Position` registers held values far from the start (elbow 3514 vs 2306, wrist 3166 vs 2326). **Cause: stale goals.** `connect()` re-enables torque while each servo still holds the goal from the previous session (the elbow's was 121 from run 1's crash), so joints lurch toward old goals the instant torque comes on. Proven with `software/hold_test.py`: goals set to present before torque, shoulder's stale goal 55° away, torque on at 30 % — **zero drift on all six** |
| 3 — open pose, held, goals := present before torque, Torque_Limit 500, step 5° | Guard tripped at the first nudge (`wrist_roll` +5°): wrist_flex had gone 2904 → 3158 and the elbow 3408 → 3730 in ~2 s, both the same direction; gripper body hit the base. Not yet explained — candidates are sag under half torque with LeRobot's P = 16, and the owner's hold |

With torque off and the arm still: 300 unretried `sync_read`s matched a retried reference
exactly; a `sync_write` of six distinct goals landed on the right servos; the normalised
write path reproduces the present raw within +1…+14 counts (and pushes a joint that sits
outside its saved range to the range edge — the gripper, below its minimum after the slam,
+112); `ensure_safe_goal_position` never clamped in 200 live reads. So the data path is
sound. What is not sound is the **`max_relative_target` clamp as a safety device**: it bounds
each goal to *present ± step*, so once a joint is moving for any other reason every hold
re-anchors to where it has got to and never pulls it back — it ratchets a lurch or a sag
into a slam.

**Writing `Goal_Position` turns torque on.** Found because the arm was "holding torque in the
slammed position" (owner) after tools that had disabled torque and then written goals; read
back `Torque_Enable = 1` on all six, elbow and wrist at 526–540 mA, load −500, 47 °C,
pressing on the base. Verified in isolation on `wrist_roll`: `Torque_Enable` 0 → write
`Goal_Position` → reads 1. So "set goals with torque off" energises the arm; every tool now
sets `Torque_Limit` first and treats a goal write as a torque-on. Torque released properly
(`Torque_Enable := 0`, no goal writes): all 0 mA, status 0.

**Run 4 — the decisive one.** Hands-off hold attempt from mid-range, `hold_test.py`, full
torque limit: goals were written equal to present **with torque off** and read back equal;
on `Torque_Enable := 1` the elbow drove 2128 → 3657 (134°) and the wrist 2108 → 2940 (98°),
stopping near the goals the servos had held *before* the write (3730, 3113). **A
`Goal_Position` written while torque is off is stored in the register but is not adopted as
the motion target; enabling torque resumes the previous target.** This is also what run 3
was: its "goals := present before torque" step did nothing, and the elbow and wrist went to
run 2's leftovers (3730 and 3113 — exactly where they ended). The 30 % "zero drift" pass
earlier was the owner's hand, not the servos. Overload / over-current protection tripped on
elbow, wrist and gripper (status 8 latched on the wrist, 49–50 °C); torque forced off at
packet level, all 0 mA, cooling. Owner: prints undamaged.

**After a servo power cycle every `Goal_Position` register reads 0** (all six, 2026-09-12),
and protection flags clear. A LeRobot `connect()` straight after power-up would therefore
enable torque with a target of 0 on every joint. Sequence verified immediately afterwards,
`hold_test.py`, owner holding the arm at mid-range: torque on at `Torque_Limit` 30 — no
motion; goals := present; ramp 150 / 300 / 600 / 1000 — no drift at any step; hold 5 s at
1000 — max drift 3 counts, 0 mA on every servo.

**Safe torque-on sequence, verified 2026-09-12 (was: to be verified next):** `Torque_Limit := ~30` (too weak to move
anything) → `Torque_Enable := 1` (resumes the stale target, but cannot act on it) →
`Goal_Position := Present_Position` (adopted, because torque is on) → ramp `Torque_Limit`
150 / 300 / 600 / 1000, checking drift at each step. Implemented in `hold_test.py`.

**Hands-off hold, then run 5 — milestone 3 closed.** Owner let go at the upright mid-range
pose: 20 s, **0 counts drift on all six, 0 mA** (bench webcam frame confirms the arm standing
unaided). Then `first_move.py` (fourth version: requires the verified hold, never toggles
torque, absolute goals from the start pose, no present-based clamp), ±3° per joint and back,
`Torque_Limit` 1000:

| Joint | +3° reached | −3° reached | back | Peak mA | Other joints |
|---|---|---|---|---|---|
| `wrist_roll` | −0.7° | +0.8° | −0.8° | 13 | 0.0° |
| `gripper` (0..100 units) | −0.2 | at range floor (0.3, −3 clamped) | +0.3 | 6 | 0.8° |
| `wrist_flex` | −0.7° | +0.2° | −0.8° | 13 | 0.8° |
| `elbow_flex` | −0.5° | +0.2° | −0.4° | 6 | 0.8° |
| `shoulder_pan` | −0.5° | +0.3° | −0.5° | 6 | 0.8° |
| `shoulder_lift` | −0.5° | −0.1° | −0.7° | 0 | 0.8° |

Every joint reached within 1° (P = factory value — LeRobot's `configure()` PIDs were **not**
written this run), no joint disturbed another beyond 0.8°, temperatures 34–43 °C. The arm
ended holding the start pose under torque.

**Also found on the way:** the 10 % limit shrink had **not persisted** on `wrist_flex` and
`gripper` — after the power cycle their limits read the pre-shrink values (1002/3137,
1328/2737) while the other four kept theirs. Both were in protection state (overload /
over-current flags) when the shrink was written; the read-back had matched. Working
hypothesis, unverified: an EEPROM write to a servo with a latched protection flag lands in
RAM only. Rewritten with the flags clear, verified by read-back. **Not confirmed: the same
two servos had reverted again by 2026-09-14** despite that flag-clear rewrite (OQ-12).

**Changed as a result:** roadmap milestone 3 done; `servos.md` rules extended; OQ-03 still
open (the "decided supply" was a 3S pack both times).

**Extents loop — 15 cycles, 260 moves, 9.5 min, stopped itself and parked.** Owner: "arm
stopped and parked, bloody marvelous." `software/extents_cycle.py`: from the calibration mid
pose, each joint in turn to its shrunk upper limit − 3°, lower limit + 3°, back to mid
(`wrist_roll` ±123°), `Goal_Velocity` 600, `Acceleration` 30, full torque limit, one joint
moving at a time so only the hand-swept envelope is visited. Every move tracked within 13
counts except the elbow's return to mid (up to 59, gravity lag), no stall, hottest servo
43 °C. Peak currents: `shoulder_lift` ~2 A lifting the arm from its forward extent (cycle 1,
foreground run), 630 mA in the logged run; `elbow_flex` and `shoulder_pan` ~590 mA; wrist
and gripper under 170 mA. **Rail sag:** 11.8 V at mid falling to 11.7 over the run, but
**10.8 V while the shoulder held the arm at its forward extent** — the 11.0 V stop tripped on
that loaded reading while the pack still read 11.7 V at rest (≈ 3.9 V/cell, far from spent).
The tool now judges the stop on the unloaded reading at mid and only warns on loaded dips.
The ~0.9 V sag under < 1 A is the pack, its lead or the adapter's screw terminals — part of
OQ-03. Log: `software/logs/extents_20260912_141344.csv` (git-ignored, on the host).

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
