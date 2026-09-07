# Status

**Where things stand, and what is in flight.** Read this after
[`AGENTS.md`](../AGENTS.md) when picking the work up on a new machine or in a new
session — it is the handover point that the per-project repos cannot provide, because
these items span more than one of them.

This is a *state* document, not a log. When an item resolves, delete it; when it belongs
to one project, move it to that project's repo and leave a link. It is not a transcript —
see [`AGENTS.md`](../AGENTS.md#what-does-not-belong-here).

**Last reviewed: 2026-09-07.**

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
git clone git@github.com:WayneKennedy/wk-devastator.git
git clone git@github.com:WayneKennedy/wk-hexapod.git
git clone git@github.com:WayneKennedy/fn-hexapod.git         # vendor reference
```

`wk-hexapod` and `fn-hexapod` are the two that are usually **not** checked out. Clone them
before doing hexapod work rather than reasoning from this repo's summary of them.

Nothing here depends on a particular AI assistant, editor or shell. The repository is the
state; a session that adds to it is expected to leave it complete.

---

## Open threads

### `fn-hexapod` cannot track upstream

**What was established (2026-09-07, from the GitHub API):** `WayneKennedy/fn-hexapod` is
not a GitHub fork (`fork: false`, no parent). It carries Freenove's commits — matching
messages and matching author timestamps — but under **different SHAs**, so its history was
rewritten rather than cloned intact. 74 commits against upstream's 123; 9 MB against
489 MB. The one commit authored locally is *"Remove Application binaries (mac/windows
clients)"*, and a 50× size drop means those binaries were stripped from **history**, not
deleted at the tip.

**Why it matters:** no shared SHAs means **no fast-forward from upstream**. Picking up new
Freenove work needs a cherry-pick or a fresh re-import, not a `git pull`.

**The live risk:** the snapshot is pinned at **2025-11-28**. Upstream
([`Freenove/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi`](https://github.com/Freenove/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi))
has moved on — 9 commits since, latest 2026-03-07, **including `Update control.py`**.
`wk-hexapod` names `control.py` as confirmed-working reference for gait and IK, so the
reference it is built against is stale.

**Unverified:** the 49 missing commits are *consistent with* a history filter dropping
commits that touched only the removed binaries. That cause has not been confirmed.

**Next step:** clone `wk-hexapod` and `fn-hexapod`, diff the upstream `control.py` against
the pinned copy, and **record this finding in those repos** — it is a single-project fact
sitting here only because neither repo was checked out when it was found.
[Placement rule](../AGENTS.md#the-placement-rule).

### Untracked terrain files on the workstation

`~/Code/FirstTerrain/` and `~/Code/Terrain_2019.zip` (237 MB) are under no version
control. They may belong to the same retired lineage as the archived terrain repos below.
Local disk only — no GitHub action outstanding. Decision needed: keep, archive offline, or
delete.

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
