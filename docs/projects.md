# Projects

Per-project detail. Each section says what the project is, what it runs on, where its
documentation starts, and what it shares with the others. The authoritative record for
any one project is that project's own repository — this page is a pointer, and is
accurate as of **2026-09-11**.

---

## koala-bot

**An open-source, 3D-printable family of small companion robots.** The first member,
Koala V1, is a self-balancing, knee-wheeled companion roughly koala-sized, printable in
PETG on a 200 × 200 mm bed. It rolls and balances on two knee-wheels, leans into turns
via 2-DOF hips, gestures with 3-DOF dual-purpose front limbs, and looks at you through a
3-RPS parallel neck.

| | |
|---|---|
| Repo | [WayneKennedy/koala-bot](https://github.com/WayneKennedy/koala-bot) — public |
| State | Pre-alpha, design phase. CAD started, fit coupons printed; V1 hardware ordered, and a test-fit pair of 12 V ST3215 servos in hand since 2026-09-07 |
| Compute | Raspberry Pi 5 + ROS 2 (intent) · real-time MCU, Teensy 4.0 leading (reflex) |
| Actuation | Feetech STS3215 12 V bus servos (limbs) · STS3032M 6 V (neck) · 12 V geared DC + encoder (drive wheels) |
| Power | Single ~12 V rail, 3S LiPo; separate 5 V buck for the Pi |
| Start at | `docs/concept.md`, then `docs/architecture.md` |
| Licence | Tri-licence: `CERN-OHL-S-2.0` hardware · `MIT` software · `CC-BY-SA-4.0` docs |

**Shares with the rest:** the printer and its PETG profile; the STS3215 servo family with
the SO-ARM101; the Pi 5 + ROS 2 tier with the hexapod; SO-ARM100 reference CAD, vendored
under Apache-2.0 in `hardware/vendor/`. The two-tier reflex/intent split described in its
`docs/architecture.md` is the family pattern — see [`common.md`](common.md#compute-the-two-tier-split).

---

## wk-hexapod

**A ROS 2 autonomous hexapod**, built on Freenove Big Hexapod (FNK0052) hardware with the
sensing substantially upgraded: an Intel RealSense D435i replaces the kit's Pi camera and
ultrasonic sensor, giving RGB, depth and a second IMU on the pan/tilt head.

| | |
|---|---|
| Repo | [WayneKennedy/wk-hexapod](https://github.com/WayneKennedy/wk-hexapod) — public |
| State | Native stack verified end to end on the bench, 2026-09-09 (USB power): RTAB-Map maps, Nav2 active, frontier exploration sends goals, mission API answers. First battery run of this stack pending |
| Compute | Raspberry Pi 5 (8 GB), ROS 2 Jazzy on Ubuntu Server 24.04, **installed natively from apt** (the Docker container was removed 2026-09-09); runs as a `systemd` service |
| Actuation | 20 hobby servos (18 leg + 2 head) via 2× PCA9685 on I²C — direct from the Pi, no reflex MCU |
| Sensing | RealSense D435i (RGB-D + IMU, depth computed in-camera) · MPU6050 body IMU · ADS7830 ADC for dual-battery monitoring |
| Reference | [WayneKennedy/fn-hexapod](https://github.com/WayneKennedy/fn-hexapod) — Freenove vendor code; confirmed-working `servo.py`, `home.py`, `stand.py`, `control.py` |
| Start at | `AGENTS.md`, then `docs/architecture.md` |
| Licence | `Apache-2.0` (software and docs only; hardware is Freenove's) — adopting the tri-licence is open in its repo |

**Progress:** milestone 0 (native stack end to end on the bench) done; milestone 1 (it
explores a room, on the battery) current. Open in its repo: velocity semantics between
Nav2 and the gait controller, CPU load with everything running, collision-monitor tuning,
and what an "approved" mission planner is. Its `docs/roadmap.md` is authoritative.

**Shares with the rest:** the Pi 5 + ROS 2 tier and the `/cmd_vel` · `/joint_commands` ·
`/joint_states` · `/imu` · `/odom` topic vocabulary with koala-bot. It is the
**intent-tier reference implementation** of the family — the only robot with a working
SLAM, navigation and mission stack — and the counter-example to the two-tier rule: every
device is a direct peripheral of the Pi, viable for a statically stable walker in a way it
would not be for a balancing robot. Its `docs/architecture.md` records what that flat
design costs; a reflex-tier retrofit is an open question there, not a plan.

---

## wk-devastator

**A tracked, skid-steer ROS 2 robot on a purchased DFRobot Devastator chassis** — bought,
part-built, abandoned, and now being resurrected. The chassis is kept; the electronics,
compute and software are all replaced.

| | |
|---|---|
| Repo | [WayneKennedy/wk-devastator](https://github.com/WayneKennedy/wk-devastator) — public |
| State | Design record; milestone 0 (measure-and-decide) in progress. Motors and Teensy 4.1 ordered, driver borrowed from koala-bot. **Motors on back order, due end of October 2026** (revised 2026-09-09) — milestone 1 waits on them |
| Chassis | DFRobot **ROB0128**, aluminium, 225 × 220 × 108 mm, 1.3 kg, 3 kg payload |
| Actuation | 2 × Pololu 25D 47:1 12 V gearmotors with 48 CPR encoders (DEC-11), replacing the kit's 6 V encoderless originals |
| Compute (planned) | 32-bit MCU running micro-ROS (reflex) · Raspberry Pi + ROS 2 (intent) |
| Start at | `AGENTS.md`, then `docs/concept.md` |
| Licence | Tri-licence: `CERN-OHL-S-2.0` hardware · `MIT` software · `CC-BY-SA-4.0` docs |

**Why it matters to the others:** it is the simplest body in the family — statically
stable, no gait, no balance loop — which makes it the cheapest second consumer of the
hexapod's SLAM and Nav2 work, and the first plausible node of a fleet. See
[`ideas.md`](ideas.md#physical-ai-and-the-hive-mind).

**Shares with the rest:** the Pi + ROS 2 intent tier and the
[topic contract](common.md#the-topic-contract) with the hexapod; the printer, for mounts
and trays; koala-bot's driver and MCU selections. **No servo overlap** — it is a DC-motor
platform, so [the STS substrate](common.md#actuators) does not apply.

**The useful history:** the first build stalled on battery limitations and over-ambitious
scope — two depth cameras and a Pi 4 mounted before the drivetrain worked, through an
L298N losing ~2 V of a 6 V rail. It was under-powered by design. The project's rules and
its perception-last roadmap follow from that, and are recorded in its own repo.

---

## SO-ARM101

**A Standard Open Arm** — the LeRobot-compatible low-cost manipulator designed by The
Robot Studio with Hugging Face, built here in its 12 V variant from the upstream design.
No fork: upstream is cloned read-only as the design authority, and **the build record has
its own repo** since 2026-09-09.

| | |
|---|---|
| Repo | [WayneKennedy/wk-soarm101](https://github.com/WayneKennedy/wk-soarm101) — public, build record |
| Upstream | [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) — public, Apache-2.0, cloned not forked |
| State | Parts printed (11 of 11 at least once; `Wrist_Roll_Pitch` without a usable copy yet), servos being commissioned (2 of 6 — IDs 1 and 2 set and verified on one bus 2026-09-09), nothing assembled |
| Actuation | Feetech STS3215 **12 V** bus servos on a Waveshare Bus Servo Adapter (A) |
| Material | White eSUN PLA+, 220 °C / 60 °C bed, supports avoided by orientation |
| Start at | `AGENTS.md`, then `docs/servos.md` |
| Licence | Tri-licence: `CERN-OHL-S-2.0` hardware · `MIT` software · `CC-BY-SA-4.0` docs. The arm design stays upstream's Apache-2.0 |

**Shares with the rest:** the STS3215 servo family with koala-bot, and its CAD is
vendored into koala-bot as reference. Its parts drove the PLA+ profile and the
press-fit findings in [`common.md`](common.md#press-fits-and-supports).

---

## wk-drone-bee35

**An aerial robot: a 3.5" ducted cinewhoop on a SpeedyBee Bee35 Pro frame**, built for
position hold and endurance rather than speed. Reference behaviour is a DJI Neo: level
hover, solid position hold, returns to hold when the sticks are released. The first
airborne member of the family, and intended as a node the mission-planning tier can reach.

| | |
|---|---|
| Repo | [WayneKennedy/wk-drone-bee35](https://github.com/WayneKennedy/wk-drone-bee35) — **private** |
| State | Parts ordered 2026-09-11; nothing built, flashed or flown. Firmware open (its OQ-01) |
| Airframe | Bee35 Pro, 153 mm, ducted; 4× T-Motor F2004 3000KV; HQProp 90 mm 3-blade; 4S Li-Ion (Molicel P45B 21700 packs shared across the fleet) |
| Flight controller | MicoAir743 V2 (BMI088, 55 A AM32 ESC). Ships with ArduPilot; iNav intended (its DEC-01), under review |
| Sensing | MicoAir MTF-01P optical flow + 12 m lidar · Flywoo GM10 Mini V3 GPS + compass · Walksnail Avatar HD video |
| Link | ELRS 2.4 GHz, RadioMaster RP3 V2 |
| Start at | `AGENTS.md`, then `docs/decisions.md` and `docs/open-questions.md` |
| Licence | None set yet |

**Why it differs from the rest:** the flight controller is reflex and intent tier in one
MCU — there is no on-board Pi and no ROS 2. How it joins the
[topic contract](common.md#the-topic-contract) and whether that forces ArduPilot (native
ROS 2 via AP_DDS, two-way MAVLink) over iNav (MAVLink transmit-only, no ROS 2) is its
OQ-01, decided once hardware is in hand.

**Shares with the rest:** the printer, for TPU sensor mounts and PETG brackets. No servo,
compute or software overlap with the ground robots.

---

## 3D printing

**A Creality Ender-5 S1 running Klipper on a Raspberry Pi 5** — the machine every
printable part on every project comes off, and the repo that records how it is set up,
calibrated and driven.

| | |
|---|---|
| Repo | [WayneKennedy/3d-printing](https://github.com/WayneKennedy/3d-printing) — **private** |
| State | Commissioned 2026-08-28 → 08-31 (stock Marlin → Klipper); in production use |
| Printer | Creality Ender-5 S1, stock. Build volume 220 × 220 × 280 mm, textured PEI on spring steel |
| Host | Raspberry Pi 5 (8 GB, NVMe), MainsailOS stack; Moonraker's HTTP API is the control surface |
| Location | Garage since 2026-09-06, inside a PVC enclosure, front and top open by default |
| Contents | `docs/` — hardware, Klipper setup, calibration, workflow, print log, backlog · `reference/` — snapshots of the live Pi config and slicer profiles |

Because the repo is private, this public one carries the *findings* — materials,
profiles, tolerances, failure modes — and not the infrastructure. See
[`common.md`](common.md#printing).

**Note on the location:** the garage has a clear corrugated PVC roof and behaves as a
greenhouse — hot in daytime sun, cold overnight. It is temporary; a purpose-built garden
workshop is planned after a house move later in 2026. Work around the garage rather than
engineering for it.
