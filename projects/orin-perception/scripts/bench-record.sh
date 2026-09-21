#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Run on the Jetson while the bench is up: capture tegrastats and the node's /orin/stats
# for DURATION seconds, then print a summary. Output files land in ~/bench/<timestamp>/.
#   ./bench-record.sh [DURATION=60] [label]
set -euo pipefail
DUR=${1:-60}; LABEL=${2:-run}
OUT=$HOME/bench/$(date +%Y%m%d-%H%M%S)-$LABEL; mkdir -p "$OUT"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}" RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}" ROS_AUTOMATIC_DISCOVERY_RANGE="${ROS_AUTOMATIC_DISCOVERY_RANGE:-LOCALHOST}"  # as launch.sh: before sourcing ROS
# ROS's setup.bash reads unset variables (AMENT_TRACE_SETUP_FILES and a chain behind it), so
# nounset aborts it. Drop -u across the sourcing only, and restore it for our own logic.
set +u
source /opt/ros/jazzy/setup.bash; source "$(cd "$(dirname "$0")/.." && pwd)/ros2_ws/install/setup.bash"
set -u
sudo -n nvpmodel -q > "$OUT/nvpmodel.txt" 2>&1 || true
{ echo "date $(date -Is)"; echo "l4t $(head -1 /etc/nv_tegra_release)"; echo "kernel $(uname -r)";
  dpkg -s nvidia-jetpack 2>/dev/null | grep ^Version; echo "tensorrt $(dpkg -s tensorrt 2>/dev/null | grep ^Version)";
  echo "ros $(ls /opt/ros)"; } > "$OUT/host.txt"
tegrastats --interval 1000 > "$OUT/tegrastats.log" &  TS=$!
timeout "$DUR" ros2 topic echo /orin/stats --field data > "$OUT/stats.jsonl" || true
kill $TS 2>/dev/null || true
python3 "$(dirname "$0")/bench_summarize.py" "$OUT" | tee "$OUT/summary.txt"
echo "-> $OUT"
