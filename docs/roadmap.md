# Roadmap

**Drivetrain first, perception last** (DEC-06) — and the arm last of all. The first build
mounted two depth cameras and a Pi before the drive worked, and never ran. This inverts
that order deliberately.

Each milestone ends with a **robot that works** — not a subsystem that might.

## Milestone 0 — Decide and measure *(current)*

Close the questions that gate everything else.

1. ~~**Measure the motor bracket and the sprocket shaft**~~ — **done 2026-09-07**
   ([`test-log.md`](test-log.md)). 25 × 52 mm envelope, 4 mm D shaft, M3 at 17 mm centres,
   134 mm between frames, and the side plates clear the motor hub.
2. ~~**Resolve the motor question**~~ — **done, DEC-11.** Two Pololu #4865, caps removed.
   The rail follows as DEC-12: 12 V from a 3S pack.
3. **Compute the power budget** (DEC-07) at realistic duty, with stall headroom. **This is
   the frontier**, and every number it needs now exists: 1.8 A stall per motor (DEC-11),
   the arm's draw ([`architecture.md`](architecture.md#the-arm-rewrites-the-budget)), and
   the Pi and MCU.
4. **Weigh the SO-ARM101 parts as they come off the plate** (OQ-12). The arm's real mass
   decides whether the tipping arithmetic is marginal or comfortable, and the parts are
   being printed regardless.
5. ~~**Check the shaft/hub interface**~~ — **done 2026-09-07.** The side plates have a
   clearance hole for the hub; nothing bottoms out. Closed OQ-11, the only risk that was
   carried into the motor purchase.

**The motors are on back order, due end of October 2026** (supplier update 2026-09-09; was ~26 September), so milestone 1 cannot start.
**Milestone 0 is not blocked by it:** items 3 and 4 need no motors, and neither does
OQ-10. The Teensy 4.1 is ordered and the driver is in hand (DEC-13), so only the measured
current draw actually waits on delivery.

**Exit:** a power budget on paper, and the arm's real mass measured. The MCU needs no bench
proving — DEC-10 buys the upstream-supported board instead.

## Milestone 1 — A robot that drives *(no perception at all)*

Chassis + motors + driver + MCU + battery. Nothing on top.

- Reflex firmware: quadrature decoding, PID wheel-velocity loop, motor PWM, watchdog.
- micro-ROS on the MCU, agent on a host: the robot appears in `ros2 topic list`.
- Subscribes `/cmd_vel`, publishes `/wheel_odom`, `/joint_states`, `/telemetry`.
- Teleoperation end to end, and a **watchdog test**: cut the host link and confirm the
  robot stops safely rather than continuing on its last command.

**Exit:** it drives from a joystick over ROS 2, reports telemetry, and fails safe.
This is a complete robot. **It is allowed to stay here indefinitely** — the next
milestone is optional in a way this one is not.

## Milestone 2 — A robot that sees

Add the intent tier: a Pi (OQ-06), **one** camera (OQ-09), SLAM.

- URDF and TF tree, camera frames included.
- One depth camera; RTAB-Map or `slam_toolbox`, reusing the hexapod's configuration
  rather than deriving a new one.
- Pose and heading strategy resolved (OQ-04) — wheel odometry is not trusted for
  rotation.

**Exit:** it builds and holds a map of a room while being driven.

## Milestone 3 — A robot that navigates

Nav2 on the hexapod's tuning as a starting point, adjusted for a faster, continuously
steerable base.

**Exit:** a commanded goal pose is reached autonomously, and recovery behaviours work.

## Milestone 4 — A fleet node

The point of the project (see [`concept.md`](concept.md#what-it-is-for)): this robot and
the hexapod on one contract, reporting to the coordination tier.

- Transport decided and working across the network boundary (OQ-05).
- Fleet time sync.
- Shared world model; the map-merge problem met honestly rather than assumed away.
- **Degradation test:** power the coordinator off mid-mission. Both robots must keep
  working (DEC-04). If they do not, the architecture is wrong and this milestone has
  failed regardless of what else works.

**Exit:** two robots, one contract, one coordinator, and no single point of failure
below it.

## Milestone 5 — A robot that carries an arm

The reason the kit came out of its box ([`concept.md`](concept.md#what-it-is-for)).
**Depends on milestone 2, not on milestone 4** — it needs the Pi, and may be taken before
the fleet node.

- Mount and reach envelope designed against **measured** masses (OQ-12), not assumed ones.
- The arm sits on the **intent tier**: STS3215s on a half-duplex TTL bus from the Pi, not
  from the reflex MCU.
- **Base positioning is coarse by construction.** A skid-steer cannot strafe, and its
  heading is [not trustworthy](architecture.md#odometry-is-weak-by-construction). Absorb
  that in the arm's workspace and an eye-in-hand camera rather than in base odometry.
  [LeKiwi](https://github.com/SIGRobotics-UIUC/LeKiwi) — the same arm on a holonomic
  three-omniwheel base — chose that drive precisely to avoid the problem. That choice is
  not available here (DEC-01 keeps the chassis), so it is a limitation to design around
  rather than one to fix.
- **Honest caveat:** LeRobot teleoperation and policy inference want an off-robot machine,
  which is the coordination tier DEC-04 expects to be *absent*. Manipulation is the one
  capability here that does **not** survive losing the tier above it, unless a policy runs
  onboard.

**Exit:** the base drives to an object, the arm picks it up and puts it somewhere else —
and it does not tip.
