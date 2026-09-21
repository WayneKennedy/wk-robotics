#!/bin/bash
# SPDX-License-Identifier: MIT
# Install orin-perception.service so the bench starts at boot. Mirrors wk-hexapod
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

# Linger, so logind never counts the service user as logged out. Without it, RemoveIPC=yes
# (Ubuntu's default) deletes the user's /dev/shm when the last SSH session closes, taking
# Fast DDS's shared-memory transport with it: nodes keep running, frames stop (2026-09-21).
echo "Enabling linger for $RUN_USER"
sudo loginctl enable-linger "$RUN_USER"

echo "Installing orin-perception.service (user=$RUN_USER, repo=$REPO_DIR)"
sed -e "s|__USER__|$RUN_USER|g" \
    -e "s|__REPO_DIR__|$REPO_DIR|g" \
    -e "s|__HOME__|$RUN_HOME|g" \
    "$SCRIPT_DIR/orin-perception.service" | sudo tee /etc/systemd/system/orin-perception.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable ${1:-} orin-perception.service

echo ""
echo "  sudo systemctl start|stop|restart orin-perception"
echo "  sudo systemctl disable orin-perception   # no auto-start"
echo "  journalctl -u orin-perception -f"
echo "A manual scripts/launch.sh needs the service stopped first: both want the camera and :8080."
