# bam-rig — printable BAM identification rig for the 12 V STS3215

Family tooling: a pendulum test bench in the form Rhoban's BAM asks for
(`../bam/docs/identification/setup.rst`), sized for the Feetech STS3215 and printable
on the family printer. It serves koala-bot, the Open Duck question and any future STS
project; the plan it implements is in
[`docs/common.md` → "The servo in simulation — BAM's fit, and the 12 V gap"](../../docs/common.md#the-servo-in-simulation--bams-fit-and-the-12-v-gap).

**Status 2026-09-23: designed and built in CAD, nothing printed, nothing measured.** Every
figure below is either copied from koala-bot's measured servo geometry (cited) or a design
choice; the ones marked `[GUESS]` have no source at all.

## What it is

| Part | Count | What it does |
|---|---|---|
| `bracket` | 1 | koala-bot's four-ear SO-101 saddle (the pocket that is proven to fit the STS3215 in PLA+/PETG) on a 6 mm bench plate with a lip that hooks the bench edge, four screw holes and room for a G-clamp. The servo lies on a Side, Bottom in the pocket, drive horn outboard |
| `arm_100`, `arm_150` | 1 each | Pendulum arms: hub pad bolted to the drive horn's four tapped M3 holes with the supplied M3×6 pan heads; bar in a plane 2 mm beyond the bracket wall so the full −90…+90° swing is clear; M8 load-bolt hole 100 / 150 mm from the output axis |
| `pot` | 2 | Load pot, Ø70 × 50 mm (inner Ø65 × 47 = 156 cm³), bolted to the arm tip through its floor. Fill with anything dense and loose; weigh it |
| `lid` | 2 | Pot lid with a locating spigot, clamped by the same nut |

Frame and placement (the koala-bot servo frame, `koala-bot/hardware/src/koala_hardware/servo_iface.py`):
X = output axis, +X toward the drive horn; Y = case width; Z = case length, servo Bottom at
Z = 0, output axis at Z = 35.115. In the rig the servo lies on a Side (−Y is down), the case
runs along the bench edge, and the whole saddle overhangs the bench edge (the plane X = 0)
by 22.45 mm so the arm and load, at X ≥ 24.45, swing past the edge in a vertical plane.
The output axis ends up 55.5 mm above the bench top. The cable bay on the Back faces
inboard, over the plate.

## Parameters (`rig.py`)

Servo geometry is **copied** from koala-bot, which is canonical — `check_koala()` compares
all 36 constants against `koala-bot/hardware/src/koala_hardware/params.py` on every run
when koala-bot is checked out beside this repo, and fails on any drift. The load-bearing ones:

| Constant | Value | Source (koala-bot name, provenance) |
|---|---|---|
| `CASE_X`, `CASE_Y` | 34.9, 24.7 | `SOCKET_CASE_X/Y` [STEP] SO-101 Gauge_0 pocket; `SOCKET_CLEAR = 0` [MEASURED 2026-09-07] fits PLA+/PETG |
| `AXIS_Z` | 35.115 | `SOCKET_AXIS_Z` = 45.23/2 + 12.5 [SPEC] |
| `EAR_X`, `HORN_SEAT_X`, `SEAT_OFFSET` | 31.8, 28.8, 0.5 | [MEASURED 2026-09-08] the three case planes |
| `DRIVE_FACE` | 19.4 | `SOCKET_DRIVE_FACE` = −17.0 + `SOCKET_HORN_SPAN` 36.4 [MEASURED 2026-09-08]; the arm's contact plane |
| `DRIVE_SQ` | 9.9 | `SERVO_DRIVE_SQ` [STEP]; horn tapped M3 (koala test-log 2026-09-08 row 2) |
| `HORN_SCREW_HEAD_DIA/H` | 5.2 / 2.0 | [SUPPLIED 2026-09-08] M3×6 pan heads in the box |
| `WEB_T` | 3.5 | `SOCKET_PLATE_T` [STEP]; M3×6 through 3.5 leaves 2.5 mm in the horn (koala test-log row 9) |
| `CLEAR_HOLE_M3`, `HEAD_CLEAR` | 3.4, 6.4 | [MEASURED 2026-09-01] coupon; `SOCKET_HEAD_CLEAR` [DESIGN] |
| `WALL`, `DEPTH`, `SHELF` | 5, 17, 5 | `SOCKET_WALL/DEPTH/SHELF`: SO-101 capture |
| `LUG_*`, `M2_*`, `*_SLOT_*` | see file | SO-101 lug holes, M2 self-tapper seats, unequal drive/idler recesses [STEP] |

Rig choices, all `[DESIGN]` unless tagged:

| Constant | Value | Why |
|---|---|---|
| `ARM_LENGTHS_MM` | 100, 150 | BAM `length` 0.10 / 0.15 m, Rhoban's set (`docs/common.md`) |
| `ARM_W`, `ARM_T` | 25 × 6 | bar section; bending at 2.2 N·m ≈ 4 MPa, far under PLA |
| `ARM_CLEAR` | 2.0 | bar inner face beyond the drive wall (`WALL_OUT` 22.45) → bar at X 24.45…30.45 |
| `PAD_R` | 12.5 | hub pad radius; the nearest bracket point is 18.1 mm from the axis, so the pad never reaches it |
| `LOAD_BOLT_DIA` | 8.4 | `[GUESS]` M8 clearance in print, nominal + 0.4 like the measured M3 figure |
| `PLATE_T`, `PLATE_REACH`, `LIP_H` | 6, 70, 15 | bench plate; needs a square bench edge ≥ 15 mm deep |
| `PLATE_HOLE_DIA` | 5.0 | `[GUESS]` M4 or No.8 wood screws; a G-clamp works without them |
| `POT_OD`, `POT_H` | 70, 50 | see *Loads* |
| `DENSITY_G_CM3` | 1.24 | `[VERIFY]` generic PLA; only for the arm-mass *estimate* |

## Build

```sh
cd tools/bam-rig
uv sync                  # build123d 0.11.1 (koala-bot's pin), trimesh, numpy
uv run python rig.py     # ~3 s; add --no-sweep to skip the clearance sweep
```

The script builds every part, asserts each is one valid solid, exports `build/*.stl` in
print orientation (+Z up, lowest face at Z = 0), refuses any STL that is not a closed
positive-volume mesh (koala-bot `meshing.export_mesh`, condensed), screens each mesh for
downward faces steeper than 45° that are not on the bed (koala-bot `printability.metrics`),
checks the bed limit (≤ 200 × 200 mm, `docs/common.md`), checks the servo envelope
(koala `case_boxes()` plus horns) does not intersect the pocket, and sweeps arm + load
through −90…+90° in 10° steps against bracket, servo and bench, requiring zero
intersection. It prints the parts table and writes `build/report.json`. `build/` is
gitignored. Exit status 1 on any failure.

## Print list (script output, 2026-09-23)

| part | count | orientation | support-free | bbox X × Y × Z mm | cm³ |
|---|---|---|---|---|---|
| bracket | 1 | as exported: saddle floor on the bed, pocket up, plate on its long edge; lip and rib reach the bed | yes | 92.4 × 49.7 × 55.0 | 49.5 |
| arm_100 | 1 | as exported: on edge, bar's long edge on the bed, horn face vertical | yes | 11.1 × 125.0 × 25.0 | 19.7 |
| arm_150 | 1 | same | yes | 11.1 × 175.0 × 25.0 | 27.2 |
| pot | 2 | floor on the bed, open end up | yes | 70.0 × 70.0 × 50.0 | 36.3 |
| lid | 2 | disc on the bed, spigot up | yes | 70.0 × 70.0 × 6.0 | 21.0 |

Every horizontal hole is a teardrop (45° roof), which is why the walls print without
support; the pan-head seats stay flat (a countersink would wedge layers apart — koala
`fasteners.m3_counterbore`). Material: **PETG** (the printer's standing profile), chosen 2026-09-23 over
PLA+: the arm hangs up to 2 kg off the horn for a session and the servo warms the pocket at
stall current, so creep and toughness matter more than stiffness; the servo pocket is the
SO-101 saddle confirmed to fit in both materials (koala-bot DEC-33). PLA+ also works. The
script's arm-mass estimate uses PLA's density; the scale replaces it either way. Print the
**arms at 100 % infill** so they are stiff and the modelled mass estimate means something;
the bracket with ≥ 4 walls. PETG is less stiff than PLA+, and the arm's droop under load is
uncalculated: with the full load hanging and the servo torqued off, measure the tip; under a
millimetre, ignore it. PETG holes print slightly undersize — the M8 hole and lid spigot are
not measurement-critical, so drill or trim if tight. All five together are one plate's worth
(bracket 92 × 50, arms 11 × 175, pots 70 × 70).

## Assembly

1. Slide the servo into the pocket, Bottom first, drive horn on the wall side that has no
   plate beyond it. Fit the four M2×5 self-tappers (the box screws, `SELFTAP_DIA` koala
   test-log 2026-09-07) through the wall pockets into the case lugs — two from each side.
2. Bolt the arm's hub to the drive horn: four M3×6 pan heads (supplied with Waveshare and
   RCmall servos) through the hub into the horn's tapped holes; the centre screw's head sits
   in the hub's relief. Reach the heads through the Ø6.4 pockets on the outer face.
3. Load: M8 bolt or threaded rod (≥ 80 mm for one pot, ≥ 130 mm for two) through the bar
   from the inboard side, head or nut against the bar; pot floor against the bar's outer
   face; contents; lid; washer; nut. **Not recorded in stock** (wk-inventory `docs/stock.md`
   searched 2026-09-23 for M8 hardware, clamps, scales, masses: nothing) — see *Hardware to
   find or buy*.
4. Push the lip against the bench edge, drive horn overhanging, and clamp the plate inboard
   of the saddle — the owner's 4-inch quick-grip F clamps (Amazon #204-1157421-6505962,
   2026-09-14, delivered 2026-09-16; ~100 mm capacity, so bench + 6 mm plate up to ~90 mm)
   suit it; screws through the four Ø5 holes are the alternative. Check by hand that the arm
   swings a full half-circle without touching anything.
5. Set the arm hanging straight down and set the servo's zero there (BAM's zero is the arm
   pointing down; `bam/testbench.py`).

### Loads

BAM wants several masses per length. Pot inner volume 156 cm³; approximate fills
`[GUESS]`, packed bulk densities from general references, not measured:
lead shot ≈ 7 g/cm³ → ~1.1 kg per pot; steel shot ≈ 4.5 → ~0.7 kg; loose steel nuts and
bolts ≈ 3–4 → ~0.5 kg; dry sand ≈ 1.5 → ~0.25 kg; rice ≈ 0.8 → ~0.12 kg. Covering the
12 V unit's full stall needs **2.0 kg at 0.15 m** (`docs/common.md`; 1.5 kg reaches 75 %):
two pots of lead shot (~2.2 kg) do it, two of steel shot (~1.4 kg) do not. Small
masses also work as a washer stack on the bolt with no pot. Whatever it is, the scale is
the source of truth.

## The measurements the owner must take, and where they go

BAM's pendulum model (`bam/testbench.py` `Pendulum`) is a **point mass at `length` on a
uniform rod of `arm_mass`**: inertia `mass·L² + arm_mass·L²/3`, gravity torque
`(mass + arm_mass/2)·g·L·sin q`. Three numbers per configuration:

| Quantity | How | BAM key |
|---|---|---|
| `length` | axis to load-bolt axis: 0.100 or 0.150 m by design. Check on the print with a rule (bolt centre to hub centre); PLA shrinkage is unmeasured on this printer | `--length` |
| `mass` | weigh **everything on the bolt together**: bolt, nut(s), washer(s), pot(s), lid(s), contents. Kitchen scale, 1 g resolution is plenty | `--mass` |
| `arm_mass` | weigh the bare arm (m_a). Find its balance point on a knife edge and measure x_com from the output-axis centre. The uniform-rod equivalent for gravity is **`arm_mass = 2·m_a·x_com/L`**; the script's estimate at 1.24 g/cm³ and 100 % infill is 24 g / 46 mm → 22 g for `arm_100` and 34 g / 71 mm → 32 g for `arm_150` (inertia-equivalent 26 g / 34 g; the ~10 % gap between the two equivalents is 2–3 g, negligible against loads ≥ 250 g) | `arm_mass` in the raw JSON — see caveats |

Record the measured values here (nothing may live only in chat) and in each recording:

| Item | Measured | Date, instrument |
|---|---|---|
| arm_100: mass, x_com | unmeasured | |
| arm_150: mass, x_com | unmeasured | |
| each load configuration: mass | unmeasured | |
| length on the print, both arms | unmeasured | |

Recording, per `bam/docs/identification/acquisition.rst` and `bam/feetech/all_record.py`
(kp sweep `[4, 8, 16, 32]`, trajectories brutal, sin_sin, lift_and_drop, up_and_down,
sin_time_square):

```sh
uv run python -m bam.feetech.all_record --mass <kg> --length 0.15 --motor sts3215_12v \
    --id 1 --port /dev/ttyACM0 --vin 12 --logdir data_raw
uv run python -m bam.process --raw data_raw --logdir data_processed --dt 0.005
```

Then `bam.fit --model m6`, and the results go where `docs/common.md` says: a
`sts3215_12v` actuator class and params in BAM, and the five MuJoCo numbers via
`bam.to_mujoco --kp 32 --vin 12`.

## Caveats

- **BAM's Feetech recorder, as published, does not log the arm mass** (`bam/logs.py` silently
  uses 0.0 if absent). **Done 2026-09-23** on the local BAM branch `local/sts3215-12v` in
  `../bam`: the recorder runs on rustypot, honours `--port`, `--id` and `--arm-mass`, and
  `all_record.py` passes it through — use that branch (its `RECORDING.md` is the procedure).
  On upstream `main` instead, add `"arm_mass": <kg>` to every raw JSON before `bam.process`.
  Setting it to 0 is a ~5–10 % error on a 250 g load and ~1 % at 1.5 kg.
- **The arm is not a uniform rod.** The hub pad thickens it at the axis and the bar runs
  12.5 mm past both the axis and the bolt. The gravity-equivalent formula above absorbs
  this exactly for gravity; the inertia term is then ~10 % of `arm_mass` off. Both
  equivalents are printed by the script.
- **The load is not a point mass.** A filled pot of radius 32.5 mm adds about m·r²/2 to the
  inertia that BAM does not model: ≈ 5 % of m·L² at 0.10 m, ≈ 2.4 % at 0.15 m. A denser
  fill in one pot beats two pots; a washer stack is closer to a point.
- **Single-sided load on the output shaft.** The pot's centre sits ~50 mm outboard of the
  horn face (≈ 0.7 N·m of bending at 1.5 kg). Rhoban's XL-330 rig is single-sided too, but
  the STS3215's output bearing has no published bending rating; use the idler-side of
  nothing here. If the servo shows play after a session, that is why.
- **Unverified fits.** Nothing printed. The saddle re-expresses koala's proven pocket with
  the same datums, but the teardrop M2 holes, the Ø8.4 M8 hole, the Ø5 plate holes and the
  0.3 mm lid spigot clearance are not coupon-tested. The bracket needs a bench with a
  square edge at least 15 mm deep for the lip; otherwise clamp the plate flat and align the
  lip to the edge by eye — the arm plane only needs the bench edge to be inboard of X = 19.
- **Loads on PLA.** 2.2 N·m static plus impacts at ±90° on a 6 mm bar and a 6 mm plate
  with a 22 mm cantilever: stresses calculate to a few MPa, but the printed part has not
  been loaded.
- **Rhoban's Onshape arm** (`setup.rst` link) is a JavaScript app with no fetchable text
  (2026-09-23); this rig is not derived from it.

## Hardware to find or buy

Searched 2026-09-23 per AGENTS.md: wk-inventory `docs/stock.md` and the owner's mailbox.
**Owned:** 4 × 4-inch quick-grip F clamps (above); M2×5 self-tappers and M3×6 pan heads in
the servo boxes. **Not found on any invoice or in stock** — check the odds box before
buying: M8 bolt ≥ 80 mm or threaded rod, 2 M8 nuts, 2 large washers; a kitchen scale (one
was used on 2026-09-17, instrument unrecorded — `docs/common.md`); dense fill (lead or
steel shot for the top of the range).
