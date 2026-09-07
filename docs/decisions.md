# Banked Decisions

Committed decisions with rationale. Unresolved items live in
[`open-questions.md`](open-questions.md). Format: `DEC-nn — decision — why`.

**Provenance matters here.** This project is at the stage where most of the interesting
choices are *not yet made*. A decision appears below only if the owner made it, or if it
follows necessarily from one that was made. **Recommendations that have been offered but
not accepted are open questions, not decisions**, and are marked as such there.

---

- **DEC-01 — Resurrect the project; keep the mechanical chassis, replace everything
  above it.** (Owner, 2026-09-07.) The DFRobot Devastator is a high-quality aluminium
  platform that is already paid for and already assembled. The electronics, compute and
  software of the first build are all superseded. This is what makes the project a
  resurrection rather than a fresh start, and it bounds the work: no chassis design.

- **DEC-02 — Target ROS 2, with the reflex tier on a 32-bit MCU running micro-ROS.**
  (Owner, 2026-09-07.) The robot joins the family
  [topic contract](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#the-topic-contract)
  rather than carrying a private protocol. Which board runs it is DEC-10.

- **DEC-03 — The fitted Arduino Nano and L298N are retired.** Follows necessarily from
  DEC-02 and from the family's own sourcing rules: the Nano is an 8-bit AVR and
  [micro-ROS requires a 32-bit target](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#micro-ros-how-the-mcu-joins-the-graph),
  and the L298N is the driver koala-bot explicitly rejected for its ~2 V drop. What
  replaces the driver is OQ-02.

- **DEC-04 — Three tiers, and each stays useful when the tier above it is unreachable.**
  Derived from DEC-02 and DEC-05. The coordinator is a desktop that will frequently be
  off or busy, so treating its absence as an outage would make the fleet useless most of
  the time. Reflex does not wait on intent; intent does not wait on coordination. See
  [`architecture.md`](architecture.md#the-load-bearing-rule).

- **DEC-05 — The family GPU workstation is the coordination-tier machine.** (Owner,
  2026-09-07.) It is the only GPU in the family and therefore the only candidate for a
  reasoning tier. Its constraints — Blackwell toolchain, NAT'd networking, desktop
  availability — are recorded in the family repo, and the third of them is the direct
  cause of DEC-04.

- **DEC-06 — Scope discipline: the drivetrain works before anything is mounted on top.**
  The owner's own account records the first build stalling on over-ambitious scope, with
  two depth cameras and a Pi mounted before the drive worked. Inverting that order is the
  single most evidence-backed choice available to this project. See
  [`roadmap.md`](roadmap.md).

- **DEC-07 — The power budget is computed before parts are bought.** The first build was
  [under-powered by design](concept.md#the-first-build-and-why-it-stopped), not abandoned
  for lack of interest. Power is therefore a design input for this build, and purchases
  follow the budget rather than producing it.

- **DEC-08 — Tri-licence**, matching the family standard: `CERN-OHL-S-2.0` hardware,
  `MIT` software, `CC-BY-SA-4.0` docs. See [`LICENSING.md`](../LICENSING.md). The
  purchased chassis is third-party and is not relicensed by this repo.

- **DEC-09 — The repository is the memory.** No project fact, measurement or decision
  lives only in a chat log or an assistant's private memory. This repo is public, so
  capabilities may be described but the machines providing them are never named.

- **DEC-10 — The MCU is a Teensy 4.1.** (Owner, 2026-09-07.) Upstream lists the **4.1 as
  Supported** and the **4.0 as "Not tested"** — the board table and the checked date are a
  family fact and live
  [in wk-robotics](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#micro-ros-how-the-mcu-joins-the-graph).
  Two things closed this together. **This robot must buy an MCU regardless:** koala-bot's
  Teensy 4.0 is not spare — qty 1 in its confirmed order, purchased 2026-09-01
  (`koala-bot/docs/sourcing.md`). And **the owner will not buy a second untested board**:
  any Teensy bought from here is a 4.1. Buying the supported part rather than the one that
  needs proving takes the bench test off this project's critical path entirely. Resolves
  the former OQ-03; the equivalent question stays live for koala-bot, which owns the 4.0.

- **DEC-11 — The drive motors are two Pololu #4865, end caps removed.** (Owner,
  2026-09-07.) *47:1 Metal Gearmotor 25Dx67L mm MP 12V with 48 CPR Encoder.* **12 V ·
  46.85:1 · 170 RPM no-load · 6.4 kg·cm and 1.8 A stall · 4 mm D shaft standing 12.5 mm
  proud · 48 CPR → 2248.86 counts per output revolution.** Against the fitted 6 V motors
  that is more speed, more torque and *less* stall current. Resolves OQ-01, and the rail
  follows as DEC-12.

  **It fits on measured numbers, not assumed ones** ([`test-log.md`](test-log.md),
  2026-09-07): the M3 mounting centres are **17 mm** on both the Devastator bracket and
  the Pololu face plate, and with the end caps removed the pair occupies **~129 mm of the
  134 mm** between the side frames, encoder leads exiting **radially**. With the caps on
  it is 134 mm in 134 mm and does not fit.

  **Encoders were kept deliberately**, though a tracked skid-steer's odometry is
  [weak by construction](architecture.md#odometry-is-weak-by-construction). Their job here
  is the **velocity PID**, not pose. An encoder-less variant — open-loop PWM, an IMU
  yaw-rate loop, position fixed by camera — was considered and rejected: an IMU gives
  heading rate but never linear velocity, and visual odometry runs at the intent tier and
  cannot close a 200–1000 Hz loop, so forward speed would stay open-loop. Milestone 1
  could then not deliver the closed-loop wheel velocity
  [`concept.md`](concept.md#what-the-resurrection-does-differently) promises *before* a
  camera is mounted, which inverts DEC-06; and it would blunt the robot as a Nav2
  portability test, its second stated purpose.

  **Ordered 2026-09-07 and on back order** — ~£50 each, RobotShop UK.

- **DEC-12 — The rail is 12 V from a 3S LiPo.** Follows necessarily from DEC-11 and from
  the arm (OQ-12): the motors and the SO-101's STS3215 servos are both 12 V parts, and 3S
  is [the family ceiling for the STS3215](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#actuators)
  — 12.6 V full, inside the servos' 14 V limit where 4S is not. This **closes OQ-08**:
  with no 6 V motor rail there is nothing for the as-found DC-DC converter to do, so it is
  discarded rather than identified. Capacity, fuse rating and the logic-rail regulator
  stay open (OQ-07).
