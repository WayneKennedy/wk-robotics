# The shared substrate

Facts true of more than one project. Anything true of only one belongs in that
project's repo — see the placement rule in [`AGENTS.md`](../AGENTS.md#the-placement-rule).

Everything below is sourced from a project repo or from a measurement taken on the
hardware, and dated where the date matters. Nothing here is speculative.

---

## Printing

**One machine, one set of profiles.** Every printable part on every project comes off a
stock Creality Ender-5 S1 running Klipper — build volume **220 × 220 × 280 mm**, textured
PEI on spring steel. Setup, calibration and the full print log live in the private
[`3d-printing`](https://github.com/WayneKennedy/3d-printing) repo; the findings that
affect design decisions are here.

### Materials in use

| Material | Nozzle / bed | Used for | Notes |
|---|---|---|---|
| **PETG** | 240 / 80 °C | Standing default; koala-bot parts | Baked into `START_PRINT`, so a bare `START_PRINT` is always safe |
| **PLA+** (eSUN) | 220 / 60 °C | SO-ARM101 parts | Validated 2026-09-06. Runs fine on the 80 °C-probed bed mesh — no separate profile needed |

Slicer profiles are versioned in `3d-printing/reference/` (`ender5s1_petg.ini`,
`ender5s1_plaplus.ini`, and per-project variants). A new project gets a profile there,
not a private copy.

### Design constraints this imposes

- **Every part fits within the bed.** koala-bot's stricter rule — *every part ≤ 200 × 200 mm* —
  is the one to design to; it leaves margin and keeps parts printable on the wider class
  of 200 mm machines the project targets.
- **Slicer time estimates are trustworthy.** Across eight completed jobs the estimate has
  landed within ±2 % of actual. Plan around it.

### Press-fits and supports

Two findings from the SO-ARM101 build (2026-09-06/07) that generalise to any project with
servo pockets:

- **Support residue, not dimensional error, is the usual cause of a failed press-fit.** An
  STS3215 would not seat in a supports-everywhere `Motor_holder_Base`. The
  support-free `Gauge_0` from the same design gave the intended tight friction fit on the
  same machine and material — so the machine was dimensionally correct and the support
  material was welded into the pocket. **Print the gauge before blaming the calibration.**
- **Check the overhang fraction before enabling supports.** All four parts on SO-ARM101
  plate 1 measure under 2 % overhang area and printed clean with supports off — screw holes
  open and unobstructed, no scarring. Supports-by-default cost a part and six hours.

### Adhesion

Small, poorly-anchored features are the first thing to release; large footprints hold.
When a print fails at feature scale rather than globally, the cause is the **surface**, not
the Z-offset — squishing the whole first layer to save a few small features degrades every
dimension on the plate. The definitive case: an identical model and G-code that failed at
layer 1 on the bare magnetic base printed intact on textured PEI with nothing else changed.

### Environment

The printer is in a garage with a clear corrugated PVC roof — it behaves as a greenhouse,
not a cold store: hot in daytime sun, cold overnight, ambient swinging widely. Two
consequences for anyone reading a calibration number or planning a long print:

- **A calibration figure is only meaningful with the ambient it was taken at.**
- **A long print will cross a hot/cold cycle.** Measured headroom (2026-09-06, ~25 °C
  ambient, enclosure fitted): bed holds 80 °C at 34 % duty, hotend 240 °C at 48 %.

The enclosure is left **open** by default. Enclosures suit ABS/ASA; PLA and PETG — which is
all this machine prints — do worse in a warm chamber, which drives heat creep in a
direct-drive hotend and blunts the part cooling PLA depends on.

---

## Actuators

**One servo family across two robots.** Feetech STS-protocol bus servos drive both the
SO-ARM101 and koala-bot's limbs. That is a real shared dependency, not a coincidence of
sourcing: it means one serial bus topology, one protocol, one set of press-fit
tolerances, one pool of spares, and tooling that transfers between projects.

| Servo | Rating | Bus | Used by |
|---|---|---|---|
| **STS3215** | 12 V, ~30 kg·cm, positional feedback | STS serial bus | SO-ARM101 (all joints) · koala-bot (hip roll + pitch, shoulder pitch + roll, elbow) |
| **STS3032M** | 6 V, 4.5 kg·cm, positional feedback | STS serial bus (separate 6 V bus). **Fixed single lead, no pass-through port** — chains through the 3-port connector boards and link cable supplied in the 4-pack | koala-bot (3-RPS neck) |

**Servo holdings, 2026-09-12 — every V1 servo the family has planned is now in hand:**

| Servo | Qty | Where | Source |
|---|---|---|---|
| Waveshare ST3215 12 V (Feetech STS3215 rebadge), firmware 3.10 (upgraded from 3.9, 2026-09-12) | 2 | SO-ARM101, IDs 1–2 | Amazon, 2026-09-07 ([wk-soarm101 `servos.md`](https://github.com/WayneKennedy/wk-soarm101/blob/main/docs/servos.md)) |
| Feetech STS3215 12 V, firmware 3.10 | 4 | SO-ARM101, IDs 3–6 (wk-soarm101 DEC-09) | RCmall via koala-bot, arrived 2026-09-12 ([koala-bot `sourcing.md`](https://github.com/WayneKennedy/koala-bot/blob/main/docs/sourcing.md)) |
| Feetech STS3215 12 V, firmware 3.10 (four read; the eight assumed the same batch, unverified) | 8 | koala-bot, eight of twelve limb joints — **four short** | same order |
| Feetech STS3032M 6 V | 4 | koala-bot, three neck + one spare | same order |

SO-ARM101 has its six. koala-bot must re-order at least four STS3215 before its limbs can
all be fitted (koala-bot OQ-16).

koala-bot's **knee is not a servo joint**: it is a wheel on a 12 V geared DC motor, and
the V1 leg ends there. A knee servo is designed for and deferred
(`koala-bot/docs/concept.md`, DEC-17), so it is not in the count of ten V1 limb joints.

The hexapod is the exception — 20 hobby servos on a **PCA9685** I²C PWM driver, inherited
from the Freenove kit. No feedback, no bus addressing. It works because a statically
stable walker can tolerate open-loop position control in a way a balancing robot cannot.

**STS3215 electrical, per servo** (vendor figures, checked 2026-09-07):

| Idle | No-load | **Stall** | Operating range | No-load speed |
|---|---|---|---|---|
| 30 mA | 200 mA | **2.7 A** | **6–14 V** | 0.22 s/60° @ 12 V |

Sizing is the count times the stall figure, because the fuse and the wiring have to
survive the fault case rather than the average: **six** on an SO-ARM101 is ~5–8 A in
realistic motion and **16.2 A** all-stalled; koala-bot's **ten** limb servos are 27 A.

**A 3S LiPo is the ceiling for STS3215.** A full 3S is 12.6 V, inside both the servo's
12 V rating and its 14 V absolute range; 4S at 16.8 V exceeds the range and destroys them.
This constrains the power architecture of any project using them.

**Torque and speed track the rail.** Both scale roughly with voltage, so a servo fed 9 V
delivers about three-quarters of its rated 30 kg·cm. A pack sagging toward its floor
therefore reads as a weakening arm, not as a tuning problem — worth knowing before chasing
the wrong fault.

### Drive motors, drivers and MCUs in hand

Two projects use 12 V geared DC motors with encoders rather than servos, and both drive
them with the same board — the **Pololu Dual TB9051FTG** (2.6 A continuous / 5 A peak per
channel, 4.5–28 V; chosen by koala-bot DEC-16, adopted by wk-devastator DEC-13). The
family holds more of both than any project needs, so the pool is tabulated here and each
project's BOM records only its own allocation.

**Holdings, 2026-09-11:**

| Part | Qty | Where |
|---|---|---|
| 37D 12 V 122 rpm 38 kg·cm geared motor + encoder (Pi Hut; koala-bot's CAD models it as DFRobot FIT0403) | 2 | koala-bot, rear ankle drives (DEC-43) |
| same | 2 | **Surplus.** Bought for koala-bot's four-wheel V1 (DEC-38, 2026-09-08), which DEC-43 cancelled on 2026-09-10; delivered 2026-09-11 (koala-bot DEC-51). Earmarked for [a pure balance bot](ideas.md#a-pure-balance-bot) — not committed |
| Pololu Dual TB9051FTG | 1 | koala-bot (DEC-16) |
| same | 1 | wk-devastator — its own since 2026-09-11 (DEC-13, amended). It was koala-bot's board on loan from 2026-09-07; the loan is dissolved, not returned |
| same | 1 | **Spare**, paired with the surplus motors |
| Teensy 4.0 | 1 | koala-bot (DEC-18) — upstream micro-ROS lists it "Not tested", koala-bot OQ-14 |
| Teensy 4.1 | 1 | wk-devastator (DEC-10) — ordered; arrival not recorded |
| **Teensy 4.1 NE** (no-Ethernet variant) | 1 | **Unallocated**, in hand 2026-09-11 — bought for whichever project is ready for it first. Upstream-Supported for micro-ROS, so it is also koala-bot's fallback if the 4.0 fails OQ-14. Obvious candidate for SO-ARM101's Teensy 4.1 phase (wk-soarm101 DEC-12) — not allocated |

The second motor pair and the two extra drivers came in one order; its date, supplier and
price are not recorded, and so are the spare Teensy's. Whichever project takes an
unallocated part records the allocation in its own BOM and updates this table.

### Configuring a servo — true for every STS project

The bus is a **single-wire half-duplex TTL UART**, 3-pin (V+, GND, signal), 1 Mbaud by
default. A generic USB-TTL cable has separate TX and RX and no direction switching, so it
will not drive these servos without a tri-state buffer — a purpose-made bus adapter is
required, not optional.

**Adapters in hand (2026-09-08):** a **Waveshare Bus Servo Adapter (A) v1.1** — the
"Motor Control Board" in the SO-ARM100 BOM, so it is the SO-ARM101 part — and a
**Feetech FE-URT-2**. Those two are the family's only adapters: the RCmall STS3215 6-packs
were listed with an **FE-URT-1** each but shipped **without** (koala-bot `test-log.md`,
2026-09-12), and the STS3032M 4-pack ships passive 3-port connector boards and a link cable, not a
USB adapter. Both bring-ups therefore share the two boards. A further equivalent, if ever needed: the *Serial
Bus Servo Driver Board* (~€5, the part in the Open Duck Mini V2 BOM).

| Adapter | USB | Servo power in | Servo ports | Notes |
|---|---|---|---|---|
| Waveshare Bus Servo Adapter (A) | USB-C, **CH343** (`1a86:55d3`, verified 2026-09-09; `cdc_acm` → `/dev/ttyACM0`) | 5.5 × 2.1 mm barrel **or** screw terminals, 9–12.6 V / 5–8.4 V (pass-through, below) | 2 × 3-pin, either is the bus | **Both jumpers on channel B** for USB control (LeRobot docs) |
| Feetech FE-URT-2 | USB-C, **CH343** (vendor listing) | Two screw-terminal inputs: **DC 4.8–12 V for TTL** servos, **DC 12–24 V for RS485** servos | TTL bus header plus 2 × XH4 RS485 — check the silkscreen before plugging a 3-pin STS lead | 3.3 V / 5 V logic-level switch; also serves the SMS (RS485) family, which nothing here uses |

A CH343 enumerates under the kernel's `cdc_acm` driver as `/dev/ttyACM*`; the FTDI note
below does not apply to it. **On Windows** the same chip binds to the generic CDC serial
driver by default and gets a COM port; WCH's **VCP driver (CH343SER)** is a separate manual
install (Waveshare's wiki note, read 2026-09-12). Feetech's FD software found the servos on
2026-09-12 with the VCP driver installed **and its baud set to 1 000 000** — the 2026-09-09
"port but no servo" was the baud (FD defaults to 115200); whether the CDC driver would also
have worked at 1 Mbaud is untested. The chip's flow-control setting is irrelevant to the
servo bus, which uses no flow-control lines. Either board needs the user in the **`dialout`** group (or a
udev rule) before the port is writable without `sudo`. The Waveshare board **does not echo
transmitted bytes** back on RX (verified 2026-09-09) — a bus scanner need not strip them.

**Verified against a Waveshare ST3215 (2026-09-09):** factory state is **ID 1, 1 Mbaud**,
model number **777**; LeRobot 0.6.1's `FeetechMotorsBus.setup_motor()` and
`broadcast_ping()` work through the Waveshare board unmodified. `Present_Voltage` reads
the rail in 0.1 V units and is the quickest proof that a servo is actually powered.

**Every STS3215 on a bus must run the same firmware, and that firmware is 3.10 (verified
2026-09-12, SO-ARM101, six servos).** Units ship with **3.9** (the 2026-09-07 Waveshare pair
did) or **3.10** (the RCmall Feetech packs). Mixed, they collide: in a `sync_read` the servos
answer in the order asked, and a 3.10 unit starts its reply too early when the unit before it
is a 3.9 unit that was not the first responder — its header lands on the previous checksum
byte, the host sees `Incorrect status packet`, and `broadcast_ping()` loses IDs.
`Return_Delay_Time` does not help; ID placement can route around it but is fragile. **The
fix is the upgrade**, and it worked first time: Feetech **FD 1.9.8.3** on Windows (LeRobot's
[documented path](https://huggingface.co/docs/lerobot/main/feetech)), servo on the Waveshare
board, *Upgrade → Online → Upgrade*, one servo selected at a time, on a supply that will not
drop mid-write. Two pitfalls: Windows binds the board's CH343 to a generic CDC driver — install
WCH's **CH343SER** VCP driver — and FD defaults to **115200 baud; set 1 000 000** before
*Search* or it lists nothing. After the upgrade every read order passed 30/30 and broadcast
ping was complete. So: read `Firmware_Major_Version` / `Firmware_Minor_Version` at
commissioning, record it, and upgrade any 3.9 unit before it joins a bus. Full record:
[wk-soarm101 `test-log.md`](https://github.com/WayneKennedy/wk-soarm101/blob/main/docs/test-log.md)
2026-09-12, DEC-11.

**Three STS3215 behaviours that bit on 2026-09-12 (SO-ARM101, LeRobot 0.6.1):** writing
`Goal_Position` **turns torque on** regardless of `Torque_Enable`; servos **keep their last
goal across power and sessions**, and LeRobot's `connect()` re-enables torque without
resetting it, so joints lurch toward stale goals — write `Goal_Position := Present_Position`
before torque comes on; and LeRobot's `max_relative_target` clamps to *present ± step*, so
it follows a moving joint rather than holding it — not a safety net. Record and evidence:
[wk-soarm101 `servos.md`](https://github.com/WayneKennedy/wk-soarm101/blob/main/docs/servos.md)
and its `test-log.md`. These apply to every STS bus in the family.

**Home and travel limits are a separate, later step, and they live in the servo.** Setup
writes ID and baud only. LeRobot's `calibrate()` (after assembly) writes **`Homing_Offset`**
so the joint's mid-range reads 2047, then records the range you sweep by hand and writes
**`Min_Position_Limit` / `Max_Position_Limit`** — all three to servo EEPROM (LeRobot 0.6.1
`write_calibration`, read 2026-09-09), so the servo itself clamps any goal past them. The
limits are only as good as the sweep: stop just short of the hard stops. For a soft first
test, upstream's `SO-ARM100/Software/WEBUI_CALIBRATION.md` caps `Torque_Limit` (reg 48) at
30 %.

**The Waveshare Bus Servo Adapter (A) is a pass-through, confirmed 2026-09-07** — owner
read the Waveshare documentation (*"the input voltage must match the servo voltage"*,
stated twice) and confirmed against the board, which carries none of the inductor or bulk
electrolytics a switching converter would need. Its two input bands are the two pack
sizes, not a choice of supply: **9–12.6 V is the 3S window** for 12 V servos, **5–8.4 V
the 2S window** for 7.4 V ones. Consequences:

- **Feeding 9 V does not get you 12 V.** There is no boost. The servos see the pack.
- **The board supplies no regulation, bulk capacitance or protection of its own** — the
  bulk capacitance and fuse under [Power integrity](#power-integrity) are external to it,
  and are not optional.
- **Use the screw terminals, not the barrel jack**, for anything past bench testing: a
  5.5 × 2.1 mm jack is typically good for only ~3–5 A, in series with the whole bus.

Three constraints that apply on every project using these servos:

- **The adapter does not power the servo, and USB alone cannot.** Neither board routes
  USB 5 V onto the servo V+, and 5 V is below the STS3215's 6–14 V range anyway — the
  servo will not even answer a ping. The servo rail is fed separately, even for ID setup.
  LeRobot's setup writes ID and baud rate only and does not move the servo; Open Duck's
  script also drives it to zero so the horn can be fitted aligned, so needs working current.
- **Match the rail to the part.** STS3215 is 12 V, **STS3032M is 6 V**, and the adapter
  passes through whatever it is given. Same bus, same protocol, different rail.
- **One servo at a time, unplugged between each.** Every unit ships as **ID 1**, so IDs
  cannot be assigned on a shared bus.

**Scripted, not GUI.** Feetech's FD / SCServo Debug tool works, but leaves no record. The
one-time write is small enough to script and log: unlock EEPROM, mode 0, zero the
acceleration limits, write the PID coefficients, `change_id`. Open Duck Mini V2's
`scripts/configure_motor.py` (`pypot.feetech.FeetechSTS3215IO`) is a working reference;
LeRobot's SO-ARM setup command does the same job against the same SO-101 follower spec.

**The FTDI latency trap.** If a bus adapter presents as an FTDI device, its default
**16 ms latency timer** caps every bus round-trip — harmless during one-time ID setup,
fatal for a fast control loop later. The fix is a udev rule:

```
SUBSYSTEM=="usb-serial", DRIVER=="ftdi_sio", ATTR{latency_timer}="1"
```

(Sourced from the Open Duck Mini V2 runtime's Pi setup, which ships exactly this rule.
Neither adapter in hand is FTDI — both are CH343 — so this applies only to a future board;
check on first plug-in.)

---

## Compute: the two-tier split

The pattern koala-bot's architecture sets out, and the one any future balancing or
dynamic project should follow:

| Tier | Hardware | Band | Role | Status |
|---|---|---|---|---|
| **Reflex** | Real-time MCU (Teensy 4.0 leading; ESP32 / RP2040 candidates) | ~200–1000 Hz, deterministic | Motor and servo output, IMU read, balance loop, encoders, safety | **Decided** |
| **Intent** | On-robot Raspberry Pi 5 + ROS 2 | ~1–50 Hz, not real-time | Perception, SLAM, behaviour, LLM personality, networking | **Decided** |
| **Mission Planning** | Off-robot central machine | seconds | Shared world model, reasoning, fleet-level tasking | **Aspirational** — see [ideas.md](ideas.md#physical-ai-and-the-hive-mind) |

**The tiers are defined by one axis: control band.** Each is a loop that runs slower than
the one below it and hands the one below setpoints, and **each must stay useful when the
tier above it is unreachable** — the balance loop survives losing the Pi, the robot
survives losing the planner. Only the first two tiers are built or committed; the third is
recorded so the two below are designed with it in mind, not because it is planned.

**The load-bearing rule: the balance loop lives on the MCU, never on the Pi.** Linux is not
real-time and ROS 2 over USB adds jitter that destabilises an inverted pendulum. IMU → PID →
output closes on the MCU; the Pi sends setpoints and reads telemetry.

**What is *not* a tier: a smart sensor.** A camera that computes depth or runs a detector
on-board closes no control loop, takes no setpoints and offers no graceful degradation —
if it dies, the intent tier is blind wherever the depth was computed. It is a peripheral
of the intent tier, and where its work runs is a separate axis, covered under
[Perception placement](#perception-placement) below.

### micro-ROS: how the MCU joins the graph

ROS 2 is a Linux system — its transport is DDS, which assumes an OS, a network stack and
megabytes of RAM. **An MCU cannot run ROS 2.** micro-ROS is the ROS 2 client library for
microcontrollers: it replaces DDS with **DDS-XRCE** (*eXtremely Resource Constrained
Environments*), and the MCU speaks XRCE over serial to a **micro-ROS Agent** process on
the Linux host, which bridges it into the real DDS graph.

The MCU then *is* a ROS 2 node — it appears in `ros2 topic list`, RViz plots it, Nav2
drives it. The boundary between the tiers becomes the topic contract rather than a bespoke
serial protocol that has to be maintained, and re-diverges, per robot. The agent is a
container:

```bash
docker run -it --rm -v /dev:/dev --privileged --net=host \
  microros/micro-ros-agent:rolling serial --dev /dev/ttyACM0 -v6
```

**It requires a 32-bit target.** An 8-bit AVR (Arduino Uno/Nano) cannot run micro-ROS at
all — a constraint that decides MCU choice, not just MCU preference.

**Board support, from `micro-ROS/micro_ros_arduino` (checked 2026-09-07):** ESP32,
Teensy 3.2/3.6, **Teensy 4.1** and Arduino Portenta H7 are listed **Supported**;
**Teensy 4.0 is listed "Not tested"**, as is Teensy 3.5. RP2040 appears only as a
community-contributed entry. This matters because **koala-bot has already bought a Teensy
4.0** (DEC-18). The 4.0 and 4.1 share the same i.MX RT1062 core and the same Teensyduino
support, so it is *expected* to work — but that expectation is **unverified**, and proving
it on the bench is worth doing before the firmware is written rather than after.

**Raspberry Pi 5 (8 GB) is the standard intent-tier host** — hexapod brain, koala-bot
cerebrum, and the printer's Klipper host. One board to know, one image to maintain.

### Perception placement

**Orthogonal to the tiers: where each stage of the perception pipeline runs.** Every
stage — image signal processing, stereo depth, detection and classification, feature
tracking, SLAM — can run in one of four places, and the choice is made per stage, not per
robot:

| Place | Examples | Costs the Pi |
|---|---|---|
| **In the sensor** | RealSense D4xx stereo ASIC; Sony IMX500 in the Raspberry Pi AI Camera; RealSense D555 Vision SoC V5 | Nothing but the bus |
| **Host accelerator** | Raspberry Pi AI HAT+ (Hailo) on the Pi 5 PCIe connector | PCIe bandwidth; the single lane is shared with NVMe |
| **Pi CPU** | depth-to-laserscan, `slam_toolbox`, RTAB-Map, Nav2 — everything the hexapod runs today | The whole cost |
| **Off-robot** | GPU workstation | Ruled out for raw streams — see below |

**Why it matters here.** The hive-mind direction fixes one end: *share a world model, not
sensor streams* ([ideas.md](ideas.md#physical-ai-and-the-hive-mind)), so perception must
stay on the robot. The intent host is a Pi 5 on every project, so the Pi 5 is the
perception bottleneck, and moving stages into the sensor or an accelerator is the only
lever that does not change the host. The hexapod (D435i, all SLAM on the Pi) and the tank
(two RealSense cameras on one USB 3 host — `wk-devastator` OQ-09) are the two instances so
far; koala-bot's CSI camera-eyes are where an in-sensor module would go.

**What the current products actually do on-device (checked 2026-09-09):**

- **RealSense D4xx (the hexapod's D435i):** stereo disparity matching on the on-board
  ASIC; the host receives finished depth frames over USB 3. **No SLAM on-device** — the
  hexapod's `slam_toolbox` and RTAB-Map run on the Pi.
- **RealSense T265** was the only member that ran visual-inertial SLAM on-device and
  emitted pose. **Discontinued.** No current RealSense does on-device SLAM.
- **RealSense D555 PoE:** D450 optical module, IMU, and the new *Vision SoC V5* —
  disparity, motion estimation, a vision DSP and an ISP on-device; depth to 1280 × 720 at
  60 fps. Power and data over one Ethernet cable, and it **streams to ROS 2 directly
  over Ethernet with no host driver**. The biggest on-device offload in the family, and
  it takes the USB 3 bandwidth question off the table. Sources:
  [product page](https://www.realsenseai.com/products/d555-poe/),
  [datasheet v1.1](https://realsenseai.com/wp-content/uploads/2025/08/D555-Datasheet-v1.1.pdf).
- **Raspberry Pi AI Camera (Sony IMX500):** runs one int8 model, up to ~8 MB and a
  640 × 640 input tensor, on the sensor and returns output tensors and regions of interest
  as metadata alongside each frame. **Detection and classification only** — no depth, no
  SLAM. Source:
  [Raspberry Pi documentation](https://www.raspberrypi.com/documentation/accessories/ai-camera.html).
- **Raspberry Pi AI HAT+ (Hailo):** a host accelerator, not a sensor — the model runs
  on the HAT, the frames still cross to the Pi. Whether a given HAT variant also carries
  an M.2 slot for the NVMe it displaces is **unverified**; check before pairing one with a
  Pi 5 that boots from NVMe.

**Rule of thumb:** put a stage in the sensor when the sensor's output is what the next
stage consumes anyway (depth for laserscan, detections for behaviour), and leave a stage
on the Pi when it needs the whole robot's state (SLAM, Nav2). No project has yet tested an
in-sensor or accelerator stage; the table above records options, not results.

### The GPU workstation

**Established 2026-09-07.** A workstation with an **NVIDIA GeForce RTX 5070 Ti (16 GB,
driver 610.62)** is available, running **Ubuntu 24.04 LTS under WSL2** on a Windows
desktop. GPU passthrough is working (`/dev/dxg` present, CUDA libraries at
`/usr/lib/wsl/lib/`), and Docker is installed. **No ML stack is installed yet** — no
PyTorch, JAX, MuJoCo or `uv` as of that date.

It is the only GPU in the family, and it unlocks two things nothing else can: **RL
policy training** (MuJoCo Playground / MJX and anything else JAX- or PyTorch-based) and
**local LLM/VLM inference** for a reasoning tier.

Four constraints, all of which bite early:

- **Blackwell means `sm_120`.** The RTX 50-series needs **CUDA 12.8 or newer** and
  framework builds carrying `sm_120` kernels — PyTorch `cu128` wheels or later, a current
  `jax[cuda12]`. Older wheels fail outright or fall back silently to CPU, which on a
  300 M-step training run looks like "it works, but slowly" rather than like an error.
- **`nvidia-smi` is not on `PATH`.** It lives at `/usr/lib/wsl/lib/nvidia-smi`. A naive
  check therefore reports *no GPU* on a machine that has one.
- **WSL2 networking is NAT'd, not mirrored.** The LAN cannot open connections *into* the
  instance. This is the concrete reason **DDS multicast discovery will not reach it**, and
  why [Zenoh](ideas.md#physical-ai-and-the-hive-mind) rather than a networking workaround
  is the indicated route for any ROS 2 role. Unicast over the private overlay network
  works — that is how the machine is reached today.
- **It is a desktop, not a server.** Availability is not guaranteed: it may be powered
  off, or busy. Any role given to it must degrade gracefully when it is absent.

**16 GB of VRAM** is comfortable for MJX-scale RL training and for quantised models in the
7–14 B class; it is the binding limit on anything larger.

### The topic contract

The vocabulary is shared deliberately: fix it once and every robot inherits it. Bodies
change; the spinal-cord protocol does not.

`/cmd_vel` · `/joint_commands` · `/joint_states` · `/imu` · `/wheel_odom` · `/telemetry`

The hexapod already speaks most of it — `/cmd_vel`, `/joint_commands`, `/joint_states`,
`/imu/data`, plus `/odom` for gait-integrated position and `/tf` for `odom`→`base_link`
(it has no wheels, so no `/wheel_odom`, and battery is `/battery/voltages` rather than
`/telemetry`) — which is what makes its navigation stack portable in principle.

---

## Collision awareness — open, family-wide

**Raised 2026-09-12 while watching SO-ARM101 cycle its joints**, which the owner treats as a
surrogate for industrial arms, where operating ranges are safety matters and "a box of
acceptable movement" is the basic tool: per-joint travel limits are
the only geometric protection any robot here has, and they cannot express "elbow past X is
fine unless the wrist is past Y", let alone another robot or a person in the same space.
LeRobot has no self-collision or world model at runtime (its policies inherit safety from the
human demonstrator); the Freenove hexapod stack has none; koala-bot's limbs will have the
same problem with more joints. **Nothing is decided.** What exists to draw on, and where it
would sit in the [two-tier split](#compute-the-two-tier-split):

| Layer | Mechanism | Tier | State here |
|---|---|---|---|
| Joint envelope | Per-joint limits **plus pairwise rules** (elbow vs wrist, shoulder vs elbow) fitted from hand-swept contact poses — cheap, MCU-sized, checks every goal before it is sent | Reflex | Not built. SO-ARM101 needs it first; the method is the calibration sweep applied to joint pairs |
| Effort reflex | Current / load / tracking-error thresholds that stop or back off a joint on unexpected resistance | Reflex | Only in bench tools (`extents_cycle.py`): stall, current, temperature stops |
| Self-collision model | URDF with collision meshes checked with FCL each control step — what MoveIt 2 does; upstream ships an SO-101 URDF and MuJoCo scene | Intent (ROS 2) | Not built; the meshes exist |
| World model | Depth camera → occupancy (octomap / voxel grid) → planning-scene obstacles; other robots publish their own poses into the same scene | Intent | Nothing; koala-bot's head camera and the hexapod's depth camera are the sensors that would feed it |
| Speed-and-separation | Slow down as anything approaches, stop inside a radius — the collaborative-robot rule (ISO/TS 15066 in industry) | Intent → reflex | Nothing |

The pattern that fits the family: the **reflex tier guarantees the arm cannot fold into
itself** (joint envelope + effort reflex, no perception needed, runs with the intent tier
dead), and the **intent tier keeps it out of the world** (geometric model + perception). A
policy or planner then commands only within what both allow. Which robot proves it first,
and whether MoveIt 2 or something lighter carries the intent-tier check, are open.

## Power integrity

Banked from an earlier InMoov build that stalled partly on this. A fully-loaded
servo/motor robot is a spiky, inductive load; bench PSUs have slow transient response and,
on a shared rail, dump that noise onto the logic — causing brownouts, servo jitter,
MCU/IMU resets and I²C corruption.

- **Prototype from a stiff, low-impedance source** — a LiPo pack, not a bench PSU. It is
  also the eventual onboard power, so there are no bench-to-battery surprises.
- **Isolate the logic rail.** MCU, Pi and IMU on their own regulator with local
  decoupling; never share the servo or motor feed points. The Pi 5 is power-hungry and
  brown-outs are a known failure mode.
- **Bulk capacitance** (~1000–2200 µF) across the servo/motor bus, to absorb transients
  and tame lead inductance.
- **Fuse the main pack lead.** LiPos deliver enormous fault current.

**The mechanism is source impedance, not "clean DC."** A bench PSU regulates through a
control loop with millisecond response; a servo stepping 200 mA → 2.7 A does it in
microseconds, and on a shared bus those dips overlap. A LiPo has milliohms of internal
resistance and no loop to settle. Lead resistance and inductance cause the same dip and
follow you between supplies — hence short, fat leads and the bulk capacitance above.

**Where a current-limited bench PSU is still the right tool** (scope note, 2026-09-07;
this does not weaken the rule above, which is about transient response *under load*):

- **First power-up and servo ID assignment.** A LiPo into a miswired bus delivers tens of
  amps without complaint; a supply limited to ~1 A turns a wiring error into a shrug. IDs
  are assigned one unplugged servo at a time, so there is no load to respond to.
- **Measuring draw**, which is where a project's power budget comes from.

Move to the pack the moment anything runs under load.

**One InMoov failure mode does not transfer.** InMoov ran PWM hobby servos, which jitter
both from brownout *and* from signal-path noise and deadband hunting. STS bus servos are
closed-loop, with their own magnetic encoder and a serial command — there is no pulse
width to misread. The brownout half still applies; the signal-side half does not.

**Nothing in this chain has a low-voltage cutoff.** Stop at ~10.5 V on a 3S (3.5 V/cell);
the adapter's 9 V floor is ~3.0 V/cell and already deep enough to hurt the pack.

### Bench power for servo robots — open

**Raised 2026-09-12.** A bench needs 12 V that behaves like a battery — stiff under a 2 A step,
no current-limit fold-back — but stays topped up from the mains. A plain brick sags or trips
on stalls; a bare LiPo must never be charged under load. What exists off the shelf, from a
first look (2026-09-12, specs partly unverified — check the port ratings before buying):

| Class | Example | 12 V out | UPS / charge-while-supplying | Verdict for a 6-servo bench |
|---|---|---|---|---|
| Portable power station (LiFePO₄) | Bluetti AC70 768 Wh (~£419); EcoFlow River 3 Plus (~£219); EcoFlow Delta Pro 3 | Regulated DC "car" port, **typically 12 V / 10 A (120 W)**; Delta Pro 3 has a **12.6 V / 30 A Anderson** | Yes — AC70 states "UPS in 20 ms"; pass-through is the normal mode for this class | **Best fit.** Battery-fed regulated DC, mains-charged, and it powers the Pi and laptop too. Confirm the car-port voltage (some sit at 13.2–13.6 V; STS3215 limit is 14 V) and its continuous rating |
| 12 V Li-ion pack with DC out | Talentcell YB1208300 (11.1 V nominal, 8.3 Ah, **6 A max**, 12.6 V/1.5 A charger) | 12 V barrel, 6 A | Pass-through is claimed for some Talentcell models; not verified per model | Marginal — 6 A is under the 10 A target; fine for one or two servos on a bench |
| "Mini DC UPS" for routers / CCTV | many, 12 V 2–5 A | Low | Yes | Too small |
| Automotive DC UPS | PowerStream DC-UPS-1212 (12 A pass-through, lead-acid, 0.8 A charge, ~$135) | 12 A | Yes, < 50 µs switch | Right current, wrong chemistry and needs a separate battery; not a desk unit |
| Build: 3S pack + BMS + power-path charger | — | whatever the pack gives | Yes if the charger has a load-sharing path | Exactly what a power station is; only worth it as a robot-mounted design, not for the desk |

A power station's DC port is a DC-DC converter fed from the battery, so it is battery DC in
the sense that matters (no mains ripple, no fold-back on transients) without being raw cell
voltage — which is better for the servos than a sagging pack. Which unit, and whether the
car-port rating is honest at 10 A continuous, is open; nothing bought.

### GPIO lines float when their process dies

Established on the hexapod, 2026-09-09, and true of any robot that drives a peripheral
straight from a Raspberry Pi GPIO: when the userspace process holding a line exits or is
killed, the kernel releases the line and it reverts to a **floating input**. An
active-high load on that pin — the hexapod's shield buzzer — then turns on and stays on
through a `reboot`. The fixes that worked, in layers: a firmware default in `config.txt`
(`gpio=<n>=op,dl`), a `systemd` service holding the line with `gpioset --mode=signal`,
and the software default off. Details in
[`wk-hexapod/docs/hardware.md`](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/hardware.md#the-buzzer-hazard).
This is one of the concrete arguments for the reflex tier: an MCU holds its pins through
a host crash; a Pi does not.

---

## Modelling and simulation

- **URDF + RViz** for serial kinematics — limbs, base yaw, head. It is the same file the
  robot's ROS 2 stack uses, so it is not a throwaway.
- **CAD motion study** for parallel mechanisms. *URDF cannot represent closed kinematic
  loops*, so anything parallel (koala-bot's torso and 3-RPS neck) is modelled in CAD or a
  loop-capable simulator.
- **Physics** — Gazebo (ROS 2-native), or PyBullet / MuJoCo for balance and gait.

---

## Documentation conventions

Every project in the family follows the same conventions, set out in each repo's
`AGENTS.md` — which is the provider-neutral entry point, with any harness-specific file
(`CLAUDE.md`, `GEMINI.md`) doing nothing but pointing at it.

- **Every repo stands alone.** A brand-new assistant, on a first read of that repository
  and nothing else, must be able to do useful work in it. This is the load-bearing rule;
  the rest follow from it.
- **The repository is the memory.** Per-harness memory holds *pointers* only — never a
  project fact, a measurement or a decision. Anything durable lands in a file.
- **Docs are written AI-first** — dense, factual, cross-referenced, greppable, on the
  assumption an AI assistant is the primary reader.
- **Every artefact meets the 4Cs** — Correct, Complete, Coherent, Concise. See
  [`AGENTS.md`](../AGENTS.md#the-4cs--the-standard-every-artefact-meets).
- **No project fact lives only in chat.** Durable decisions land in the repo.
- **Decided and open are kept apart** — a `decisions.md` for what is committed and the
  durable *why*; an `open-questions.md` for what is still unresolved. Items move between
  them as they resolve, and an open question is never stated as settled.
- **A test log records what actually happened**, including "no change needed" results.

## Licensing

Mixed hardware/software/docs projects use the standard open-hardware **tri-licence**:

| Area | Licence | SPDX |
|---|---|---|
| Hardware — CAD, mechanical, PCB, printable parts | CERN Open Hardware Licence v2, Strongly Reciprocal | `CERN-OHL-S-2.0` |
| Software — firmware, host software, tooling | MIT | `MIT` |
| Docs and media | Creative Commons Attribution-ShareAlike 4.0 | `CC-BY-SA-4.0` |

Source files carry an `SPDX-License-Identifier:` header. Full licence texts are included
verbatim in the repo rather than linked. Vendored third-party CAD keeps its own licence in
its own directory — SO-ARM100 reference CAD inside koala-bot is Apache-2.0.

This repository is documentation only, so it is `CC-BY-SA-4.0` throughout.
