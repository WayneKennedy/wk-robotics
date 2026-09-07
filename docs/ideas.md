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
  part number, separate spares pool, separate bus voltage — assume a fresh 14-servo order
  either way. What a 12 V build would cost is worked through under
  [stock or modified](#stock-or-modified--the-fork-that-must-be-decided-before-buying).
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

#### Stock or modified — the fork that must be decided before buying

Modifying the design toward the family pattern (12 V servos, a reflex MCU, ROS 2) is an
obvious temptation. The verified control-loop facts decide how much each modification
actually costs. All of the following were read from upstream on 2026-09-07.

**How the stock robot is actually controlled.** `rustypot_position_hwi.py` writes **goal
positions** over rustypot at 1 Mbaud, with **kp = 32, kd = 0** loaded into each servo's
internal loop. The policy runs at **50 Hz** (`ctrl_dt=0.02`, `sim_dt=0.002` in
`playground/open_duck_mini_v2/joystick.py`). The IMU is a **BNO055** on I²C, driven by
`adafruit_bno055` in `IMUPLUS_MODE` with an axis remap for upside-down mounting
(`mini_bdx_runtime/imu.py`) — **an IMU is already in the design; it is not a modification.**

**The training envelope, from `playground/common/randomize.py` and `joystick.py`:**

| Randomised at training | Range |
|---|---|
| Actuator **kp** | ×U(0.9, 1.1) — **±10 %** (narrowed from ±20 %; the old range is in the comment) |
| Action delay | 0–3 env steps = **0–60 ms** |
| IMU delay | 0–3 env steps = **0–60 ms** |
| Link masses | ×U(0.9, 1.1); torso additionally +U(−0.1, +0.1) kg |
| Torso CoM | +U(−0.05, +0.05) m |
| Armature / friction loss | ×U(1.0, 1.05) / ×U(0.9, 1.1) |
| Floor friction | U(0.5, 1.0) |

Training also hard-caps `max_motor_velocity = 5.24 rad/s` (**50 rpm**) with
`USE_MOTOR_SPEED_LIMITS = True`.

**What each modification therefore costs:**

- **Reflex MCU under the policy — cheap, and inside the envelope.** A serial hop is
  single-digit ms against a **0–60 ms** trained delay tolerance. But the MCU is *not*
  load-bearing here the way it is on koala-bot: a 50 Hz learned policy explicitly trained
  against randomised jitter is a different regime from a PID inverted pendulum, where
  [the two-tier rule](common.md#compute-the-two-tier-split) comes from. The real argument
  for it is family-level — it makes the duck a second consumer of koala-bot's reflex
  firmware and the [topic contract](common.md#the-topic-contract), which is exactly what
  [the shared ROS 2 package idea](#a-shared-ros-2-package-across-robots) currently lacks.
- **ROS 2 on the stock compute — tight.** The Pi Zero 2W has 512 MB RAM and is already
  running ONNX inference at 50 Hz. The plausible shapes are micro-ROS on the MCU with the
  Pi Zero as a thin agent, or ROS 2 offboard with the duck as a node. **Untested.**
- **BNO055 → BNO085 (the koala-bot part) — small but not a drop-in.** Different protocol
  (SH-2), so `imu.py` is rewritten against `adafruit_bno08x`. Saves the €40 BOM line and
  consolidates the family on one IMU.
- **12 V servos — three separate consequences, one of them serious.**
  1. *Mechanically fine.* SO-101 uses 7.4 V and 12 V STS3215 in common printed housings,
     so case and horn geometry carry over.
  2. *Electrically it forces a CAD change.* The duck is 2S; `common.md` fixes 3S as the
     ceiling for a 12 V STS3215. A third cell means a different holder and, almost
     certainly, a modified `battery_pack_lid` and body bay — plus a mass and CoM change.
     **Not yet checked against the CAD.**
  3. *Control is the real risk.* Whether a 12 V SKU at 12 V presents an effective
     stiffness within the **±10 %** kp envelope of a 7.4 V SKU at 7.4 V is **unverified** —
     it depends on how Feetech wound the 12 V variant, and the two SKUs' torque-speed
     curves have not been compared here. Outside that envelope, the shipped policies do
     not transfer. The 50 rpm speed cap is the benign direction (a faster servo is simply
     under-used). **Hypothesis, untested:** scaling the kp register down in proportion to
     supply voltage may bring the response back inside the envelope. The rigorous route is
     re-running [BAM](https://github.com/Rhoban/bam) on a 12 V unit, re-fitting the sim
     actuator model and re-training — which needs a GPU this workstation does not have.

**Recommendation (not a decision): buy the 7.4 V servos and build stock first.** The servo
order is the only part of this fork that is expensive to reverse, and €196 buys a
known-good baseline. Without one, a modified duck that will not walk cannot be diagnosed —
servo stiffness, added mass, MCU latency and a wiring fault all present identically. With
one, every modification is a measurable delta. Suggested order afterwards, cheapest and
most reversible first: **MCU + micro-ROS → IMU swap → 12 V / 3S conversion last**, since
only the last requires re-identification and re-training.

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
- **What would change this:** a third consumer. A modified
  [Open Duck Mini V2](#open-duck-mini-v2) running koala-bot's reflex firmware would be one.
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
