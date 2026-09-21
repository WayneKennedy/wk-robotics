# mission-planner — the third tier, started

**Read [`../../AGENTS.md`](../../AGENTS.md) first.** This folder is the Mission Planning tier
described in [`docs/ideas.md` → Physical AI and the hive mind](../../docs/ideas.md#physical-ai-and-the-hive-mind):
a band above the robots' intent tier, working in seconds, that observes the fleet and may send it
goals. The tier's load-bearing rule applies from day one: **a robot stays useful when this tier is
unreachable.** Nothing here may be something a robot waits on.

Opened 2026-09-21 by the owner. What exists is the host install and a shell environment; no node
has been written, and the planner's design, messages and placement across the two workstations
are open (see the placement note in `ideas.md`).

## Host

[The GPU workstation](../../docs/common.md#the-gpu-workstation), native Ubuntu 24.04 since
2026-09-21, on the home LAN. Machine identifiers are in the private `wk-inventory` repo.

| File | Does |
|---|---|
| [`scripts/setup-host.sh`](scripts/setup-host.sh) | `sudo` once: ROS 2 Jazzy from apt as the family does, plus the robots' message packages. Idempotent |
| [`scripts/ros-env.sh`](scripts/ros-env.sh) | `source` in a shell: domain 0, Fast DDS, `SUBNET` discovery, set before sourcing ROS |
| `ros2_ws/` | Empty workspace, for the planner's packages when they exist |

**Deviations from [the family install](../../docs/common.md#ros-2-installs-are-familial)**, all
deliberate: a desktop, not Ubuntu Server; the timezone stays the owner's (UTC is the rule for
*robots*); discovery is `SUBNET`, not the benches' `LOCALHOST`, because seeing the robots is the
point.

## Verified 2026-09-21

With the hexapod's stack running on the same LAN, `ros2 topic list` on this host listed its whole
graph (Nav2, autonomy manager, LEDs, sonar). Data arrived for `std_msgs` and `sensor_msgs` types:
`/joint_states` 72 Hz, `/imu/data_raw` 106 Hz, `/ultrasonic/range` 16.5 Hz, `/battery/voltages`
echoed. `/imu/data` and `/tf` delivered nothing within 10 s, with a publisher listed on
`/imu/data`; `/imu/data_raw`, the same type from the same robot, did arrive, so the cause is on
the robot, not this link. Not investigated.

## Not yet

- **The hexapod's own types** (`hexapod_interfaces`, e.g. `/autonomy/state`,
  `/face_recognition/faces`) cannot be decoded here until that package is built on this host.
- **Off-LAN robots** need Zenoh or unicast discovery; plain DDS multicast only reaches the home
  LAN ([`ideas.md`](../../docs/ideas.md#physical-ai-and-the-hive-mind)).
- **Domain 0 shared with every robot** means this host sees every graph, and vice versa; the
  family's domain policy is open ([`common.md`](../../docs/common.md#ros-2-installs-are-familial)).
