# Devastator — agent / contributor onboarding

> **The project record moved to Basic Memory on 2026-11-10** (project `main`, folder `robotics/devastator/`; start at the
> *Devastator* note). `README.md` and every file under `docs/` are canonical there and frozen here; read them in Basic
> Memory, not from this checkout. This repo keeps what is about the code and artefacts: this file, `CLAUDE.md`,
> `GEMINI.md`, `CONTRIBUTING.md`, `LICENSING.md`, `firmware/`, `software/`, `cad/` and `docs/images/`.

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
software are all being replaced. **Its first job is a SLAM rover** on a Jetson Orin Nano
with a RealSense D435i and an RPLIDAR C1 (DEC-19, 2026-10-14). It is also the intended
**mobile base for the family's [SO-ARM101](https://github.com/TheRobotStudio/SO-ARM100)** —
which is what prompted the resurrection — but that role is **deferred** and its feasibility
is **open** (OQ-12). Full intent: [`docs/concept.md`](docs/concept.md).

**Only the motors are fitted (2026-10-14).** The rest of the original electronics are
still on the chassis and are documented as *as-found*, not as a design. Do not read
[`docs/hardware.md`](docs/hardware.md) as a bill of materials for the new robot; the new
design is [`docs/electronics.md`](docs/electronics.md).

## Where things live

- [`docs/concept.md`](docs/concept.md) — what it is, what it is for, and the honest
  history of the first attempt.
- [`docs/architecture.md`](docs/architecture.md) — the three tiers, micro-ROS, the
  topic contract, and the power budget.
- [`docs/hardware.md`](docs/hardware.md) — chassis specification and the **as-found**
  inventory, with photographs.
- [`docs/electronics.md`](docs/electronics.md) — the new build's power tree, the Teensy's
  wiring, the host-agnostic link to either intent host, the layout zoning and bring-up order.
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

**Milestone 0, parts in hand.** The drivetrain is measured and its motors are **fitted**
(2026-10-14, [`docs/test-log.md`](docs/test-log.md)); the Teensy 4.1 (DEC-10) and the
driver (DEC-13) are in hand. No code written.

**The intent host is the Jetson Orin Nano first, a Pi 5 the alternative** (DEC-16,
2026-10-14), and the electronics are designed so either plugs into the same reflex tier:
[`docs/electronics.md`](docs/electronics.md). A first-pass power budget exists there
(DEC-07); the fuse and pack capacity wait on a stall test (OQ-07, OQ-14).

**Frontier: the owner is measuring the two decks; then draw the layout in FreeCAD**
([`docs/roadmap.md`](docs/roadmap.md) milestone 0, item 6) under the deck rule — reflex
tier on the lower deck, the upper deck free for the plug-and-play intent host (DEC-18).
Then buy the small electrical parts in [`docs/sourcing.md`](docs/sourcing.md) and start
milestone 1.
