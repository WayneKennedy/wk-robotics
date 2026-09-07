# wk-devastator — agent / contributor onboarding

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

**A tracked ROS 2 robot built on a purchased DFRobot Devastator chassis**, resurrected
from a build that stalled in 2025. The chassis is kept; the electronics, compute and
software are all being replaced. It is also the intended **mobile base for the family's
[SO-ARM101](https://github.com/TheRobotStudio/SO-ARM100)** — which is what prompted the
resurrection, and whose feasibility is **open** (OQ-12: on estimated masses, a ~500 mm
reach on a 225 mm chassis tips — the arm has not been weighed). Full intent: [`docs/concept.md`](docs/concept.md).

**Nothing has been built yet.** The original electronics are still fitted and are
documented as *as-found*, not as a design. Do not read
[`docs/hardware.md`](docs/hardware.md) as a bill of materials for the new robot.

## Where things live

- [`docs/concept.md`](docs/concept.md) — what it is, what it is for, and the honest
  history of the first attempt.
- [`docs/architecture.md`](docs/architecture.md) — the three tiers, micro-ROS, the
  topic contract, and the power budget.
- [`docs/hardware.md`](docs/hardware.md) — chassis specification and the **as-found**
  inventory, with photographs.
- [`docs/decisions.md`](docs/decisions.md) — **banked decisions** (the durable *why*).
- [`docs/open-questions.md`](docs/open-questions.md) — **pending decisions**.
- [`docs/roadmap.md`](docs/roadmap.md) — milestones 1–3.
- [`docs/sourcing.md`](docs/sourcing.md) — what still needs buying, UK-focused.
- [`docs/references.md`](docs/references.md) — upstream links and prior art.
- [`docs/test-log.md`](docs/test-log.md) — what was actually measured, including
  "no change needed" results.

## This repo does not stand alone in one respect

Facts true of **more than one** robot live in
[wk-robotics](https://github.com/WayneKennedy/wk-robotics) — the printer and its
profiles, the compute pattern, the topic contract, micro-ROS, power integrity, the
GPU workstation, licensing. **Link to them; never copy them.** A fact copied here
will drift. Facts true of *this* robot alone live here and nowhere else.

## Working conventions

- **No project fact lives only in chat.** Record durable decisions in `decisions.md`;
  put anything unresolved in `open-questions.md`. Move items between them as they
  resolve.
- **Distinguish decided from open.** `decisions.md` is committed; `open-questions.md`
  is still debated. Never state an open question as settled. In particular, several
  entries there are *recommendations made to the owner and not yet accepted* — they
  are labelled as such and must not be promoted without a decision.
- **Verified beats plausible.** Measured numbers carry the date and the conditions
  they were measured under. An unverified figure is labelled as one.
- **Docs are written AI-first** — dense, factual, cross-referenced, greppable, on the
  assumption an AI assistant is the primary reader.
- **This repository is public.** No credentials, host names, network addresses or
  overlay-network identifiers. Capabilities may be described; the machines that
  provide them may not be named.

## The rules this project is built to obey

Three, and they all come from the same place — the first build failed by ignoring them:

1. **Scope discipline.** Milestone 1 carries **no perception**. Over-scope is the
   recorded cause of the original stall; see
   [`concept.md`](docs/concept.md#the-first-build-and-why-it-stopped).
2. **The power budget is a design input, not a discovery.** The first build was
   under-powered by design. Numbers before purchases.
3. **Each tier survives the loss of the tier above it.** The robot must stay useful
   when the coordinator is unreachable — the coordinator is a desktop and *will* be
   unreachable.

## Status

**Not started.** Chassis and original electronics exist and are documented. No parts
ordered, no code written, no decisions taken beyond those in
[`decisions.md`](docs/decisions.md). Frontier: resolve the motor question (OQ-01),
which gates almost everything else.
