# firmware

Reflex-tier firmware for the on-robot MCU: quadrature decoding, the PID wheel-velocity
loop, motor PWM, and the safety watchdog. Runs
[micro-ROS](memory://main/robotics/robotics-common),
so the MCU is a ROS 2 node rather than something behind a translation layer.

**Empty.** Nothing is written yet; the target board, a **Teensy 4.1** (DEC-10), is in hand
since 2026-10-14, as are the motors and driver. The proposed pin assignment, the driver's
breakout wiring, the watchdog behaviour and the host link are in
[*Devastator Electronics*](memory://main/robotics/devastator/devastator-electronics)
— confirm the pins against the Teensy 4.1 pin card before wiring, and record the as-built
there. See [*Devastator Architecture*](memory://main/robotics/devastator/devastator-architecture) for the topic contract this
must implement, and [*Devastator Roadmap*](memory://main/robotics/devastator/devastator-roadmap) for what milestone 1 requires.

Software here is `MIT` — add an `SPDX-License-Identifier: MIT` header to new files.
