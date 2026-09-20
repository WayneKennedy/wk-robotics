#!/bin/bash
# SPDX-License-Identifier: MIT
# Stop the bench and wait until the RealSense is released. Killing only `ros2 launch`
# can orphan realsense2_camera_node, which then holds /dev/video* and the next launch's
# camera loops on "Device or resource busy" at ~1 fps (found 2026-09-19).
for pat in "ros2 [l]aunch orin_perception" "perception_[n]ode" "realsense2_[c]amera_node" "web_[v]ideo_server"; do
  pgrep -f "$pat" | xargs -r kill 2>/dev/null
done
for i in $(seq 1 30); do pgrep -f "realsense2_[c]amera_node" >/dev/null || break; sleep 1; done
pgrep -f "realsense2_[c]amera_node" | xargs -r kill -9 2>/dev/null
sleep 3
echo "bench stopped; camera processes left: $(pgrep -f 'realsense2_[c]amera_node' | wc -l)"
