# Status

**Where things stand, and what is in flight.** Read this after
[`AGENTS.md`](../AGENTS.md) when picking the work up on a new machine or in a new
session — it is the handover point that the per-project repos cannot provide, because
these items span more than one of them.

This is a *state* document, not a log. When an item resolves, delete it; when it belongs
to one project, move it to that project's repo and leave a link. It is not a transcript —
see [`AGENTS.md`](../AGENTS.md#what-does-not-belong-here).

**Last reviewed: 2026-09-13.**

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
git clone https://github.com/TheRobotStudio/SO-ARM100.git    # upstream, not a fork
git clone git@github.com:WayneKennedy/wk-soarm101.git
git clone git@github.com:WayneKennedy/wk-devastator.git
git clone git@github.com:WayneKennedy/wk-hexapod.git
git clone git@github.com:WayneKennedy/wk-drones.git
# Hexapod vendor reference: a sparse clone of Freenove's upstream — recipe in wk-hexapod docs/operations.md
```

`wk-hexapod` and its vendor reference are checked out on the robot's own Pi, where hexapod
work happens; on the workstation they usually are not. Clone them before doing hexapod
work rather than reasoning from this repo's summary of them.

Nothing here depends on a particular AI assistant, editor or shell. The repository is the
state; a session that adds to it is expected to leave it complete.

---

## Open threads

### AI compute purchase — AI HAT+ 2, Jetson or DGX Spark

**Ordered from The Pi Hut, owner-confirmed 2026-09-13:** Raspberry Pi AI HAT+ 2 and
[Waveshare 2-Channel PCIe Expander for Raspberry Pi 5](https://thepihut.com/products/2-channel-pcie-expander-for-raspberry-pi-5?variant=54400781156737),
retailer SKU **WAV-30490**, manufacturer model PCIe TO 2-CH PCIe HAT (two downstream FFC
connectors). Delivery and operation are not yet confirmed; AI HAT+ 2 compatibility remains
untested.

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
Spark is considered for ground use. **Jetson purchase remains pending:** owner is weighing
the 8 GB Orin Nano Super against the 16 GB Orin NX. Next: confirm the intended AI HAT/SSD
wiring and cable reach, then validate NVMe cold boot plus concurrent inference/storage
operation. Select target workloads to assess the Jetson memory need.
No architecture change decided.

### koala-bot on the GPU workstation has uncommitted work — 2026-09-13

Its checkout there had 31 modified files at the first check that day and 59 a few hours
later: work in progress on that machine, one commit behind origin. Not looked at; not
touched. Its links to `wk-devastator` and `wk-soarm101` were therefore **not** rewritten
to the new `projects/` paths; the archived repos keep those URLs alive until koala-bot is
next edited. Reconcile before koala-bot work on either machine. Resolves when that work
is committed and pushed.

Everything else on that machine was brought current the same day: `wk-robotics` and
`wk-drones` pulled (the latter renamed from its old directory name and remote), and the
`3d-printing` clone, which sat on a pre-redaction history with no common ancestor and
nothing local, was deleted and re-cloned. The hexapod's Pi was unreachable, so its
`wk-hexapod` checkout was not checked; pull there before hexapod work.

### Surplus drive hardware — home undecided

Two 37D motors and one Dual TB9051FTG arrived 2026-09-11 with no project to go to:
koala-bot's four-wheel V1 was cancelled before its follow-on order shipped. A Teensy 4.1 NE
arrived the same day, bought deliberately unallocated for whichever project is ready first.
The inventory
is in [`common.md`](common.md#drive-motors-drivers-and-mcus-in-hand); the candidate use is
[a pure balance bot](ideas.md#a-pure-balance-bot). Resolves when that idea earns a repo
or the parts are allocated elsewhere.

### SO-ARM101 is the reflex-tier proving ground

Decided 2026-09-12 (wk-soarm101 DEC-12): once the LeRobot loop has been run on the arm, its
servo bus moves to a Teensy 4.1 to develop the MCU-drives-the-bus pattern before koala-bot
and wk-devastator depend on it. Cross-project because what it proves feeds
[`common.md` → Compute](common.md#compute-the-two-tier-split) and the topic contract. Which
Teensy is open; the unallocated 4.1 NE in the pool is the candidate. Resolves when the
arm moves under an MCU and the lesson lands in `common.md`.

### Collision awareness — no robot here has it

Raised 2026-09-12: joint limits cannot prevent self-collision, and no stack in the family
models geometry at runtime. The layered picture and where each layer sits in the two-tier
split are in [`common.md` → Collision awareness](common.md#collision-awareness--open-family-wide).
Resolves when one robot carries a working joint envelope on its reflex tier and the lesson
is written back here.

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
