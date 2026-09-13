# References

## The platform

- [DFRobot Devastator, The Pi Hut listing](https://thepihut.com/products/devastator-tank-mobile-robot-platform-metal-dc-gear-motor)
  — ROB0128, the exact SKU owned. £81.60 inc VAT, checked 2026-09-07.
- DFRobot product wiki (`wiki.dfrobot.com`) — instruction manual and example code.
  The example code is for the original Arduino-based build and is not a basis for this one.

## Software

- [micro-ROS](https://micro.ros.org/) — the ROS 2 client library for microcontrollers.
- [`micro-ROS/micro_ros_arduino`](https://github.com/micro-ROS/micro_ros_arduino) — the
  Arduino/Teensy library, and the authority on board support (see DEC-10).
- [Zenoh](https://zenoh.io/) — `rmw_zenoh` and `zenoh-bridge-ros2dds`, the candidate
  transport for links that leave one LAN segment (OQ-05).
- [Nav2](https://docs.nav2.org/) and `slam_toolbox` / RTAB-Map — reuse the hexapod's
  configuration rather than deriving a new one.

## The arm

- [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) — the **Standard
  Open Arm** this robot is intended to carry (Apache-2.0). The repo name is the
  *repository*, not the revision: it ships both SO-100 and SO-101, and the family builds
  the **SO-101 follower**. Its CAD is already vendored into koala-bot as servo reference.
- [LeKiwi](https://github.com/SIGRobotics-UIUC/LeKiwi) — the same arm on a **holonomic
  three-omniwheel** base, Pi 5, LeRobot-native. The closest prior art to milestone 5, and
  the sharpest illustration of where a tracked skid-steer differs: it cannot strafe.
- [LeRobot](https://github.com/huggingface/lerobot) — the learning and teleoperation stack
  the SO-101 ecosystem is built around.

## Family

- [wk-robotics](https://github.com/WayneKennedy/wk-robotics) — the index, and everything
  true of more than one robot.
- [wk-hexapod](https://github.com/WayneKennedy/wk-hexapod) — the SLAM, Nav2 and
  RealSense work this project is intended to reuse. **The most directly relevant
  repository to read before milestone 2.**
- [koala-bot](https://github.com/WayneKennedy/koala-bot) — the two-tier architecture,
  the driver and MCU selections, and the sourcing notes this project inherits.
