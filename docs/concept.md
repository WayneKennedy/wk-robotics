# Concept

What this arm is, what it is for, and how it relates to upstream and the rest of the family.

## What it is

**One build of the SO-101 follower arm** — the Standard Open Arm designed by
[The Robot Studio](https://www.therobotstudio.com) with Hugging Face for
[LeRobot](https://huggingface.co/docs/lerobot). Six degrees of freedom, six Feetech
STS3215 bus servos at 1/345 gearing, ~500 mm reach, ~500 g payload (upstream figures, not
measured here). The design is **not modified**: parts are printed from upstream's STLs and
assembled per upstream's guide (DEC-01).

The one variant choice is the **12 V servo** (DEC-02). Upstream's standard follower uses
7.4 V STS3215s (16.5 kg·cm); this build uses the 12 V ones (~30 kg·cm), which upstream
offers as the more powerful option and which the family already standardises on
([wk-robotics `common.md`](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#actuators)).
Consequence: a 12 V rail, not the 5 V supply in upstream's default BOM.

## What it is for

**Not yet decided** (owner, 2026-09-09) — see OQ-08. The arm is being built because the
design is good, cheap and LeRobot-native, and because the family's servo work needed a
real part to prove itself on. What it *does* once built is open. The candidates on the
table, none chosen:

- **A LeRobot arm** — imitation learning end to end on the platform the design is made
  for. Needs a leader or substitute (OQ-02) and a desk.
- **The manipulator on [wk-devastator](https://github.com/WayneKennedy/wk-devastator)**,
  driven by whatever drives the tank. Needs that robot's OQ-12 to close and an
  interface (OQ-06).
- **Both**, at different times — a desk arm that is occasionally mounted.

One thing it has already been, regardless: **the proving ground for the servo family.**
Every STS3215 fact the family relies on — press-fit tolerance in PLA+, bus adapter
behaviour, the configure-by-script procedure — was first established on this build's parts
and servos, and is banked in wk-robotics.

## Relation to upstream

Upstream is **cloned, not forked**, as `../SO-ARM100` beside this repo. It is the design
authority: geometry, BOM, assembly order, calibration guidance. This repo never restates
those; it records what upstream cannot know — which physical servo carries which ID, which
printed copy of a part is the usable one, what this build measured and decided.

If this build ever needs a part upstream does not have — a mount for the devastator, say —
it is designed here under the hardware licence and, if generally useful, offered upstream.

## Relation to the family

| Fact class | Lives in |
|---|---|
| The design | upstream `SO-ARM100` |
| STS3215 electrical, bus adapters, how to configure a servo, power integrity | [wk-robotics `common.md`](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md) |
| Print jobs, slicer profiles, machine state | the family's private `3d-printing` repo |
| Which parts exist and are usable, servo IDs, decisions, measurements | **here** |
| The mobile base and whether it can carry the arm | [wk-devastator](https://github.com/WayneKennedy/wk-devastator) |
