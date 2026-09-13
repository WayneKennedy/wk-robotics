# Concept

What this robot is, what it is for, and why it is being built a second time.

## What it is

A **tracked, skid-steer, statically stable mobile robot** on a purchased DFRobot
Devastator chassis, carrying a reflex/intent compute stack and speaking the family's
ROS 2 topic contract.

It is deliberately the **simplest body in the family**. No balance loop, no gait, no
closed kinematic chains, and no manipulator *of its own design* — the arm it is meant to
carry is an upstream project mounted as payload (below). A differential-drive base
publishes `/cmd_vel` and consumes it continuously, with nothing to integrate and nothing
to keep upright.

## What it is for

Four things. The first is what sent the kit looking for a use; the rest are in order of
how much they justify the work.

1. **It is a mobile base for the SO-ARM101.** (Owner, 2026-09-07.) The
   [Standard Open Arm](https://github.com/TheRobotStudio/SO-ARM100) is
   [already being printed](../../../docs/projects.md#so-arm101)
   as a family project and has no base. Arm on a driving chassis is **mobile
   manipulation** — the one capability neither the hexapod nor koala-bot is aimed at, and
   the reason this chassis was dug out rather than left in its box.
   **Feasibility is not established:** the arm's **~500 mm reach against a 225 mm
   chassis** is a tipping problem before it is a payload problem. See
   [OQ-12](open-questions.md), and [`roadmap.md`](roadmap.md) milestone 5 — nothing is
   mounted before milestone 1 exits.

2. **It is the cheapest second consumer of the family's ROS 2 stack.** The hexapod's
   SLAM and Nav2 work is
   [portable in principle and not in practice](../../../docs/ideas.md#a-shared-ros-2-package-across-robots).
   A second body that speaks the same contract is what turns that from an assertion
   into a test — and a tracked base is the easiest body Nav2 will ever drive.
3. **It is the first node of a fleet.** The
   [hive-mind direction](../../../docs/ideas.md#physical-ai-and-the-hive-mind)
   needs two bodies on one contract before any of its interesting problems — map
   merging, shared world model, graceful degradation — can even be posed. This robot
   plus the hexapod is the minimum viable fleet.
4. **It is already paid for.** The chassis is a high-quality aluminium platform that sat
   in a box, assembled, doing nothing.

**What it is not for:** it teaches nothing about balance (koala-bot's job) and nothing
about learned locomotion, and it **designs no manipulator** — the arm is upstream's. What
this robot contributes to manipulation is *mobility under it*. The body stays the simplest
in the family and the robot stays a *systems* robot rather than a *capability* one; that
is still the point.

## The first build, and why it stopped

**Recorded from the owner's account, 2026-09-07.** The robot was bought and part-built,
then abandoned. It **petered out on battery limitations and over-ambitious scope**: both
Intel RealSense cameras and a Raspberry Pi 4 were mounted on top, and the final wiring
and programming were never completed. It never ran.

The arithmetic supports that account and sharpens it:

| Load | Draw |
|---|---|
| Raspberry Pi 4 under load | ~5–7 W |
| RealSense depth camera × 2 | ~2–3.5 W each |
| Two 6 V motors at a modest 1 A each | ~12 W (**2.3 A stall apiece**) |
| **Total demand** | **~25–30 W** |

That was asked of a small battery, through an
[L298N](hardware.md#as-found-inventory) giving away roughly **2 V of a 6 V rail** —
a third of the supply lost to the driver before the motors saw any of it.

**It was under-powered by design, not abandoned for lack of interest.** That distinction
is the most useful thing this repository records, because it says what the resurrection
must do differently.

**A plausible second cause, unverified:** two RealSense D4xx share a single USB 3 host
controller on a Pi 4, which is a known bandwidth conflict. This may be why final
bring-up never succeeded even where power allowed. Which two camera models were fitted
is **unrecorded**.

## What the resurrection does differently

- **Keep the chassis, replace everything else.** The mechanical platform is the good
  part and the reason to resurrect rather than start over.
- **Milestone 1 carries no perception at all** — see [`roadmap.md`](roadmap.md). A
  complete, teleoperable robot with closed-loop wheel velocity and real odometry comes
  before a single camera is mounted. This directly inverts the failure mode above.
- **The power budget is computed before parts are bought**, not discovered afterwards.
  The family's [power-integrity rules](../../../docs/common.md#power-integrity)
  were themselves banked from an earlier build stalling on the same class of problem.
- **Modern and standard over bespoke.** micro-ROS rather than a hand-rolled serial
  protocol; the family's topic contract rather than a private vocabulary.

## Design principles

- **Simplest body, hardest systems.** Complexity belongs in the software and the fleet
  architecture, not the mechanism.
- **Each tier survives the loss of the tier above it.** Non-negotiable; see
  [`architecture.md`](architecture.md).
- **Nothing is mounted until the tier below it works.**
