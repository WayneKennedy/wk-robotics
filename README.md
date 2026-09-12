# wk-robotics

**The table of contents for my robotics and physical-AI work, and the home for
everything those projects have in common.**

Each robot lives in its own repository. This one holds three things they cannot
hold individually:

1. **The index** — what exists, what state it is in, where it lives (below).
2. **The shared substrate** — the printer, the actuators, the compute pattern and
   the conventions that recur across projects ([`docs/common.md`](docs/common.md)).
3. **The idea bench** — candidate future projects, before they earn a repo
   ([`docs/ideas.md`](docs/ideas.md)).

Nothing here duplicates a project repo. When a fact belongs to one robot it stays
in that robot's repo and this one links to it; when a fact is true of several, it
moves here and they link back.

## The projects

| Project | What it is | State | Repo |
|---|---|---|---|
| **koala-bot** | Self-balancing, knee-wheeled companion robot; first of a printable family | Design phase — CAD started, coupons printed; all V1 servos and drive hardware in hand, nothing assembled | [WayneKennedy/koala-bot](https://github.com/WayneKennedy/koala-bot) (public) |
| **wk-devastator** | Tracked ROS 2 robot on a DFRobot Devastator chassis; resurrection of a stalled build | Design record only — nothing built; motor question gates the rest | [WayneKennedy/wk-devastator](https://github.com/WayneKennedy/wk-devastator) (public) |
| **wk-hexapod** | ROS 2 autonomous hexapod on Freenove Big Hexapod hardware | Native ROS 2 stack verified end to end on the bench (2026-09-09): SLAM maps, Nav2 active, exploration sends goals; first battery run pending | [WayneKennedy/wk-hexapod](https://github.com/WayneKennedy/wk-hexapod) (public) |
| **SO-ARM101** | Standard Open Arm — LeRobot-compatible manipulator, built from the upstream design in its 12 V variant | Parts printed, servos being commissioned (2 of 6), nothing assembled | [WayneKennedy/wk-soarm101](https://github.com/WayneKennedy/wk-soarm101) (public) · upstream [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) |
| **wk-drone-bee35** | Aerial robot: 3.5" ducted cinewhoop on a SpeedyBee Bee35 Pro frame, built for position hold and endurance, not speed | Parts ordered 2026-09-11, nothing built. iNav first for a DJI-like hands-off loiter; ArduPilot and the mission-planning tier are a later evolution (its DEC-06) | [WayneKennedy/wk-drone-bee35](https://github.com/WayneKennedy/wk-drone-bee35) (public) |
| **3D printing** | Creality Ender-5 S1 on Klipper — the machine every printable part comes off | Commissioned and calibrated; in production use | [WayneKennedy/3d-printing](https://github.com/WayneKennedy/3d-printing) (private) |

Supporting: [`fn-hexapod`](https://github.com/WayneKennedy/fn-hexapod) — the
Freenove vendor code the hexapod's working reference servo/gait routines come from.

Longer per-project notes — hardware, what each one shares, where its documentation
starts — are in [`docs/projects.md`](docs/projects.md).

## What they have in common

The projects are not independent. They share a printer, an actuator family, a
compute split and a documentation standard; a lesson learned on one is usually
worth banking for all of them. That is [`docs/common.md`](docs/common.md).

The strongest threads today:

- **One printer, one set of profiles.** Every printable part on every project comes
  off the same Ender-5 S1.
- **One servo family.** Feetech STS-protocol bus servos drive both the SO-ARM101 and
  koala-bot's limbs — shared electrical bus, shared tooling, shared press-fit tolerances.
- **One compute pattern.** Raspberry Pi 5 for intent, a real-time MCU for reflex,
  ROS 2 as the contract between them.

## Documents

| File | Contents |
|---|---|
| [`docs/status.md`](docs/status.md) | Where things stand and what is in flight — **read this to pick work up** |
| [`docs/projects.md`](docs/projects.md) | Per-project detail: hardware, status, entry points |
| [`docs/common.md`](docs/common.md) | The shared substrate — printing, actuators, compute, power |
| [`docs/ideas.md`](docs/ideas.md) | Future project candidates and open discussion |
| [`AGENTS.md`](AGENTS.md) | Onboarding for any AI assistant or contributor — **start here** |

## For AI assistants

The onboarding is **provider-neutral**: [`AGENTS.md`](AGENTS.md) is the single entry
point, and the per-harness files (`CLAUDE.md`, `GEMINI.md`) do nothing but point at it.
This repository — and every project it indexes — is written to stand alone: a brand-new
assistant reading it cold should be able to do useful work without any prior session
history. Durable facts live in files, not in an assistant's private memory.

## Licence

Documentation, licensed [CC BY-SA 4.0](LICENSE). Each project repo carries its own
licensing; see [`docs/common.md`](docs/common.md#licensing) for the pattern they follow.
