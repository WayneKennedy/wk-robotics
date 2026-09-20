#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# Host setup for the Orin perception bench (Jetson Orin Nano, JetPack 7.2.1 / L4T R39.2.1,
# Ubuntu 24.04). Mirrors the family's reference ROS 2 install, wk-hexapod
# scripts/ubuntu-setup.sh, step for step where the hardware allows (see wk-robotics
# docs/common.md, "ROS 2 across the family", for the deliberate differences). Idempotent.
#
# Usage: sudo ./setup-orin.sh [--skip-build]   (log: ~/setup-orin.log)
set -e
SKIP_BUILD=false
[[ "${1:-}" == "--skip-build" ]] && SKIP_BUILD=true
ACTUAL_USER="${SUDO_USER:-$USER}"
HOME_DIR=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export DEBIAN_FRONTEND=noninteractive
log()  { echo -e "\033[0;32m[INFO]\033[0m $1"; }
[[ $EUID -ne 0 ]] && { echo "Run with sudo" >&2; exit 1; }

# ---------------------------------------------------------------------------
log "Step 1: JetPack SDK (CUDA 13, TensorRT 10, cuDNN, OpenCV) from the r39.2 NVIDIA apt source"
# Jetson-only step; the Pi hosts have no equivalent. --no-install-recommends as the family does.
apt-get update -qq
apt-get install -y -qq --no-install-recommends nvidia-jetpack python3-libnvinfer python3-libnvinfer-dev

# ---------------------------------------------------------------------------
log "Step 2: ROS 2 apt repository (ros2-apt-source, as the hexapod)"
if ! ls /etc/apt/sources.list.d/ros2* >/dev/null 2>&1; then
    apt-get install -y -qq curl
    V=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F tag_name | awk -F\" '{print $4}')
    curl -sL -o /tmp/ros2-apt-source.deb \
        "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${V}/ros2-apt-source_${V}.noble_all.deb"
    dpkg -i /tmp/ros2-apt-source.deb
    apt-get update -qq
else
    log "  already configured"
fi

# ---------------------------------------------------------------------------
log "Step 3: apt packages (ROS 2 Jazzy base, RealSense, web_video_server, Python libs)"
APT_PACKAGES=(
    ros-jazzy-ros-base ros-dev-tools python3-colcon-common-extensions python3-rosdep python3-vcstool
    ros-jazzy-rmw-fastrtps-cpp
    ros-jazzy-realsense2-camera ros-jazzy-web-video-server
    ros-jazzy-cv-bridge ros-jazzy-image-transport ros-jazzy-vision-msgs ros-jazzy-diagnostic-updater
    python3-numpy python3-opencv python3-pip python3-dev build-essential cmake
    v4l-utils
)
apt-get install -y -qq --no-install-recommends "${APT_PACKAGES[@]}"

# ---------------------------------------------------------------------------
log "Step 4: udev rules (RealSense as non-root)"
if [[ ! -f /etc/udev/rules.d/99-realsense-libusb.rules ]]; then
    curl -sL -o /etc/udev/rules.d/99-realsense-libusb.rules \
        https://raw.githubusercontent.com/IntelRealSense/librealsense/master/config/99-realsense-libusb.rules
    udevadm control --reload-rules && udevadm trigger
else
    log "  present"
fi

# ---------------------------------------------------------------------------
log "Step 5: user groups for $ACTUAL_USER"
for grp in dialout video plugdev render; do
    if getent group "$grp" >/dev/null && ! id -nG "$ACTUAL_USER" | grep -qw "$grp"; then
        usermod -aG "$grp" "$ACTUAL_USER"; log "  added to $grp"
    fi
done

# ---------------------------------------------------------------------------
log "Step 6: pip packages (system interpreter, no venv — as the hexapod)"
sudo -u "$ACTUAL_USER" pip3 install --break-system-packages -r "$REPO_DIR/requirements.txt"

# ---------------------------------------------------------------------------
log "Step 7: rosdep"
[[ -f /etc/ros/rosdep/sources.list.d/20-default.list ]] || rosdep init
sudo -u "$ACTUAL_USER" rosdep update

# ---------------------------------------------------------------------------
if $SKIP_BUILD; then
    log "Step 8: workspace build skipped"
else
    log "Step 8: build workspace"
    sudo -u "$ACTUAL_USER" bash -c "source /opt/ros/jazzy/setup.bash && cd '$REPO_DIR/ros2_ws' && \
        rosdep install --from-paths src --ignore-src -y -r && colcon build --symlink-install"
fi

echo ""
log "Setup complete. Log out and in if group membership changed."
log "  Engines:  scripts/build-engines.sh      Run: scripts/launch.sh      Numbers: scripts/bench-record.sh"
echo "SETUP-OK $(date -Is)"
