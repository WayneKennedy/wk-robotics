# Projects

Per-project detail. Each section says what the project is, what it runs on, where its
documentation starts, and what it shares with the others. The authoritative record for
any one project is that project's own repository or `projects/` folder — this page is a
pointer, and is
accurate as of **2026-09-13**.

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
| State | Pre-alpha, design phase. CAD started, fit coupons printed. All sixteen V1 servos in hand since 2026-09-12 and the drive/balance base since 2026-09-11; fasteners not yet ordered; nothing assembled |
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
kit's own sensors: an OV5647 Pi camera and an HC-SR04 ultrasonic on the pan/tilt head. A
RealSense D435i replaced them from 2025-12-31 until 2026-09-18, when it was banked with the
Orin Nano ([its DEC-25](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/decisions.md)).

| | |
|---|---|
| Repo | [WayneKennedy/wk-hexapod](https://github.com/WayneKennedy/wk-hexapod) — public |
| State | Native stack verified end to end with the D435i: on the bench 2026-09-09, a frontier reached on the battery 2026-09-15. Since 2026-09-18 the code needs drivers and a mapping route for the kit's sensors (its OQ-19) |
| Compute | Raspberry Pi 5 (8 GB), ROS 2 Jazzy on Ubuntu Server 24.04, **installed natively from apt** (the Docker container was removed 2026-09-09); runs as a `systemd` service |
| Actuation | 20 hobby servos (18 leg + 2 head) via 2× PCA9685 on I²C — direct from the Pi, no reflex MCU |
| Sensing | OV5647 Pi camera · HC-SR04 ultrasonic · MPU6050 body IMU · ADS7830 ADC for dual-battery monitoring |
| Reference | [Freenove upstream](https://github.com/Freenove/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi) — vendor code, read directly from a sparse clone of `Code/Server/`; recipe, pinned commit and the CC BY-NC-SA caveat in its `docs/references.md` (DEC-20) |
| Start at | `AGENTS.md`, then `docs/architecture.md` |
| Licence | `Apache-2.0` (software and docs only; hardware is Freenove's) — adopting the tri-licence is open in its repo, and blocked on OQ-15 there: whether any driver is a derived work of the CC BY-NC-SA vendor code |

**Progress:** milestone 0 (native stack end to end on the bench) done; milestone 1 (it
explores a room, on the battery) current. Open in its repo: velocity semantics between
Nav2 and the gait controller, CPU load with everything running, collision-monitor tuning,
and what an "approved" mission planner is. Its `docs/roadmap.md` is authoritative.

**Shares with the rest:** the Pi 5 + ROS 2 tier and the `/cmd_vel` · `/joint_commands` ·
`/joint_states` · `/imu` · `/odom` topic vocabulary with koala-bot. It is the family's
**baseline intent-tier reference** ([its DEC-26](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/decisions.md)) — CPU-only Pi 5, primitive
sensors, the only robot with a navigation and mission stack that has run — with the
Devastator as the second reference a step above it. Its hardware ceiling is the kit's: the
GPIO riser blocks the AI HAT+ 2 and its PWM hobby servos rule out ST3215s, so new hardware
goes to a [custom hexapod](ideas.md#a-printed-hexapod), not this one. It is also the
counter-example to the two-tier rule: every
device is a direct peripheral of the Pi, viable for a statically stable walker in a way it
would not be for a balancing robot. Its `docs/architecture.md` records what that flat
design costs; a reflex-tier retrofit is an open question there, not a plan.

---

## Devastator

**A tracked, skid-steer ROS 2 robot on a purchased DFRobot Devastator chassis** — bought,
part-built, abandoned, and now being resurrected. The chassis is kept; the electronics,
compute and software are all replaced.

| | |
|---|---|
| Where | [`projects/devastator/`](../projects/devastator/README.md) in this repo since 2026-09-13; formerly the `wk-devastator` repo, archived |
| State | Design record; milestone 0 (measure-and-decide) in progress. Motors and Teensy 4.1 ordered; driver in hand — its own since 2026-09-11, no longer borrowed from koala-bot (DEC-13, amended). **Motors on back order, due end of October 2026** (revised 2026-09-09) — milestone 1 waits on them |
| Chassis | DFRobot **ROB0128**, aluminium, 225 × 220 × 108 mm, 1.3 kg, 3 kg payload |
| Actuation | 2 × Pololu 25D 47:1 12 V gearmotors with 48 CPR encoders (DEC-11), replacing the kit's 6 V encoderless originals |
| Compute (decided, not built) | Teensy 4.1 on micro-ROS, the motor controller (reflex; its DEC-10) · Raspberry Pi 5 + AI HAT+ 2 + a camera not yet chosen, ROS 2 (intent; its DEC-15). The first build's Pi 4 is retired (DEC-14) |
| Start at | `AGENTS.md`, then `docs/concept.md` |
| Licence | Tri-licence: `CERN-OHL-S-2.0` hardware · `MIT` software · `CC-BY-SA-4.0` docs |

**Why it matters to the others:** it is the simplest body in the family — statically
stable, no gait, no balance loop — which makes it the cheapest second consumer of the
hexapod's navigation work, and the first plausible node of a fleet. It is the family's
**second intent-tier reference** (its DEC-15), a step above the hexapod: it adds the
reflex tier the hexapod lacks and an inference accelerator. See
[`ideas.md`](ideas.md#physical-ai-and-the-hive-mind).

**Shares with the rest:** the Pi + ROS 2 intent tier and the
[topic contract](common.md#the-topic-contract) with the hexapod; the printer, for mounts
and trays; koala-bot's driver and MCU selections. **No servo overlap** — it is a DC-motor
platform, so [the STS substrate](common.md#actuators) does not apply.

**The useful history:** the first build stalled on battery limitations and over-ambitious
scope — two depth cameras and a Pi 4 mounted before the drivetrain worked, through an
L298N losing ~2 V of a 6 V rail. It was under-powered by design. The project's rules and
its perception-last roadmap follow from that, and are recorded in its folder.

---

## SO-ARM101

**A Standard Open Arm** — the LeRobot-compatible low-cost manipulator designed by The
Robot Studio with Hugging Face, built here in its 12 V variant from the upstream design.
No fork: upstream is cloned read-only as the design authority. The build record was its
own repo, `wk-soarm101`, from 2026-09-09 to 2026-09-13 and is now a folder here.

| | |
|---|---|
| Where | [`projects/soarm101/`](../projects/soarm101/README.md) in this repo — the build record; `wk-soarm101` archived |
| Upstream | [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) — public, Apache-2.0, cloned not forked |
| State | Parts printed (11 of 11 at least once; `Wrist_Roll_Pitch` without a usable copy yet), assembled, calibrated and moving under script 2026-09-12 (milestones 1–3 done); teleoperation, camera and the 12 V supply decision still open |
| Actuation | Feetech STS3215 **12 V** bus servos on a Waveshare Bus Servo Adapter (A) |
| Material | White eSUN PLA+, 220 °C / 60 °C bed, supports avoided by orientation |
| Start at | `AGENTS.md`, then `docs/servos.md` |
| Licence | Tri-licence: `CERN-OHL-S-2.0` hardware · `MIT` software · `CC-BY-SA-4.0` docs. The arm design stays upstream's Apache-2.0 |

**Shares with the rest:** the STS3215 servo family with koala-bot, and its CAD is
vendored into koala-bot as reference. Its parts drove the PLA+ profile and the
press-fit findings in [`common.md`](common.md#press-fits-and-supports).

---

## edukit-rover

**A CamJam EduKit #3 robot in a 3D-printed chassis**, found built on 2026-09-20 and adopted as
the family's floor: the cheapest platform that can still host the intent tier. It lives in this
file rather than its own repo — no CAD and no roadmap yet (owner, 2026-09-20).

| | |
|---|---|
| Repo | None — this section is the record |
| State | Chassis printed and assembled with motors, the EduKit motor board, an HC-SR04 and the kit breadboard. **No Pi fitted, and never powered in this form** (owner, 2026-09-20) |
| Compute | Raspberry Pi 4 B, allocated from stock 2026-09-20 — the Devastator's obsolete first-build board ([its DEC-14](../projects/devastator/docs/decisions.md)). RAM unrecorded; no purchase record found |
| Actuation | 2× brushed DC motors through the EduKit dual H-bridge on the GPIO header, motor power from the kit's 4×AA box. **No encoders, so no wheel odometry** |
| Sensing | HC-SR04 ultrasonic on the printed nose. ECHO is 5 V and must reach the Pi through the kit's 330 Ω / 470 Ω divider — **confirm both resistors before first power-on**. The kit's line sensor is unaccounted for |
| Bought | CamJam EduKit #3, Amazon sold by The Pi Hut, 2019-12-19, £14.87. Was "on invoice only, in hand unknown" in the private `wk-inventory` repo until the owner found it built; moved here 2026-09-20 |
| Start at | This section |

**Why it is worth building.** [The two-tier split](common.md#compute-the-two-tier-split) puts the
intent tier on a Pi 5, and the hexapod is the baseline reference for it, but nothing has measured
the floor. This rover is statically stable — differential drive with a castor — so the
load-bearing rule that the balance loop lives on the MCU does not bite here. It can legitimately
run intent-only with no reflex tier at all, which almost nothing else in the family can.

**The binding constraint is sensing, not compute.** With no encoders there is no odometry, so no
SLAM and no Nav2: the platform supports reactive behaviour — wander, avoid, follow a line — and a
Pi 4 B is already over-specified for that. Finding where a Pi 4 actually strains means *adding*
sensing, a camera being the obvious step, not taking compute away. Either result is worth
recording against the hexapod's DEC-26.

**Open, and undecided by the owner:** whether it runs ROS 2 like the rest of the family or plain
Python on GPIO. **Power is a real question** — the 4×AA box drives the motors only, and a Pi 4 B
wants up to 3 A at 5 V where the kit assumed a Pi Zero or Pi 3, so it needs its own pack and
should not share the motor supply.

---

## Holybro 10" (wk-drones)

**The family's aerial robot candidate: a 10" multirotor bought to carry a Raspberry Pi or
Jetson hard-wired to its flight controller** — the onboard topology in
[`common.md`](common.md#aircraft-and-the-tiers). It is the only aircraft in the
[wk-drones](https://github.com/WayneKennedy/wk-drones) fleet that meets the family's robot
criterion. The others — a 3.5" ducted cinewhoop (Bee35, its DEC-07), a 5" freestyle quad and
several planes — fly under a human pilot and
are indexed only through the fleet repo.

| | |
|---|---|
| Repo | [WayneKennedy/wk-drones](https://github.com/WayneKennedy/wk-drones) `aircraft/holybro-10/` — public; the fleet record, `wk-drone-bee35` until 2026-09-13 |
| State | Parts identified from invoices 2026-09-17: Holybro X500 V2 frame kit, Matek H743 Wing V3 flight controller. Nothing flashed; build state unknown. Its `docs/bom.md`, `docs/decisions.md` and `docs/open-questions.md` are authoritative |
| Compute | Companion Pi or Jetson Orin Nano (intent), undecided — owner leaning Jetson (its OQ-03), wired by UART or USB to the Matek H743 Wing V3 (reflex) |
| Start at | `AGENTS.md` in wk-drones, then `aircraft/holybro-10/README.md` |
| Licence | `MIT`; not run as an OSS project |

**Why it differs from the rest:** the reflex tier is a flight controller running autopilot
firmware, not an MCU running the family's own code, and the intent tier is a payload the
airframe was chosen to carry. Two-way MAVLink from the flight controller is what lets
intent command it, so the firmware choice is not free: ArduPilot, not iNav. How it joins
the [topic contract](common.md#the-topic-contract) is unrecorded.

**Shares with the rest:** the printer, for mounts. With the other aircraft, not the ground
robots: the fleet's ELRS link, Walksnail video and 4S Li-Ion packs (wk-drones `fleet/`).
No servo or software overlap with the ground robots.

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
