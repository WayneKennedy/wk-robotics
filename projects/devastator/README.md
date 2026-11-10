# Devastator 🛞🤖

> **The project record moved to Basic Memory on 2026-11-10** (project `main`, folder `robotics/devastator/`; start at the
> *Devastator* note). This README and `docs/` — concept, architecture, decisions, open questions, roadmap, hardware,
> electronics, sourcing, references, test log — are canonical there; the copies here were deleted on 2026-11-10 (git history keeps them). This repo keeps what is about the
> code and artefacts: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING.md`, `LICENSING.md`, `firmware/`,
> `software/` (incl. the `hailo_perception` package), `cad/` and `docs/images/`.

> A folder in [wk-robotics](../../README.md) since 2026-09-13. Formerly the repository
> `wk-devastator`, now archived; its history is carried here. Family-wide facts and rules are
> one level up; this folder holds only what is true of this project.

**A tracked ROS 2 robot, resurrected from a stalled build.** The chassis is a
DFRobot Devastator; everything above it is being replaced.

**Status:** milestone 0 — the **two Pololu 25D 12 V gearmotors with encoders are fitted**
(2026-10-14), the Teensy 4.1 and the driver are in hand, and the electronics are designed
([*Devastator Electronics*](memory://main/robotics/devastator/devastator-electronics)) around a Jetson Orin Nano intent host with a
Pi 5 as the drop-in alternative (DEC-16). First use case: a **SLAM rover** with the Orin,
the D435i and an RPLIDAR C1 (DEC-19); the arm is deferred. Reflex tier on the lower deck,
intent on the upper (DEC-18). Next: the owner measures the decks, then the layout is drawn.
No code written. See [*Devastator Roadmap*](memory://main/robotics/devastator/devastator-roadmap) for direction,
[*Devastator Decisions*](memory://main/robotics/devastator/devastator-decisions) for what is settled, and
[*Devastator Open Questions*](memory://main/robotics/devastator/devastator-open-questions) for what is not.

## What it is

A **statically stable, tracked, skid-steer mobile base** carrying a two-tier
reflex/intent stack and speaking the family's ROS 2 topic contract. It is the
simplest body in the family — no balance loop, no gait, and no manipulator it designs
itself — which is precisely what makes it useful: the cheapest platform on which the
shared navigation stack and a multi-robot architecture can actually be tested, and the
intended mobile base for the family's
[SO-ARM101](https://github.com/TheRobotStudio/SO-ARM100) (deferred, DEC-19; feasibility
open — [OQ-12](memory://main/robotics/devastator/devastator-open-questions)).

- Aluminium tracked chassis, **225 × 220 × 108 mm**, 1.3 kg, 3 kg payload.
- Reflex tier on a 32-bit MCU running **micro-ROS** — encoder decoding, closed-loop
  wheel velocity, safety watchdog.
- Intent tier running **ROS 2** — SLAM, Nav2, mission — on a Jetson Orin Nano first, with a
  Raspberry Pi 5 + AI HAT+ 2 as the drop-in alternative (DEC-16, amending DEC-15); one
  camera. The family's second intent-tier reference, a step above the hexapod.
- Designed from the outset to keep working when the coordination tier is unreachable.

## Why it exists

It was bought, part-built, and abandoned. The build is documented honestly in
[*Devastator Concept*](memory://main/robotics/devastator/devastator-concept): it stalled on
battery limitations and over-ambitious scope, with two depth cameras and a Pi 4 mounted
before the drivetrain worked. **The resurrection inverts that order.** Milestone 1
carries no perception at all.

## Documents

| File | Contents |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Onboarding for any AI assistant or contributor — **start here** |
| [*Devastator Concept*](memory://main/robotics/devastator/devastator-concept) | What it is, what it is for, and the history |
| [*Devastator Architecture*](memory://main/robotics/devastator/devastator-architecture) | The three tiers, micro-ROS, power |
| [*Devastator Hardware*](memory://main/robotics/devastator/devastator-hardware) | Chassis spec and the as-found inventory |
| [*Devastator Electronics*](memory://main/robotics/devastator/devastator-electronics) | The new build's power tree, wiring, host-agnostic reflex link, layout |
| [*Devastator Decisions*](memory://main/robotics/devastator/devastator-decisions) | Banked decisions — the durable *why* |
| [*Devastator Open Questions*](memory://main/robotics/devastator/devastator-open-questions) | Unresolved. Never state these as settled |
| [*Devastator Roadmap*](memory://main/robotics/devastator/devastator-roadmap) | Milestones 1–3 |
| [*Devastator Sourcing*](memory://main/robotics/devastator/devastator-sourcing) | What still needs buying |
| [*Devastator References*](memory://main/robotics/devastator/devastator-references) | Upstream and prior art |
| [*Devastator Test Log*](memory://main/robotics/devastator/devastator-test-log) | What was actually measured |

## Family

This robot is one of several. The index, and everything true of more than one of them —
the printer, the compute pattern, the topic contract, micro-ROS — is in
[wk-robotics](../../README.md). Facts that belong there are
linked, never copied.

## Licence

Tri-licence — hardware `CERN-OHL-S-2.0`, software `MIT`, docs `CC-BY-SA-4.0`.
See [`LICENSING.md`](LICENSING.md).
