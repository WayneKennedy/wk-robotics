# mission-planner — the third tier, started

**Read [`../../AGENTS.md`](../../AGENTS.md) first.** This folder is the Mission Planning tier
described in [`docs/ideas.md` → Physical AI and the hive mind](../../docs/ideas.md#physical-ai-and-the-hive-mind):
a band above the robots' intent tier, working in seconds, that observes the fleet and may send it
goals. The tier's load-bearing rule applies from day one: **a robot stays useful when this tier is
unreachable.** Nothing here may be something a robot waits on.

Opened 2026-09-21 by the owner. What exists is the host installs, a shell environment and a stream page;
no node has been written, and the planner's design, messages and placement across the two workstations
are open (see the placement note in `ideas.md`).

## Hosts

The tier spans both workstations, following the placement split in `ideas.md`, which is still
the assistant's proposal and not accepted.
[The always-on workstation](../../docs/common.md#the-workstation--the-always-on-server) holds
what must stay up. Today that is the stream page; later it could hold a Zenoh router or the
coordinator. [The GPU workstation](../../docs/common.md#the-gpu-workstation) adds reasoning
when it is on. Both run Ubuntu 24.04 on the home LAN and have ROS 2 Jazzy, installed
2026-09-21 by the same script. Machine identifiers are in the private `wk-inventory` repo.

| File | Does |
|---|---|
| [`scripts/setup-host.sh`](scripts/setup-host.sh) | `sudo` once: ROS 2 Jazzy from apt as the family does, plus the robots' message packages. Idempotent |
| [`scripts/ros-env.sh`](scripts/ros-env.sh) | `source` in a shell: domain 0, Fast DDS, `SUBNET` discovery, set before sourcing ROS |
| `ros2_ws/` | Empty workspace, for the planner's packages when they exist |
| [`stream-page/`](stream-page/) | The stream page: `index.html` and its `Caddyfile` |
| [`systemd/`](systemd/) | `stream-page.service` and its installer, on the always-on workstation |

**Deviations from [the family install](../../docs/common.md#ros-2-installs-are-familial)**, all
deliberate: Ubuntu Desktop on the GPU workstation, not Server; the GPU workstation keeps the owner's timezone (UTC is the rule for
*robots*); discovery is `SUBNET`, not the benches' `LOCALHOST`, because seeing the robots is the
point.

## Stream page

Both perception benches' annotated streams, side by side: the HAT (`/hailo/image_annotated`) and
the Orin (`/orin/image_annotated`). Caddy on the always-on workstation serves `index.html` and
reverse-proxies each bench's `web_video_server` on port 8080 under `/hailo/` and `/orin/`, so
the browser uses one origin. **The page does not use ROS.** Each bench already compresses to
MJPEG, and moving raw images to another host over DDS would cost about 70 MB/s for the Orin's
1280×720 at 25 fps.

- **Listens on the tailnet address only**, port 8088, because the streams show household members
  identified by name. The address, port and bench upstreams are in
  `/etc/default/stream-page` on the host. That file is host state that git does not hold
  ([startup rule 8](../../docs/common.md#robot-startup-is-familial)); its values are in
  `wk-inventory`.
- **Install:** create that file (the installer prints the keys), then `systemd/install.sh --now`.
- **Verified 2026-09-21:** the page loaded from both workstations, and on the always-on
  workstation both streams flowed through the proxy (5.4 MB and 13.4 MB in 5 s). One frame
  from each was decoded and showed live annotations. No browser was available to view the page
  itself.
- A bench whose stream stalls with the connection still open is not detected; reload the page.

## Verified 2026-09-21

With the hexapod's stack running on the same LAN, `ros2 topic list` on the GPU workstation listed its whole
graph (Nav2, autonomy manager, LEDs, sonar). Data arrived for `std_msgs` and `sensor_msgs` types:
`/joint_states` 72 Hz, `/imu/data_raw` 106 Hz, `/ultrasonic/range` 16.5 Hz, `/battery/voltages`
echoed. `/imu/data` and `/tf` delivered nothing within 10 s, with a publisher listed on
`/imu/data`. Later `/ultrasonic/range` stopped too, and the always-on workstation briefly could not
get `/joint_states`. `/imu/data_raw`, the same type from the same robot, arrived at both hosts
throughout, so the fault is on the robot. The cause is
[startup rule 10](../../docs/common.md#robot-startup-is-familial)'s fault, confirmed on the robot;
the fix waits on a restart ([wk-hexapod OQ-25](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/open-questions.md)).

## Not yet

- **The hexapod's own types** (`hexapod_interfaces`, e.g. `/autonomy/state`,
  `/face_recognition/faces`) cannot be decoded on either workstation until that package is built there.
- **Off-LAN robots** need Zenoh or unicast discovery; plain DDS multicast only reaches the home
  LAN ([`ideas.md`](../../docs/ideas.md#physical-ai-and-the-hive-mind)).
- **Domain 0 shared with every robot** means these hosts see every graph, and vice versa; the
  family's domain policy is open ([`common.md`](../../docs/common.md#ros-2-installs-are-familial)).
