#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# ROS 2 install for a mission-planner host (x86_64, Ubuntu 24.04: the GPU and the always-on workstation). Mirrors the family's
# reference install, wk-hexapod scripts/ubuntu-setup.sh, step for step where the role allows; see
# wk-robotics docs/common.md, "ROS 2 installs are familial". Deliberate differences from the
# reference: no timezone step (UTC is the rule for robots; this is not one), no config.txt, camera,
# udev, group or pip steps (no hardware, no Python deps yet), and message packages for decoding
# what the robots publish in place of drivers. Idempotent.
#
# Usage: sudo ./setup-host.sh [--skip-build]   (build is skipped anyway while ros2_ws/src is empty)
set -e
SKIP_BUILD=false
[[ "${1:-}" == "--skip-build" ]] && SKIP_BUILD=true
ACTUAL_USER="${SUDO_USER:-$USER}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export DEBIAN_FRONTEND=noninteractive
log()  { echo -e "\033[0;32m[INFO]\033[0m $1"; }
[[ $EUID -ne 0 ]] && { echo "Run with sudo" >&2; exit 1; }

# ---------------------------------------------------------------------------
log "Step 1: ROS 2 apt repository (ros2-apt-source, as the hexapod)"
if ! ls /etc/apt/sources.list.d/ros2* >/dev/null 2>&1; then
    apt-get install -y -qq curl
    V=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F tag_name | awk -F\" '{print $4}')
    curl -sL -o /tmp/ros2-apt-source.deb \
        "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${V}/ros2-apt-source_${V}.noble_all.deb"
    dpkg -i /tmp/ros2-apt-source.deb
else
    log "  already configured"
fi

# ---------------------------------------------------------------------------
log "Step 2: apt packages (ROS 2 Jazzy base, Fast DDS, the robots' message types)"
APT_PACKAGES=(
    ros-jazzy-ros-base ros-dev-tools python3-colcon-common-extensions python3-rosdep python3-vcstool
    ros-jazzy-rmw-fastrtps-cpp
    # Message types the robots publish beyond ros-base's common_interfaces: the perception
    # benches (vision_msgs) and the hexapod's Nav2 stack (nav2_msgs).
    ros-jazzy-vision-msgs ros-jazzy-nav2-msgs
)
apt-get update -qq
apt-get install -y -qq --no-install-recommends "${APT_PACKAGES[@]}"

# ---------------------------------------------------------------------------
log "Step 3: rosdep"
[[ -f /etc/ros/rosdep/sources.list.d/20-default.list ]] || rosdep init
sudo -u "$ACTUAL_USER" rosdep update

# ---------------------------------------------------------------------------
if $SKIP_BUILD || [[ -z "$(find "$REPO_DIR/ros2_ws/src" -name package.xml 2>/dev/null)" ]]; then
    log "Step 4: workspace build skipped"
else
    log "Step 4: build workspace"
    sudo -u "$ACTUAL_USER" bash -c "source /opt/ros/jazzy/setup.bash && cd '$REPO_DIR/ros2_ws' && \
        rosdep install --from-paths src --ignore-src -y -r && colcon build --symlink-install"
fi

echo ""
log "Setup complete.  Shell:  source scripts/ros-env.sh   then   ros2 topic list"
echo "SETUP-OK $(date -Is)"
