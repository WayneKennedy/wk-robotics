# Status

**Where things stand, and what is in flight.** Read this after
[`AGENTS.md`](../AGENTS.md) when picking the work up on a new machine or in a new
session — it is the handover point that the per-project repos cannot provide, because
these items span more than one of them.

This is a *state* document, not a log. When an item resolves, delete it; when it belongs
to one project, move it to that project's repo and leave a link. It is not a transcript —
see [`AGENTS.md`](../AGENTS.md#what-does-not-belong-here).

**Last reviewed: 2026-09-15.**

---

## Resuming on a new machine

```bash
git clone git@github.com:WayneKennedy/wk-robotics.git    # or https://github.com/WayneKennedy/wk-robotics.git
cd wk-robotics
```

Then read [`AGENTS.md`](../AGENTS.md) in full — it is the complete, provider-neutral
onboarding, and it is written to make sense cold.

The sibling repos are expected as **peers of this directory**, not submodules:

```bash
cd ..
git clone git@github.com:WayneKennedy/koala-bot.git
git clone git@github.com:WayneKennedy/3d-printing.git        # private
git clone git@github.com:WayneKennedy/wk-inventory.git       # private: stock, project register, machine identifiers
git clone https://github.com/TheRobotStudio/SO-ARM100.git    # upstream, not a fork
git clone git@github.com:WayneKennedy/wk-hexapod.git
git clone git@github.com:WayneKennedy/wk-drones.git
# Hexapod vendor reference: a sparse clone of Freenove's upstream — recipe in wk-hexapod docs/operations.md
git clone git@github.com:AshishA26/Orion-Quadruped.git      # upstream reference, read-only, ~2.7 GB; see Open threads
```

`wk-hexapod` and its vendor reference are checked out on the robot's own Pi, where hexapod
work happens; on the workstation they usually are not. Clone them before doing hexapod
work rather than reasoning from this repo's summary of them.

Nothing here depends on a particular AI assistant, editor or shell. The repository is the
state; a session that adds to it is expected to leave it complete.

---

## Open threads

### Orion-Quadruped upstream clone — purpose not yet recorded

Cloned to `../Orion-Quadruped` on 2026-09-14, read-only, no fork. Upstream is
[AshishA26/Orion-Quadruped](https://github.com/AshishA26/Orion-Quadruped), default branch
`master`, 312 commits from 2025-11-06 to 2026-09-03, 143 stars (checked 2026-09-14). **No
licence file and no licence on GitHub** — all rights reserved by default, so nothing from
it can be vendored or redistributed without asking the author; reading and building from
it privately is the only safe use until that is resolved. Its three Git submodules
(Isaac ROS common, Argus camera, rf2o laser odometry) are **not initialised**.

What it is: a 12-DOF quadruped on a Jetson Orin Nano (Isaac ROS in Docker, TensorRT) with
a custom STM32F401 FreeRTOS reflex board over UART — the family's
[two-tier split](common.md#compute-the-two-tier-split) as built by someone else. Twelve
270° PWM hobby servos (20 kg-class SunFounder / DSServo, per `models/Electronics/`) on a
PCA9685; BNO055 IMU; INA3221 three-rail battery monitoring; RPLIDAR A1M8 with
`slam_toolbox` and `nav2`; dual CSI stereo cameras; PPO locomotion training in Isaac Lab
with a SolidWorks → URDF → USD pipeline; KiCad control and power boards. 3D-printed
chassis with silicone-moulded feet and bearings in every joint. Its `README.md` is a
complete map of the tree.

Why it is here is unrecorded. Candidate homes: a quadruped entry under
[`ideas.md` → Externally designed builds](ideas.md#externally-designed-builds) (the
SpotMicro line there is the only quadruped mention today), or a reference for the pending
[Jetson purchase](common.md#ai-compute--purchase-comparison), since it is a working
Orin Nano robot stack. Resolves when the owner records the intent and this entry moves
to that home.

### AI compute purchase — AI HAT+ 2, Jetson or DGX Spark

**Ordered from The Pi Hut, owner-confirmed 2026-09-13:** Raspberry Pi AI HAT+ 2 and
[Waveshare 2-Channel PCIe Expander for Raspberry Pi 5](https://thepihut.com/products/2-channel-pcie-expander-for-raspberry-pi-5?variant=54400781156737),
retailer SKU **WAV-30490**, manufacturer model PCIe TO 2-CH PCIe HAT (two downstream FFC
connectors). **Delivered 2026-09-15** — The Pi Hut #1620881, ordered 2026-09-13: AI HAT+ 2
£192.00, expander £14.40, plus a 52Pi Tiny M.2 PCIe Adapter £11.50 and a PCIe Cable
Selection Pack £7.70 (with a screwdriver set; £238.40 total), per the invoice read
2026-09-17. Operation is not confirmed; AI HAT+ 2 compatibility remains untested.

Owner considers the installed NVMe HATs essential. The identified existing adapter,
cable constraints, connector conflict and possible
switch/enclosure alternatives are in
[`common.md` → AI HAT+ 2 and NVMe](common.md#ai-hat-2-and-nvme).
Owner also raised Orin Nano Super, reComputer Super J401 NX 16 GB and NVIDIA DGX Spark
on 2026-09-13. The
[capability and cost comparison](common.md#ai-compute--purchase-comparison)
records the assessment and remaining limits, including the existing RTX workstation as
the first ground-compute option. Owner mentioned onboard real-time inference on a Holybro
drone: that is the Holybro 10" in wk-drones, the family's aerial-robot candidate
([`projects.md`](projects.md#holybro-10-wk-drones)); its payload, power and latency
requirements are not established.
Spark is considered for ground use. **Jetson ordered 2026-09-17: the 8 GB Orin Nano Super
Developer Kit**, not the 16 GB Orin NX — RS order 3020377767, stock no. 264-7384, qty 1
(order confirmation read 2026-09-17). RS's follow-up notification gives £320.00 ex VAT
(£384 inc, matching the live listing of 2026-09-16) and a delivery date of 2026-09-18;
part 945-13766-0005-000 (the EU/UK region variant). Not delivered as of 2026-09-17. **Leaning to the Holybro X500** as its highest-value use (owner,
2026-09-17; not decided — wk-drones `aircraft/holybro-10` OQ-03). **Storage allocated:** a
spare WD_BLACK SN850 1 TB NVMe from the owner's parts box (owner, 2026-09-17). Per
[NVIDIA's carrier layout](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html)
the kit has an M.2 Key-M 2280 slot at PCIe 3.0 x4 and a Key-M 2230 slot at PCIe 3.0 x2; the
SN850 is a 2280 PCIe 4.0 drive, so it belongs in the 2280 slot and runs at Gen 3 speed.
This unit has no heatsink (owner, 2026-09-17). Stockist
survey, Super-mode and JetPack detail are in
[`common.md`](common.md#ai-compute--purchase-comparison). Next: confirm the intended AI HAT/SSD
wiring and cable reach, then validate NVMe cold boot plus concurrent inference/storage
operation. Select target workloads for the Jetson.
No architecture change decided.

### The GPU workstation holds no robotics checkouts — 2026-09-14

Owner-reported 2026-09-14: the koala-bot clone on the GPU workstation was committed,
pushed and deleted, and that machine no longer has any robotics repo checked out. This
workstation is now the sole working folder for every robotics repo, koala-bot included.
`koala-bot` origin `main` is `cacc81c` (2026-09-12); nothing newer arrived, so its links
to `wk-devastator` and `wk-soarm101` are still the archived-repo URLs and will be
rewritten on the next koala-bot edit. The hexapod's Pi still carries its own `wk-hexapod`
checkout; pull there before hexapod work. Resolves when the koala-bot links are rewritten.

### Surplus drive hardware — home undecided

Two 37D motors and one Dual TB9051FTG arrived 2026-09-11 with no project to go to:
koala-bot's four-wheel V1 was cancelled before its follow-on order shipped. A Teensy 4.1 NE
arrived the same day, bought deliberately unallocated for whichever project is ready first.
They are
listed in [wk-inventory `docs/stock.md`](https://github.com/WayneKennedy/wk-inventory/blob/main/docs/stock.md); the candidate use is
[a pure balance bot](ideas.md#a-pure-balance-bot). Resolves when that idea earns a repo
or the parts are allocated elsewhere.

### SO-ARM101 is the reflex-tier proving ground

Decided 2026-09-12 (SO-ARM101 DEC-12) and brought forward 2026-09-14 (DEC-14: the LeRobot
phase ends at calibration; the runtime is a Teensy 4.1 on micro-ROS into ROS 2): the arm's
servo bus moves to a Teensy 4.1 to develop the MCU-drives-the-bus pattern before koala-bot
and wk-devastator depend on it. Cross-project because what it proves feeds
[`common.md` → Compute](common.md#compute-the-two-tier-split) and the topic contract. Which
Teensy, the bus connection, the agent host and the ROS 2 distribution are open (the arm's
OQ-09); the unallocated 4.1 NE in the pool is the candidate. Resolves when the arm moves
under an MCU and the lesson lands in `common.md`.

### Collision awareness — SO-ARM101 has a first, host-side version

Raised 2026-09-12: joint limits cannot prevent self-collision, and no stack in the family
models geometry at runtime. The layered picture and where each layer sits in the two-tier
split are in [`common.md` → Collision awareness](common.md#collision-awareness--open-family-wide).
**Since 2026-09-14 SO-ARM101 carries a world keep-out in host Python** — forward kinematics
from upstream's URDF, a plane-minus-cylinder forbidden region checked on every link, IK, and
guarded moves that traced a square and a cube ([its roadmap, milestone 4](../projects/soarm101/docs/roadmap.md)).
The arm's own base is modelled too, it wakes itself from any contact pose, and the model checks
against a tape within 1.5 cm (milestone 4, closed 2026-09-15). Still to come: the check moved to
the reflex tier (milestone 5, Teensy 4.1).
Resolves when one robot carries a working envelope on its reflex tier and the lesson is
written back here.

### SO-ARM101 speed work — 4.6 to 7.5 cm/s, 2026-09-18

**Done and stopped cleanly.** The question "how fast can this arm work" is answered for the 12 cm
cube: **8 cm/s commanded, 7.5 cm/s real, max tracking lag 86 of 150** — a **63% gain** on the
4.6 cm/s the arm was really doing when validated (the logged 5 cm/s was 8% optimistic; see the
arm's [`test-log.md`](../projects/soarm101/docs/test-log.md)).

Three things got it there: **`P_Coefficient` 16 -> 32 on the four arm joints** (EEPROM, owner
approved, the arm's OQ-17 — ~20% less following error and no oscillation); **corner easing** and a
new **joint-space speed cap**, because above ~8 cm/s the limit is a joint *reversal* at a path
corner, not steady-state error; and the honest time-parameterisation of 2026-09-17. Supply is a
**Maplin desk PSU, 12 V 3 A**, which never exceeded 16% of its rating — ample, and OQ-03's
recommendation is unchanged for lifting and stalling.

**Two corrections came out of it, both worth carrying.** A first pass claimed the rail sag was the
*current path*; it is not established — the servos' own ADC cannot separate wiring drop from a dip
inside the servo, so the bulk-capacitance recommendation is weaker than written, and upstream asks
for none (OQ-03, corrected after the owner challenged it). And **the bus corrupts 1.3-2.4% of
telemetry reads and always has**, on every supply — recorded until now as isolated incidents. That
has caused false guard trips, is mitigated by a plausibility filter in `shapes.py`, and is raised
as **OQ-18**; it matters before the Teensy reads telemetry at reflex-tier rates (OQ-09).

**The arm is parked, torque off, on the bench, and the tuning is durable** — power-cycled
2026-09-18, after which all four arm joints still read `P_Coefficient` 32 and every position limit
and homing offset re-read equal to the calibration JSON.

### Untracked terrain files on the workstation

`~/Code/FirstTerrain/` and `~/Code/Terrain_2019.zip` (237 MB) are under no version
control. They may belong to the same retired lineage as the archived terrain repos below.
Local disk only — no GitHub action outstanding. Decision needed: keep, archive offline, or
delete.

### Moved to a project home

**SO-ARM101 servo commissioning** (2026-09-09) — held here for one day while the build had
no repo of its own. Now in
[wk-soarm101 `docs/servos.md`](../projects/soarm101/docs/servos.md).

### Deferred, already recorded elsewhere

Ideas and candidate projects are in [`ideas.md`](ideas.md); per-project backlogs live in
each project's own repo. Nothing is duplicated here.

---

## The GitHub estate

Current as of 2026-09-13. Robotics repos and their state are
in [`projects.md`](projects.md); this section covers only what changed and why, so it is
not re-derived.

**Retired — archived (read-only, reversible), superseded by `codename-talis`:**

| Repo | Note |
|---|---|
| `ZappGame-Terrain` | Terrain work absorbed into `codename-talis` |
| `com.zappfyre.game.terrain` | As above |
| `star-citizen-virpil-controls` | HOTAS bindings; retired alongside the pair |

**Deleted:** `WayneKennedy/7dtd-map` — a fork of
[`kui/7dtd-map`](https://github.com/kui/7dtd-map), removed 2026-09-07 once its purpose was
served. PR [#247](https://github.com/kui/7dtd-map/pull/247) *"Support non-RGBA PNGs in
world file processing"* was merged upstream on 2026-08-10 as commit `bcf28b57e`; both fork
branches were verified `ahead_by=0` with zero unique commits before deletion, so nothing
was lost. **That repo is now consumed from upstream, not forked.**

**Renamed 2026-09-13:** `wk-drone-bee35` → `wk-drones`, now a fleet record with the Bee35
under `aircraft/bee35/`; GitHub redirects the old name.

**Consolidated 2026-09-13:** `wk-devastator` → [`projects/devastator/`](../projects/devastator/)
and `wk-soarm101` → [`projects/soarm101/`](../projects/soarm101/) in this repository,
history carried over with `git subtree add`. Reasoning: both were small, docs-led records
that restated the family rules and linked back to this repo from a dozen files each; as
folders they share one `AGENTS.md` layer and one clone. The old repos are **archived, not
deleted**, with a banner in each README, because GitHub redirects renamed repos but not
merged ones and koala-bot still links to them. `koala-bot`, `wk-hexapod`, `3d-printing`
and `wk-drones` stay peers: OSS with its own licensing, pulled onto a Pi, private, and
mostly-not-robots respectively.

**Deleted 2026-09-13:** `WayneKennedy/fn-hexapod`, a 9 MB rewritten-history snapshot of
Freenove's 477 MB hexapod repository, kept only so the robot's Pi could clone the ten
files it needed. Replaced by a sparse clone of upstream (wk-hexapod DEC-20 records the
reasoning and the pinned commit). Every link to it here and in wk-hexapod was replaced
before deletion; nothing unique was lost, its content was upstream's.

**Branch naming:** `main` everywhere, and `init.defaultBranch = main` is set globally on
the workstation.
