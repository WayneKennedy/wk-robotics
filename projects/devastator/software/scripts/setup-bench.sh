#!/bin/bash
#
# Host setup for the AI HAT+ 2 perception bench (Raspberry Pi 5, Ubuntu Server 24.04).
# Mirrors the family's reference ROS 2 install, wk-hexapod scripts/ubuntu-setup.sh, step for
# step where the hardware allows (see wk-robotics docs/common.md, "ROS 2 installs are
# familial", for the deliberate differences). Idempotent: safe to re-run.
#
# Usage: sudo ./setup-bench.sh [--skip-build] [--skip-models]
#
set -e
SKIP_BUILD=false
SKIP_MODELS=false
for a in "$@"; do case $a in
    --skip-build)  SKIP_BUILD=true ;;
    --skip-models) SKIP_MODELS=true ;;
    -h|--help) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $a" >&2; exit 1 ;;
esac; done

ACTUAL_USER="${SUDO_USER:-$USER}"
HOME_DIR=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)
SW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
log() { echo -e "\033[0;32m[INFO]\033[0m $1"; }
[[ $EUID -ne 0 ]] && { echo "Run with sudo" >&2; exit 1; }
export DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
log "Step 1: timezone (family rule: robots run UTC)"
timedatectl set-timezone Etc/UTC

# ---------------------------------------------------------------------------
log "Step 2: Hailo-10H driver and runtime from Raspberry Pi's apt archive"
# Pi-hosted, not in Ubuntu: see docs/common.md, "Operating system for the HAT's Pi 5".
if ! dpkg -s h10-hailort >/dev/null 2>&1; then
    apt-get install -y -qq curl gnupg
    curl -fsSL https://archive.raspberrypi.com/debian/raspberrypi.gpg.key \
        | gpg --dearmor -o /usr/share/keyrings/raspberrypi-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/raspberrypi-archive-keyring.gpg] http://archive.raspberrypi.com/debian/ bookworm main" \
        > /etc/apt/sources.list.d/raspberrypi.list
    apt-get update -qq
    apt-get install -y -qq --no-install-recommends h10-hailort-pcie-driver h10-hailort
else
    log "  already installed"
fi

# ---------------------------------------------------------------------------
log "Step 3: ROS 2 apt repository (ros2-apt-source, as the hexapod)"
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
log "Step 4: apt packages (ROS 2 Jazzy base + this node's deps)"
APT_PACKAGES=(
    ros-jazzy-ros-base ros-dev-tools python3-colcon-common-extensions python3-rosdep python3-vcstool
    ros-jazzy-rmw-fastrtps-cpp
    ros-jazzy-usb-cam ros-jazzy-web-video-server
    ros-jazzy-cv-bridge ros-jazzy-image-transport ros-jazzy-image-transport-plugins
    ros-jazzy-vision-msgs ros-jazzy-diagnostic-updater
    libopencv-dev python3-numpy python3-opencv
    build-essential cmake v4l-utils
)
apt-get install -y -qq --no-install-recommends "${APT_PACKAGES[@]}"

# ---------------------------------------------------------------------------
log "Step 5: user groups for $ACTUAL_USER"
for grp in dialout video plugdev i2c gpio render; do
    if getent group "$grp" >/dev/null && ! id -nG "$ACTUAL_USER" | grep -qw "$grp"; then
        usermod -aG "$grp" "$ACTUAL_USER"; log "  added to $grp"
    fi
done

# ---------------------------------------------------------------------------
log "Step 6: rosdep"
[[ -f /etc/ros/rosdep/sources.list.d/20-default.list ]] || rosdep init
sudo -u "$ACTUAL_USER" rosdep update

# ---------------------------------------------------------------------------
if $SKIP_MODELS; then
    log "Step 7: models skipped"
else
    log "Step 7: Hailo Model Zoo HEFs (v5.4.0, Hailo-10H builds)"
    MODELS="$HOME_DIR/hailo/models"
    sudo -u "$ACTUAL_USER" mkdir -p "$MODELS"
    for m in yolov8s scrfd_2.5g arcface_mobilefacenet; do
        if [[ -s "$MODELS/$m.hef" ]]; then
            log "  present: $m.hef"
        else
            sudo -u "$ACTUAL_USER" curl -sSL -o "$MODELS/$m.hef" \
                "https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/ModelZoo/Compiled/v5.4.0/hailo10h/$m.hef"
            log "  fetched: $m.hef"
        fi
    done
fi

# ---------------------------------------------------------------------------
if $SKIP_BUILD; then
    log "Step 8: workspace build skipped"
else
    log "Step 8: build workspace (--symlink-install, as the family does)"
    sudo -u "$ACTUAL_USER" bash -c "source /opt/ros/jazzy/setup.bash && cd '$SW_DIR/ros2_ws' && \
        rosdep install --from-paths src --ignore-src -y -r && colcon build --symlink-install"
fi

# ---------------------------------------------------------------------------
echo ""
log "Setup complete. Log out and in if group membership changed."
log "  Verify the HAT:  hailortcli fw-control identify   (expect HAILO10H)"
log "  Run:             scripts/launch.sh"
log "  Watch:           http://<this-host>:8080/stream?topic=/hailo/image_annotated"
