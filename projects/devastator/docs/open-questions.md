# Open Questions (pending decisions)

Unresolved. Resolve → move to [`decisions.md`](decisions.md).

**Several of these carry a recommendation.** A recommendation is *not* a decision — it
is one option with an argument attached, offered and not yet accepted. Do not build
against one, and do not promote one to `decisions.md`, without the owner deciding.

---

## Electronics

- **OQ-07 — Battery capacity, fuse rating and the logic-rail regulator.** *Narrowed
  2026-09-07:* chemistry and voltage are settled at **3S LiPo, 12 V** (DEC-12); what
  remains is how much of it. Must be sized for **stall current**, not average draw, and
  prototyping happens from the eventual pack rather than a bench supply. **If the arm
  rides on the same pack (OQ-12), stall means something much larger** — see
  [`architecture.md`](architecture.md#the-arm-rewrites-the-budget).

## Software and networking

- **OQ-05 — Zenoh or plain DDS.** DDS discovery is multicast and reaches only the home
  LAN. *Amended 2026-09-21:* the coordinator host is no longer behind WSL2 NAT; it is on the
  LAN and receives robot topics over plain DDS. The question remains for any robot off it.
  **Recommendation, not accepted:** **Zenoh** (`zenoh-bridge-ros2dds` or `rmw_zenoh`)
  rather than a host-networking workaround, because the same wall reappears the moment
  any robot is on a different network. The counter-argument is that a workaround is
  cheaper *today* and this robot may never leave the LAN.

- **OQ-06 — Which intent computer.** Resolved 2026-09-18 by DEC-15: a Pi 5 with the
  AI HAT+ 2. Which unit is open under OQ-13; two of the family's Pi 5s have no on-robot
  role ([common.md](../../../docs/common.md#companion-computers-in-hand--the-raspberry-pi-5-fleet)).

## Perception

- **OQ-13 — Fitting the AI HAT+ 2, allocated to this robot on 2026-09-18.** The owner's
  AI HAT+ 2 (Hailo-10H, delivered 2026-09-15) could not go on the hexapod: it is powered
  through the GPIO header, cannot be stacked on, and the hexapod's header is taken
  ([wk-hexapod DEC-24](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/decisions.md);
  facts in [common.md](../../../docs/common.md#ai-hat-2-and-nvme)). Here the header is
  free, but the HAT needs a **Pi 5** (OQ-06), a place on the single PCIe lane alongside
  any NVMe (the family's [switch candidate](../../../docs/common.md#ai-hat-2-and-nvme) is
  unverified for Hailo-10H), and a line in the power budget (DEC-07) of up to 8 W peak
  on LLM loads, a third-party figure. Not before the drivetrain works (DEC-06).
  **2026-09-19: the HAT runs on Ubuntu 24.04 natively** on the family's bench Pi 5
  (rev 1.0): DKMS driver `hailo1x_pci` 5.1.1 and firmware 5.1.1 from Raspberry Pi's apt
  archive, `hailortcli` identifies a HAILO10H — recipe and limits in
  [common.md](../../../docs/common.md#operating-system-for-the-hats-pi-5). What remains
  for this robot: fitting it, the PCIe/NVMe sharing question, and the power budget line.

- **OQ-04 — Where pose and heading come from.** Wheel odometry on a tracked skid-steer
  is [weak by construction](architecture.md#odometry-is-weak-by-construction) — rotation
  especially. Candidates: encoders for translation, an IMU for heading, and depth-camera
  SLAM for global pose, which is the route the hexapod already runs (RealSense +
  RTAB-Map). Undecided, and deliberately deferred past milestone 1.

- **OQ-09 — Which depth camera.** The first build's pair was a D435i and a T265
  ([`sourcing.md`](sourcing.md)); neither is on the tank now. The T265 is end-of-life and
  unsupported by current librealsense, so it is out. The family's one D435i is banked
  with the Orin Nano, not this robot's Pi 5
  ([common.md](../../../docs/common.md#perception-placement)). Roadmap milestone 2 plans
  **one** camera on the Pi 5 + AI HAT+ 2 (DEC-15); which, and whether it gives depth, is
  open.

## Mechanical

- **OQ-12 — Whether the chassis can carry the SO-ARM101 without tipping.** The goal is in
  [`concept.md`](concept.md#what-it-is-for); this is whether the geometry allows it.

  | Verified | |
  |---|---|
  | Chassis footprint · mass · rated payload | 225 × 220 mm · 1.3 kg · **3 kg** ([`hardware.md`](hardware.md#the-chassis)) |
  | SO-101 follower | **6 DoF**, reach **~500 mm**, payload **~500 g** ([Robotics Center](https://www.roboticscenter.ai/hardware/so-101), checked 2026-09-07) |
  | Feetech STS3215 | **55 ± 1 g** each; 6 per arm = **330 g** ([servodatabase](https://servodatabase.com/servo/feetech/sts3215), checked 2026-09-07) |

  **Arm mass — measured 2026-09-17: 810 g.** Fully assembled with the serial bus driver, no
  external wiring; weighed by the owner
  ([SO-ARM101 `test-log.md`](../../soarm101/docs/test-log.md), its OQ-04). This **replaces the
  1.0–1.3 kg bottom-up estimate** and lands 340 g below the ~1.15 kg midpoint the moments below
  were computed from, so **those figures are stale and need redoing.** Vendor listings quoting
  **2.5 kg** are shipped-kit weight, as suspected. A mounted arm will add the loom to whatever
  drives the bus, which 810 g excludes.

  **What the lighter arm does and does not buy — the mass budget improves, the tipping barely
  does.** Arm mass sits on *both* sides of the moment balance: it overturns (its CoM is ahead of
  the pivot) and it restores (it presses on the contact patch). Substituting 810 g for 1.15 kg
  drops the overturning sum by ~38 kg·mm and the restoring sum by ~37 kg·mm — very nearly a
  wash, because **the dominant overturning term is the 500 g payload at 390 mm, which has not
  changed.** Expect the verdict below to stand. Two things to settle when the sums are redone,
  rather than guessed at here: whether the restoring term should include the **1.3 kg chassis**
  (the figure used, ~2.5 kg, is the *payload* line, which reads like an omission), and where the
  arm's CoM actually sits now it can be weighed and balanced rather than estimated.

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
  also raises the drive torque required; the chosen motors give **6.4 kg·cm** each
  (DEC-11), which the loaded figure must be checked against.

  **Cheap to close, and already in progress:** **weigh the printed parts as they come off
  the plate**, then redo the arithmetic with real masses and a chosen mount position. The
  arm is being printed anyway, so the measurement costs nothing.

- **OQ-10 — Whether the existing white mounting plate is printed or laser-cut.** Decides
  whether it can simply be reprinted to a new layout, or must be redesigned. One look at
  the edge finish settles it.
