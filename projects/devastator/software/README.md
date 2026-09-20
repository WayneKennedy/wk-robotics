# software

Intent-tier ROS 2 packages that run on the robot's Pi: bringup and launch, URDF, SLAM
and Nav2 configuration, mission logic.

**Layout:** `ros2_ws/src/<package>/`, the family's standard — a colcon workspace inside the
checkout, built with `--symlink-install`, as
[wk-hexapod](https://github.com/WayneKennedy/wk-hexapod) and
[`projects/orin-perception/`](../../orin-perception/AGENTS.md) do. See
[*ROS 2 installs are familial*](../../../docs/common.md#ros-2-installs-are-familial).

**Contents.** `hailo_perception` — the intent-tier perception node (objects and face
recognition on an AI HAT+ 2), developed and measured on the family's bench Pi 5, not on the
robot: milestone 1 carries no Pi and no perception at all (DEC-06). The bringup, URDF, SLAM
and Nav2 configuration are still to come. Where possible they should *reuse*
[wk-hexapod](https://github.com/WayneKennedy/wk-hexapod)'s configuration rather than
derive its own; being the second consumer of that stack is the point of this robot.

Software here is `MIT` — add an `SPDX-License-Identifier: MIT` header to new files.
