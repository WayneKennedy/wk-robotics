# wk-soarm101 🦾

**A 12 V SO-101 follower arm, built from the upstream design.** The Standard Open Arm by
The Robot Studio and Hugging Face, printed and commissioned here, with nothing changed
in the design. This repo is the build record; the design lives upstream.

**Status:** parts printed, servos being commissioned, nothing assembled. Two of six
servos carry their IDs (`shoulder_pan` 1, `shoulder_lift` 2, verified on one bus
2026-09-09). The remaining four are not yet sourced. See
[`docs/roadmap.md`](docs/roadmap.md) for direction, [`docs/decisions.md`](docs/decisions.md)
for what is settled, and [`docs/open-questions.md`](docs/open-questions.md) for what is not.

## What it is

The **SO-101 follower**: 6 degrees of freedom, six Feetech STS3215 bus servos at 1/345
gearing, ~500 mm reach, designed for imitation learning with
[LeRobot](https://huggingface.co/docs/lerobot). This build uses the **12 V** servo
variant (~30 kg·cm) rather than the standard 7.4 V one, so it needs a 12 V rail.

- Design, STLs and bill of materials: [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100), cloned as a sibling, never forked.
- Parts printed in white eSUN PLA+ on the family's Ender-5 S1.
- Servo bus driven by a Waveshare Bus Servo Adapter (A), the upstream BOM part.
- **Purpose and runtime controller not yet decided** (OQ-08, OQ-09): a desk LeRobot arm, the manipulator on [wk-devastator](https://github.com/WayneKennedy/wk-devastator), or both in turn.

## Why a repo, when upstream has one

Upstream answers *what an SO-101 is*. It cannot answer which of these servos is ID 3,
whether the wrist part off the printer was usable, or why this build runs at 12 V. Those
facts need a home that is not a chat transcript and not a private print log.

## Documents

| File | Contents |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Onboarding for any AI assistant or contributor — **start here** |
| [`docs/concept.md`](docs/concept.md) | What it is, what it is for, relation to upstream |
| [`docs/hardware.md`](docs/hardware.md) | Printed parts and their state; electronics in hand |
| [`docs/servos.md`](docs/servos.md) | The servo map — IDs, joints, how they were set |
| [`docs/decisions.md`](docs/decisions.md) | Banked decisions — the durable *why* |
| [`docs/open-questions.md`](docs/open-questions.md) | Unresolved. Never state these as settled |
| [`docs/roadmap.md`](docs/roadmap.md) | Print → commission → assemble → calibrate → teleoperate → mount |
| [`docs/sourcing.md`](docs/sourcing.md) | In hand versus still needed |
| [`docs/references.md`](docs/references.md) | Upstream, LeRobot, vendor documentation |
| [`docs/test-log.md`](docs/test-log.md) | What was actually measured |

## Family

This arm is one of several robots. The index, and everything true of more than one of
them — the printer, the STS3215 servo family and how to configure one, the bus adapters,
power — is in [wk-robotics](https://github.com/WayneKennedy/wk-robotics). Facts that
belong there are linked, never copied.

## Licence

Tri-licence — hardware `CERN-OHL-S-2.0`, software `MIT`, docs `CC-BY-SA-4.0`.
See [`LICENSING.md`](LICENSING.md). The arm design itself is upstream's, Apache-2.0,
and is not carried in this repository.
