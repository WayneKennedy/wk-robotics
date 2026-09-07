# Idea bench

Projects and directions that do not have a repository yet. This is the discussion home
for "what next" — a place to think in the open before committing scope.

**Nothing on this page is committed.** An item here is a candidate, not a plan. When one
earns a repo it moves out: into the index in [`README.md`](../README.md) and a section in
[`projects.md`](projects.md).

## How to use this page

Each candidate gets: what it is, why it is interesting, what it would reuse from the
[shared substrate](common.md), and what is unresolved about it. Keep the last one
honest — the interesting part of an unbuilt project is what you do not yet know.

---

## Carried over from project backlogs

These are recorded in a project repo as deferred, and are listed here because they are
plausible *separate* projects rather than features of an existing one.

### Climbing sibling to Koala

A second member of the koala-bot family: all-gripper limbs, no wheels. Hybrid actuation —
passive-latch hang at near-zero energy, ballistic brachiation (declutch to swing, re-engage
as a brake), and a central winch with tendons to haul the body up. The biomimetic
principle is *spend energy only on transitions — grip, pull, release — and coast the rest*.

- **Reuses:** the koala-bot shared brain and topic contract; the STS servo family; the printer.
- **Unresolved:** everything mechanical. Gripper design, clutch mechanism, and whether the
  winch is central or per-limb.
- **Source:** `koala-bot/docs/backlog.md`. Deferred under koala-bot's scope discipline —
  finish V1 end-to-end before the family.

### InMoov resurrection

An existing ~80 %-built InMoov — head, neck and shoulders, with an upstream-contributed
Pi-camera eye mod — to be brought up on a Pi 5 brain with modern Mega + PCA9685
electronics, on a powered-wheelchair base.

- **Reuses:** the Pi 5 intent tier; the power-integrity lessons, which came from this build
  in the first place.
- **Unresolved:** whether upstream inactivity since 2024 makes this a maintenance burden
  rather than a shortcut.
- **Currently:** shelved as inspiration. A good future testbed for parallel mechanisms, an
  AI brain, and electronics lessons at humanoid scale.

### SpotMicro · Annin Robotics AR4

Named as later personal builds in `koala-bot/docs/backlog.md`. Nothing decided.

---

## Open directions

Threads worth pulling that are not yet attached to a specific build.

### A shared ROS 2 package across robots

The [topic contract](common.md#the-topic-contract) is currently a convention held in
prose. It could be a package — message definitions, a URDF library, common launch
patterns — that every robot depends on rather than reimplements.

- **Argument for:** the hexapod's navigation stack is portable in principle today and not
  in practice; a shared package is what would close that gap.
- **Argument against:** two robots is a thin basis for an abstraction, and koala-bot's
  ROS 2 layer is not written yet. Premature.
- **Unresolved:** whether to wait for koala-bot's stack to exist before extracting anything.

### LeRobot and learned manipulation

The SO-ARM101 exists to work with LeRobot. Once the follower arm is built, the question is
what it is *for* — teleoperated data collection, a learned policy, or a testbed for
putting a learned component into one of the mobile robots.

- **Unresolved:** everything downstream of "build the arm". Worth revisiting once it moves.

---

## Adding an idea

Append a section under the right heading. If the idea is a deferred feature of an existing
robot, it belongs in that repo's `backlog.md` instead — only put it here if it is a
plausible project in its own right.
