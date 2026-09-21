#!/bin/bash
# SPDX-License-Identifier: MIT
# Source ROS 2 Jazzy and the workspace, set the family's environment, launch the bench.
# Mirrors wk-hexapod scripts/launch.sh.
#   scripts/launch.sh                              # bench.launch.py, yolov8s
#   scripts/launch.sh yolo_engine:=yolov8m.engine  # any launch argument
#   scripts/launch.sh other.launch.py [args]
set -e
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
# Bench deviation from the family default: discovery limited to this host. On the shared LAN
# the hexapod's whole graph (domain 0) is visible here, and its /camera/camera/color/image_raw
# collides with the D435i's by name (found 2026-09-19; wk-robotics docs/common.md, ROS 2 audit).
export ROS_AUTOMATIC_DISCOVERY_RANGE="${ROS_AUTOMATIC_DISCOVERY_RANGE:-LOCALHOST}"
# Before sourcing ROS: its ros_environment hook sets ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET if unset,
# which silently defeated a default applied afterwards (found 2026-09-21).
source /opt/ros/jazzy/setup.bash
source "$REPO_DIR/ros2_ws/install/setup.bash"
LAUNCH_FILE="bench.launch.py"
if [[ "${1:-}" == *.launch.py ]]; then LAUNCH_FILE="$1"; shift; fi
exec ros2 launch orin_perception "$LAUNCH_FILE" "$@"
