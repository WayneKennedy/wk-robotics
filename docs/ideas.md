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
Reinforced 2026-09-18: the kit cannot take ST3215s (standard-size PWM hobby servos, lugged
at each end, driven from a PWM board on the GPIO riser), and the owner judges a new custom
design more feasible than remaking it ([`status.md`](status.md)).

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

### A two-armed wheeled torso — the Orin ground robot

**Raised by the owner 2026-09-18** as the direction for the Jetson Orin Nano + D435i
pair ([`status.md`](status.md)). Agreed in principle; **no name, no repo, nothing
decided beyond the shape.** It is [XLeRobot](https://github.com/Vector-Wangel/XLeRobot)'s
idea — LeKiwi base, two SO-101 arms, a head — with three owner-set departures:

- **A printed humanoid torso, not a cart.** The IKEA-cart body is ruled out outright.
- **The arms hang vertically from shoulders**, not mounted flat as two table-top SO-ARMs.
  **Demonstrated 2026-09-18, by accident:** the owner's SO-ARM101 is stored clamped by its
  base plate against a vertical surface, arm hanging, gripper reaching down into a box
  below — the proposed alignment. So the mount is a *wall mount*: the base flange on a
  vertical torso face at shoulder height with **joint 1's axis horizontal**. The pan
  servo becomes the shoulder's first degree of freedom, swinging the arm in the plane of
  the face it is mounted on, and it carries a gravity moment whenever the arm leaves
  vertical — a load the table-mounted arm never puts on that joint (first assistant
  reading of the photo, 2026-09-18, said inverted with joint 1 vertical; owner
  corrected it). The lift servo then raises the arm out of that plane. The rest pose is
  a hanging pendulum, stable, and the workspace is below and in front of the shoulder —
  the floor-level workspace task 1 needs. Which torso face (front: pan = abduction;
  side: pan = flexion) is open. LeRobot's calibration is per-joint and
  orientation-agnostic, but any learned policy is specific to this mounting. **Numbers from the
  URDF (2026-09-18, [SO-ARM101 `hardware.md`](../projects/soarm101/docs/hardware.md#dimensions-and-masses-from-the-urdf)):**
  hanging length shoulder-lift axis to fingertip **461 mm** (to tool point 411 mm), so the
  shoulder-lift axis sits at about **0.5 m** above the floor for a fingertip that just
  reaches it, and the pan/base flange some 65 mm above and behind that. Arm mass beyond
  the pan joint 485 g. Gravity moment about the horizontal pan axis with the arm swung
  out straight and horizontal: **1.12 N·m unloaded (38 % of the servo's 2.94 N·m)**, and
  3.1 N·m with upstream's 500 g payload at the tool point — over the rating, so the arm
  may not carry a full payload swung out horizontally in the pan plane; task 1 lifts
  below the shoulder, where the moment is far smaller. The shoulder-lift joint's moment
  (0.84 N·m unloaded) is the same as on a table.
  koala-bot's shoulder work (its DEC-54: roll-first, on the torso's lateral faces) is the
  closest prior art in the family for the torso side of the joint.
- **The head sits on a neck just above the shoulders** and carries the D435i. XLeRobot's
  head is two servos; koala-bot has a 3-RPS neck design.

**Form reference, owner 2026-09-20.** The owner supplied a screenshot of an AliExpress
kit — a bimanual humanoid torso, arms hanging at its sides, a stereo head on a short neck,
on a bolted pedestal — as "more like the form I was thinking for a humanoid based on two
vertically mounted SO-ARMs", **shown for general layout only**. Scope, in the owner's
words: the general form **from the sternum up** is the possible inspiration. What it
contributes is therefore shoulder and head geometry and nothing below — not the flat-panel
body (which has no volume for battery, compute or servo bus), not the pedestal, not the
arms' internals.

It confirms three of the departures above — head on a neck just above the shoulder line,
arms hanging as pendulums, a printed torso rather than a cart — and **adds a third
shoulder-mounting option**: the arm's base flange on a *shoulder yoke standing proud of
the torso*, rather than flat on a front or side face. That buys clearance for the arm to
swing past the body, at the cost of a cantilevered bracket.

**Arm layout, owner's reading of the image 2026-09-20:** the kit's arm carries a **bicep
roll in place of a wrist roll** — the same joint count as an SO-101, with the roll moved
proximal. This changes nothing about the arms here, which are SO-101s: pan, lift, elbow,
wrist flex, wrist roll, gripper. (Assistant's note, unverified: the distal roll is the one
task 1 wants — approach a toy from above, spin the jaws to its yaw — where a bicep roll
mainly re-aims the elbow's swing plane. Relevant only if an arm variant is ever
considered.) An earlier assistant reading of the same image, that the kit's arm carried a
*shoulder* roll the SO-101 lacks, was wrong; the owner corrected it.

**Locomotion is open.** The owner doubts a three-omniwheel kiwi base: its balance under a
tall torso, and its footing on anything but flat indoor carpet. **Upstream reached the
same conclusion** (read 2026-09-18): XLeRobot 0.4.0 (2025-12-02) replaced the LeKiwi
omni base with a **dual-wheel differential base** — "more stable, higher moving speed,
better passability, and larger torque", at the cost of "one DoF of moving left and
right" — in two versions: the same 12 V STS3215 servos in wheel mode on 5-inch walker
wheels (the default; upstream calls the servos noisy and limited in speed, torque and
payload), or brushless scooter motors on the Bracket Bot platform. The same release made
the arm base "more versatile (choose your own mounting direction)". Its assembly page is
still marked under construction and has no BOM
([assembly](https://xlerobot.readthedocs.io/en/latest/hardware/getting_started/assemble_2wheel.html),
[hardware readme](https://github.com/Vector-Wangel/XLeRobot/tree/main/hardware)).
For the record, LeKiwi's base as-is is three 12 V ST3215s (or a 5 V variant) on 4-inch
omniwheels ([BOM](https://github.com/SIGRobotics-UIUC/LeKiwi/blob/main/BOM.md)), and
XLeRobot 0.3.0 reused it unchanged: 17 STS3215 12 V = 12 arms + 3 base + 2 head
([BOM](https://xlerobot.readthedocs.io/en/latest/hardware/getting_started/material.html)). The alternative is a
differential base on the **two 37D 12 V 122 rpm gearmotors in stock** with the Pololu
TB9051FTG beside them (private wk-inventory `docs/stock.md`), plus casters — generic and
heavier, at the cost of holonomic motion, which LeKiwi has and a two-arm manipulator
finds convenient. Nothing measured; kiwi-drive performance on carpet pile and thresholds
is a reasonable doubt, not a finding.

**Tasks** (the owner's test for this idea, see [Adding an idea](#adding-an-idea)):

1. **Pick up all the children's toys from the floor and return them to the toy chest**
   (owner, 2026-09-18). This fixes the workspace at **floor level to toy-chest rim**, not
   worktop height — the opposite of XLeRobot's cart, and a short robot suits it. What it
   demands, none of it examined: a grasp for toys of many shapes and sizes within the
   SO-101's payload (unstated here — read it from the design before assuming); a head
   that sees the floor from above the D435i's 0.28 m minimum range; finding toys around a
   room and navigating to the chest, which is the mapping job that earns the Orin + D435i
   their place on this robot rather than a Pi; and, since it works among children's
   things, koala-bot's child-safety spec (its OQ-10, audience 2–5) applies to it too.
   The learned-policy shape is one LeRobot dataset for the pick-and-drop and a
   conventional navigation stack around it (the hexapod's Nav2 work).

Further tasks, if any, are the owner's to add; the form follows from the list.

**What it reuses:** the finished SO-ARM101 (a second arm is still to build, SO-ARM101
DEC-15); the 12 V STS3215 pool (count against koala-bot's twelve before assuming any are
free); a spare Pi 5 or the Orin; the D435i; LeKiwi/XLeRobot's LeRobot software.
**What it costs:** CAD for the torso, shoulders, neck and base — simpler than koala-bot's
limbs, all boxes and mounts — and the second arm. Powered up every day, which is the
owner's test for the pair's home.

**Ordering, assistant's recommendation, not accepted:** a LeKiwi base first if the omni
doubt is settled in its favour (it is stage one of XLeRobot either way); otherwise the
differential base first, since it is the part with no upstream to lean on.

**Added 2026-09-20, also an assistant's recommendation, not accepted:** design the torso
once and bolt it to a bench column first. That is
[SO-ARM101 DEC-15](../projects/soarm101/docs/decisions.md)'s two arms 30 cm apart stood
upright with a head on them — daily use with no base, no Nav2 and no Orin — and the same
torso moves onto a base when locomotion is settled. The interface to get right early is
how the torso meets the column, so that it later meets a base instead.

## Externally designed builds

Existing open designs worth building as-is, rather than projects to design. The value is
inverted from the rest of this page: the mechanics are settled, so what is unresolved is
what the build *teaches* and what it costs to run alongside the others.

### Open Duck Mini V2

> **Parked 2026-09-07, the day it was raised.** Considered as a pivot away from koala-bot
> and rejected as one: koala-bot remains the active design project. Not a judgement on the
> design — everything below was verified and still holds. This is a *when*, not a *whether*.
>
> **Reaffirmed 2026-09-18 (owner):** deferred because a learned walking policy is new
> ground for the owner, and that alone is enough. Still a *when*.

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

**Tasks** (owner, 2026-09-18): companionship and learning — the learning being the
owner's, in RL sim-to-real, as much as the robot's. No manipulation, no navigation task.

**Printable now, buildable now only with a servo order** (re-read 2026-09-18): the STLs
are printable immediately in the validated PLA+, subject to the unchecked ≤ 200 × 200 mm
part-size rule and the unproven TPU for the two foot soles. The **servos are not the
owner's**: the design is the 7.4 V STS3215 on 2S; the family stock is the 12 V variant,
and the 12 V-on-3S conversion is the unverified fork below. Stock build means buying 14
7.4 V units (~€196).

**Could it be walking this week? Checked 2026-09-21, when the owner asked: no.** It is the
only walking biped surveyed that is printable tomorrow — everything else is CAD-less,
buy-only or orphaned — but three things stand between printing and walking:

- **The BOM electronics are not in stock.** The unallocated stock list
  ([wk-inventory `docs/stock.md`](https://github.com/WayneKennedy/wk-inventory/blob/main/docs/stock.md))
  holds no Pi Zero 2W, no BNO055 or BNO08x, no 18650 cells and no BMS. Every one is an
  order with a lead time. **TPU filament is in hand in quantity (owner, 2026-09-21)**,
  though the stock list does not carry it — having it is not the same as having printed
  it, and TPU on this printer is still unproven.
- **"Reallocate the servos" means koala-bot's — and only 8 are in hand.** The build takes
  14 STS3215. koala-bot holds 8; its backfill 6-pack shipped 2026-09-15 and was last
  recorded undelivered on 2026-09-17, so 14 depends on that parcel. SO-ARM101's six are
  commissioned. **The cost is low: koala-bot is blocked at the design stage (owner,
  2026-09-21)**, so its servos are idle, and the move reverses — unscrew, re-ID, return.
  This is the [proven-build thread](status.md#a-proven-printed-build-alongside-koala-bot--open-2026-09-18)
  in `status.md`, where the duck is one of several candidates.
- **Those servos make it the modified build, not the stock one.** They are 12 V, so it is
  the [12 V fork](#stock-or-modified--the-fork-that-must-be-decided-before-buying) with
  both its costs: the policy-stiffness question *and* the 2S → 3S battery-bay CAD change.
  A **tethered 12 V bench supply** sidesteps the battery bay for first tests, leaving only
  the policy question.

Also unmeasured: total print time (not yet sliced — the slicer estimate is trustworthy to
±2 % on this printer, so slicing the 51 pieces answers it), the unproven TPU soles, and an
upstream assembly guide that is marked incomplete. **The fork's recommendation stands, for
diagnosability rather than to protect koala-bot:** 14 × 7.4 V servos (~€196) buy a stock
baseline, and a 12 V duck that will not walk cannot be told apart from a wiring fault.

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
  **2026-09-07** (re-checked 2026-09-21). Read as *design finished and stable* — kits are
  still sold — rather than actively maintained; do not plan on upstream fixes. The
  maintainer's current work is the Microduck ([below](#microduck--the-successor-buy-only)),
  a different robot on different actuators.
- **It cannot get up after a fall (repo-verified, 2026-09-21).** There is no get-up
  policy, script, reward or fall detector anywhere in the three repos. A fall is a
  *terminal condition* in training — `fall_termination = get_gravity(data)[-1] < 0.0` in
  both `joystick.py` and `standing.py` — so the policy has never seen a fallen state, and
  `standing.py` is stand-still balance from near-upright, not recovery. The runtime's only
  state branch is a pause button: no IMU fall check, no safe-shutdown, no recovery. Both
  committed policies are walk-only, and the maintainer's own V2.5 TODO
  ([issue #33](https://github.com/apirrone/Open_Duck_Mini/issues/33)) lists no standup
  item. **A human picks it up.** Secondary sources claiming otherwise are describing the
  Microduck. Consequence for any task statement: it is a companion that walks, not one
  that survives unattended.
- **A builder reports the 12 V knee swap cured falling over.**
  [Issue #52](https://github.com/apirrone/Open_Duck_Mini/issues/52): *"I swapped the 7.4V
  19kg STS3215 motors in the knees for their 12V 30kg counterparts, which stopped the duck
  from falling over."* Unanswered by the maintainer, and a single report — but it is
  evidence on the [12 V fork](#stock-or-modified--the-fork-that-must-be-decided-before-buying)
  pointing the opposite way to the stiffness worry recorded there, and it suggests knee
  torque is marginal for *walking* on the stock build. The maintainer's own framing in
  `docs/sim2real.md`: *"we are using cheap servomotors that are hard to model and not
  overly powerful."*

**The policy, measured 2026-09-21** (parsed from the committed ONNX, not inferred). Both
`BEST_WALK_ONNX*.onnx` are the same architecture, different weights:

| | |
|---|---|
| Shape | `obs[101] → 512 → 256 → 128 → 28`, SiLU/Swish |
| Output | 14 joint means (tanh) + 14 log-std, the log-std discarded at inference |
| Parameters | **220,262** · 860 KiB as float32 |
| Rate | **50 Hz**, onnxruntime CPU on the Pi Zero 2W |
| Structure | A plain MLP. **No recurrence, no adaptation or encoder module** |

The observation is proprioception only — projected gravity, commands, joint positions and
velocities, three frames of previous action, foot contacts, reference motion. **Nothing in
it sees**; the robot feels terrain through its feet after the foot lands. That bears on
[where a policy sits in the two-tier split](common.md#compute-the-two-tier-split).

#### Microduck — the successor, buy-only

**Not a candidate build; recorded because it holds the get-up engineering and because it
corrects what this page used to say about the `microduck_*` repos.** Pollen Robotics
(Hugging Face's robotics arm), [store](https://store.pollen-robotics.com/products/microduck)
**€340 / $399 assembled**, pre-orders opened 2026-08-27, lead time quoted 4–6 months as of
2026-09-21. 25 cm, 780–800 g, Rockchip RK3566, camera, 8×8 ToF, two IMUs.

- **It moved off Feetech.** 15 × **Dynamixel XL330** (14 policy-controlled plus a mouth),
  confirmed from the runtime source, not press. So it shares no actuator, spares pool or
  bus tooling with this family.
- **Software is open, hardware is not.** The Rust runtime
  ([`pollen-robotics/microduck`](https://github.com/pollen-robotics/microduck)) and the
  training envs ([`microduck_rl`](https://github.com/pollen-robotics/microduck_rl)) are
  Apache-2.0 — **this corrects the earlier note that the runtime was not public.** But the
  press kit states the mechanical and electronic design files are not open, and the
  Onshape document 403s. **You cannot build one.**
- **It does get up**, and the mechanism is documented: a recovery reward layer *gated on
  actually being fallen* (trunk z < 0.10 m or tilt > 40°) folded into the walk policy, so
  it contributes exactly zero during clean walking; plus a predictive protective-fall
  reflex in the runtime that drops servo gains from 200 to 50 and lets the robot go limp
  on the way down, ending when the gyro says motion stopped. With no arms it rolls and
  folds — `hip_roll_neutral` was deliberately removed from the rewards because *getting up
  requires spreading the legs*. Supine is markedly harder than prone (trunk rests 48 mm off
  the floor on its back against 75 mm face-down) and is introduced last on a curriculum.

**The transferable lesson, whatever gets built here:** getting up is a *separate training
problem* with its own rewards and its own curriculum, not a bonus that falls out of a walk
policy. Budget it as such from the start.
- ~~Part sizes have not been checked~~ **Checked 2026-09-21: every part passes.** All 36
  STLs in `print/` clear both the Ender-5 S1's 220 × 220 × 280 mm volume and koala-bot's
  stricter ≤ 200 × 200 mm rule, in the orientation upstream ships them, and all 36 are
  watertight. The binding part is **`head.stl` at 199.85 × 197.32 × 59.4 mm** — 0.15 mm
  inside the rule, so treat it as fixed rather than adjustable. Part count confirms
  upstream's guide exactly: 36 distinct STLs, **51 printed pieces**. Measured with
  [`tools/design-viewer`](../tools/design-viewer/), which renders this design's assembly
  and parts from upstream geometry.

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

## Designed here

Candidates that would be original mechanical design, not a build of someone else's.

### A ROBO-ONE-class humanoid

**Raised by the owner 2026-09-20 after watching footage of ROBO-ONE matches, and kept for
the form factor rather than the sport:** a servo-driven biped of roughly 0.35–0.45 m that
walks well and stands itself up after a topple. The owner's framing — *"more as a form
factor that works"* — with a **Teensy 4.1 reflex tier and an onboard Pi**, which is this
family's [two-tier split](common.md#compute-the-two-tier-split) rather than ROBO-ONE
practice.

**Tasks** (per the state-the-tasks-first rule above): **unstated, and this does not
advance until they are.** "Walks and gets up" is a capability, not a task. Competing is one
possible answer and would set every constraint below; a companion that walks the house is
another and would set quite different ones. The sport is named here because its rules are
the only published, tested definition of *what a small humanoid must physically do* — not
because entering is decided.

**What the class is.** ROBO-ONE is a Japanese humanoid fighting competition, running since
2002, organised by 一般社団法人二足歩行ロボット協会. It is alive: the 44th ran 2025-09-20/21;
the **45th ran 2026-09-26/27**; ROBO-ONE Light's 28th ran 2026-03-07/08. **Rules are
published in English and current** — the [45th rules](https://www.robo-one.com/upload/roboones/93_780ae3facd3ac2e9f16c51af0187693aoriginal_en.pdf)
were revised 2026-07-28, and Light's are maintained as markdown in a public repo,
[nishibra/ROBO-ONE_rule](https://github.com/nishibra/ROBO-ONE_rule).

What the rules actually require, as read 2026-09-21:

- **Weight ≤ 4 kg** (4.5 kg if entered as autonomous). **ROBO-ONE Light: ≤ 1.2 kg
  including batteries.** Weight is set per event, not a permanent ladder.
- **No height limit exists.** Height enters only through the sole-to-leg-length ratio
  (for ≤ 5 kg: sole ≤ 40 % of leg length, max 13 cm; width ≤ 25 %).
- **Two arms are mandatory**, each with at least one working axis. This disqualifies both
  Open Duck Mini and Bimo by construction.
- **DOF is otherwise unregulated** — no minimum leg DOF, no total. The 16–24 DOF norm is
  convention.
- **No servo restriction for custom robots.** The < 20 kg·cm cap applies only to
  *officially certified commercial* machines.
- **It must get up inside the referee's 10-count**; three downs is a KO. Also: bipedal
  walking with ≥ 10 mm foot clearance, provable as three consecutive steps in each
  direction, and no crouch-walking.
- **A direct mechanical battery cut-off is mandatory** as of the 2026-07-28 revision —
  MOSFET or relay-only power control is explicitly not permitted. Fire or smoke is an
  immediate TKO.

**The servo question is settled, and not the way it looks.** ~30 kg·cm at 12 V is *ample*
for walking at this scale — the detail and the real limits are in
[`common.md`](common.md#is-the-sts3215-class-enough-for-a-walking-biped).

**Unresolved, and what makes this a hard project rather than a build:**

- **No competitive ROBO-ONE machine publishes CAD.** Verified 2026-09-21 across the
  rankings: 3D-printed entrants place well — "Alex" is 35 cm, 1.2 kg, 17 × Kondo KRS-3304
  on a printed frame, Best-32 at the 26th Light — but the pages carry photographs, not
  design files. The only official STL set is the **4-servo Beginners kit**,
  [nishibra/ROBO-ONE_Beginners_auto](https://github.com/nishibra/ROBO-ONE_Beginners_auto).
  **There is nothing to fork.** This is original mechanical design in the same weight class
  as koala-bot.
- **Nothing open exists on STS3215 with arms.** The whole surveyed field is in
  [`common.md`](common.md#is-the-sts3215-class-enough-for-a-walking-biped); the nearest
  things are legs-only ([Bimo](#bimo--reference-only-no-cad), Open Duck) or orphaned
  ([Zeroth-01](https://github.com/Justin-Riekehof/zeroth-01-build), 16 DOF with STS3215
  arms and STS3250 legs, whose company folded and whose official CAD is offline).
- **Getting up is a second training problem**, with its own rewards and curriculum — see
  the Microduck note [above](#microduck--the-successor-buy-only). For a fighting robot it
  is also a *rules* requirement, not a nicety.
- **Mass is the wall, not torque.** Every open in-class design found is 2.1–3.4 kg, i.e.
  main-class only; Light's 1.2 kg ceiling across 16–20 STS3215 is brutal, since these
  servos are heavy for their torque.
- **Where the policy runs is open** — see [the third compute regime](common.md#a-third-regime-the-policy-on-the-mcu).
- **Training is possible locally**, subject to [the GPU workstation](common.md#the-gpu-workstation).

**Reuses:** the printer; the STS3215 family, bus tooling and press-fit knowledge; the
reflex-tier firmware pattern and the topic contract; the Teensy 4.1 already in hand.
**Does not reuse:** any existing mechanical design.

### Bimo — reference only, no CAD

**Not adoptable (owner, 2026-09-21), and recorded for its architecture.**
[mekion/the-bimo-project](https://github.com/mekion/the-bimo-project), Apache-2.0. A 45 cm,
~1.6 kg, **8 × STS3215 12 V** hip-and-knee biped that walks omnidirectionally on a CPG and
on an RL policy — **direct proof the 12 V STS3215 walks a biped of this size**. Kit $500,
pre-order.

**It publishes no CAD.** No STL, no STEP, no URDF; the README still says CAD files are
coming soon, and the controller PCB has no schematic or gerbers either. The only geometry
is `IsaacLab/bimo/assets/Bimo.usd`, a simulation asset — viewable through
[`tools/design-viewer`](../tools/design-viewer/), useful for seeing how an 8-DOF biped
carries its servos, useless for printing.

**Why it is worth knowing anyway — it is the family's only worked example of a policy on
an MCU.** A custom RP2040 board (bare chip, not a Pico) drives 8 STS servos on one UART at
1 Mbaud, reads a **BNO08x** — the koala-bot IMU family — plus four VL53L0X through a
TCA9548A, cuts servo power on a GPIO, reads pack voltage on an ADC, and splits the fast
loop and blocking sensors across the two cores. Three firmware builds: tethered to a host,
standalone CPG, and **standalone distilled neural policy**. It also powers an SBC over USB-C
at 5 V 4 A, so tethered operation is an option rather than the only path. Details of the
policy route are in [`common.md`](common.md#a-third-regime-the-policy-on-the-mcu).

---

## Open directions

Threads worth pulling that are not yet attached to a specific build.

### Vsim — onboard planning, worth watching

**Recorded 2026-09-21 as technology to learn from, not something to adopt** (owner:
*"we can learn what's possible and adopt what we can"*). Vsim Technology Ltd, Cambridge,
Companies House 14509090, incorporated 2022-11-28. Founders **Dr Fengyun (Michelle) Lu** and
**Dr Kier Storey**, each over a decade at NVIDIA and both co-authors of the
[Isaac Gym paper](https://arxiv.org/abs/2108.10470). $24 M raised, the $21.5 M seed led by
EQT Ventures (2024-09); ARIA funds them on its Robot Dexterity programme. Coverage that
prompted this: [BBC News, 2026-09-17](https://www.bbc.co.uk/news/articles/c79g0j3d4q9o).

**What the "policies in real time" claim actually is — three separable things:**

1. **A GPU-first physics engine** — the real differentiator. Real-time hard-contact and
   thin-deformable demos: a house of cards at true 0.3 mm card thickness with no
   stabilisation, 1,000+ rods at 256 segments on an RTX 4090.
2. **Onboard sampling-based MPC** — *"about a second … ahead into the future for 20,000
   different kind of combinations"* (Storey, BBC), replanned while the robot moves. **This
   involves no training.** It is online planning, with decades of prior art and an open
   implementation in [MuJoCo MPC](https://github.com/google-deepmind/mujoco_mpc).
3. **Fast training and fine-tuning** — minutes to train, seconds to adapt, for *narrow
   tabletop manipulation*. The BBC's own word is "minutes".

So nobody is synthesising a robust locomotion policy from scratch in real time; the
~10⁸-timestep cost of that is untouched.

**Not usable.** Fully proprietary: no paper, no benchmark, no repo, no package, no
waitlist, and **no independent verification of any number**. The one outside expert the
BBC quotes speaks in the conditional and is funded under the same ARIA programme.

**What transfers:** the *idea* of onboard planning as the answer to "no trained policy
covers this" — see [the third compute regime](common.md#a-third-regime-the-policy-on-the-mcu).
The open route to trying it is MuJoCo MPC, on intent-tier or Orin-class hardware.

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

- **Identity is a coordinator service; embeddings stay local** (owner, 2026-09-19, from
  the HAT bench). Face embeddings do not travel between robots — they only mean something
  to the network that made them ([hailo_perception README](../projects/devastator/software/ros2_ws/src/hailo_perception/README.md)).
  So: a robot that meets a face it cannot name sends the coordinator the *crop* (a few
  KB, on an unknown only — no streams); the coordinator recognises it against the
  family's people, or asks a human, and answers with the person's record (name, whatever
  the family keeps about them); the robot enrols the crop into its own gallery with its
  own model and never asks about that face again. Photos and identity records are held
  centrally, vectors per robot. The HAT bench already does the halves that run on the
  robot: unknown-face crops are recorded, and after-the-fact enrolment from a crop works.
  Nothing on the coordinator side exists.
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

### A door camera that recognises who is approaching

Raised by the owner 2026-09-19 after the HAT bench recognised him and his wife live. A
fixed camera at the door running the same detection-and-recognition pipeline as
[hailo_perception](../projects/devastator/software/ros2_ws/src/hailo_perception/README.md), on a
Pi 5 with the AI HAT+ 2 or on any host that can run it; the first fixed node of the
[hive-mind](#physical-ai-and-the-hive-mind) direction rather than a robot. **Tasks:**
announce a known person at the door; distinguish household from visitor. Nothing decided.

**Privacy is a design input, not an afterthought** (owner's own caveat). The bench's
current behaviour would be wrong at a door: it records every unknown face. What a door
camera should do instead, as constraints for whoever builds it:

- Recognise only people who enrolled themselves; everyone else is "a person", not a
  face record. Do not store unknown crops at all, or delete them within minutes.
- Keep the field of view inside the property. In the UK a domestic camera that captures
  the street or a neighbour's property brings data-protection law into scope (the ICO
  publishes guidance for home CCTV), and facial recognition of people who have not
  consented is biometric data, the most protected kind. Unverified detail; check the
  current guidance before installing.
- Everything on the LAN: no cloud service sees a frame. The tailnet is the only remote
  path, as for the rest of the family.
- Make the recognition data disposable: galleries are caches rebuilt from enrolment
  photos, and a person can be removed by deleting their files.

**2D recognition can be spoofed by a photograph**, which matters at a door and not on
a bench. What a phone's Face ID adds is not accuracy but *liveness*: a projected
infrared dot pattern gives a 3D map of the face and an IR image, so a flat picture
fails. The family's nearest equivalents, none tried: the D435i (active IR stereo depth —
a depth check over the face box rejects a flat photo; the Orin half of the bench could
test this against the HAT's 2D pipeline with a phone photo of the owner); a Luxonis
OAK-D Pro (IR dot projector plus IR flood illuminator, on-device inference, sold in part
for this); a challenge, blink or turn, in software. Intel's purpose-built RealSense ID
F455 face-authentication camera existed but its status after Intel's wind-down is
unverified. Iris or fingerprint would be more biometric still but stop being a door
*camera*.

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

### A bench supply with fixed rails

A disused ATX PC power supply rebuilt as a hobby bench supply: **fixed 3.3 V, 5 V and 12 V
binding posts**, plus a variable rail on a DPS-style CV/CC module, in a printed case. From a
YouTube build the owner saw (owner, 2026-09-17).

**The trigger is a safety problem, not a capability gap.** The Eventek bench supply's
variable-voltage knob is low-friction, and a knock puts an arbitrary voltage on the servo
bus. Nothing downstream would stop it: the Waveshare adapter is a **pass-through with no
regulation, protection or clamp** ([common.md → Configuring a servo](common.md#configuring-a-servo--true-for-every-sts-project)),
so the servos see whatever the supply is set to, and their `Max_Voltage_Limit` reads
**14.0 V** (read off all six, 2026-09-17). A fixed post cannot be knocked.

- **Reuses:** the printer; the [power-integrity rules](common.md#power-integrity).
- **Unresolved:**
  - **No donor.** Nothing matching in [wk-inventory `stock.md`](https://github.com/WayneKennedy/wk-inventory/blob/main/docs/stock.md),
    and no bench-supply or ATX purchase in the invoices (searched 2026-09-17). Every part
    is a purchase, including the donor PSU.
  - **A buck module cannot boost.** "0.5–36 V" on a DPS-style panel is the module's own
    rating; fed from an ATX 12 V rail it can only go *down*. A 36 V top end needs a boost
    stage or a higher input — settle this before buying the module.
  - **Donor vintage decides whether the build works at all.** ATX12VO units (2019+) carry
    only 12 V; the 3.3 V and 5 V rails that are the point of this build are generated on the
    motherboard, not in the PSU. Older multi-rail ATX is the right donor.
  - Many ATX units need `PS_ON` pulled to GND to start, and a minimum load on 5 V / 3.3 V
    to regulate.
  - **Whether it is the right answer for robot work.** [Power integrity](common.md#power-integrity)
    says prototype from a stiff, low-impedance source — a LiPo, not a bench PSU. This build
    serves general electronics work; it does not supersede that.
- **Competing for the same time:** nine unfinished projects in
  [wk-inventory `projects.md`](https://github.com/WayneKennedy/wk-inventory/blob/main/docs/projects.md),
  against the owner's stated goal of fewer unused parts and more finished projects.
- **Cheaper answer to the immediate problem:** a fixed 12 V, 5 A+ brick removes the knob
  hazard outright and closes the arm's long-open
  [OQ-03](../projects/soarm101/docs/open-questions.md), independently of whether this
  project ever happens.

**A second, much smaller route — M5Dial + M5Stack PPS Module 13.2** (owner, 2026-09-17). The
[PPS 13.2](https://docs.m5stack.com/en/module/Module13.2-PPS) is a programmable buck: 0.5–30 V
at 0–5 A, 100 W, **±30 mV / ±5 mA readback**, isolated comms, 4 mm banana sockets, ~£25. The
owner has an unused **M5Dial v1.1** (a gift; [wk-inventory `stock.md`](https://github.com/WayneKennedy/wk-inventory/blob/main/docs/stock.md)),
which would give it a job.

- **The catch: the Dial is not a Core.** The PPS is a Module-series part that mates over
  **M-Bus** (two 15-pin 2.54 mm rows) and answers I2C at **0x35**; the Dial is a Stamp-S3 puck
  with **no M-Bus**, so nothing can stack on it. It does expose I2C on Port A and Port B, so a
  hand-wired Port-A-to-M-Bus adapter is **plausible but unverified** — including whether Port A
  can power the module's host side, which is opto/transformer isolated from the output.
- **It still needs a separate 9–36 V input brick.** The PPS only steps down, and with no input
  "it will show no I2C device and will not work". So this route is module + brick + adapter +
  firmware, not a plug-in.
- **What it genuinely solves:** a *digital* encoder can be clamped in firmware — cap the
  settable maximum at, say, 12.5 V and the knob physically cannot reach 20 V. An analogue pot
  cannot do that, and that is exactly the hazard that started this. The readback would also beat
  the instrument [OQ-03](../projects/soarm101/docs/open-questions.md) currently relies on
  (the servos' own ADC at 20 Hz).
- **Why it is still not the arm's supply:** a servo rail whose voltage depends on an ESP32
  booting and running correct firmware is a worse rail than a fixed brick, and the module's
  **power-up output behaviour is unspecified** in its documentation. For a bus with a 14.0 V
  absolute limit and no protection upstream, that is the wrong unknown to accept. Good bench
  instrument; not the fix for the arm.

### A correlated bench logger

A Teensy sampling a rail through a divider at tens of kSPS, streaming to the host that is
driving the robot, so a voltage trace and the robot's own telemetry share one time base.
**Its original justification is gone, and that is recorded here rather than quietly dropped.** It
was prompted by SO-ARM101 OQ-03's rail sag — which **turned out not to exist** (2026-09-18): the
dips were corrupt frames caught by a `min()` across six servos, and the rail holds 11.9–12.1 V.
There is nothing left for a voltage logger to find there.

**What remains is a different and better-posed want.** The measurement this family cannot make is
**anything transient correlated with what a robot was doing at the time** — servo current at a
stall, rail behaviour on a drone's arming surge, a printer's heater duty. That is a real gap and a
reusable instrument; it is just no longer urgent, and it should not be built on the strength of a
question that has since closed.

- **Board: the Teensy 4.0** ([wk-inventory `stock.md`](https://github.com/WayneKennedy/wk-inventory/blob/main/docs/stock.md)),
  freed from koala-bot 2026-09-18. Its one limitation — micro-ROS lists it "Not tested" — **does
  not apply here**, because a logger is bare Teensyduino: ADC, DMA, a serial stream. Its header
  kit was bought with it, so it breadboards without soldering. Same i.MX RT1062 as the 4.1, so
  the ADC is the same silicon.
- **Reuses:** the printer for a case; the family's Teensy toolchain, so this doubles as
  low-stakes practice for the reflex-tier work in SO-ARM101 OQ-09.
- **Unresolved:**
  - **Sampling rate.** A millisecond dip needs ≥10 kSPS, ideally 100 k — DMA-driven, not an
    `analogRead()` loop.
  - **The shared clock, which is the real design problem.** Do not sync two free-running clocks.
    Either have the host send one marker byte at a known `time.time()` and the logger stamp its
    arrival (±50 ppm drift is ±3 ms over a minute), or have `shapes.py` hold the arm still for a
    second mid-run and align the trace on the flat spot.
  - **It answers neither open question as things stand.** OQ-03 is closed, and for
    [OQ-18](../projects/soarm101/docs/open-questions.md) the 1.3–2.4%
    corrupted servo frames are a *serial* fault; chasing those wants a **logic analyser** on the
    half-duplex bus, which is a different instrument. Decide which question is being bought.
  - Whether a ~£30–80 USB scope would simply be better. Against it: a scope captures a window,
    where what OQ-03 needs is a whole run correlated against the robot's own telemetry.
- **Already done, and it closed the question:** logging per-servo voltage instead of `min()`
  during a cube cost nothing and disproved the sag outright (2026-09-18). Worth remembering as the
  pattern — **exhaust what the machine already measures before buying an instrument to measure
  it.**

---

## Adding an idea

Append a section under the right heading. If the idea is a deferred feature of an existing
robot, it belongs in that repo's `backlog.md` instead — only put it here if it is a
plausible project in its own right.

**State the tasks before the form** (owner, 2026-09-18). The owner's motivation is to build
something aesthetically pleasing, which is its own reward — but designing for looks alone
leaves the robot with nothing to *do*, and that is the failure mode for the
[physical-AI direction](#physical-ai-and-the-hive-mind): learned behaviour is defined per
task, so a robot without tasks has nothing to learn. The insight came from XLeRobot: its
cart is ugly to the owner, but it puts the head and arms at worktop height, where
household tasks (laundry folding, for one) actually are. Every new idea here names the
practical tasks it would carry out, and the form follows from where those tasks happen.
Entries above written before this rule gain a task statement when next touched.
