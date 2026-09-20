#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Fingerprint a host's ROS 2 install so the family's hosts can be diffed against the
# reference (the hexapod's Pi; see docs/common.md, "ROS 2 across the family").
# Run on the host, or:  ssh <host> bash -s < scripts/ros2-fingerprint.sh > <host>.txt
# Output is plain text, one fact per line, stable order, diff-friendly. No secrets, no
# host names (the caller names the file).
set -u
sec() { printf '\n## %s\n' "$1"; }
sec os;        . /etc/os-release; echo "id=$ID version=$VERSION_ID codename=$VERSION_CODENAME"; echo "kernel=$(uname -r) arch=$(uname -m)"
               [ -f /etc/nv_tegra_release ] && echo "l4t=$(head -1 /etc/nv_tegra_release | tr -s ' ')"
               [ -f /proc/device-tree/model ] && echo "model=$(tr -d '\0' < /proc/device-tree/model)"
sec apt-sources; grep -h -v '^#' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null | grep -E -i 'ros|nvidia|raspberrypi|realsense|http' | sed -E 's/\[signed-by=[^]]*\] ?//' | sort -u
sec foreign-packages; dpkg-query -W -f='${Package} ${Version}\n' 2>/dev/null | grep -E 'rpt|deb12' | sort || true
sec ros-distro; ls /opt/ros 2>/dev/null; dpkg -s ros2-apt-source 2>/dev/null | grep ^Version | sed 's/^/ros2-apt-source /'
sec ros-packages; dpkg-query -W -f='${Package} ${Version}\n' 'ros-*' 'python3-colcon-*' 'python3-rosdep' 'python3-vcstool' 'ros-dev-tools' 2>/dev/null | sort
sec rmw-installed; dpkg-query -W -f='${Package}\n' 'ros-*-rmw-*' 2>/dev/null | grep -v -E 'dds-common|implementation' | sort
sec ros-env; for f in ~/.bashrc ~/.profile /etc/profile.d/*.sh /etc/environment; do [ -f "$f" ] && grep -H -E 'ROS_|RMW_|CYCLONEDDS|FASTRTPS|setup\.bash|colcon' "$f" 2>/dev/null; done | sort -u
sec ros-systemd; systemctl list-unit-files --no-legend 2>/dev/null | grep -i -E 'ros|hexapod|perception|robot' | sort
sec rosdep; ls /etc/ros/rosdep/sources.list.d/ 2>/dev/null; [ -d ~/.ros/rosdep ] && echo "user-cache=yes" || echo "user-cache=no"
sec workspaces; find ~ -maxdepth 6 -type d -name ros2_ws 2>/dev/null | sort | while read -r d; do [ -d "$d/src" ] && { echo "$d:"; ls "$d/src" | sed "s/^/  /"; }; done
sec udev; ls /etc/udev/rules.d/ 2>/dev/null | sort
sec groups; id -nG | tr ' ' '\n' | sort | tr '\n' ' '; echo
sec python; python3 --version; python3 -m pip --version 2>/dev/null | awk '{print $1,$2}' || echo "pip=absent"; ls -d ~/.venvs/* ~/venv* 2>/dev/null
               echo "pip-installed (not apt): /usr/local + --user"; python3 -m pip list --format=freeze --path /usr/local/lib/python3*/dist-packages 2>/dev/null | sort | sed 's/^/  /'; python3 -m pip list --format=freeze --user 2>/dev/null | sort | sed 's/^/  user:/'
sec locale; locale 2>/dev/null | grep -E '^(LANG|LC_ALL)='
sec hardware-libs; dpkg-query -W -f='${Package} ${Version}\n' 'librealsense2*' 'libhailort*' 'hailo*' 'nvidia-jetpack' 'tensorrt' 'cuda-toolkit*' 2>/dev/null | sort
sec kernel-modules; lsmod 2>/dev/null | awk 'NR>1{print $1}' | grep -E -i 'uvcvideo|hailo|nvgpu|realsense' | sort
