# Architecture

How the compute is split, how the tiers talk, and what the power has to supply.

## Three tiers

The family's [two-tier split](../../../docs/common.md#compute-the-two-tier-split)
plus a coordination tier above it. Each tier owns a latency band.

| Tier | Where | Band | Owns |
|---|---|---|---|
| **Reflex** | 32-bit MCU on the robot | ~200–1000 Hz | Quadrature decoding, PID wheel-velocity loop, motor PWM, safety watchdog |
| **Intent** | Raspberry Pi 5 + AI HAT+ 2 + one camera (DEC-15) | ~1–50 Hz | SLAM, Nav2, local mission, perception |
| **Coordination** | Off-robot machine | seconds | Fleet reasoning, shared world model, task assignment |

### The load-bearing rule

**Each tier must stay useful when the tier above it is unreachable.**

- Reflex does not wait on intent. If the Pi stops, the wheels stop safely — the
  watchdog is the mechanism, not an afterthought.
- Intent does not wait on coordination. If the coordinator is unreachable, the robot
  keeps navigating autonomously.

This is not defensive over-engineering. The intended coordinator is a **desktop
workstation** — see the family's
[GPU workstation](../../../docs/common.md#the-gpu-workstation) —
which will be powered off, asleep or busy a large fraction of the time. The
architecture is chosen so that this is a normal operating condition rather than an
outage.

### Why this robot needs an MCU at all

Not for the reason koala-bot does. koala-bot's reflex tier exists because a balance
loop must be deterministic; a tracked, statically stable base has no such requirement,
and the hexapod drives its servos straight off the Pi for exactly that reason.

The justification here is different and narrower: **quadrature encoder decoding and a
closed-loop wheel-velocity PID.** Both want timing the Linux scheduler does not
guarantee, and both are cheap and reliable on an MCU. **The justification rests on the
encoders** — which is why an encoder-less variant was rejected rather than merely not
chosen. See DEC-11.

## micro-ROS, and how the tiers connect

The MCU runs [micro-ROS](../../../docs/common.md#micro-ros-how-the-mcu-joins-the-graph),
so it is a genuine ROS 2 node rather than something behind a translation layer. It
publishes and subscribes on the family
[topic contract](../../../docs/common.md#the-topic-contract):

| Direction | Topic | Notes |
|---|---|---|
| MCU subscribes | `/cmd_vel` | Body twist; converted to per-track velocity targets on the MCU |
| MCU publishes | `/wheel_odom` | Integrated from encoders — **see the accuracy caveat below** |
| MCU publishes | `/joint_states` | Track velocities |
| MCU publishes | `/telemetry` | Battery voltage, current, watchdog state |

**The alternative — a bespoke serial protocol plus a Pi-side translator — is rejected.**
It works, but the protocol then has to be maintained, and it is the thing that quietly
diverges between robots. Using micro-ROS makes the tier boundary the topic contract
itself, which is the whole point of having one.

### Odometry is weak by construction

A skid-steer **tracked** vehicle turns by slipping its tracks. Encoder-derived rotation
is therefore wrong in a way no amount of calibration fixes — translation is reasonable,
heading is not. `/wheel_odom` is published because it is cheap and useful for velocity
control and short-horizon dead reckoning, **not** because it can be trusted for pose.

Heading and global pose come from elsewhere: an IMU for orientation, and the
depth-camera SLAM route the hexapod already runs. See OQ-04.

## Networking

DDS discovery is multicast and works within one LAN segment. The family's mission-planner
host is on that LAN since its native rebuild (2026-09-21) and receives robot topics over plain
DDS; any robot or coordinator *off* the LAN does not — a general problem recorded in the
family repo.

**Zenoh** (`zenoh-bridge-ros2dds`, or `rmw_zenoh`) is the indicated answer rather than a
networking workaround, because the same wall appears again the moment any robot is on a
different network. **Not yet decided — OQ-05.**

## Power

The first build failed here, so this is a design input rather than something discovered
during bring-up. See [`concept.md`](concept.md#the-first-build-and-why-it-stopped) for
the original numbers.

The family's [power-integrity rules](../../../docs/common.md#power-integrity)
apply in full and are not restated here. The project-specific requirements:

- **A computed power budget precedes any purchase.** Motors at realistic duty, not
  no-load; compute at load, not idle; margin for stall.
- **Isolate the logic rail.** The Pi and MCU do not share feed points with the motors.
- **Fuse the pack, and size for stall**, not for average draw.
- **Prototype from the eventual battery**, not a bench supply — the family rule, and the
  one the first build most obviously broke.

The rail is **12 V from a 3S LiPo** (DEC-12), following the motor choice (DEC-11).

### The arm rewrites the budget

The first build's failure was arithmetic on a **~25–30 W** robot
([`concept.md`](concept.md#the-first-build-and-why-it-stopped)). A robot carrying the
SO-ARM101 ([OQ-12](open-questions.md)) is not that robot, and the budget cannot be
inherited from it.

Six STS3215 on the arm bus draw ~5–8 A in realistic motion and **16.2 A** all-stalled —
per-servo figures and the sizing rule are family facts and live
[in wk-robotics](../../../docs/common.md#actuators).
At 12 V that fault case alone is **~195 W**, on top of the drive. Three consequences, all
of which bite before a pack is bought:

- **Fuse and wire for the arm's stall case, not its motion case.** The existing rule says
  size for stall; the arm raises what stall means by an order of magnitude.
- **The arm and the drive motors share a pack and must not share a sagging rail.** Both
  are spiky inductive loads on the same 3S. The logic-rail isolation rule already covers
  the Pi and MCU; the arm bus wants its own bulk capacitance at the adapter's screw
  terminals for the same reason.
- **The arm's servo bus is fed from the pack directly.** The
  [Waveshare Bus Servo Adapter (A)](../../../docs/common.md#configuring-a-servo--true-for-every-sts-project)
  is a pass-through with no regulation or protection of its own, so pack voltage *is*
  servo voltage and pack sag *is* lost torque.

**This was a further argument for 12 V, and it prevailed:** the arm needs a 3S rail
regardless, so a 6 V drive rail would have meant two rails and a converter between them.
Settled as DEC-12.
