# wk-robotics — agent / contributor onboarding

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

- **The repository is the memory.** Anything durable — a decision, a measurement, a
  constraint, a lesson — lands in a file here. A fact that exists only in one assistant's
  private memory or chat history does not exist.
- **Per-harness memory holds pointers only.** It is legitimate for an assistant's own
  memory to record *"the printer facts are in `3d-printing/docs/`"* or a preference about
  how the user likes to be addressed. It is not legitimate for it to hold a project fact,
  a measurement, or a decision. If you find yourself about to save one, write it to a
  repo file instead and save the pointer.
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
  [`README.md`](README.md) · [`docs/projects.md`](docs/projects.md)
- **Commonality** — facts true of more than one project: the printer, the actuator
  family, the compute pattern, the conventions. [`docs/common.md`](docs/common.md)
- **Idea bench** — candidate projects that do not have a repo yet.
  [`docs/ideas.md`](docs/ideas.md)
- **Handover** — where things stand and what is in flight, so work can be picked up on
  another machine or in a new session. [`docs/status.md`](docs/status.md)

### The placement rule

**A fact lives in exactly one place.**

| The fact is… | It lives… |
|---|---|
| True of *one* project | In that project's repo, or its `projects/<name>/` folder here. Link to it from the index; never copy it |
| True of *several* projects | Here, in `docs/common.md`. The project repos link back |
| Not yet true of anything | In `docs/ideas.md`, labelled as unbuilt |
| In flight, spanning projects | In `docs/status.md`, until it resolves or finds a home |

When a fact stops being project-specific, move it here and replace it with a link. When an
idea earns a repo, move it out of `ideas.md` and into the index.

### What does not belong here

- **Operational detail of a single machine or robot** in the index or `docs/`. That is the
  project repo's, or project folder's, job.
- **Credentials, host names, network addresses, tailnet or LAN identifiers**, or anything
  else that is only in a private repo because it is private. **This repository is
  public.** Not every repo it indexes is — check before quoting. `3d-printing` is
  private: its calibration and material *findings* are fine to reference here, its access
  and infrastructure details are not.
- **Chat transcripts.** Distil the conclusion; discard the conversation.

---

## Working conventions

- **No project fact lives only in chat.** If a session establishes something durable, it
  lands in a repo before the session ends — this one, or the project's.
- **Distinguish decided from open.** Never state an open question as settled. Projects
  here keep the two in separate documents (`decisions.md` vs `open-questions.md`).
- **Verified beats plausible.** Measured numbers carry the date and the conditions they
  were measured under. An unverified figure is labelled as one.
- **Cross-link generously.** The value of this repo is its links; a reader landing on any
  document should be one hop from the authoritative source.
- **Docs are written AI-first** — dense, factual, cross-referenced, greppable, on the
  assumption an AI assistant is the primary reader.

## The projects and where they are

Full detail is in [`docs/projects.md`](docs/projects.md). Two projects are folders here;
the rest are sibling repos checked out alongside this one:

| Project | Path | Repo |
|---|---|---|
| koala-bot | `../koala-bot` | [WayneKennedy/koala-bot](https://github.com/WayneKennedy/koala-bot) — public |
| SO-ARM101 (build record) | [`projects/soarm101/`](projects/soarm101/AGENTS.md) | In this repo since 2026-09-13; `wk-soarm101` archived |
| SO-ARM101 (design) | `../SO-ARM100` | [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) — upstream clone, read-only |
| 3D printing | `../3d-printing` | [WayneKennedy/3d-printing](https://github.com/WayneKennedy/3d-printing) — private |
| Devastator | [`projects/devastator/`](projects/devastator/AGENTS.md) | In this repo since 2026-09-13; `wk-devastator` archived |
| wk-hexapod | `../wk-hexapod` | [WayneKennedy/wk-hexapod](https://github.com/WayneKennedy/wk-hexapod) — public |
| wk-drones | `../wk-drones` | [WayneKennedy/wk-drones](https://github.com/WayneKennedy/wk-drones) — public, the drone fleet; only its Holybro 10" is a robot |
| Freenove hexapod (vendor) | `../freenove-hexapod` | [Freenove/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi](https://github.com/Freenove/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi) — upstream, sparse clone, read-only; recipe in wk-hexapod `docs/operations.md` |

Read those repos and folders directly rather than re-deriving their state from this
index. Each carries its own `AGENTS.md` with what is specific to it; this page is the
family layer above them, and a project's file does not restate it.

## Sessions

This repository doubles as the home for AI sessions that span more than one project — a
design discussion touching both the arm and the printer, say, or an idea that does not
belong to any existing robot yet. Work that belongs to a single project is done in that
project's repo or `projects/` folder, against that project's own `AGENTS.md`.

**Leave the repository complete.** A session ends by writing what it established into a
file — the index, `docs/common.md`, `docs/ideas.md`, or `docs/status.md` for anything
still in flight. The next session may be a different assistant on a different machine with
no history at all; [`docs/status.md`](docs/status.md) is what it reads to carry on.
