# wk-devastator 🛞🤖

**A tracked ROS 2 robot, resurrected from a stalled build.** The chassis is a
DFRobot Devastator; everything above it is being replaced.

**Status:** resurrection, not yet started. The chassis and its original electronics
exist and are documented here; no new work has been done. This repo is currently the
**design record** — see [`docs/roadmap.md`](docs/roadmap.md) for direction and
[`docs/open-questions.md`](docs/open-questions.md) for what is undecided.

## What it is

A **statically stable, tracked, skid-steer mobile base** carrying a two-tier
reflex/intent stack and speaking the family's ROS 2 topic contract. It is the
simplest body in the family — no balance loop, no gait, no manipulator — which is
precisely what makes it useful: it is the cheapest platform on which the shared
navigation stack and a multi-robot architecture can actually be tested.

- Aluminium tracked chassis, **225 × 220 × 108 mm**, 1.3 kg, 3 kg payload.
- Reflex tier on a 32-bit MCU running **micro-ROS** — encoder decoding, closed-loop
  wheel velocity, safety watchdog.
- Intent tier on a Raspberry Pi running **ROS 2** — SLAM, Nav2, mission.
- Designed from the outset to keep working when the coordination tier is unreachable.

## Why it exists

It was bought, part-built, and abandoned. The build is documented honestly in
[`docs/concept.md`](docs/concept.md#the-first-build-and-why-it-stopped): it stalled on
battery limitations and over-ambitious scope, with two depth cameras and a Pi 4 mounted
before the drivetrain worked. **The resurrection inverts that order.** Milestone 1
carries no perception at all.

## Documents

| File | Contents |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Onboarding for any AI assistant or contributor — **start here** |
| [`docs/concept.md`](docs/concept.md) | What it is, what it is for, and the history |
| [`docs/architecture.md`](docs/architecture.md) | The three tiers, micro-ROS, power |
| [`docs/hardware.md`](docs/hardware.md) | Chassis spec and the as-found inventory |
| [`docs/decisions.md`](docs/decisions.md) | Banked decisions — the durable *why* |
| [`docs/open-questions.md`](docs/open-questions.md) | Unresolved. Never state these as settled |
| [`docs/roadmap.md`](docs/roadmap.md) | Milestones 1–3 |
| [`docs/sourcing.md`](docs/sourcing.md) | What still needs buying |
| [`docs/references.md`](docs/references.md) | Upstream and prior art |
| [`docs/test-log.md`](docs/test-log.md) | What was actually measured |

## Family

This robot is one of several. The index, and everything true of more than one of them —
the printer, the compute pattern, the topic contract, micro-ROS — is in
[wk-robotics](https://github.com/WayneKennedy/wk-robotics). Facts that belong there are
linked, never copied.

## Licence

Tri-licence — hardware `CERN-OHL-S-2.0`, software `MIT`, docs `CC-BY-SA-4.0`.
See [`LICENSING.md`](LICENSING.md).
