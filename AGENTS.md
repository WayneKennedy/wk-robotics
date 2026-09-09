# wk-soarm101 — agent / contributor onboarding

**Read this first.** It is the entry point for any AI assistant or human working in
this repository, and it is written to be complete on a first read with no prior
context. It is **provider-neutral**: `CLAUDE.md` and `GEMINI.md` do nothing but
point here.

## The 4Cs — the standard every artefact meets

Every artefact — docs, source, CAD, commit messages — must be:

1. **Correct** — fact-based. No speculation unless labelled as such. "Unknown" and
   "unverified" are valid answers; confident guesses are not.
2. **Complete** — nothing essential missing.
3. **Coherent** — everything fits together; no contradictions.
4. **Concise** — nothing superfluous.

All four hold at once: completeness never excuses bloat; brevity never excuses gaps;
and none of the other three count if the content is wrong.

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

## This repo does not stand alone in one respect

Facts true of **more than one** robot live in
[wk-robotics](https://github.com/WayneKennedy/wk-robotics) — the printer and its
profiles, the **STS3215 servo family and how to configure one**, the bus adapters, power
integrity, licensing. **Link to them; never copy them.** A fact copied here will drift.
Facts true of *this arm* alone live here and nowhere else.

Two neighbours hold facts that touch this build:

- [koala-bot](https://github.com/WayneKennedy/koala-bot) shares the servo family and
  vendors the upstream CAD as reference. Its two Amazon test-fit servos became this
  arm's first two joints ([`docs/servos.md`](docs/servos.md)).
- [wk-devastator](https://github.com/WayneKennedy/wk-devastator) is the intended
  mobile base. Whether it can carry the arm is its OQ-12 and needs **this arm's real
  mass** — see [`docs/open-questions.md`](docs/open-questions.md).

The print jobs themselves are in the family's private `3d-printing` repo. Their
*results* — which parts exist and whether they are usable — are recorded here.

## Working conventions

- **No project fact lives only in chat.** Record durable decisions in `decisions.md`;
  put anything unresolved in `open-questions.md`. Move items between them as they
  resolve.
- **Distinguish decided from open.** Never state an open question as settled.
  Recommendations offered to the owner and not yet accepted are open questions.
- **Verified beats plausible.** Measured numbers carry the date and the conditions
  they were measured under. An unverified figure is labelled as one.
- **Every servo write is logged.** IDs and calibration are set by script, never by a
  GUI, and each write lands in [`docs/servos.md`](docs/servos.md) and
  [`docs/test-log.md`](docs/test-log.md). Label the servo physically at the same time.
- **Docs are written AI-first** — dense, factual, cross-referenced, greppable.
- **This repository is public.** No credentials, host names, network addresses or
  overlay-network identifiers. Capabilities may be described; the machines that
  provide them may not be named.

## Status

**Parts printed, servos being commissioned, nothing assembled.** All 11 follower parts
have been printed at least once; one (`Wrist_Roll_Pitch`) has no confirmed-usable copy
yet. Two of six servos are commissioned — `shoulder_pan` ID 1 and `shoulder_lift` ID 2,
verified together on one bus 2026-09-09. The other four servos are **not yet sourced**
(OQ-01). Details: [`docs/hardware.md`](docs/hardware.md), [`docs/servos.md`](docs/servos.md).
