# Devastator — agent / contributor onboarding

**Read this first, after the family's [`AGENTS.md`](../../AGENTS.md)** two levels up: the
4Cs, harness independence, the placement rule and the working conventions are defined
there once and apply here in full. This file holds only what is true of this project.
It is provider-neutral; `CLAUDE.md` and `GEMINI.md` here do nothing but point at it.

**A folder in wk-robotics since 2026-09-13.** It was its own repository,
[`wk-devastator`](https://github.com/WayneKennedy/wk-devastator), from its start until then; that repo is
archived and its history is carried here unchanged.

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

## Placement

Facts true of **more than one** robot live one level up in
[`docs/common.md`](../../docs/common.md) — the printer and its profiles, the compute
pattern, the topic contract, micro-ROS, power integrity, the GPU workstation, licensing.
**Link to them; never copy them.** Facts true of *this* robot alone live in this folder
and nowhere else.

## Conventions specific to this project

- Several entries in `docs/open-questions.md` are *recommendations made to the owner
  and not yet accepted*. They are labelled as such and must not be promoted to
  `docs/decisions.md` without a decision.
- Capabilities of the machines involved may be described; the machines may not be
  named (the family's public-repo rule).

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

**Milestone 0, and waiting on a part.** Chassis and original electronics exist and are
documented; the drivetrain has now been **measured**
([`docs/test-log.md`](docs/test-log.md)). No code written.

The motor question that gated everything is **closed** — DEC-11 buys two Pololu #4865, and
the 12 V / 3S rail follows as DEC-12. **They are on back order, due end of October 2026** (revised 2026-09-09; was ~26 September),
so milestone 1 cannot start. A Teensy 4.1 is ordered (DEC-10); the motor driver is
**in hand** — this robot's own since 2026-09-11, no longer borrowed from koala-bot
(DEC-13, amended).

**Frontier: compute the power budget** (DEC-07). It is not blocked by the back order, and
every number it needs now exists. Neither are the arm's mass (OQ-12) or the plate question
(OQ-10). The drivetrain's mechanical questions are all closed.
