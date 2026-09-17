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
- **New use (2026-09-09, candidate):** its existing torso is the obvious mount if the
  SO-ARM101 pair is ever tried as humanoid shoulders — see
  [wk-soarm101 OQ-08](../projects/soarm101/docs/open-questions.md).

### A printed hexapod

Raised by the owner on 2026-09-09 while deciding not to modify the Freenove kit's power
path (`wk-hexapod` OQ-14): any significant deviation from Freenove's design — a USB-C PD
power path that charges with the servos live, or anything else structural — would be a
new, printed hexapod rather than a change to that robot.

- **Reuses:** everything above the hardware in `wk-hexapod` — controller, SLAM, Nav2,
  autonomy — which is written against the topic contract and a servo-angle interface, not
  the kit; the printer; plausibly the STS servo family, which would add position feedback
  the kit's hobby servos lack.
- **Unresolved:** everything mechanical and electrical, and whether it would carry a
  reflex tier (the kit does not — `wk-hexapod` OQ-09).
- **Not committed.** A thought recorded so it is not lost.

### A pure balance bot

Raised by the owner on 2026-09-11, when a second pair of 37D motors arrived that
koala-bot no longer needs: they were bought for its four-wheel V1 (DEC-38) and DEC-43
cancelled the front drives before they shipped. A two-wheeled inverted pendulum and
nothing else — the balance loop koala-bot depends on, isolated from its limbs, head and
CAD.

- **Reuses:** the surplus 37D pair and the spare Dual TB9051FTG —
  held as unallocated stock in [wk-inventory `docs/stock.md`](https://github.com/WayneKennedy/wk-inventory/blob/main/docs/stock.md); the family rule
  that [the balance loop lives on the MCU](common.md#compute-the-two-tier-split) and
  koala-bot's reflex-tier design; the printer for the chassis.
- **Unresolved:** everything except the motors and driver — IMU, wheels and hubs
  (koala-bot's one Ø80 pair is committed to its ankles), battery, form. An unallocated
  Teensy 4.1 NE is in the same pool and would fit; it is not earmarked for this. Whether it is a
  standalone project or koala-bot's balance-loop testbed is the question that decides
  where its repo and docs go; the firmware would plausibly be the same loop either way.
- **Not committed.** Surplus hardware looking for a job, recorded so the parts are not
  lost.

### SpotMicro · Annin Robotics AR4

Named as later personal builds in `koala-bot/docs/backlog.md`. Nothing decided.

**Quadruped leg layouts, noted 2026-09-14** while comparing the original SpotMicro
([KDY0523, Thingiverse thing:3445283](https://www.thingiverse.com/thing:3445283), 12 ×
MG996R) with Orion, the read-only clone recorded in
[`status.md`](status.md#orion-quadruped-upstream-clone--purpose-not-yet-recorded):

- **SpotMicro** carries the knee servo in the upper leg and drives the shin directly off
  its horn (per the SpotMicroAI assembly guide for the same frame). Distal mass moves
  with every step.
- **Orion** co-locates the femur and tibia servos at the shoulder: the femur sits on one
  horn, the other drives a bellcrank and a long link down to the knee (`Bellcrank`,
  `Linkage_Long`, `Linkage_Short` in its `models/`). Its firmware IK (`LegIK.c`) has to
  add the femur angle back into the tibia servo command because of that coupling. The
  leg below the shoulder is passive printed parts and bearings only.

Relevance to koala-bot: its V1 rear knees are active with the STS3215 at the knee
(koala-bot DEC-31), and its own sizing notes already flag distal mass as the cost.
A shoulder-mounted knee servo with a link is the alternative; it is a closed loop, so
[CAD motion study, not URDF](common.md#modelling-and-simulation). Not a V1 change —
recorded so it is not re-derived.

---

## Externally designed builds

Existing open designs worth building as-is, rather than projects to design. The value is
inverted from the rest of this page: the mechanics are settled, so what is unresolved is
what the build *teaches* and what it costs to run alongside the others.

### Open Duck Mini V2

> **Parked 2026-09-07, the day it was raised.** Considered as a pivot away from koala-bot
> and rejected as one: koala-bot remains the active design project. Not a judgement on the
> design — everything below was verified and still holds. This is a *when*, not a *whether*.

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

**Reuses:** the printer; the Feetech STS bus protocol, bus-adapter tooling, servo press-fit
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
- **Training is now possible locally** — see [the GPU workstation](common.md#the-gpu-workstation),
  established 2026-09-07. The shipped ONNX policies need no GPU at all; training a new one
  (upstream's headline run is 300 M timesteps) is a job for that machine, subject to the
  Blackwell toolchain constraint recorded there.
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
     actuator model and re-training — a job for [the GPU workstation](common.md#the-gpu-workstation).

**Recommendation (not a decision): buy the 7.4 V servos and build stock first.** The servo
order is the only part of this fork that is expensive to reverse, and €196 buys a
known-good baseline. Without one, a modified duck that will not walk cannot be diagnosed —
servo stiffness, added mass, MCU latency and a wiring fault all present identically. With
one, every modification is a measurable delta. Suggested order afterwards, cheapest and
most reversible first: **MCU + micro-ROS → IMU swap → 12 V / 3S conversion last**, since
only the last requires re-identification and re-training.

**If it is ever picked up**, start from the recommendation above — 7.4 V servos, stock
build first — rather than re-deriving it. The two open technical questions are the 12 V
kp envelope and whether a 3S pack fits the battery bay; both are cheap to close and
neither has been.

---

## Open directions

Threads worth pulling that are not yet attached to a specific build.

### Physical AI and the hive mind

**The stated direction of the work (owner, 2026-09-07): understand *Physical AI* by doing
it, aiming at a "hive mind" — a central mission-planning and reasoning machine, with
remote physical agents that extend its area of awareness.** This is an aspiration, not a plan;
nothing on this page is committed. It is recorded here because it reframes what the other
projects are *for*, and that is a fact about the work even when the build is not decided.

**It is a third tier on the existing architecture, not a new one.** The tier table in
[`common.md`](common.md#compute-the-two-tier-split) already separates reflex (MCU,
~1 kHz, deterministic) from intent (on-robot Pi, ROS 2). **Mission Planning** is a third
band above those, operating in seconds, and it is the only tier that is aspirational
rather than decided.

**The load-bearing rule is the same one, extended: each tier must stay useful when the
tier above it is unreachable.** A robot whose link to the mission planner drops degrades
to autonomous; it does not stop. A fleet that dies when the network hiccups is the failure
mode this rule exists to prevent.

Smart sensors — cameras that compute depth or run a detector on-board — are **not a
fourth tier**; they are a placement choice inside the intent tier. See
[Perception placement](common.md#perception-placement).

**What the problem actually consists of**, in rough order of difficulty:

- **Share a world model, not sensor streams.** Raw depth from several robots will not
  cross a LAN — a constraint already met at single-robot scale on
  [the tank](projects.md#devastator). Each robot runs its own SLAM and perception; the
  core receives poses, semantic observations and map fragments. "Extending the area of
  awareness" is a **map-merge** problem, not a streaming one.
- **Map merging is the hard part.** Each robot's `map` frame is arbitrary until something
  aligns them, and robots that have never seen the same place share no frame at all. The
  tractable versions are a shared known origin or fiducials at surveyed positions; the
  general case is a research problem.
- **Time sync is the prerequisite nobody enjoys.** Fusing observations across robots needs
  a common clock — `chrony` across the fleet at minimum.
- **DDS does not travel.** ROS 2 discovery is multicast and works on one LAN segment; it
  degrades across WiFi, subnets and overlay networks. The current answer for multi-robot
  and wide-area ROS 2 is **Zenoh** (`rmw_zenoh`, or `zenoh-bridge-ros2dds` alongside
  existing DDS). Worth knowing before designing around plain DDS.

**The mission planner has a candidate machine** (2026-09-07): [the GPU
workstation](common.md#the-gpu-workstation) — 16 GB Blackwell, Docker present, reachable
over the private overlay network. It is a good fit for the reasoning tier and for RL
training both, but the two roles have different demands and only one is hard:

- **Training is batch and offline.** It cares about the GPU and nothing else. Settled.
- **Mission Planning is a live service**, and this machine is a **desktop** — powered off or
  busy when it is being used for something else. That is not a blocker; it is a direct
  argument for the tier rule above. A fleet whose robots stall when the desktop sleeps has
  the architecture wrong. **The Mission Planning tier must be treated as optional from day
  one**, and this hardware choice guarantees it gets tested.
- **Its networking is the real constraint.** The WSL2 instance is **NAT'd, not mirrored**,
  so the LAN cannot open connections into it; it is reachable only over the overlay
  network. Unicast is therefore fine, but **DDS multicast discovery will not cross that
  boundary** — the concrete instance of the "DDS does not travel" problem above.
  **Zenoh** is the answer (`zenoh-bridge-ros2dds`, or `rmw_zenoh`), not a WSL networking
  workaround. **Undecided but strongly indicated.**

**What this implies for sequencing.** A hive needs **two bodies speaking one contract**,
and there is currently one partly-working robot. So this direction is the *motivation* for
[a shared ROS 2 package](#a-shared-ros-2-package-across-robots), which is argued down
elsewhere on this page as premature — the argument changes if the fleet is the goal rather
than a by-product. The cheapest second node is [the tank](projects.md#devastator):
already owned, and a differential-drive base is the easiest body Nav2 will ever drive.
koala-bot and the duck are **capability** projects (balance, learned locomotion) rather
than fleet projects, and do not shorten this path.

**Note on the term.** *Physical AI* is a current industry label for systems that perceive
and act in the world through learned policies rather than hand-written control. Two
entry points already exist on this page: [the duck](#open-duck-mini-v2) for RL sim-to-real
locomotion, and [LeRobot](#lerobot-and-learned-manipulation) for learned manipulation on
the SO-ARM101. The hive mind is the systems layer above both, not a substitute for either.

### Roving eyes: a whoop fleet

**Unbuilt. Raised 2026-09-13 (owner) as an aspiration, not a plan.** A fleet of tiny
whoops sent out as roving eyes for a ground-based mission planner: the **off-board
topology** in [`common.md`](common.md#aircraft-and-the-tiers), reflex on each airframe,
intent on the ground, the two linked by radio rather than wire. Nothing is bought,
designed or scheduled, and no aircraft in [wk-drones](https://github.com/WayneKennedy/wk-drones)
is earmarked for it.

What it depends on, none of it settled:

- **Two-way MAVLink on a whoop-sized flight controller**, which means ArduPilot. Whether
  ArduPilot runs on the all-in-one boards used in 65–75 mm whoops is **unverified**; the
  working assumption is that most are small-flash F4 parts targeted only by Betaflight,
  which would push the smallest viable roving eye up towards a 3.5" airframe. Check this
  before anything else.
- **The radio link.** ELRS MAVLink mode gives roughly 2.4 KB/s down and 1.2 KB/s up per
  link at the fastest packet rate (ELRS docs, via
  [Bee35 OQ-02](https://github.com/WayneKennedy/wk-drones/blob/main/aircraft/bee35/docs/open-questions.md)),
  shared with RC; a fleet multiplies that across transmitters or telemetry radios.
- **Position sensing without GPS indoors**, and a planner that treats each aircraft as
  something that flies itself and accepts tasking, never as something it steers.

Earns a folder in wk-drones when an airframe is chosen; earns a row in the index here
when one has flown under ground-station command.

### A shared ROS 2 package across robots

The [topic contract](common.md#the-topic-contract) is currently a convention held in
prose. It could be a package — message definitions, a URDF library, common launch
patterns — that every robot depends on rather than reimplements.

- **Argument for:** the hexapod's navigation stack is portable in principle today and not
  in practice; a shared package is what would close that gap.
- **Argument against:** two robots is a thin basis for an abstraction, and koala-bot's
  ROS 2 layer is not written yet. Premature.
- **What would change this:** a third consumer. The
  [Devastator tank](projects.md#devastator) is the strongest candidate — already owned,
  and a differential-drive base speaks `/cmd_vel` natively with no gait or balance loop in
  the way. A modified [Open Duck Mini V2](#open-duck-mini-v2) running koala-bot's reflex
  firmware would be another, at considerably more effort.
- **What reframes it entirely:** [the hive mind](#physical-ai-and-the-hive-mind). If a
  fleet is the goal rather than a by-product, a shared contract is the point of the work,
  not an extraction from it.
- **Unresolved:** whether to wait for koala-bot's stack to exist before extracting anything.

### LeRobot and learned manipulation

The SO-ARM101 build has its own folder, `projects/soarm101/`, and the question of what it is *for* lives there as
[wk-soarm101 OQ-08](../projects/soarm101/docs/open-questions.md)
— LeRobot first (its DEC-08), then a two-arm handover, humanoid shoulders, or the tank's
manipulator. Not restated here. What remains a *family* question is the one above under
[Physical AI and the hive mind](#physical-ai-and-the-hive-mind): how a learned component
from that arm gets into the mobile robots.

---

## Adding an idea

Append a section under the right heading. If the idea is a deferred feature of an existing
robot, it belongs in that repo's `backlog.md` instead — only put it here if it is a
plausible project in its own right.
