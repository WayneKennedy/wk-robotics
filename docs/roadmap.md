# Roadmap

**Drivetrain first, perception last** (DEC-06). The first build mounted two depth
cameras and a Pi before the drive worked, and never ran. This inverts that order
deliberately.

Each milestone ends with a **robot that works** — not a subsystem that might.

## Milestone 0 — Decide and measure *(current)*

No purchases. Close the questions that gate everything else:

1. **Measure the motor bracket and the sprocket shaft** (OQ-11). Nothing can be ordered
   until a replacement motor is known to fit.
2. **Resolve the motor question** (OQ-01) — the rail voltage, and therefore the battery
   and driver, follow from it.
3. **Flash a micro-ROS example to the Teensy 4.0** (OQ-03). Upstream lists it as "Not
   tested"; ten minutes now beats discovering it mid-firmware.
4. **Compute the power budget** (DEC-07) at realistic duty, with stall headroom.

**Exit:** OQ-01, OQ-03 and OQ-11 closed; a power budget exists on paper.

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
