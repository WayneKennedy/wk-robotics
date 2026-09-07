# Banked Decisions

Committed decisions with rationale. Unresolved items live in
[`open-questions.md`](open-questions.md). Format: `DEC-nn — decision — why`.

**Provenance matters here.** This project is at the stage where most of the interesting
choices are *not yet made*. A decision appears below only if the owner made it, or if it
follows necessarily from one that was made. **Recommendations that have been offered but
not accepted are open questions, not decisions**, and are marked as such there.

---

- **DEC-01 — Resurrect the project; keep the mechanical chassis, replace everything
  above it.** (Owner, 2026-09-07.) The DFRobot Devastator is a high-quality aluminium
  platform that is already paid for and already assembled. The electronics, compute and
  software of the first build are all superseded. This is what makes the project a
  resurrection rather than a fresh start, and it bounds the work: no chassis design.

- **DEC-02 — Target ROS 2, with the reflex tier on a 32-bit MCU running micro-ROS.**
  (Owner, 2026-09-07.) The robot joins the family
  [topic contract](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#the-topic-contract)
  rather than carrying a private protocol. **Teensy 4.0 is the owner's named candidate**
  — see OQ-03, which is not a rejection of it but a support caveat worth closing early.

- **DEC-03 — The fitted Arduino Nano and L298N are retired.** Follows necessarily from
  DEC-02 and from the family's own sourcing rules: the Nano is an 8-bit AVR and
  [micro-ROS requires a 32-bit target](https://github.com/WayneKennedy/wk-robotics/blob/main/docs/common.md#micro-ros-how-the-mcu-joins-the-graph),
  and the L298N is the driver koala-bot explicitly rejected for its ~2 V drop. What
  replaces the driver is OQ-02.

- **DEC-04 — Three tiers, and each stays useful when the tier above it is unreachable.**
  Derived from DEC-02 and DEC-05. The coordinator is a desktop that will frequently be
  off or busy, so treating its absence as an outage would make the fleet useless most of
  the time. Reflex does not wait on intent; intent does not wait on coordination. See
  [`architecture.md`](architecture.md#the-load-bearing-rule).

- **DEC-05 — The family GPU workstation is the coordination-tier machine.** (Owner,
  2026-09-07.) It is the only GPU in the family and therefore the only candidate for a
  reasoning tier. Its constraints — Blackwell toolchain, NAT'd networking, desktop
  availability — are recorded in the family repo, and the third of them is the direct
  cause of DEC-04.

- **DEC-06 — Scope discipline: the drivetrain works before anything is mounted on top.**
  The owner's own account records the first build stalling on over-ambitious scope, with
  two depth cameras and a Pi mounted before the drive worked. Inverting that order is the
  single most evidence-backed choice available to this project. See
  [`roadmap.md`](roadmap.md).

- **DEC-07 — The power budget is computed before parts are bought.** The first build was
  [under-powered by design](concept.md#the-first-build-and-why-it-stopped), not abandoned
  for lack of interest. Power is therefore a design input for this build, and purchases
  follow the budget rather than producing it.

- **DEC-08 — Tri-licence**, matching the family standard: `CERN-OHL-S-2.0` hardware,
  `MIT` software, `CC-BY-SA-4.0` docs. See [`LICENSING.md`](../LICENSING.md). The
  purchased chassis is third-party and is not relicensed by this repo.

- **DEC-09 — The repository is the memory.** No project fact, measurement or decision
  lives only in a chat log or an assistant's private memory. This repo is public, so
  capabilities may be described but the machines providing them are never named.
