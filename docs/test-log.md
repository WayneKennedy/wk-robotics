# Test log

What was actually measured, on what date, under what conditions — including
"no change needed" results, which are findings too.

The robot is not built, and most of the as-found inventory in
[`hardware.md`](hardware.md) is still *identification from photographs* rather than
measurement, labelled as such there. The drivetrain is the exception: it has been
measured, and those entries are below.

## Format

Each entry: date · what was tested · conditions · result · what changed as a result.

## Entries

### 2026-09-07 · Drivetrain envelope, measured

**Conditions:** direct measurement of the fitted motors and the chassis, robot part-built
and motors in place.

**Result:**

| | |
|---|---|
| Motor + gearbox | **25 mm OD × 52 mm** |
| Output shaft | **4 mm D** |
| Face mounting | **2 × M3 at 17 mm centres** |
| Between side frames | **134 mm**, cross-checked against the electronics plate that spans them |
| Motor seating | **Flush** to the frame, no recess |
| Gearbox marking | **6 V, 133 RPM** |

**What changed:** made OQ-01 decidable and closed most of OQ-11. The marking confirms
[`hardware.md`](hardware.md#the-original-motors)'s 6 V / 133 RPM **from the hardware**,
where it had rested on the vendor listing. **17 mm supersedes an initial 16.5 mm reading**
taken earlier the same day; the remeasure is the figure of record. The 25 × 52 envelope
identifies the part as the commodity **25D / 25GA** class, which is what made a
replacement search tractable at all.

### 2026-09-07 · Do koala-bot's 37D motors fit? — **No**

**Conditions:** measured Devastator envelope against the 37D class koala-bot bought.

**Result:** **No.** A 37 mm body cannot go in a 25 mm envelope on 17 mm centres.

**What changed:** removed the in-family part from consideration and cost nothing to
establish. [`hardware.md`](hardware.md) had carried this as *"likely too large —
unverified"*; it is now verified. **The project's first recorded negative result.**

### 2026-09-07 · Does a Pololu 25D with encoder fit the 134 mm span?

**Conditions:** desk check of measured chassis dimensions against Pololu's published
lengths and a product photograph of the encoder end. Not a physical trial — no motor in
hand.

**Result:** **Caps on, no. Caps off, yes.** With end caps fitted the pair is 2 × 67 mm =
**134 mm in a 134 mm span** — zero clearance. With the caps removed it is 2 × ~64.5 mm ≈
**129 mm, about 5 mm clear**. The six encoder leads exit **radially at the base of the
cap**, so removing the cap does not move the exit. The factory no-cap variant (#3241,
`25Dx64L`) is discontinued and replaced by #4865, whose cap Pololu states is removable.

**What changed:** made DEC-11 possible. **Supersedes an earlier claim in this project's
working notes that the leads exit axially** — they do not; that reading came from a
summarised product page and was wrong. Two assembly notes follow: route both looms before
the motors go in, because the centre is unreachable afterwards; and caps-off leaves the
encoder PCBs exposed on a vehicle that throws grit, so print a shroud.

### 2026-09-07 · Does the shaft/hub interface clear? — **Yes**

**Conditions:** inspection of the fitted assembly, with the original motors in place.

**Result:** **No interference.** The chassis side plates carry a **clearance hole for the
motor hub**, so the gearbox boss and shaft pass through the plate rather than butting
against it. The motor face seats **flush** on the plate, held by the M3 screws, and the hub
protrudes on the far side unobstructed.

**What changed:** **closes OQ-11.** The question had been narrowed to whether the Pololu
shaft's 12.5 mm proud of the face plate would bottom out against a hub of unknown bore
depth. It cannot — nothing is being bottomed against. This was the one dimension not
checked before ordering (DEC-11), so it retires the only risk carried into that purchase.

**One check left for delivery day, and it is not this question:** the clearance hole was
made for the *DFRobot* gearbox's boss. Confirm the Pololu 25D's boss diameter passes the
same hole — readable from Pololu's
[25D dimension diagram](https://www.pololu.com/file/0J1042/25d-metal-gearmotor-dimension-diagram.pdf)
without waiting for the parts.

## Next entries expected

From [`roadmap.md`](roadmap.md) milestone 0 — **none of them blocked by the motor back
order**:

- Mass of the SO-ARM101 parts as they come off the plate (OQ-12).
- Whether the white mounting plate is printed or laser-cut (OQ-10).
- Measured current draw of the drivetrain at realistic duty and at stall (DEC-07) —
  this one *does* need the motors.
