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

for pat in "ros2 [l]aunch hailo_perception" "perception_[n]ode" "usb_cam_node_[e]xe" "web_[v]ideo_server"; do
  kill_matching "$pat"
done
for i in $(seq 1 30); do [ "$(count_matching "usb_cam_node_[e]xe")" -eq 0 ] && break; sleep 1; done
kill_matching "usb_cam_node_[e]xe" -9
sleep 2
echo "bench stopped; camera processes left: $(count_matching "usb_cam_node_[e]xe")"
