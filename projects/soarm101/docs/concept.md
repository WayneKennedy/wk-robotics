# Concept

What this arm is, what it is for, and how it relates to upstream and the rest of the family.

## What it is

**One build of the SO-101 follower arm** — the Standard Open Arm designed by
[The Robot Studio](https://www.therobotstudio.com) with Hugging Face for
[LeRobot](https://huggingface.co/docs/lerobot). Six degrees of freedom, six Feetech
STS3215 bus servos at 1/345 gearing, ~500 mm reach, ~500 g payload (upstream figures, not
measured here). The **commissioned arm is not modified**: parts are printed from upstream's STLs and
assembled per upstream's guide (DEC-01).

The one variant choice is the **12 V servo** (DEC-02). Upstream's standard follower uses
7.4 V STS3215s (16.5 kg·cm); this build uses the 12 V ones (~30 kg·cm), which upstream
offers as the more powerful option and which the family already standardises on
([wk-robotics `common.md`](../../../docs/common.md#actuators)).
Consequence: a 12 V rail, not the 5 V supply in upstream's default BOM.

## What it is for

**First, what it was designed for:** imitation learning with LeRobot — a leader arm
teleoperates the follower, demonstrations are recorded with cameras, a policy is trained on
the family's GPU workstation, and the follower runs it. DEC-08 set out to explore that first;
**DEC-14 (2026-09-14) ended it at calibration** — with no leader arm (DEC-13) there was little
more to learn from it. **What it is for is now decided in outline (DEC-15): the cooperating
pair below**, coordinated by planning against each other's hit boxes rather than by a learned
policy. The candidates as they stood, kept for the record:

- **A LeRobot arm** — imitation learning end to end on the platform the design is made
  for. Needs a leader or substitute (OQ-02) and a desk.
- **The manipulator on [wk-devastator](../../../projects/devastator/README.md)**,
  driven by whatever drives the tank. Needs that robot's OQ-12 to close and an
  interface (OQ-06).
- **Both**, at different times — a desk arm that is occasionally mounted.
- **One of a cooperating pair** — a second follower is likely to be printed, and the two
  used to reproduce an industrial two-arm handover (one arm places a pallet where the
  other picks it up) at desk scale, solved with learned policies. The leading candidate as
  of 2026-09-09; detail and what already exists for it under OQ-08.
- **Shoulders on a humanoid torso** — the same pair mounted on a body rather than a
  bench, as upstream's XLeRobot does over a mobile base and as the family's shelved
  InMoov torso might allow. Same hardware as the pair above in a different frame; OQ-08.

One thing it has already been, regardless: **the proving ground for the servo family.**
Every STS3215 fact the family relies on — press-fit tolerance in PLA+, bus adapter
behaviour, the configure-by-script procedure — was first established on this build's parts
and servos, and is banked in wk-robotics.

## Relation to upstream

Upstream is **cloned, not forked**, as `../SO-ARM100` beside this repo. It is the design
authority for baseline geometry, BOM, assembly order and calibration guidance. This
folder records what upstream cannot know — which physical servo carries which ID, which
printed copy of a part is the usable one, what this build measured and decided.

If this build ever needs a part upstream does not have — a mount for the devastator, say —
it is designed here under the hardware licence and, if generally useful, offered upstream.

**2026-09-21 — owner-requested lightweight investigation:** local derived CAD is now
carried in [`cad/lightweight-v1/`](../cad/lightweight-v1/README.md), with upstream
attribution and Apache-2.0 retained. This is a prototype study, not an adopted change
to the assembled arm. Its scope, rejected variants and remaining validation are in the
[report](../cad/lightweight-v1/report.md); adoption remains OQ-19.

## Relation to the family

| Fact class | Lives in |
|---|---|
| Baseline design | upstream `SO-ARM100` |
| Local prototype geometry and its analysis | [`cad/lightweight-v1/`](../cad/lightweight-v1/README.md) |
| STS3215 electrical, bus adapters, how to configure a servo, power integrity | [wk-robotics `common.md`](../../../docs/common.md) |
| Print jobs, slicer profiles, machine state | the family's private `3d-printing` repo |
| Which parts exist and are usable, servo IDs, decisions, measurements | **here** |
| The mobile base and whether it can carry the arm | [wk-devastator](../../../projects/devastator/README.md) |
