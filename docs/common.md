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
| **STS3215** | 12 V, ~30 kg·cm, positional feedback | STS serial bus | SO-ARM101 (all joints) · koala-bot (hip, knee, shoulder, elbow) |
| **STS3032M** | 6 V, 4.5 kg·cm, positional feedback | STS serial bus (separate 6 V bus) | koala-bot (3-RPS neck) |

The hexapod is the exception — 20 hobby servos on a **PCA9685** I²C PWM driver, inherited
from the Freenove kit. No feedback, no bus addressing. It works because a statically
stable walker can tolerate open-loop position control in a way a balancing robot cannot.

### Configuring a servo — true for every STS project

The bus is a **single-wire half-duplex TTL UART**, 3-pin (V+, GND, signal), 1 Mbaud by
default. A generic USB-TTL cable has separate TX and RX and no direction switching, so it
will not drive these servos without a tri-state buffer — a purpose-made bus adapter is
required, not optional.

**The adapter is already owned.** An **FE-URT-1** was bundled with each STS3215 6-pack
(`koala-bot/docs/sourcing.md`, purchased 2026-09-01) — two in total. Whether the STS3032M
4-pack included one is **unrecorded**; check the box before planning around it.
Equivalents if a third is ever needed: Waveshare's *Bus Servo Adapter (A)*, or the
*Serial Bus Servo Driver Board* (~€5, the part in the Open Duck Mini V2 BOM).

Three constraints that apply on every project using these servos:

- **The adapter does not power the servo.** USB 5 V will not drive a 12 V STS3215; the
  servo rail is fed separately. Configuration *moves* the servo — it drives to zero
  position so the horn can be fitted aligned — so it needs working current, not a trickle.
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
**Which USB-serial chip the FE-URT-1 presents is unverified** — check on first plug-in.)

**A 3S LiPo is the ceiling for STS3215.** A full 3S is 12.6 V, within the servo's 12 V
rating; 4S at 16.8 V destroys them. This constrains the power architecture of any project
using them.

---

## Compute: the two-tier split

The pattern koala-bot's architecture sets out, and the one any future balancing or
dynamic project should follow:

| Tier | Hardware | Role | Rule |
|---|---|---|---|
| **Reflex** | Real-time MCU (Teensy 4.0 leading; ESP32 / RP2040 candidates) | Motor and servo output, IMU read, balance loop, encoders, safety | Fast (~200–1000 Hz), deterministic |
| **Intent** | Raspberry Pi 5 + ROS 2 | Perception, SLAM, mission and behaviour, LLM personality, networking | Not real-time |

**The load-bearing rule: the balance loop lives on the MCU, never on the Pi.** Linux is not
real-time and ROS 2 over USB adds jitter that destabilises an inverted pendulum. IMU → PID →
output closes on the MCU; the Pi sends setpoints and reads telemetry.

**micro-ROS** (DDS-XRCE over serial) makes the MCU a native ROS 2 node, so the boundary is
a topic contract rather than a bespoke protocol.

**Raspberry Pi 5 (8 GB) is the standard intent-tier host** — hexapod brain, koala-bot
cerebrum, and the printer's Klipper host. One board to know, one image to maintain.

### The topic contract

The vocabulary is shared deliberately: fix it once and every robot inherits it. Bodies
change; the spinal-cord protocol does not.

`/cmd_vel` · `/joint_commands` · `/joint_states` · `/imu` · `/wheel_odom` · `/telemetry`

The hexapod already speaks the common subset — `/cmd_vel` for velocity, `/odom` for
gait-integrated position, `/tf` for `odom`→`base_link` — which is what makes its
navigation stack portable in principle.

---

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
