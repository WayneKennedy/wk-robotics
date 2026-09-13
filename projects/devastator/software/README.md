# software

Intent-tier ROS 2 packages that run on the robot's Pi: bringup and launch, URDF, SLAM
and Nav2 configuration, mission logic.

**Empty**, and deliberately so until milestone 2 — milestone 1 carries no Pi and no
perception at all (DEC-06). Where possible this should *reuse*
[wk-hexapod](https://github.com/WayneKennedy/wk-hexapod)'s configuration rather than
derive its own; being the second consumer of that stack is the point of this robot.

Software here is `MIT` — add an `SPDX-License-Identifier: MIT` header to new files.
