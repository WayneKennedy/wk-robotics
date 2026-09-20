#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Run on a workstation: sync this project folder to the Jetson and colcon-build it there.
# The folder lands where a repo checkout would (~/Code/wk-robotics/projects/orin-perception),
# so the host follows the family layout (workspace inside the checkout, as the hexapod).
# Once the branch is on origin this becomes `git pull` on the host.
#   ./deploy.sh <jetson-ssh-host>
set -euo pipefail
HOST=${1:?usage: deploy.sh <jetson-ssh-host>}
HERE=$(cd "$(dirname "$0")/.." && pwd)
DEST='~/Code/wk-robotics/projects/orin-perception'
ssh "$HOST" "mkdir -p $DEST"
rsync -a --delete --exclude __pycache__ --exclude 'ros2_ws/build' --exclude 'ros2_ws/install' --exclude 'ros2_ws/log' \
      "$HERE/" "$HOST:$DEST/"
ssh "$HOST" "source /opt/ros/jazzy/setup.bash && cd $DEST/ros2_ws && colcon build --symlink-install 2>&1 | tail -3"
