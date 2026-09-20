# Status

**Where things stand, and what is in flight.** Read this after
[`AGENTS.md`](../AGENTS.md) when picking the work up on a new machine or in a new
session — it is the handover point that the per-project repos cannot provide, because
these items span more than one of them.

This is a *state* document, not a log. When an item resolves, delete it; when it belongs
to one project, move it to that project's repo and leave a link. It is not a transcript —
see [`AGENTS.md`](../AGENTS.md#what-does-not-belong-here).

**Last reviewed: 2026-09-18.**

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

### The single expensive items — where each earns most (opened 2026-09-18)

The owner has one each of the **Jetson Orin Nano**, the **AI HAT+ 2** and the **RealSense
D435i**, and wants each where it gives most value.

**Decided 2026-09-18 (owner):**
- **The hexapod keeps ROS 2 and returns to the kit's camera and ultrasonic**; it stays the
  family's baseline intent-tier reference, with the kit's hardware ceiling
  ([wk-hexapod DEC-25, DEC-26](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/decisions.md)).
- **The Devastator is the second intent-tier reference, a step above it:** Teensy 4.1
  reflex tier as motor controller, Pi 5 + AI HAT+ 2 + a camera not yet chosen
  ([its DEC-15](../projects/devastator/docs/decisions.md)).
- **The Orin and the D435i are a pair** — in-camera depth is what justifies the D435i's
  cost, and the Orin can use it fully ([`common.md`](common.md#perception-placement)).

**Open:**
- **Where the Orin + D435i pair goes.** The Holybro 10" is a candidate — depth
  avoidance is essential there (owner, 2026-09-17), the RealSense mount is owned, and
  ArduPilot's avoidance path names the D435i
  ([wk-drones Holybro OQ-09](https://github.com/WayneKennedy/wk-drones/blob/main/aircraft/holybro-10/docs/open-questions.md))
  — but the owner is not sold, for two reasons: an unflown airframe puts both items at
  crash risk, and it would fly rarely — too large for the garden or the local beach, so
  only at a flying field or on permitted private land. Until decided, both are
  unallocated stock.
- **The Devastator's camera** (its OQ-09) and which spare Pi 5 it takes (its OQ-13).

### A proven printed build alongside koala-bot — open (2026-09-18)

koala-bot continues at background pace, throttled by the owner's frontier-AI token limits
(its OQ-20). The owner doubts the ambition of its unique limb geometry and wants
"something proven that you can print and assemble as easily as SO-ARM was". **Nothing is
decided.** Candidates from the record: the tank (blocked on motors not guaranteed for
end October); [Open Duck Mini V2](ideas.md#open-duck-mini-v2) (parked 2026-09-07; 7.4 V
servos, a fresh order); and **LeKiwi** — the SO-101 arm on a three-omniwheel base driven
by three 12 V STS3215s, Pi 5, LeRobot-native
([upstream BOM](https://github.com/SIGRobotics-UIUC/LeKiwi/blob/main/BOM.md); already the
tank's closest prior art in its `references.md`). An assistant's recommendation, not
accepted: LeKiwi, because it reuses the finished arm, the 12 V servos and a spare Pi 5,
and its base plate carries a Pi or Orin cage. Not yet checked against the upstream BOM,
print list or stock.

**The owner's two directions for the Orin ground robot (2026-09-18).** LeKiwi is seen as
a no-regrets immediate build, but too little "wow" for nearly $1,000 of compute and
sensing. The two directions, both needing CAD but simpler than koala-bot's, both robots
that would be powered up every day:

1. **A quadruped remix on STS3215s** ("MicroSpot", or reluctantly Orion): the owner's
   remix of a well-known unfinished project, given back finished. Blocker: no STS3215
   design files for either were known. Found 2026-09-18, unverified beyond its README:
   [`alarin/smalldog`](https://github.com/alarin/smalldog) — a 12-DoF printed quadruped
   on 12 × ST3215, parametric CadQuery CAD, FEA, ROS 2 / MuJoCo sim and an RL policy.
   Not a SpotMicro derivative; licence, maturity and print sizes unchecked.
2. **A wheeled humanoid torso on the two 37D motors in stock**, two SO-ARMs and a head
   carrying the D435i. This is the shape of upstream's own
   [XLeRobot](https://github.com/Vector-Wangel/XLeRobot): LeKiwi base, two SO-101 arms,
   a 2-motor head, 17 STS3215s, $660, under four hours' assembly
   ([BOM](https://xlerobot.readthedocs.io/en/latest/hardware/getting_started/material.html)),
   with a Jetson Orin Nano variant sold as a kit. The differences from the owner's
   picture are the base (omniwheels on three STS3215s, not the 37Ds) and the torso (an
   IKEA cart, not a printed humanoid). **Agreed in principle by the owner 2026-09-18,
   with departures** — printed torso (no cart), arms hanging from shoulders, head on a
   neck, and doubt about the omni base. Banked as an idea:
   [`ideas.md`](ideas.md#a-two-armed-wheeled-torso--the-orin-ground-robot).
   **Form reference, 2026-09-20:** the owner supplied an AliExpress kit screenshot for
   general layout and scoped the inspiration to **the sternum up** — shoulder and head
   geometry only, not the body, the pedestal or the arms. Read against the record in
   [`ideas.md`](ideas.md#a-two-armed-wheeled-torso--the-orin-ground-robot), which also
   carries an unaccepted assistant proposal: build the torso on a bench column first and
   move it onto a base later.

### ROS 2 install audit — hexapod, bench host, Orin (opened 2026-09-19)

Owner's rule: ROS 2 installs are familial, the hexapod's `ubuntu-setup.sh` is the
reference ([`common.md`](common.md#ros-2-installs-are-familial)). **To do at the end of
the current bring-up:** audit all three hosts against that table, bring each deviation
into line or record it as a decision in the host's project.

**Audit done 2026-09-20**, all three hosts, results in
[`common.md`](common.md#ros-2-installs-are-familial). The install spine is uniform —
same Ubuntu, same Jazzy from apt, same `ros2-apt-source` mechanism, same base packages,
Fast DDS on domain 0 everywhere, and no ROS in any `.bashrc`. **What is left to do:**

1. ~~Bench host workspace~~ — **done 2026-09-20.** It now builds from a checkout at
   `~/Code/wk-robotics/projects/devastator/software/ros2_ws` with `--symlink-install`, runs
   from the repo's `scripts/launch.sh`, and the stale `~/ros2_ws` is gone. The enrolled
   galleries (`wayne`, `bev`×4) were preserved. Pattern recorded in
   [*Host checkouts*](common.md#host-checkouts).
2. **Push `orin-perception-bench` to origin.** Until then `projects/orin-perception/`
   exists only in a local worktree and an rsync on the Orin.
3. ~~Timezone~~ — **done 2026-09-20.** The owner ruled that all robots run UTC; the two Pis
   were moved and all three hosts now agree. Recorded as
   [*Robots run on UTC*](common.md#robots-run-on-utc).
4. ~~Realign the hexapod's script~~ — **done 2026-09-20**, with one correction to this
   audit. `ros-jazzy-camera-ros` was genuine drift and is now listed in `ubuntu-setup.sh`
   (it drives the kit's OV5647 for DEC-25). **`ros-jazzy-slam-toolbox` was not drift at
   all** — it is a hard dependency of `ros-jazzy-nav2-bringup`, and removing it would take
   Nav2 with it; it was merely mis-marked as manually installed, which is what made it look
   deliberate. Marked `auto` on the robot. The robot's manual package set now matches the
   script exactly. **Still open:** its ROS packages are ~3 months older than the other two
   hosts'. Not upgraded — that wants a window where the robot can be watched coming back up.
5. **Decide the discovery-range question** (below) — measured at 35× throughput. Both
   benches now pin `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` in their `launch.sh`, so the
   symptom is contained; what is open is the family rule (one domain per robot, or
   localhost-only by default and the domain opened deliberately).
6. **The Orin's last step — face recognition** — needs a person in front of the D435i. It is
   the only thing left between it and parity with the HAT half.

### Repo shape and host checkouts (open — raised by the owner 2026-09-20)

**Not decided.** The owner asked whether to push back on the
[2026-09-13 consolidation](#the-github-estate) that made the Devastator and the SO-ARM101 folders
here rather than peer repos, and proposed instead that **this repository be cloned and
regularly fetched on every robot intent host**.

**What the record already says.** The consolidation's own criterion for staying a peer repo
was, in order: OSS licensing (koala-bot), **pulled onto a Pi** (wk-hexapod), private
(3d-printing), mostly-not-robots (wk-drones). At the time the two consolidated projects were
docs-only, so "pulled onto a Pi" did not fire. **It fires now:**
`projects/devastator/software/ros2_ws/src/hailo_perception/` runs on the bench host and
`projects/orin-perception/` runs on the Orin.

**The assistant's recommendation (2026-09-20), for the owner to accept or reject:** keep the
consolidation and adopt the clone rule, because the clone rule *retires* the criterion rather
than contradicting it — if this repo is on every intent host, a folder-project is pulled onto
a Pi exactly as easily as a peer repo would be, and the reason to split them back out goes
away. Supporting facts, all verified 2026-09-20: the repo is ~14.5 MB including history; it is
public, so robots can clone it anonymously over HTTPS with no deploy key; the bench host and
the Orin both have git 2.43.0 and can already reach GitHub; and **the hexapod's Pi has cloned
it since at least 2026-09-19** — so the pattern exists, it is simply neither uniform nor kept
fresh (that clone was 5 commits behind when checked). Adopting it also fixes audit item 1 by
construction. `wk-hexapod` should stay a peer either way: it is not a small docs-led record
but a large working repo with its own decisions, roadmap, firmware and six-package workspace,
and it is the family's reference install.

**Open sub-questions the owner has not ruled on:** whether host clones are strictly read-only
consumers (`git pull` only, authoring on the workstation) to avoid divergent heads across
machines; whether robots clone over HTTPS rather than SSH, since an SSH deploy key on a robot
on a shelf can push; and whether "regularly fetched" means a `git fetch` timer (safe — never
touches the working tree) rather than an automatic `pull`, which on a `--symlink-install`
workspace would change the code a running robot is executing.

### Claude CLI placement (open — raised by the owner 2026-09-20)

**Not decided.** The hexapod's Pi is the only host with a local Claude CLI install; the
owner's stated motive is minimising how many hosts need a `/login`, and they invited pushback.

**The assistant's recommendation: keep it as it is — do not install on the other two.** The
motive is sound and there is a stronger reason for it than convenience: every extra install is
another credential, another config to drift, and another `.claude.json` accumulating session
history on a machine that lives on a shelf. The evidence is this session — **the entire
three-host ROS 2 audit was done from the workstation over SSH**, including reading apt
history, diffing package sets, comparing file checksums across hosts and summarising a 16 MB
log, with no agent on any remote host. `scripts/ros2-fingerprint.sh` is the generalisation of
that pattern: `ssh <host> bash -s < script` gives an assistant the host's state without an
assistant on the host.

**Note that this is separable from the clone question above** — cloning this repo on a host
does not imply installing an assistant there; the clone serves `git pull` deploys and gives an
assistant working *over SSH* the repo's context on-host.

**When to revisit:** a robot that must be worked on while off the LAN — a field run on
battery, away from the workstation — is the case SSH does not cover, and the hexapod is the
robot most likely to be in it. That may be why the install is there.

### Perception bench: the same experiment on the HAT and on the Orin (opened 2026-09-19)

Two hosts, one experiment, so the results compare. **Owner's brief:** object and face
recognition from a camera, streamed to a web client. **Spec, so a second session can run
the Orin half independently:**

| | AI HAT+ 2 bench host (Pi 5, Ubuntu 24.04, ROS 2 Jazzy) | Orin Nano (JetPack 7.2.1, Ubuntu 24.04) |
|---|---|---|
| Camera | USB UVC webcam (C920 clone), `/dev/video0`, 1280×720 MJPEG, via `ros-jazzy-usb-cam` | Intel RealSense D435i colour stream via `realsense2_camera` (the hexapod's config is the starting point) |
| Objects | YOLOv8s/m Hailo-10H HEFs, Model Zoo v5.4.0 (on the host in `~/hailo/models`) | YOLOv8s/m on the GPU: TensorRT via an Ultralytics export, or Isaac ROS if it supports JetPack 7 (unverified) |
| Faces | `scrfd_2.5g` detection + `arcface_mobilefacenet` embeddings (Model Zoo, Hailo-10H builds) | An equivalent SCRFD + ArcFace pair on the GPU (InsightFace models, TensorRT) |
| Recognition | Gallery of enrolled embeddings on the host, cosine match; enrolment from the stream or from recorded unknown-face crops | Same gallery format — but embeddings only transfer between hosts if the network, weights and alignment are identical, and even then the cross-host similarity is unmeasured. **Share enrolment images, not vectors**, unless the Orin runs the same `arcface_mobilefacenet` (see the HAT package README) |
| Stream | Annotated image topic → `ros-jazzy-web-video-server` (MJPEG in a browser) | Same |
| Record | End-to-end fps at 1280×720, per-stage latency, Pi CPU load, chip and Pi temperatures, power if measurable | Same, plus which JetPack power mode |
| Spoof test (added 2026-09-19) | Show the camera a phone photo of an enrolled person: expected to be recognised (2D only) | Same photo: can the D435i's depth over the face box reject it? The liveness question the door-camera idea needs |

Language: C++ ROS 2 nodes on the HAT (no Python binding on 24.04); on the Orin whatever
its toolchain makes easiest. Results land in `common.md` beside the
[HAT measurements](common.md#first-measurements-on-the-ai-hat-2-2026-09-19). Code for the HAT half
lives in `projects/devastator/software/` as that robot's future perception node (DEC-15);
the Orin half's home follows its allocation, undecided — keep it in a folder under this
repo's `projects/` until then. **State:** HAT half **running** since 2026-09-19 —
`projects/devastator/software/ros2_ws/src/hailo_perception/` (C++ ROS 2 node, README has the
numbers: 24 fps at 640×480 with objects and face detection, both inferences serial);
face recognition working — owner enrolled and recognised at 0.78 similarity, 19 fps with
identity running. **Orin half built 2026-09-19** in
[`projects/orin-perception/`](../projects/orin-perception/AGENTS.md) (branch
`orin-perception-bench`): Python ROS 2 node on TensorRT 10 FP16 engines — YOLOv8s/m from an
Ultralytics ONNX export, InsightFace `det_500m` (SCRFD-500M) + `w600k_mbf` (MobileFaceNet
ArcFace), not the HAT's `scrfd_2.5g`, which InsightFace does not publish by URL; same topics,
parameter names and gallery format as the HAT node, under `/orin`. Host installed with a
step-for-step copy of the hexapod's setup script (the family audit is in
[`common.md`](common.md#ros-2-installs-are-familial)). **Measured 2026-09-20** over a 21-hour
run: **28.2 fps at 1280×720** with objects, face detection and face embedding all serial,
32.8 ms per frame, 89 ms end to end, streaming MJPEG — numbers and the contention finding in
[`common.md`](common.md#first-measurements-on-the-orin-nano-2026-09-20).

**Where it stopped, and it is one step short of the HAT half.** Objects, face detection,
face embedding and the web stream all run; **face recognition was never exercised** — the
gallery directory was never created and no enrolment happened in the whole 21-hour run, so
every face stayed `unknown`. The recognition path itself is **verified working on the Orin's
GPU engines** (2026-09-20: enrolled a face from `bus.jpg` through SCRFD → ArcFace → gallery
write in the HAT's format, model provenance recorded); previously it had only been checked on
a workstation CPU through onnxruntime. **What remains needs a person in front of the camera:**
bring the bench up with `scripts/launch.sh`, publish a name on `/orin/enroll`, and confirm it
comes back on `/orin/faces` — the step the HAT half passed at 0.78 similarity.
**Load, power, thermals and a YOLOv8s vs YOLOv8m comparison were captured 2026-09-20** and
are in [`common.md`](common.md#first-measurements-on-the-orin-nano-2026-09-20); running them
exposed two script bugs, both now fixed.

### AI compute purchase — AI HAT+ 2, Jetson or DGX Spark

**Ordered from The Pi Hut, owner-confirmed 2026-09-13:** Raspberry Pi AI HAT+ 2 and
[Waveshare 2-Channel PCIe Expander for Raspberry Pi 5](https://thepihut.com/products/2-channel-pcie-expander-for-raspberry-pi-5?variant=54400781156737),
retailer SKU **WAV-30490**, manufacturer model PCIe TO 2-CH PCIe HAT (two downstream FFC
connectors). **Delivered 2026-09-15** — The Pi Hut #1620881, ordered 2026-09-13: AI HAT+ 2
£192.00, expander £14.40, plus a 52Pi Tiny M.2 PCIe Adapter £11.50 and a PCIe Cable
Selection Pack £7.70 (with a screwdriver set; £238.40 total), per the invoice read
2026-09-17. **Operation confirmed 2026-09-19** on the family's bench Pi 5 under Ubuntu 24.04: driver, firmware and `hailortcli` identify a HAILO10H — recipe in [`common.md`](common.md#operating-system-for-the-hats-pi-5). The PCIe expander is still untested.

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
part 945-13766-0005-000 (the EU/UK region variant). **Delivered and flashed 2026-09-18:**
JetPack 7.2.1 (L4T R39.2.1, Ubuntu 24.04.4, kernel 6.8.12-1021-tegra), desktop install
(owner), board config `jetson-orin-nano-devkit-super`, root on the NVMe (930 GB, grown on
first boot); boots to the 25W mode by default, MAXN_SUPER available as nvpmodel mode 2 and
not yet chosen as default. Key-only SSH, on the tailnet with Tailscale SSH; identifiers in
wk-inventory `docs/jetsons.md`. Flash procedure and its host-side gotchas are in
[`common.md`](common.md#flashing-a-jetson-from-a-2404-host). **Leaning to the Holybro X500** as its highest-value use (owner,
2026-09-17; not decided — wk-drones `aircraft/holybro-10` OQ-03). **Storage allocated:** a
spare WD_BLACK SN850 1 TB NVMe from the owner's parts box (owner, 2026-09-17). Per
[NVIDIA's carrier layout](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html)
the kit has an M.2 Key-M 2280 slot at PCIe 3.0 x4 and a Key-M 2230 slot at PCIe 3.0 x2; the
SN850 is a 2280 PCIe 4.0 drive, so it belongs in the 2280 slot and runs at Gen 3 speed.
This unit has no heatsink (owner, 2026-09-17). Stockist
survey, Super-mode and JetPack detail are in
[`common.md`](common.md#ai-compute--purchase-comparison). NVMe cold boot is verified (2026-09-18: the first boot after flashing was from power-off);
concurrent inference/storage load is not yet tested. Next: select target workloads for the Jetson;
decide whether MAXN_SUPER becomes the default after a sustained-load thermal check. No DP
cable or DP-to-HDMI adapter is in wk-inventory's stock list, so the desktop has not been
seen on a monitor.
No architecture change decided.

**The hexapod cannot take the AI HAT+ 2 — it goes to the Devastator (owner, 2026-09-18).**
From the hexapod's side ([wk-hexapod DEC-24](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/decisions.md)):
on 2026-09-18 its NVMe SSD was moved into a USB 3 enclosure to free the PCIe connector
for the HAT. The Pi booted from USB unchanged (root and boot mount by label), but the
enclosure's Realtek RTL9210B bridge hides TRIM, and forcing it hung the disk and the host
(negative result in [wk-hexapod `test-log.md`](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/test-log.md)).
The blocker is not PCIe but the header: the AI HAT+ 2 is powered through the GPIO header
and its socket cannot be stacked on, while the Freenove shield occupies the hexapod's
header on a riser of fixed height. The SSD is back on its PCIe base and the hexapod is
as it was. Detail in [`common.md` → AI HAT+ 2 and NVMe](common.md#ai-hat-2-and-nvme).
The Waveshare switch and the enclosure route are therefore moot for the hexapod; they
remain on the table for the Devastator, which has no header conflict but needs a Pi 5
first ([Devastator OQ-06, OQ-13](../projects/devastator/docs/open-questions.md)).

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

**The headline correction: the rail sag never existed** (OQ-03, closed 2026-09-18). It had been on
record since 2026-09-14, with a bulk-capacitance recommendation built on it. Logging all six
servos' voltage instead of `min()` showed **no moving servo ever below 11.4 V**, with the only low
samples isolated single frames on the two joints that were *not* moving. The figure was `min()`
across six servos catching corrupt frames — ~6000 chances a run — so it measured **the bus's error
rate, not the supply**, which is why 2 A, 3 A and 10 A all "sagged" alike. True rail under load is
11.9-12.1 V, and no capacitance is indicated.

That makes **OQ-18 — the bus corrupts 1.3-2.4% of telemetry reads, on every supply, and always
has** — the more serious thread: it does not merely trip guards, it **manufactured a finding that
survived four days and three supplies**. Mitigated in `shapes.py` (temperature plausibility filter;
the voltage guard now uses the median of six rather than the minimum), not diagnosed. It matters
before the Teensy reads telemetry at reflex-tier rates (OQ-09).

**Method note worth carrying to other projects: `min()` and `max()` are broken statistics on a bus
with a known error rate**, and this repo had extreme-value guards throughout.

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
