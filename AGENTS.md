# wk-robotics — agent / contributor onboarding

> **The project record moved to Basic Memory on 2026-11-10** (project `main`, folder `robotics/`; start at the
> *Robotics* note). `README.md`, `docs/common.md`, `docs/projects.md`, `docs/status.md`, `docs/ideas.md` and
> `projects/mission-planner/AGENTS.md` are canonical there; the copies here were deleted on 2026-11-10 (git history keeps them); read them in Basic Memory, not from
> this checkout. This repo keeps what is about the code and artefacts: this file, `CLAUDE.md`, `GEMINI.md`,
> `scripts/`, `tools/`, `projects/orin-perception/`, and each project's firmware, software and CAD.

**Read this first.** It is the entry point for any AI assistant or human working in this
repository, and it is written to be complete on a first read with no prior context.

This file is **provider-neutral**. Every harness — Claude Code, Codex, Gemini, Cursor,
Copilot, or one that does not exist yet — reads this same file and gets the same
instructions. The per-harness files in the repo root (`CLAUDE.md`, `GEMINI.md`) do nothing
but point here.

---

## The 4Cs — the standard every artefact meets

Every artefact — docs, source, CAD, commit messages — must be:

1. **Correct** — fact-based. No speculation unless labelled as such. "Unknown" and
   "unverified" are valid answers; confident guesses are not.
2. **Complete** — nothing essential missing.
3. **Coherent** — everything fits together; no contradictions.
4. **Concise** — nothing superfluous.

All four hold at once: completeness never excuses bloat; brevity never excuses gaps; and
none of the other three count if the content is wrong.

## Harness independence

**A brand-new assistant, on a first read of this repository alone, must be able to do
useful work.** That is a hard requirement, not an aspiration. It has three consequences:

- **Basic Memory is the memory; the repositories hold code and artefacts** (split rule:
  [*Memory Map*](memory://main/memory-map)). Anything durable — a decision, a measurement, a constraint, a lesson — lands
  in a Basic Memory note, or in a repo file when it is about the code or an artefact. A
  fact that exists only in one assistant's private memory or chat history does not exist.
- **Per-harness memory holds pointers only.** It is legitimate for an assistant's own
  memory to record *"the printer facts are in Basic Memory, folder `3d-printing/`"* or a preference about
  how the user likes to be addressed. It is not legitimate for it to hold a project fact,
  a measurement, or a decision. If you find yourself about to save one, write it to a
  Basic Memory note (or the repo file it is about) instead and save the pointer.
- **Instructions live in `AGENTS.md`.** Harness-specific files carry only what is
  genuinely useless to other harnesses — a tool name, a slash command, a file-format
  quirk. If a note would help any assistant, it belongs here.

This rule holds across every project in the family, not just this repository.

---

## What this repository is

**The table of contents for a set of robotics and physical-AI projects, and the home for
what they have in common.** Most robots live in their own repository; two small ones,
the Devastator and the SO-ARM101 build, live here under `projects/`. This repository
exists because some things are true of several of them at once.

Three jobs, and nothing else:

- **Index** — what exists and what state it is in.
  [`README.md`](README.md) · [*Robotics Projects*](memory://main/robotics/robotics-projects)
- **Commonality** — facts true of more than one project: the printer, the actuator
  family, the compute pattern, the conventions. [*Robotics Common*](memory://main/robotics/robotics-common)
- **Idea bench** — candidate projects that do not have a repo yet.
  [*Robotics Ideas*](memory://main/robotics/robotics-ideas)
- **Handover** — where things stand and what is in flight, so work can be picked up on
  another machine or in a new session. [*Robotics Status*](memory://main/robotics/robotics-status)

### The placement rule

**A fact lives in exactly one place.**

| The fact is… | It lives… |
|---|---|
| True of *one* project | In that project's repo, or its `projects/<name>/` folder here. Link to it from the index; never copy it |
| True of *several* projects | Here, in [*Robotics Common*](memory://main/robotics/robotics-common). The project repos link back |
| Not yet true of anything | In [*Robotics Ideas*](memory://main/robotics/robotics-ideas), labelled as unbuilt |
| In flight, spanning projects | In [*Robotics Status*](memory://main/robotics/robotics-status), until it resolves or finds a home |
| An item owned but allocated to no project, or the list of unfinished projects (any hobby) | In Basic Memory, folder `inventory/` (private): [*Stock*](memory://main/inventory/stock), [*Project Register*](memory://main/inventory/project-register). Allocating an item moves its row into the project's BOM |

When a fact stops being project-specific, move it here and replace it with a link. When an
idea earns a repo, move it out of [*Robotics Ideas*](memory://main/robotics/robotics-ideas) and into the index.

### What does not belong here

- **Operational detail of a single machine or robot** in the index or the family notes.
  That belongs to the project's own notes and repo.
- **Credentials, host names, network addresses, tailnet or LAN identifiers**, or anything
  else that is only in a private repo because it is private. **This repository is
  public.** Not every repo it indexes is — check before quoting. `3d-printing` is
  private: its calibration and material *findings* are fine to reference here, its access
  and infrastructure details are not. **Machine identifiers go in Basic Memory, folder `inventory/`**
  (private; the `wk-inventory` repo it came from is frozen since 2026-11-07); public
  files describe a machine by role and link there. The same folder holds the owner's
  stock list and project register: link to them, never copy rows.
- **Chat transcripts.** Distil the conclusion; discard the conversation.

---

## Working conventions

- **Check what is owned before suggesting a purchase.** Read the private
  [*Stock*](memory://main/inventory/stock)
  and search the owner's invoices ([below](#invoices-and-order-history)), and say what was
  found. The full rule, and the owner's goal behind it — fewer unused parts, more finished
  projects — are in
  [*Inventory Guide*](memory://main/inventory/inventory-guide).
- **No project fact lives only in chat.** If a session establishes something durable, it
  lands in Basic Memory, or in the repo file it is about, before the session ends.
- **Distinguish decided from open.** Never state an open question as settled. Projects
  here keep the two in separate notes (*Decisions* vs *Open Questions*).
- **Verified beats plausible.** Measured numbers carry the date and the conditions they
  were measured under. An unverified figure is labelled as one.
- **Cross-link generously.** The value of this repo is its links; a reader landing on any
  document should be one hop from the authoritative source.
- **Docs are written AI-first** — dense, factual, cross-referenced, greppable, on the
  assumption an AI assistant is the primary reader.
- **FreeCAD is the design tool and the viewer** (owner, 2026-10-01). All design activity
  happens in FreeCAD, and a model is shown to the owner by opening it there. Do not build a
  web viewer, a published page or any other bespoke viewer for a design. How:
  [*Robotics Common*](memory://main/robotics/robotics-common).

## Invoices and order history

**What was bought, when, from whom and for how much is in the owner's mailbox**, and an
assistant can read it rather than ask. The owner's mail is hosted at Fastmail, which runs
an official MCP server at `https://api.fastmail.com/mcp`
([Fastmail's guide](https://www.fastmail.help/hc/en-us/articles/15869557281295-Connecting-AI-tools-via-Fastmail-s-MCP-server)).
Any MCP-capable harness can connect to it; access is granted by the owner through
Fastmail's OAuth consent screen, in three levels: read, make changes, send. Connected to
the owner's Claude account as a connector and verified for reading on 2026-09-17; other
harnesses are not connected. No credential, token or address belongs in any repo.

- **Use it for** supplier order confirmations and invoices: search by supplier or part
  name, then read the confirmation for line items, prices and dates. The wk-drones
  Holybro BOM was built this way.
- **An invoice proves a purchase, not a fit.** Which robot a part was bought for, and
  whether it is fitted, still comes from the owner or the hardware; record it as such.
- **Public repos take** part, supplier, order number, price and date. **They never take**
  postal addresses, phone numbers, email addresses or payment identifiers, all of which
  appear in order emails.
- **Limits:** the server has no tools for mail rules or filters; the owner changes those
  by hand. Write and send tools are untested here; do not send or modify mail unless the
  owner asks.
- Screen scraping a webmail client is not an acceptable substitute (owner, 2026-09-17).

## The projects and where they are

Full detail is in [*Robotics Projects*](memory://main/robotics/robotics-projects). Two projects are folders here;
the rest are sibling repos checked out alongside this one:

| Project | Path | Repo |
|---|---|---|
| koala-bot | `../koala-bot` | [WayneKennedy/koala-bot](https://github.com/WayneKennedy/koala-bot) — public |
| SO-ARM101 (build record) | [`projects/soarm101/`](projects/soarm101/AGENTS.md) | In this repo since 2026-09-13; `wk-soarm101` archived |
| SO-ARM101 (design) | `../SO-ARM100` | [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) — upstream clone, read-only |
| 3D printing | `../3d-printing` | [WayneKennedy/3d-printing](https://github.com/WayneKennedy/3d-printing) — private |
| Devastator | [`projects/devastator/`](projects/devastator/AGENTS.md) | In this repo since 2026-09-13; `wk-devastator` archived |
| mission-planner | [`projects/mission-planner/`](projects/mission-planner/AGENTS.md) | In this repo since 2026-09-21; not a robot — the tier above them |
| wk-hexapod | `../wk-hexapod` | [WayneKennedy/wk-hexapod](https://github.com/WayneKennedy/wk-hexapod) — public |
| wk-drones | `../wk-drones` | [WayneKennedy/wk-drones](https://github.com/WayneKennedy/wk-drones) — public, the aircraft fleet (drones and planes); only its Holybro 10" is a robot |
| Freenove hexapod (vendor) | `../freenove-hexapod` | [Freenove/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi](https://github.com/Freenove/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi) — upstream, sparse clone, read-only; recipe in [*Hexapod Operations*](memory://main/robotics/hexapod/hexapod-operations) |

Read those repos and folders directly rather than re-deriving their state from this
index. Each carries its own `AGENTS.md` with what is specific to it; this page is the
family layer above them, and a project's file does not restate it.

## Sessions

This repository doubles as the home for AI sessions that span more than one project — a
design discussion touching both the arm and the printer, say, or an idea that does not
belong to any existing robot yet. Work that belongs to a single project is done in that
project's repo or `projects/` folder, against that project's own `AGENTS.md`.

**Leave the repository complete.** A session ends by writing what it established into a
file — the index, [*Robotics Common*](memory://main/robotics/robotics-common), [*Robotics Ideas*](memory://main/robotics/robotics-ideas), or [*Robotics Status*](memory://main/robotics/robotics-status) for anything
still in flight. The next session may be a different assistant on a different machine with
no history at all; [*Robotics Status*](memory://main/robotics/robotics-status) is what it reads to carry on.
