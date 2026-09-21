#!/bin/bash
# SPDX-License-Identifier: MIT
# Install hailo-perception.service so the bench starts at boot. Mirrors wk-hexapod
# systemd/install.sh: fills in the repo path and user from the current checkout.
#   systemd/install.sh            # install and enable
#   systemd/install.sh --now      # and start it
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RUN_USER="${SUDO_USER:-$USER}"
RUN_HOME="$(getent passwd "$RUN_USER" | cut -d: -f6)"

if [[ ! -f "$REPO_DIR/ros2_ws/install/setup.bash" ]]; then
    echo "Workspace not built. Run: cd $REPO_DIR/ros2_ws && colcon build --symlink-install" >&2
    exit 1
fi

echo "Enabling systemd-time-wait-sync (bounded to 90 s so an offline boot still starts)"
sudo mkdir -p /etc/systemd/system/systemd-time-wait-sync.service.d
sudo cp "$SCRIPT_DIR/time-wait-sync-timeout.conf" \
    /etc/systemd/system/systemd-time-wait-sync.service.d/timeout.conf
sudo systemctl daemon-reload
sudo systemctl enable systemd-time-wait-sync.service

echo "Installing hailo-perception.service (user=$RUN_USER, repo=$REPO_DIR)"
sed -e "s|__USER__|$RUN_USER|g" \
    -e "s|__REPO_DIR__|$REPO_DIR|g" \
    -e "s|__HOME__|$RUN_HOME|g" \
    "$SCRIPT_DIR/hailo-perception.service" | sudo tee /etc/systemd/system/hailo-perception.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable ${1:-} hailo-perception.service

echo ""
echo "  sudo systemctl start|stop|restart hailo-perception"
echo "  sudo systemctl disable hailo-perception   # no auto-start"
echo "  journalctl -u hailo-perception -f"
echo "A manual scripts/launch.sh needs the service stopped first: both want the camera and :8080."
