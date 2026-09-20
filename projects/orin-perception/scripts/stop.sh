#!/bin/bash
# SPDX-License-Identifier: MIT
# Stop the bench and wait until the RealSense is released. Killing only `ros2 launch`
# can orphan realsense2_camera_node, which then holds /dev/video* and the next launch's
# camera loops on "Device or resource busy" at ~1 fps (found 2026-09-19).
# Never kill ourselves or an ancestor. The bracketed patterns below stop pgrep matching its
# own command line, but NOT a caller's: an ssh session whose command happens to mention a node
# name is matched by `pgrep -f` and killed, which severs the connection mid-sequence and
# orphans the rest (hit twice on 2026-09-20). Collect this shell and every ancestor and skip
# them.
SAFE="$$"
_p=$PPID
while [ -n "$_p" ] && [ "$_p" -gt 1 ]; do
  SAFE="$SAFE|$_p"
  _p=$(ps -o ppid= -p "$_p" 2>/dev/null | tr -d ' ')
done
kill_matching() { pgrep -f "$1" | grep -Ev "^($SAFE)\$" | xargs -r kill ${2:-} 2>/dev/null; }
count_matching() { pgrep -f "$1" | grep -Evc "^($SAFE)\$"; }

for pat in "ros2 [l]aunch orin_perception" "perception_[n]ode" "realsense2_[c]amera_node" "web_[v]ideo_server"; do
  kill_matching "$pat"
done
for i in $(seq 1 30); do [ "$(count_matching "realsense2_[c]amera_node")" -eq 0 ] && break; sleep 1; done
kill_matching "realsense2_[c]amera_node" -9
sleep 3
echo "bench stopped; camera processes left: $(count_matching "realsense2_[c]amera_node")"
