# SO-ARM101 build — agent / contributor onboarding

**Read this first, after the family's [`AGENTS.md`](../../AGENTS.md)** two levels up: the
4Cs, harness independence, the placement rule and the working conventions are defined
there once and apply here in full. This file holds only what is true of this project.
It is provider-neutral; `CLAUDE.md` and `GEMINI.md` here do nothing but point at it.

**A folder in wk-robotics since 2026-09-13.** It was its own repository,
[`wk-soarm101`](https://github.com/WayneKennedy/wk-soarm101), from its start until then; that repo is
archived and its history is carried here unchanged.

## What this project is

**One build of the SO-101 follower arm**, the LeRobot-compatible manipulator designed by
The Robot Studio with Hugging Face, in its **12 V servo variant**. The design is not
changed and not forked: upstream
[TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) is cloned
alongside this repo as a read-only reference, and **this repo holds only what is true of
this build** — which parts exist, which servo carries which ID, what was measured, what
was decided, what is open. Full intent: [`docs/concept.md`](docs/concept.md).

**The design authority is upstream.** For geometry, the bill of materials and the
assembly order, read the upstream README and the
[LeRobot SO-101 guide](https://huggingface.co/docs/lerobot/so101); do not re-derive
them here. This repo records where *this* build departs from or instantiates them.

## Where things live

- [`docs/concept.md`](docs/concept.md) — what it is, what it is for, and how it
  relates to upstream and the rest of the family.
- [`docs/hardware.md`](docs/hardware.md) — what exists: printed parts and their
  state, electronics in hand.
- [`docs/servos.md`](docs/servos.md) — **the servo map**: which physical servo has
  which ID and joint, how it was set, and what calibration will add.
- [`docs/decisions.md`](docs/decisions.md) — **banked decisions** (the durable *why*).
- [`docs/open-questions.md`](docs/open-questions.md) — **pending decisions**.
- [`docs/roadmap.md`](docs/roadmap.md) — print → commission → assemble → calibrate →
  teleoperate → mount.
- [`docs/sourcing.md`](docs/sourcing.md) — in hand versus still needed.
- [`docs/references.md`](docs/references.md) — upstream, LeRobot, vendor docs.
- [`docs/test-log.md`](docs/test-log.md) — what was actually measured, dated.
- `software/` — any host-side scripts this build needs beyond LeRobot. Empty so far.

## Placement

Facts true of **more than one** robot live one level up in
[`docs/common.md`](../../docs/common.md) — the printer and its profiles, the **STS3215
servo family and how to configure one**, the bus adapters, power integrity, licensing.
**Link to them; never copy them.** Facts true of *this arm* alone live in this folder and
nowhere else.

Two neighbours hold facts that touch this build:

- [koala-bot](https://github.com/WayneKennedy/koala-bot) shares the servo family and
  vendors the upstream CAD as reference. Its two Amazon test-fit servos became this
  arm's first two joints ([`docs/servos.md`](docs/servos.md)).
- [Devastator](../devastator/README.md) is the intended
  mobile base. Whether it can carry the arm is its OQ-12 and needs **this arm's real
  mass** — see [`docs/open-questions.md`](docs/open-questions.md).

The print jobs themselves are in the family's private `3d-printing` repo. Their
*results* — which parts exist and whether they are usable — are recorded here.

## Conventions specific to this project

- **Every servo write is logged.** IDs and calibration are set by script, never by a
  GUI, and each write lands in [`docs/servos.md`](docs/servos.md) and
  [`docs/test-log.md`](docs/test-log.md). Label the servo physically at the same time.
- Recommendations offered to the owner and not yet accepted are open questions, not
  decisions.

## Status

**Parts printed, servos being commissioned, nothing assembled.** Direction: learn it as
a LeRobot arm first (DEC-08); its ultimate purpose and runtime controller stay open
(OQ-08, OQ-09). All 11 follower parts
have been printed at least once; one (`Wrist_Roll_Pitch`) has no confirmed-usable copy
yet. Two of six servos are commissioned — `shoulder_pan` ID 1 and `shoulder_lift` ID 2,
verified together on one bus 2026-09-09. The other four servos are **not yet sourced**
(OQ-01). Details: [`docs/hardware.md`](docs/hardware.md), [`docs/servos.md`](docs/servos.md).
