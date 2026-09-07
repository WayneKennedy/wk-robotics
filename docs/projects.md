# Projects

Per-project detail. Each section says what the project is, what it runs on, where its
documentation starts, and what it shares with the others. The authoritative record for
any one project is that project's own repository — this page is a pointer, and is
accurate as of **2026-09-07**.

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
| State | Pre-alpha, design phase. CAD started, fit coupons printed, V1 hardware ordered |
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
| State | Locomotion, odometry and perception complete; SLAM, Nav2 and autonomy in progress |
| Compute | Raspberry Pi 5 (8 GB), ROS 2 Jazzy on Ubuntu Server 24.04 |
| Actuation | 20 servos (18 leg + 2 head) via PCA9685 — direct from the Pi, no reflex MCU |
| Sensing | RealSense D435i (RGB-D + IMU) · MPU6050 body IMU · ADS7830 ADC for dual-battery monitoring |
| Reference | [WayneKennedy/fn-hexapod](https://github.com/WayneKennedy/fn-hexapod) — Freenove vendor code; confirmed-working `servo.py`, `home.py`, `stand.py`, `control.py` |
| Not checked out | Neither repo is currently cloned under `~/Code/` |

**Progress by phase:** locomotion (IK + tripod gait, `/cmd_vel`, poses) — done. Odometry
(gait integration, `/odom`, `odom`→`base_link` TF, IMU complementary filter,
`MoveDistance` action) — done. Perception (D435i, depth-to-laserscan, URDF camera frames)
— done. SLAM (`slam_toolbox` and RTAB-Map configured; untested against the physical D435i)
— in progress. Navigation (Nav2 tuned for slow hexapod motion; planners, semantic
waypoints and return-to-home outstanding) — in progress. Autonomy (systemd auto-start
done; mission queue, battery-aware behaviour and wander mode outstanding) — in progress.

**Shares with the rest:** the Pi 5 + ROS 2 tier and the `/cmd_vel` · `/odom` · `/imu`
topic vocabulary with koala-bot. It is the counter-example to the two-tier rule — servos
are driven straight off the Pi via PCA9685, which is viable for a statically stable
walker in a way it would not be for a balancing robot.

---

## SO-ARM101

**A Standard Open Arm** — the LeRobot-compatible low-cost manipulator designed by The
Robot Studio with Hugging Face. Being built from the upstream design; there is no fork,
the upstream repo is cloned directly and the build record lives in the printing log.

| | |
|---|---|
| Upstream | [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) — public, Apache-2.0 |
| State | Printing the follower arm — plate 1 of 4 complete (2026-09-07), 4 parts clean |
| Actuation | Feetech STS3215 bus servos |
| Material | White eSUN PLA+, 220 °C / 60 °C bed, no supports |
| Build record | The print log in the private `3d-printing` repo |

**Shares with the rest:** the STS3215 servo family with koala-bot, and its CAD is
vendored into koala-bot as reference. Its parts drove the PLA+ profile and the
press-fit findings in [`common.md`](common.md#press-fits-and-supports).

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
