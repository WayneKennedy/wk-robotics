# Idea bench

Projects and directions that do not have a repository yet. This is the discussion home
for "what next" — a place to think in the open before committing scope.

**Nothing on this page is committed.** An item here is a candidate, not a plan. When one
earns a repo it moves out: into the index in [`README.md`](../README.md) and a section in
[`projects.md`](projects.md).

## How to use this page

Each candidate gets: what it is, why it is interesting, what it would reuse from the
[shared substrate](common.md), and what is unresolved about it. Keep the last one
honest — the interesting part of an unbuilt project is what you do not yet know.

---

## Carried over from project backlogs

These are recorded in a project repo as deferred, and are listed here because they are
plausible *separate* projects rather than features of an existing one.

### Climbing sibling to Koala

A second member of the koala-bot family: all-gripper limbs, no wheels. Hybrid actuation —
passive-latch hang at near-zero energy, ballistic brachiation (declutch to swing, re-engage
as a brake), and a central winch with tendons to haul the body up. The biomimetic
principle is *spend energy only on transitions — grip, pull, release — and coast the rest*.

- **Reuses:** the koala-bot shared brain and topic contract; the STS servo family; the printer.
- **Unresolved:** everything mechanical. Gripper design, clutch mechanism, and whether the
  winch is central or per-limb.
- **Source:** `koala-bot/docs/backlog.md`. Deferred under koala-bot's scope discipline —
  finish V1 end-to-end before the family.

### InMoov resurrection

An existing ~80 %-built InMoov — head, neck and shoulders, with an upstream-contributed
Pi-camera eye mod — to be brought up on a Pi 5 brain with modern Mega + PCA9685
electronics, on a powered-wheelchair base.

- **Reuses:** the Pi 5 intent tier; the power-integrity lessons, which came from this build
  in the first place.
- **Unresolved:** whether upstream inactivity since 2024 makes this a maintenance burden
  rather than a shortcut.
- **Currently:** shelved as inspiration. A good future testbed for parallel mechanisms, an
  AI brain, and electronics lessons at humanoid scale.

### SpotMicro · Annin Robotics AR4

Named as later personal builds in `koala-bot/docs/backlog.md`. Nothing decided.

---

## Externally designed builds

Existing open designs worth building as-is, rather than projects to design. The value is
inverted from the rest of this page: the mechanics are settled, so what is unresolved is
what the build *teaches* and what it costs to run alongside the others.

### Open Duck Mini V2

**A ~42 cm bipedal BDX-droid replica that walks from a reinforcement-learned policy.**
Upstream is [`apirrone/Open_Duck_Mini`](https://github.com/apirrone/Open_Duck_Mini),
Apache-2.0, default branch **`v2`** — 3,988 stars, 510 forks (checked 2026-09-07). The
[tnkr.ai guide](https://tnkr.ai/explore/docs/open-duck-mini/open-duck-mini-v2#home) is a
build front-end for the same design and sells an assembled kit at **$600**; the
authoritative source is the repo.

| | |
|---|---|
| Actuation | **14 × Feetech STS3215, 7.4 V** on a Waveshare bus-servo board · 2 × 9 g PWM servos (antennas) |
| Compute | Raspberry Pi Zero 2W — ONNX policy inference on-board, **no reflex MCU, no ROS 2** |
| Sensing | BNO055 IMU · 4 × SS-10 foot contact switches |
| Power | 2 × 18650 in 2S, BMS + 5 V regulator, USB-C charger |
| Printing | 36 distinct STLs / **51 pieces** — PLA at 15 % infill, except `foot_bottom_tpu.stl` ×2 in **TPU at 40 %** |
| Cost | **€398** base BOM, **€432** with the expression pack (LEDs, speaker, mic, Pi camera) |
| Licence | Apache-2.0 |

**Software stack** — four upstream repos: the hub (CAD links, print and assembly guides,
BOM); [`Open_Duck_Playground`](https://github.com/apirrone/Open_Duck_Playground) for
training in MuJoCo Playground (MJX/JAX);
[`Open_Duck_reference_motion_generator`](https://github.com/apirrone/Open_Duck_reference_motion_generator)
(Placo) for the imitation-reward reference motions; and
[`Open_Duck_Mini_Runtime`](https://github.com/apirrone/Open_Duck_Mini_Runtime) on the Pi.
Actuator identification uses Rhoban's [BAM](https://github.com/Rhoban/bam). **Two
pretrained walk policies are committed to the hub repo** (`BEST_WALK_ONNX.onnx`,
`BEST_WALK_ONNX_2.onnx`), so a correct build walks without training anything.

**Why it is interesting:** it is the only candidate on this page that delivers
**RL sim-to-real** — a learned locomotion policy, trained in simulation and transferred to
hardware. No current project does this: the hexapod is analytic IK, koala-bot's balance
loop is classical PID on an MCU, the arm is teleoperated. It is also a *finished* design,
so the work is assembly and bring-up rather than a second from-scratch mechanical project.

**Reuses:** the printer; the Feetech STS bus protocol, FE-URT-1 tooling, servo press-fit
and bracket knowledge from [`common.md`](common.md#actuators). That is the extent of it —
see below.

**Unresolved / what it does not give you:**

- **The servo overlap is family-level, not part-level.** The duck is the **7.4 V**
  STS3215 on a 2S pack; koala-bot and SO-ARM101 use the **12 V** variant on 3S. Separate
  part number, separate spares pool, separate bus voltage. Whether a 12 V unit can serve
  at 7.4 V is **unverified**, and the shipped policies were identified (BAM) against 7.4 V
  actuator dynamics — assume a fresh 14-servo order.
- **TPU is unproven on the Ender-5 S1.** The validated material set is PETG and PLA+
  ([`common.md`](common.md#materials-in-use)). Two foot-sole parts need TPU. Test print
  before committing.
- **No NVIDIA GPU on the workstation** (`nvidia-smi` absent, 2026-09-07). The shipped ONNX
  policies run without a GPU; training a new one needs a cloud GPU — upstream's headline
  run is 300 M timesteps.
- **It breaks the two-tier compute rule.** Policy inference runs on the Pi Zero 2W with no
  real-time MCU beneath it — a second counter-example alongside the hexapod, and a
  different regime again (a learned policy at low rate, not a PID inverted pendulum). What
  that implies for [the two-tier split](common.md#compute-the-two-tier-split) is an open
  question, not a settled exception.
- **No ROS 2 anywhere in the stack**, so nothing joins the
  [topic contract](common.md#the-topic-contract) without being written.
- **Upstream cadence.** Hub repo last pushed **2026-01-31**; the runtime to
  **2026-07-23**. Since July the maintainer's public work is a `microduck_*` family
  (Rust, v1/v1.5 assets) whose runtime repo is **not public**. Read as *design finished
  and stable* — kits are still sold — rather than actively maintained; do not plan on
  upstream fixes.
- **Part sizes have not been checked** against koala-bot's ≤ 200 × 200 mm design rule.

**Whether to build it is open** — see the pivot thread in [`status.md`](status.md).

---

## Open directions

Threads worth pulling that are not yet attached to a specific build.

### A shared ROS 2 package across robots

The [topic contract](common.md#the-topic-contract) is currently a convention held in
prose. It could be a package — message definitions, a URDF library, common launch
patterns — that every robot depends on rather than reimplements.

- **Argument for:** the hexapod's navigation stack is portable in principle today and not
  in practice; a shared package is what would close that gap.
- **Argument against:** two robots is a thin basis for an abstraction, and koala-bot's
  ROS 2 layer is not written yet. Premature.
- **Unresolved:** whether to wait for koala-bot's stack to exist before extracting anything.

### LeRobot and learned manipulation

The SO-ARM101 exists to work with LeRobot. Once the follower arm is built, the question is
what it is *for* — teleoperated data collection, a learned policy, or a testbed for
putting a learned component into one of the mobile robots.

- **Unresolved:** everything downstream of "build the arm". Worth revisiting once it moves.

---

## Adding an idea

Append a section under the right heading. If the idea is a deferred feature of an existing
robot, it belongs in that repo's `backlog.md` instead — only put it here if it is a
plausible project in its own right.
