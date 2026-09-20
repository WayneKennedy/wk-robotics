#!/bin/bash
# SPDX-License-Identifier: MIT
# Source ROS 2 Jazzy and the workspace, set the family's environment, launch the bench.
# Mirrors wk-hexapod scripts/launch.sh and projects/orin-perception/scripts/launch.sh.
#   scripts/launch.sh                           # bench.launch.py
#   scripts/launch.sh video_device:=/dev/video2 # any launch argument
#   scripts/launch.sh other.launch.py [args]
set -e
SW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source /opt/ros/jazzy/setup.bash
source "$SW_DIR/ros2_ws/install/setup.bash"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
# Bench deviation from the family default, the same one the Orin bench makes: discovery is
# limited to this host. On the shared LAN the hexapod's whole graph (domain 0) is visible
# here, and its /camera/camera/color/image_raw collides by name with a local camera's. On
# the Orin that contention cost 35x throughput (wk-robotics docs/common.md, ROS 2 audit).
export ROS_AUTOMATIC_DISCOVERY_RANGE="${ROS_AUTOMATIC_DISCOVERY_RANGE:-LOCALHOST}"
LAUNCH_FILE="bench.launch.py"
if [[ "${1:-}" == *.launch.py ]]; then LAUNCH_FILE="$1"; shift; fi

# usb_cam rejects a symlink, and the C920 clone has re-enumerated mid-run (2026-09-19), so
# /dev/videoN is not stable. Resolve the stable by-id path to its real node unless the
# caller passed video_device: themselves.
ARGS=("$@")
if [[ ! " ${ARGS[*]} " == *" video_device:="* ]]; then
    BYID=$(ls /dev/v4l/by-id/*-video-index0 2>/dev/null | head -1)
    RESOLVED=$(readlink -f "$BYID" 2>/dev/null)
    ARGS+=("video_device:=${RESOLVED:-/dev/video0}")
fi
exec ros2 launch hailo_perception "$LAUNCH_FILE" "${ARGS[@]}"
