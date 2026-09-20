#!/bin/bash
# SPDX-License-Identifier: MIT
# Stop the bench and wait until the camera is released. Mirrors
# projects/orin-perception/scripts/stop.sh.
#
# NOTE THE BRACKETS, e.g. perception_[n]ode. A plain `pkill -f perception_node` also matches
# the command line of the shell running it, so `ssh <host> 'pkill -f perception_node'` kills
# its own session mid-sequence — leaving usb_cam and web_video_server orphaned holding the
# camera, so the next launch fails. The bracket makes the pattern not match its own text.
# For the same reason: always stop the bench by running THIS FILE on the host, never by
# pasting an inline pkill into an ssh command. (Hit 2026-09-20 during the move to a checkout.)
for pat in "ros2 [l]aunch hailo_perception" "perception_[n]ode" "usb_cam_node_[e]xe" "web_[v]ideo_server"; do
  pgrep -f "$pat" | xargs -r kill 2>/dev/null
done
for i in $(seq 1 30); do pgrep -f "usb_cam_node_[e]xe" >/dev/null || break; sleep 1; done
pgrep -f "usb_cam_node_[e]xe" | xargs -r kill -9 2>/dev/null
sleep 2
echo "bench stopped; camera processes left: $(pgrep -f 'usb_cam_node_[e]xe' | wc -l)"
