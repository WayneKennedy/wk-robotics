# Open Questions (pending decisions)

Unresolved. Resolve → move to [`decisions.md`](decisions.md).

**Several of these carry a recommendation.** A recommendation is *not* a decision — it
is one option with an argument attached, offered and not yet accepted. Do not build
against one, and do not promote one to `decisions.md`, without the owner deciding.

---

## Gating

- **OQ-01 — What replaces the 6 V motors.** This gates the rail voltage, the battery,
  the driver and the power budget, so it is first. The fitted motors are 6 V with a
  **7.5 V ceiling**, which no pack the rest of the family uses can feed directly — a
  2S LiPo alone peaks at 8.4 V. The owner has said motors with encoders are a likely
  swap.
  **Recommendation, not accepted:** buy **12 V encoder motors**. The motors are being
  replaced anyway and are the sole source of the voltage conflict; at 12 V the odd rail
  and its converter disappear, and koala-bot's 3S pack, driver choice and power work all
  transfer unchanged. **A third argument arrived with the arm (OQ-12):** the SO-101 "Pro"
  follower runs **12 V STS3215** servos — the same part and voltage koala-bot bought
  (`koala-bot/docs/sourcing.md`) — so a 12 V rail feeds drive *and* arm from one 3S pack,
  where a 6 V drive rail would need a second. **Blocked on OQ-11** — a motor that does not fit the bracket is not
  a candidate whatever its voltage.

- **OQ-11 — Mechanical compatibility of any replacement motor.** Two dimensions,
  neither measured: the Devastator's **motor bracket** (koala-bot's 37D class is *likely*
  too large — unverified) and the **4 mm output shaft** the drive sprocket takes. A
  different shaft means new hubs as well as new motors. **Measure before ordering.**

## Electronics

- **OQ-02 — Motor driver.** The L298N is retired (DEC-03); nothing has replaced it.
  **Recommendation, not accepted:** the **Pololu Dual TB9051FTG** koala-bot already
  selected — 4.5–28 V, so it covers either outcome of OQ-01, with current sense and
  thermal protection. Reusing the family part also means one driver to understand.

- **OQ-07 — Battery chemistry, voltage and capacity.** Follows from OQ-01 and DEC-07.
  Must be sized for **stall current**, not average draw, and prototyping happens from the
  eventual pack rather than a bench supply. **If the arm rides on the same pack (OQ-12),
  stall means something much larger** — see
  [`architecture.md`](architecture.md#the-arm-rewrites-the-budget).

- **OQ-08 — Identity of the fitted DC-DC converter module.** Toroidal inductor, two
  trimpots, no legible part number. Its rating and set-point are unknown, so it cannot be
  relied on. Either identify and measure it, or discard it. Moot if OQ-01 resolves to
  12 V motors, which remove the need for a separate motor rail.

## Software and networking

- **OQ-05 — Zenoh or plain DDS.** DDS discovery is multicast and does not reach the
  coordinator, which sits behind NAT in a WSL2 instance on a private overlay network.
  **Recommendation, not accepted:** **Zenoh** (`zenoh-bridge-ros2dds` or `rmw_zenoh`)
  rather than a host-networking workaround, because the same wall reappears the moment
  any robot is on a different network. The counter-argument is that a workaround is
  cheaper *today* and this robot may never leave the LAN.

- **OQ-06 — Which Pi for the intent tier.** A **Pi 4** is already fitted from the first
  build; the family standard is a **Pi 5**
  ([common.md](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#compute-the-two-tier-split)).
  Milestone 1 needs no Pi at all, so this genuinely does not need deciding yet — which is
  the argument for not deciding it.

## Perception

- **OQ-04 — Where pose and heading come from.** Wheel odometry on a tracked skid-steer
  is [weak by construction](architecture.md#odometry-is-weak-by-construction) — rotation
  especially. Candidates: encoders for translation, an IMU for heading, and depth-camera
  SLAM for global pose, which is the route the hexapod already runs (RealSense +
  RTAB-Map). Undecided, and deliberately deferred past milestone 1.

- **OQ-09 — Which RealSense cameras, and whether two are viable.** The models fitted to
  the first build are **unrecorded**. Two RealSense D4xx share a single USB 3 host
  controller on a Pi 4, a known bandwidth conflict and a **plausible, unverified** second
  reason the original bring-up failed. **Recommendation, not accepted:** start with one.

## Mechanical

- **OQ-12 — Whether the chassis can carry the SO-ARM101 without tipping.** The goal is in
  [`concept.md`](concept.md#what-it-is-for); this is whether the geometry allows it.

  | Verified | |
  |---|---|
  | Chassis footprint · mass · rated payload | 225 × 220 mm · 1.3 kg · **3 kg** ([`hardware.md`](hardware.md#the-chassis)) |
  | SO-101 follower | **6 DoF**, reach **~500 mm**, payload **~500 g** ([Robotics Center](https://www.roboticscenter.ai/hardware/so-101), checked 2026-09-07) |
  | Feetech STS3215 | **55 ± 1 g** each; 6 per arm = **330 g** ([servodatabase](https://servodatabase.com/servo/feetech/sts3215), checked 2026-09-07) |

  **Arm mass is the missing number.** Vendor listings quote **2.5 kg** for an SO-ARM101,
  but that is a *shipped kit* figure — 330 g of servos plus printed PLA does not reach it.
  Bottom-up estimate **1.0–1.3 kg, unverified**.

  **Mass budget passes; tipping does not.** Arm + Pi + battery + driver ≈ **2.2–2.5 kg**
  against a 3 kg rating: inside, but tight. Taking moments about the front of the track
  contact patch (~110 mm ahead of centre), arm mounted at deck centre and held horizontal
  at full reach — **all figures estimated, assumptions as stated**:

  - Overturning: `0.5 kg × 390 mm` (payload) + `~1.15 kg × ~110 mm` (arm CoM) ≈ **320 kg·mm**
  - Restoring: `~2.5 kg × 110 mm` ≈ **275 kg·mm**

  It goes over — and that is **static**. Braking, or a lip taken with the arm extended, is
  worse. Mitigations, none yet chosen: mount the arm base **rearward** on the deck; put the
  battery at the opposite end as deliberate ballast; **limit the horizontal reach envelope
  in firmware**. Each moves the sum substantially, and each constrains where the battery
  and Pi go — so this is an input to milestone 0, not a milestone-5 discovery. Total mass
  also raises the drive torque required, which feeds back into OQ-01.

  **Cheap to close, and already in progress:** **weigh the printed parts as they come off
  the plate**, then redo the arithmetic with real masses and a chosen mount position. The
  arm is being printed anyway, so the measurement costs nothing.

- **OQ-10 — Whether the existing white mounting plate is printed or laser-cut.** Decides
  whether it can simply be reprinted to a new layout, or must be redesigned. One look at
  the edge finish settles it.
