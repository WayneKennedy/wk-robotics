# firmware

Reflex-tier firmware for the on-robot MCU: quadrature decoding, the PID wheel-velocity
loop, motor PWM, and the safety watchdog. Runs
[micro-ROS](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#micro-ros-how-the-mcu-joins-the-graph),
so the MCU is a ROS 2 node rather than something behind a translation layer.

**Empty.** Nothing is written yet, but the target board is settled *and ordered* —
**Teensy 4.1** (DEC-10). Milestone 0 has not closed, and the motors are due ~26 September
(DEC-11); firmware written against the board alone need not wait for them. See
[`../docs/architecture.md`](../docs/architecture.md) for the topic contract this must
implement, and [`../docs/roadmap.md`](../docs/roadmap.md) for what milestone 1 requires.

Software here is `MIT` — add an `SPDX-License-Identifier: MIT` header to new files.
