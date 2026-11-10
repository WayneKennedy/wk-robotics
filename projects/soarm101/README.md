# SO-ARM101 build 🦾

> **The project record moved to Basic Memory on 2026-11-10** (project `main`, folder `robotics/soarm101/`; start at the
> *SO-ARM101* note). This README, `docs/` — concept, decisions, open questions, roadmap, hardware, servos, sourcing,
> references, test log — and `cad/lightweight-v1/report.md` are canonical there; the copies here were deleted on 2026-11-10 (git history keeps them). This repo keeps what
> is about the code and artefacts: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING.md`, `LICENSING.md`,
> `software/`, `cad/freecad/` (README and INDEX) and `cad/lightweight-v1/` (model, analysis and README).

> A folder in [wk-robotics](../../README.md) since 2026-09-13. Formerly the repository
> `wk-soarm101`, now archived; its history is carried here. Family-wide facts and rules are
> one level up; this folder holds only what is true of this project.

**A 12 V SO-101 follower arm, built from the upstream design.** The Standard Open Arm by
The Robot Studio and Hugging Face, printed and commissioned here, with nothing changed
in the commissioned hardware. This folder holds the build record and a
[local lightweight prototype study](cad/lightweight-v1/README.md); the baseline design
lives upstream.

**Status:** assembled, calibrated against the world, and moving under its own geometric checks
(milestone 4 closed 2026-09-15): measured joint stops and zeros, a model that agrees with a tape
within 1.5 cm, capsule self-collision and a bench keep-out on every move, and a wake-up from any
contact pose. Next: the Teensy 4.1 on micro-ROS (milestone 5). No camera fitted yet; two are on
order. See
[*SO-ARM101 Roadmap*](memory://main/robotics/soarm101/so-arm101-roadmap) for direction, [*SO-ARM101 Decisions*](memory://main/robotics/soarm101/so-arm101-decisions)
for what is settled, and [*SO-ARM101 Open Questions*](memory://main/robotics/soarm101/so-arm101-open-questions) for what is not.

## What it is

The **SO-101 follower**: 6 degrees of freedom, six Feetech STS3215 bus servos at 1/345
gearing, ~500 mm reach, designed for imitation learning with
[LeRobot](https://huggingface.co/docs/lerobot). This build uses the **12 V** servo
variant (~30 kg·cm stall) rather than the standard 7.4 V one, so it needs a 12 V rail.

- Baseline design, STLs and bill of materials: [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100), cloned as a read-only sibling.
- Parts printed in white eSUN PLA+ on the family's Ender-5 S1.
- Servo bus driven by a Waveshare Bus Servo Adapter (A), the upstream BOM part.
- **Endgame:** two arms 30 cm apart on one desk edge, each planning against the other's hit boxes (DEC-15). **Runtime:** a Teensy 4.1 on micro-ROS into ROS 2 (DEC-14; board, bus connection and host still open in OQ-09). Mounting on [wk-devastator](../../projects/devastator/README.md) stays possible (roadmap milestone 6).

## Why a repo, when upstream has one

Upstream answers *what an SO-101 is*. It cannot answer which of these servos is ID 3,
whether the wrist part off the printer was usable, or why this build runs at 12 V. Those
facts need a home that is not a chat transcript and not a private print log.

## Documents

| File | Contents |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Onboarding for any AI assistant or contributor — **start here** |
| [*SO-ARM101 Concept*](memory://main/robotics/soarm101/so-arm101-concept) | What it is, what it is for, relation to upstream |
| [*SO-ARM101 Hardware*](memory://main/robotics/soarm101/so-arm101-hardware) | Printed parts and their state; electronics in hand |
| [*SO-ARM101 Servos*](memory://main/robotics/soarm101/so-arm101-servos) | The servo map — IDs, joints, how they were set |
| [*SO-ARM101 Decisions*](memory://main/robotics/soarm101/so-arm101-decisions) | Banked decisions — the durable *why* |
| [*SO-ARM101 Open Questions*](memory://main/robotics/soarm101/so-arm101-open-questions) | Unresolved. Never state these as settled |
| [*SO-ARM101 Roadmap*](memory://main/robotics/soarm101/so-arm101-roadmap) | Print → commission → assemble → calibrate → geometry → Teensy on micro-ROS → mount |
| [*SO-ARM101 Sourcing*](memory://main/robotics/soarm101/so-arm101-sourcing) | In hand versus still needed |
| [*SO-ARM101 References*](memory://main/robotics/soarm101/so-arm101-references) | Upstream, LeRobot, vendor documentation |
| [*SO-ARM101 Test Log*](memory://main/robotics/soarm101/so-arm101-test-log) | What was actually measured |
| [`cad/lightweight-v1/`](cad/lightweight-v1/README.md) | Lightweight hypothesis investigation, alternate STEP set and unperformed physical validation |

## Family

This arm is one of several robots. The index, and everything true of more than one of
them — the printer, the STS3215 servo family and how to configure one, the bus adapters,
power — is in [wk-robotics](../../README.md). Facts that
belong there are linked, never copied.

## Licence

Tri-licence — hardware `CERN-OHL-S-2.0`, software `MIT`, docs `CC-BY-SA-4.0`.
See [`LICENSING.md`](LICENSING.md). The upstream-derived lightweight CAD set retains
**Apache-2.0**, including its unchanged reference parts.
