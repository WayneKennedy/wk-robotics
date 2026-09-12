# Status

**Where things stand, and what is in flight.** Read this after
[`AGENTS.md`](../AGENTS.md) when picking the work up on a new machine or in a new
session — it is the handover point that the per-project repos cannot provide, because
these items span more than one of them.

This is a *state* document, not a log. When an item resolves, delete it; when it belongs
to one project, move it to that project's repo and leave a link. It is not a transcript —
see [`AGENTS.md`](../AGENTS.md#what-does-not-belong-here).

**Last reviewed: 2026-09-12.**

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
git clone git@github.com:WayneKennedy/wk-drone-bee35.git
git clone git@github.com:WayneKennedy/fn-hexapod.git         # vendor reference
```

`wk-hexapod` and `fn-hexapod` are checked out on the robot's own Pi, where hexapod work
happens; on the workstation they usually are not. Clone them before doing hexapod work
rather than reasoning from this repo's summary of them.

Nothing here depends on a particular AI assistant, editor or shell. The repository is the
state; a session that adds to it is expected to leave it complete.

---

## Open threads

### `fn-hexapod` cannot track upstream — **resolved, moved**

Diffed 2026-09-09 on the robot: upstream's only change since the 2025-11-28 snapshot is
`np.mat` → `np.asmatrix` in `control.py` (numpy 2 compatibility); every other
`Code/Server` file is byte-identical, and `wk-hexapod`'s controller does not use `np.mat`.
Nothing to port. The provenance facts (rewritten history, no shared SHAs, `master` branch)
and the re-import question now live in
[`wk-hexapod/docs/open-questions.md`](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/open-questions.md)
(OQ-10) and `docs/references.md` there.

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

### Untracked terrain files on the workstation

`~/Code/FirstTerrain/` and `~/Code/Terrain_2019.zip` (237 MB) are under no version
control. They may belong to the same retired lineage as the archived terrain repos below.
Local disk only — no GitHub action outstanding. Decision needed: keep, archive offline, or
delete.

### Moved to a project home

**SO-ARM101 servo commissioning** (2026-09-09) — held here for one day while the build had
no repo of its own. Now in
[wk-soarm101 `docs/servos.md`](https://github.com/WayneKennedy/wk-soarm101/blob/main/docs/servos.md).

### Deferred, already recorded elsewhere

Ideas and candidate projects are in [`ideas.md`](ideas.md); per-project backlogs live in
each project's own repo. Nothing is duplicated here.

---

## The GitHub estate

Current as of 2026-09-07, after a tidy-up on that date. Robotics repos and their state are
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

**Branch naming:** `main` everywhere, and `init.defaultBranch = main` is set globally on
the workstation. One exception remains — **`fn-hexapod` is still on `master`**, which is
undecided rather than deliberate.
