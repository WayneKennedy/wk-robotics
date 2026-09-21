# SPDX-License-Identifier: MIT
# Source, don't execute:  source scripts/ros-env.sh
# The family's ROS environment for a mission-planner shell, set before sourcing ROS as the
# startup rule requires (wk-robotics docs/common.md, "Robot startup is familial", rule 3).
# SUBNET, not the benches' LOCALHOST: this host exists to see the robots' graphs.
_MP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
export ROS_AUTOMATIC_DISCOVERY_RANGE="${ROS_AUTOMATIC_DISCOVERY_RANGE:-SUBNET}"
source /opt/ros/jazzy/setup.bash
[[ -f "$_MP_DIR/ros2_ws/install/setup.bash" ]] && source "$_MP_DIR/ros2_ws/install/setup.bash"
unset _MP_DIR
