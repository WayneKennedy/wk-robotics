# Test log

What was actually measured, on what date, under what conditions — including "no change
needed" results, which are findings too. Print-job telemetry lives in the private
`3d-printing` repo; only fit and function results are here.

## Format

Each entry: date · what was tested · conditions · result · what changed as a result.

## Entries

### 2026-09-14 · Wrist roll zero: the placeholder is ~85° off; the moving jaw is the reference

**Owner at raw 2035 (the placeholder zero), seen from behind:** moving jaw **up and to the
right**; camera mount in the north-west quadrant, about 45°. Upstream's URDF puts the moving
jaw's hinge **up and to the left, 40° from vertical** at roll 0 — so the placeholder is wrong,
by roughly 85° if "up and to the right" is about 45°.

**Sign verified:** raw 1362 → 2035 turned the camera mount anticlockwise (seen from behind),
from on top to north-west, and positive URDF roll also turns the jaw anticlockwise in the
model — sign +1 holds; only the zero is off.

**The camera is not a usable reference for the zero.** Upstream's camera URDF
(`so101_new_calib_camera.urdf`) places its wrist camera 45° anticlockwise of the moving jaw;
the owner's placeholder screws put this build's mount about 90° from the jaw. Upstream's
camera variant uses a different mount (`wrist_camera_mount_so101_v1`) from the hex-nut
recess on this build's `Wrist_Roll_Follower`. The moving jaw is the same part as upstream's,
so it defines the zero: in the model the jaw points straight up at URDF roll −40.2°, so the
zero is the raw count where the jaw points straight up, plus 457.

**Method in progress:** roll to the owner's-estimate "jaw straight up" (raw 2547) and let the
owner report the residual.

### 2026-09-14 · Gripper gap: four measured points; the simple hinge model does not hold

**Conditions:** arm holding at the zero pose; owner's calipers across the jaw ends. The jaws
were driven by `guarded_move.py --gripper RAW` (new: the gripper joins the planned and
checked set like the roll, jaw capsule tested against every link). Readings at the position
the jaws actually reached:

| Gripper raw | Opening from the closed stop | Gap at the jaw ends | Hinge model predicted |
|---|---|---|---|
| 1289 | 0° (closed stop) | 0 mm — assumed; **supported by the 1365 point** | — |
| 1365 | 6.7° | **8.67 mm** | 8.6 mm (interpolated from the assumed zero and 11 mm) |
| 1386 | 8.5° | **11 mm** | 11.3 mm (from the first point) |
| 1472 | 16.1° | **21 mm** | — (the first point) |
| 1591 | 26.6° | **37 mm** (owner: "at the very tip") | 33.7 mm (from the first two) |

**Result:** a one-parameter hinge model (gap = L·sin θ) predicted the second point within
0.3 mm but missed the third by 3.3 mm — the gap grows faster at wider openings than a jaw tip
on a simple arc would. Refitted to all three it leaves ±1 mm residuals. **The lookup is
therefore the measured points with linear interpolation** (`software/calibration/gripper_gap.json`):
25 mm ↔ raw 1502, 30 mm ↔ 1539. **The near-closed point confirms the closed end:** commanded 1357 (the lowest the tools will
command), reached 1365, measured 8.67 mm where interpolation from the assumed zero predicted
8.6 mm — so the jaws do meet at the closed stop and the table holds from closed to 37 mm.
Not measured: anything wider than 37 mm.

### 2026-09-14 · Wrist roll: camera-top orientation, a moulded stop, and a move to the placeholder zero

**Owner's observations at the bench:** with the roll at raw **1362** (−60° by the model's
placeholder zero 2047), a wrist camera on the two placeholder screws in the mounting holes
would sit **vertical, on top, looking horizontally forward along the forearm axis** — the
natural roll zero. The roll has **a mechanical stop moulded into the print** ("presumably to
protect wire stretching"), which looks to be about **three-quarters of the way round** its
travel from that orientation. This corrects the earlier assumption that the roll is limited
only by its cable.

**Move:** `guarded_move.py` gained `--roll RAW`, which puts `wrist_roll` into the planned,
checked and streamed set (keep-out and self-collision at every sample, since rolling swings
the jaw). Roll 1362 → 2047 in 41 steps, reached 2035; other joints within 6 counts. Held for
the owner to judge the camera direction against the roll's range.

**Also changed:** the move tools' stale-goal precondition (goal vs present) relaxed from 30
to 60 counts — it refused this move because the shoulder sagged 31 counts under the
horizontal forearm, while the stale goals it exists to catch differ by hundreds. The first
edit put the explanatory comment inside a dict expression and broke all three tools; caught
by the next dry run before anything moved, fixed, all three compile.

**Temperatures:** the shoulder read **47 °C** (others 34–36 °C) — residual heat from the
torque-300 stop sweeps and lifting the arm off its forward stop; while holding it drew ~6 mA
at +5 counts and stayed at 47 °C over 20 s.

**At the placeholder zero (raw 2035) the owner judged the camera canted about 45°, left side
of frame down** — consistent, by eye, with the 59° the counts put between 2035 and the
camera-top orientation at 1362. Owner: "I don't see it being a problem" — a camera cant is a
fixed mounting offset, correctable in software.

**Open:** the roll zero should follow the URDF's definition (where the moving jaw sits at
roll 0), with the camera recorded as an offset from it — not chosen by the camera; and the
roll's travel — its stop measured with `find_stops.py`, which does not yet sweep the roll
and must respect the encoder wrap at 0 / 4095.

### 2026-09-14 · Pan checked with a square: straight-ahead is the stop midpoint

**Conditions:** arm holding at the zero pose, torque on; owner laid a square off the desk edge:
"the arm is as close to perpendicular to the edge as I can measure". Pan read **1985**.

**Result:** the model puts that at **+0.35°** from the pan zero 1981 (the stop midpoint), so
straight out from the desk edge *is* the stop midpoint, within the square's resolution (about a
degree). The owner's earlier by-eye straight-ahead (2036) was the one that was off, by 4.8°. It
also confirms what the keep-out assumes: the base is clamped square to the desk edge, so the
desk-edge plane is perpendicular to the model's forward axis.

**All four arm zeros are now checked against the world:** pan ~1° (square), shoulder ~1° (level),
elbow ±1.5° (level + tape), wrist ±2° (level + tape).

### 2026-09-14 · Spirit level on the gripper: wrist zero moved +2.1°; all four arm zeros now checked

**Conditions:** same zero pose, iPhone level along the long flat edge of the gripper's fixed
jaw (owner): **+4°, front end up.**

**Result:** with the stop-midpoint wrist zero (2046) the model's approach axis reads +1.8°.
**2070 (+2.1°) makes it read +4.0° and puts the model's reach at the tape pose at exactly
24.9 cm** — the level and the tape agree. If the jaw edge instead followed the fixed-jaw body's
axis (the roll sits at −60°, which would tilt any edge offset into the reading) the level would
ask for 2082–2093, but the tape then overshoots by 3–6 mm; so 2070, ±2°. It coincides with the
2026-09-12 hand-sweep midpoint; the stop midpoint was the one that was off.

**Re-read by the owner the same evening** (the phone's pressure had folded the elbow 8 counts,
0.7°): gripper "4–5° up", forearm "still +2°", upper arm 3°. Model at that pose with the final
zeros: gripper +3.1°, forearm +0.9° (outline) to +3.1° (horn line), upper arm 3.0° — all within
the stated uncertainties. Zeros left unchanged: the phone level resolves ~1°, and the tape
reach is exact at these zeros.

**State of the zeros after the evening's checks:**

| Joint | Zero | How | Good to |
|---|---|---|---|
| `shoulder_pan` | 1981 | stop midpoint, confirmed by a square off the desk edge (next entry up) | ~1° |
| `shoulder_lift` | 1925 | stop midpoint, refined by the level | ~1° |
| `elbow_flex` | 3031 | level on the forearm + tape | ±1.5° |
| `wrist_flex` | 2070 | level on the gripper + tape | ±2° |

**Lesson for any arm here:** the stop midpoint is a starting point, not the zero. Two of four
joints were 2–5° off it, including one whose span matched the URDF exactly. A phone level at
the zero pose plus one tape measurement settled all four in minutes.

### 2026-09-14 · Spirit-level check at the zero pose: shoulder confirmed, elbow zero moved +4.8°

**Conditions:** arm holding at the measured zero pose (previous entry), raw 1985 / 1959 /
2978 / 2044. iPhone level (owner), readings front-to-back along the arm's forward axis.

| Surface | Level | Model with stop-midpoint zeros |
|---|---|---|
| Desk top at the base | 0° (level in this axis) | — |
| Upper arm, long edge | 3° from vertical, top forward | 3.4° (joint) / 2.4° (body axis) |
| Forearm, long edge | **+2°, front end up** (owner: "a net 94 degrees at elbow") | **−1.4° (horn line) / −3.6° (outline)** |

**Shoulder:** confirmed; 1920 → 1925 makes the model read the 3.0° measured. **Elbow:** the
forearm reads 3.4–6.2° higher than the model (the range is the model's uncertainty about which
physical line the phone sat on). **Cross-check against the independent tape measurement**
(first guarded move, 24.9 cm forward): the same elbow shift takes the model's reach there from
22.3 cm to 23.7–24.9 cm. Both agree, so the elbow zero moves to **3031 (+4.8°, ±1.5°)**, and
the model then reaches 24.3 cm (0.6 cm short). Height does not discriminate — "midway between
the jaws" is uncertain along the downward-pointing jaw.

**What this corrects:** the stop-measurement entry called the elbow's midpoint zero tight
(±0.3°) because its span matched the URDF's. Equal span only says the travel is the right
length; this elbow's travel is not centred on the URDF zero — its stops are at −101° / +92°.
Because the URDF's +97° fold limit then lies beyond the real stop, **the model's joint limits
are now the measured servo limits** (`kinematics.apply_measured_limits`), not the URDF's.

**Changed as a result:** `JOINT_ZERO` shoulder 1925, elbow 3031; model limits from the
calibration file. Wrist zero (±7.5°) not yet checked — a level on the gripper at this pose
would do it.

### 2026-09-14 · Arm set to the measured zero pose for a spirit-level check

**Conditions:** after the second power cycle the arm hung limp with the shoulder on its
forward stop (3104–3110, past the new limit 3083). `hold_test.py --keep` ramped to 1000 with
no drift. `guarded_move.py` to every joint's measured zero (1981 / 1920 / 2976 / 2046).

**Planner change:** the first plan was refused at its own start — the shoulder at 3104 reads
+104° by the model, and the plan rejected any sample outside the URDF's ±100° (less 3°), although
the measured stop is further out. The plan now judges travel only against the measured servo
limits (stops ∓ 3°, less a further 3°); the URDF limits stay in IK, where they keep chosen goals
conservative. Re-planned: 70 steps, clean.

**Reached:** pan 1985 (+4 counts), elbow 2978 (+2), wrist 2044 (−2), **shoulder 1959, 39
counts (3.4°) short of 1920** — the horizontal forearm's moment pulls the upper arm forward and
the servo's proportional-only control leaves that as steady error (the first target, with the
forearm near vertical, held within 4). Model at the reached pose: pan +0.4°, shoulder +3.4°,
elbow +0.2°, wrist −0.2°. Held under torque for the owner's level, desk not level (owner).

### 2026-09-14 · OQ-12 resolved: EEPROM writes made with `Lock` = 1 are lost at power-off

**Conditions:** second power cycle of the evening (owner), read-only check.

**Result:** the canary — `wrist_roll` `Max_Position_Limit` written 4095 → 4094 with `Lock` = 1
— **read 4095**: the write had lived in RAM only. Every other limit and homing offset, written
with `Lock` = 0, still matched the JSON. Together with the first power cycle that closes
OQ-12: **a Feetech STS3215 EEPROM register written while `Lock` = 1 reads back correctly and
is lost at power-off, and LeRobot 0.6.1's `enable_torque()` sets `Lock` = 1** — which is how
the 2026-09-12 shrink was lost on two servos and kept on four. At power-up `Lock` read 1 on
all six again; three power-ups so far (0 → 0 that morning, 1 → 1 twice tonight) are
consistent with the lock keeping its last value across power-off — consistent, not proven.

**Tools audited for EEPROM writes:** `calibrate.py home` opens the lock (LeRobot's
`disable_torque()`) — homing offsets were always safe; `calibrate.py sweep-stop` wrote limits
without it — fixed to call `disable_torque()` first; `shrink_limits.py` never opened it —
retired (superseded by the measured limits); `find_stops.py` now closes the lock *before* its
temporary widening so that widening can never persist; LeRobot's `setup_motor()` (used by
`set_servo_id.py`) disables torque first — safe.

**Changed as a result:** OQ-12 resolved; `servos.md` rule 4 and wk-robotics `common.md`
state the rule; the three tools above fixed or retired.

### 2026-09-14 · New limits survive a power cycle; a canary for the other half of OQ-12

**Conditions:** supply switched off and on by the owner, arm supported. Read-only register
check against `calibration/wk_soarm101.json`, then one deliberate test write.

**Result:** limits and homing offsets on all six servos **match the JSON exactly** after the
power cycle — the limits written with `Lock` = 0 earlier the same day persisted. At power-up
every servo read `Torque_Enable` 0, `Goal_Position` 0 (as on 2026-09-12), status 0, and
**`Lock` 1** — where the same check that morning, also after a power-up, read `Lock` 0. The
last value written before power-off was 1 tonight and apparently 0 the night before, so the
lock state may persist across power cycles; unverified. The arm went limp at power-off and
the shoulder settled at 3110, against its forward stop (3118).

**Canary:** `wrist_roll` `Max_Position_Limit` written 4095 → **4094** with `Lock` = 1 and
torque off; reads 4094 (RAM). Harmless — the roll has no stop. **Prediction if the `Lock`
explanation is right: 4095 after the next power cycle.** If it still reads 4094 the
explanation is wrong, and the value must be put back to 4095 either way (the JSON says 4095;
the tools refuse on a calibration mismatch).

### 2026-09-14 · Mechanical stops measured on five joints; limits rewritten; the EEPROM Lock

**Conditions:** `software/find_stops.py`, one joint at a time, the others holding at full
torque; each joint's configuration chosen by simulating its sweep against the keep-out and
the base first. Torque limit 180 (300 for the shoulder, so gravity does not read as a stop);
contact = 40 counts of lag for three steps. Owner at the bench: "the only potential fragility
being overdriving and stripping servo gears". `wrist_roll` not swept — no mechanical stop,
only its cable.

| Joint | Configuration of the rest | Min stop | Max stop | Midpoint | Span | URDF span |
|---|---|---|---|---|---|---|
| `shoulder_pan` | upper arm back 15°, forearm up, wrist in line (everything within 36 mm of the pan axis) | 715 | 3247 | 1981 | 222.6° | 220° |
| `shoulder_lift` | max: forearm down-forward; min: forearm vertical, capsule veto off (torque 300) | 723 | 3118 | 1920 | 210.5° | 200° |
| `elbow_flex` | min: upper arm vertical; max: upper arm back 32°, wrist −60° | 1879 | 4074 | 2976 | 193.0° | 193.7° |
| `wrist_flex` | (earlier entry) | 881 | 3212 | 2046 | 204.9° | 190° |
| `gripper` | — | 1289 (closed) | 2741 (open) | — | 127.6° | 110° |

Every contact read the same way — lag under 10 counts, then position frozen while the goal
ran on and current rose to 80–250 mA (capped by the torque limit). Repeats: the elbow min
1879 matched 1880 from a different arm configuration (so it is the joint's own stop), the
gripper closed 1289 matched twice. The shoulder min 723 agrees with the folded rest pose
(736) and the 2026-09-12 hand sweep (736). **The elbow's fold stop is 21 counts from the
encoder wrap at 4095** — the likely root of the elbow's −259° read on 2026-09-12; the tool
now stops a sweep at the wrap instead of writing goals past it. All six at status 0 after.

**Zeros.** Midpoints become the model's zeros for pan, shoulder, elbow and wrist
(`kinematics.JOINT_ZERO`). **Corrected by the level check the same evening — equal span does not make the midpoint the
zero; the elbow's was 4.8° out.** As first written: tight where the measured travel equals the URDF's (elbow ±0.3°,
pan ±1.3°); the shoulder and wrist travel 10.5° and 14.9° more than the URDF, so their zeros
are uncertain by up to ±5.2° and ±7.5°. The pan midpoint is 4.8° from the owner's by-eye
straight-ahead (2036) — unresolved.

**Tape re-check, and a correction to the guarded-move entry.** That entry compared the tape
(24.9 cm forward of the pan axis) with the model's tool x of 0.247 m — but that x is the
URDF base frame, whose origin is 3.9 cm behind the pan axis. **The model actually put the
tool 20.8 cm ahead of the pan axis, 4.1 cm short, not within 2 mm.** Its z is measured
from the base plate's underside (z = 0; the base mesh spans −2 … +70 mm), not its top. With
the measured zeros the same pose models at **22.3 cm forward and z −3.1 cm**: forward still
2.6 cm short, height within about 5 mm of "~3 cm below the plate". The remaining forward
error sits inside the shoulder and wrist zero uncertainty; a spirit level on the upper arm
(URDF zero = vertical) would pin the shoulder.

**Servo limits rewritten: measured stop ∓ 3°, replacing the blanket 10 % shrink.**

| Joint | Old | New | Gain in travel |
|---|---|---|---|
| `shoulder_pan` | 1009–3084 | 749–3212 | +34° |
| `shoulder_lift` | 962–2771 | 757–3083 | +45° |
| `elbow_flex` | 2095–3813 | 1913–4039 | +35° |
| `wrist_flex` | 1216–2924 | 915–3177 | +49° |
| `gripper` | 1469–2596 | 1323–2706 | +22° |

Read back matching; `calibration/wk_soarm101.json` and LeRobot's cache copy updated. The
first attempt refused: **every servo read `Lock` = 1**, where the morning's dump read 0.
LeRobot 0.6.1's `enable_torque()` writes `Lock` = 1 after `Torque_Enable` and
`disable_torque()` writes 0 — so after `hold_test.py` every EEPROM write lands in RAM only
and is lost at power-off. The limits were written with `Lock` = 0, then 1 restored. This is
the leading explanation of OQ-12. **Not yet verified across a power cycle.**

**Also:** `extents_cycle.py` retired behind an explicit override flag — it sweeps with no
geometry checks, struck the supply this morning, and the wider limits would make it worse.

### 2026-09-14 · Stop finding: wrist done; elbow sweep found the desk underside instead

**Conditions:** `software/find_stops.py` (new): the joint's `Torque_Limit` dropped to 180,
goal stepped 1° per 0.25 s toward each stop, contact = 40 counts of lag for three
consecutive steps (or >500 mA twice — never the trigger at this torque). Other joints hold
at full torque. Servo limits widened for the sweep and restored after; nothing written to
EEPROM. Owner at the bench.

| Joint | Configuration of the rest | Min stop | Max stop | Zero (midpoint) | Span | Note |
|---|---|---|---|---|---|---|
| `wrist_flex` | forearm pointing up, gripper in free air | **881** | **3212** | **2046** (estimate was 2070, −2.1°) | 204.9° (URDF 190°) | clean both ways |
| `elbow_flex` | **upper arm 50° forward** (assistant's choice) | 1880 (provisional) | ~~3850~~ | — | — | **the max is the desk underside, not a stop** |
| `gripper` | — | 1289 (jaws closed) | interrupted | — | — | resumed later |

**The elbow strike.** With the upper arm leaned 50° forward, the forearm folding toward the
elbow's max swings *down and back* — elbow angle is relative to the upper arm, so at +97°
the forearm points 147° below forward, i.e. 57° behind straight down — and it reached the
underside of the desk at raw 3850 (owner, watching; the tool logged it as a stop). No
protection flags, all six at status 0 afterwards; damage to desk or arm not yet reported.
Two faults, both the assistant's: the configuration was chosen from a wrong picture of the
sweep, and the keep-out let it happen because the cylinder exemption had no floor — the
space behind the desk-edge plane below the desk top is desk. **Fixed:** the keep-out now
forbids everything behind the plane that is either outside the cylinder or below the desk
top (`DESK_TOP_Z = 0`), which flags the strike pose with 27 points; the stop finder vetoes
any step whose capsules would touch the base and warns on other overlaps. The correct
elbow configuration is the upper arm vertical (owner), with the wrist pitched −60° so the
gripper points forward, which the fixed checks pass at every elbow angle to 3700 and warn
on from 3850 (shoulder–lower arm capsules).

**Changed as a result:** `kinematics.keepout_clear` gains the desk floor; the elbow's max
and derived zero are discarded from `calibration/stops.json`; the wrist's stops stand.

### 2026-09-14 · Self-collision: capsule hit boxes from upstream's meshes, validated offline

**Conditions:** no servo touched. `software/kinematics.py` gains a capsule per collision mesh
in upstream's `so101_new_calib.urdf` (17 capsules over 7 links, fitted 2026-09-14: PCA
axis, radius = the largest perpendicular vertex distance, ends pulled in until the caps
just cover every vertex — so every capsule contains its whole mesh and the test is
conservative), placed by the forward kinematics, with the closest-segment distance between
every non-adjacent link pair. A pair "collides" when its capsules overlap.

**Calibrated against poses the arm ran through contact-free today** (the first target, the
square and the cube, sampled every 1 cm): three joint-crowded pairs overlap slightly there
because the capsules are fat at the joints, and get an allowance — lower arm–gripper
−14 mm seen, −15 allowed; shoulder–lower arm −17 seen, −20 allowed; upper arm–wrist −1 seen,
−10 allowed. Two pairs overlap in every pose by construction and are not tested (base–upper
arm, wrist–jaw). No margin on top: the capsules already cover the meshes.

| Pose | Verdict |
|---|---|
| calibration mid, URDF zero, first target | clean |
| 20 cm square path, 12 cm cube path (81 and 193 points) | clean — both dry runs accepted |
| owner's turret-pointing pose (earlier entry) | **9 pairs overlapping**, worst shoulder–gripper −70 mm, base–gripper −63 mm |
| a joint-space plan from mid to that pose | **refused at step 67 of 88**, lower arm–gripper −15 mm, before anything moves |
| folded rest pose | 10 pairs overlapping — a real contact pose, correctly flagged |
| 50 random in-limit poses through IK | 36 accepted, 11 refused by the checks, 70 ms per solve with all checks |

The checks now run in the same place as the keep-out: IK acceptance (`solve`), every sample
of a guarded plan, every point of a shape. Not verified live: no move was made after the
change; the next live move is the first end-to-end run of the full check.

**Changed as a result:** roadmap milestone 4 self-collision item done for one arm; what
remains geometric is the desk surface (moves from the rest pose) and the second arm's hit
boxes in the same check (DEC-15).

### 2026-09-14 · A hand-set pose that passes the keep-out and points the gripper into the turret

**Conditions:** torque off, pose set by the owner to make the point; bench camera frame and
`kinematics.py --live`. Raw 1994 / 1568 / 3615 / 3199 / 1362 / 1462 → model −4.6°,
−26.2° (upper arm leaning back), +58.1° (forearm folded forward-down), **+99.3°** on
`wrist_flex` (past the URDF's ±95°), gripper 4.6 cm above the base plate and 1.5 cm ahead
of the pan axis, approach axis pointing at the turret. **Keep-out verdict: CLEAR, with no
point tested** — every part is inside the 0.18 m cylinder, which is the installer's zone by
definition. **Nothing in the tools would stop a closing elbow or wrist from driving the
gripper into the pan carrier from here**: the joint limits do not describe it, the keep-out
does not cover it, and the effort guards act only after contact. In the camera the gripper
is closing on the base with the wrist servo hard against its stop.

**Changed as a result:** self-collision (link against link, and every link against the base
and turret) is the next geometry item on the roadmap. Upstream's URDF carries a collision
mesh for every link including the base (`Simulation/SO101/assets/*.stl`), which is the
source for it.

### 2026-09-14 · Shapes on a loop under IK: a 20 cm square and a 12 cm cube

**Conditions:** torque on and holding from the guarded move, Eventek at 12.0 V, bench
camera on. `software/shapes.py`: every 1 cm along the shape solved by IK (position + pitch,
warm-started), each point inside the URDF and servo limits and clear of the keep-out —
which was settled during this run as *behind the desk-edge plane, minus the 0.18 m
cylinder about the pan axis, tested on every part of the arm*
([`hardware.md`](hardware.md) → Bench). Guarded joint-space approach to the start, then
the loop streamed at 20 Hz, tool speed 5 cm/s, `Goal_Velocity` 800.

| Shape | Centre from the pan axis (fwd, left, up) | Pitch | Points | Loops | Time | Peak mA | °C | Rail |
|---|---|---|---|---|---|---|---|---|
| 20 cm square, vertical, facing the arm (y–z plane) | 0.24, 0, 0.06 m | 45° | 81 | 3 | 54 s | 130 | 38–39 | 11.8–12.0 V |
| 12 cm cube, all 12 edges (16 traversals) | 0.30, 0, 0.06 m | 30° | 193 | 2 | 84 s | 351 | 38 | 11.8–12.0 V |

Worst IK residual 1.0 mm on both; no tracking, current or temperature trip in the runs
above. A later open-ended cube run (`--loops 0`, stopped by its stop file after two loops
at the owner's word: 44 s and 86 s, peaks 312 and 325 mA, 38 °C, 11.9–12.0 V) held in
place on the stop file and torque was then released servo by servo — all six status 0,
0 mA, 35–38 °C. **A 20 cm cube is not reachable**: every placement tried puts the near-bottom
corners past the elbow's shrunk maximum (3779 with the 3° margin) or beyond reach; 15 cm
cubes fail the same way; 12 cm at 30 cm ahead is the largest that solves. **The camera
view was not compared against the model for these runs** — the tool positions are the
model's.

**False trip, fixed:** the first square attempt held after loop 1 on a temperature read of
**130 °C one sample after 38 °C** — a corrupted `sync_read`, not the servo (the next read
was 38 °C again). Both move tools now trip on current or temperature only when two
consecutive samples exceed the threshold; tracking error still trips on one.

**Changed as a result:** keep-out rule settled in `hardware.md`; `shapes.py` added;
debounce in `shapes.py` and `guarded_move.py`. The extents cycle does not yet apply the
keep-out and would repeat the supply strike; it is not to be run again until it does.

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
below the top of the base plate** — **the comparison that followed is wrong: see the correction in the stop-measurement entry
(the model's x is the base frame, 3.9 cm behind the pan axis; the model was 4.1 cm short).**
As first written: forward within 2 mm, height 2 cm high in the model. At
this reach 2 cm is ~5° of pitch across the chain, the size of the elbow residual at the
hand-set zero; the count-to-angle zero (±10°) is the limiting error, not the URDF. **Also
measured: the desk edge is 25 mm ahead of the pan axis**, which moves the keep-out plane to
x = 0.0638 m in `kinematics.py`. A first reading of the rule as "no link body behind the
edge" would have refused a vertical upper arm (13 mm overhang); **the owner clarified the
same day that the rule is on the end-effector only**, so the check now tests the gripper
alone: rest, mid, URDF zero and today's target all pass (rearmost tool x +0.126, +0.193,
+0.327, +0.247 m); a reach-back test pose (shoulder −40°, elbow −60°, wrist −30°) fails at
−0.139 m ([`hardware.md`](hardware.md) → Bench).

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
2026-09-12 run. **But the bench was not: the Eventek supply, sitting on the desk behind
the base, was struck during these warm-up moves and now lies on its side** (owner, reported
later the same day). The tools did not detect it. Likely candidate, unverified: the
`shoulder_lift` move to its lower target 996 (−77°, upper arm swept far back over the desk),
which reached 1017 with the run's largest tracking error (+21) in cycle 1 and 986 (−10) in
cycle 2. The extents cycle sweeps every joint's full shrunk range and has no world model;
layer (1) of the safety model in [`hardware.md`](hardware.md) → Bench was not met.

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

### 2026-09-13 · Arm reached back and hit the wall behind the table (owner report)

**Conditions:** unlogged driving session on the desk-edge mount; tools, poses and supply not
recorded. **Reported 2026-09-14 by the owner:** the upper arm and lower arm both extended
back and hit the wall behind the mounting table — at the arm's position before the
desk-edge relocation; the new mount has no wall behind it. Damage, servo flags and readings at the
time: not recorded; the next morning's health check found all six servos at status 0 and
the calibration offsets intact, and two EEPROM changes of unknown origin (`wrist_flex` and
`gripper` limits reverted, `gripper` `Max_Torque_Limit` 500) — whether they relate to this
is unknown. **Changed as a result:** this is the incident behind the bench keep-out rule
([`hardware.md`](hardware.md) → Bench) and the safety model recorded there.

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
