# The shared substrate

Facts true of more than one project. Anything true of only one belongs in that
project's repo — see the placement rule in [`AGENTS.md`](../AGENTS.md#the-placement-rule).

Sources are project repos, hardware measurements and linked manufacturer documentation,
dated where the date matters. Untested options and unresolved compatibility are labelled.

---

## Printing

**One machine, one set of profiles.** Every printable part on every project comes off a
stock Creality Ender-5 S1 running Klipper — build volume **220 × 220 × 280 mm**, textured
PEI on spring steel. Setup, calibration and the full print log live in the private
[`3d-printing`](https://github.com/WayneKennedy/3d-printing) repo; the findings that
affect design decisions are here.

### Materials in use

| Material | Nozzle / bed | Used for | Notes |
|---|---|---|---|
| **PETG** | 240 / 80 °C | Standing default; koala-bot parts | Baked into `START_PRINT`, so a bare `START_PRINT` is always safe |
| **PLA+** (eSUN) | 220 / 60 °C | SO-ARM101 parts | Validated 2026-09-06. Runs fine on the 80 °C-probed bed mesh — no separate profile needed |

Slicer profiles are versioned in `3d-printing/reference/` (`ender5s1_petg.ini`,
`ender5s1_plaplus.ini`, and per-project variants). A new project gets a profile there,
not a private copy.

### Design constraints this imposes

- **Every part fits within the bed.** koala-bot's stricter rule — *every part ≤ 200 × 200 mm* —
  is the one to design to; it leaves margin and keeps parts printable on the wider class
  of 200 mm machines the project targets.
- **Slicer time estimates are trustworthy.** Across eight completed jobs the estimate has
  landed within ±2 % of actual. Plan around it.

### Press-fits and supports

Two findings from the SO-ARM101 build (2026-09-06/07) that generalise to any project with
servo pockets:

- **Support residue, not dimensional error, is the usual cause of a failed press-fit.** An
  STS3215 would not seat in a supports-everywhere `Motor_holder_Base`. The
  support-free `Gauge_0` from the same design gave the intended tight friction fit on the
  same machine and material — so the machine was dimensionally correct and the support
  material was welded into the pocket. **Print the gauge before blaming the calibration.**
- **Check the overhang fraction before enabling supports.** All four parts on SO-ARM101
  plate 1 measure under 2 % overhang area and printed clean with supports off — screw holes
  open and unobstructed, no scarring. Supports-by-default cost a part and six hours.

### Adhesion

Small, poorly-anchored features are the first thing to release; large footprints hold.
When a print fails at feature scale rather than globally, the cause is the **surface**, not
the Z-offset — squishing the whole first layer to save a few small features degrades every
dimension on the plate. The definitive case: an identical model and G-code that failed at
layer 1 on the bare magnetic base printed intact on textured PEI with nothing else changed.

### Environment

The printer is in a garage with a clear corrugated PVC roof — it behaves as a greenhouse,
not a cold store: hot in daytime sun, cold overnight, ambient swinging widely. Two
consequences for anyone reading a calibration number or planning a long print:

- **A calibration figure is only meaningful with the ambient it was taken at.**
- **A long print will cross a hot/cold cycle.** Measured headroom (2026-09-06, ~25 °C
  ambient, enclosure fitted): bed holds 80 °C at 34 % duty, hotend 240 °C at 48 %.

The enclosure is left **open** by default. Enclosures suit ABS/ASA; PLA and PETG — which is
all this machine prints — do worse in a warm chamber, which drives heat creep in a
direct-drive hotend and blunts the part cooling PLA depends on.

---

## Actuators

**One servo family across two robots.** Feetech STS-protocol bus servos drive both the
SO-ARM101 and koala-bot's limbs. That is a real shared dependency, not a coincidence of
sourcing: it means one serial bus topology, one protocol, one set of press-fit
tolerances, one pool of spares, and tooling that transfers between projects.

| Servo | Rating | Bus | Used by |
|---|---|---|---|
| **STS3215** | 12 V, ~30 kg·cm, positional feedback | STS serial bus | SO-ARM101 (all joints) · koala-bot (hip roll + pitch, shoulder pitch + roll, elbow) |
| **STS3032M** | 6 V, 4.5 kg·cm, positional feedback | STS serial bus (separate 6 V bus). **Fixed single lead, no pass-through port** — chains through the 3-port connector boards and link cable supplied in the 4-pack | koala-bot (3-RPS neck) |

**Servo holdings, 2026-09-12 — every V1 servo the family has planned is now in hand:**

| Servo | Qty | Where | Source |
|---|---|---|---|
| Waveshare ST3215 12 V (Feetech STS3215 rebadge), firmware 3.10 (upgraded from 3.9, 2026-09-12) | 2 | SO-ARM101, IDs 1–2 | Amazon 204-4694570-7173960, ordered 2026-09-02, delivered 2026-09-04, £31.90 each ([`servos.md`](../projects/soarm101/docs/servos.md)) |
| Feetech STS3215 12 V, firmware 3.10 | 4 | SO-ARM101, IDs 3–6 (wk-soarm101 DEC-09) | RCmall via koala-bot, arrived 2026-09-12 ([koala-bot `sourcing.md`](https://github.com/WayneKennedy/koala-bot/blob/main/docs/sourcing.md)) |
| Feetech STS3215 12 V, firmware 3.10 (four read; the eight assumed the same batch, unverified) | 8 | koala-bot, eight of twelve limb joints — four short until a **6-pack ordered from RCmall 2026-09-14** arrives (then 14: 12 fitted, 2 spare) | same order; backfill pack (AliExpress, £103.15) shipped 2026-09-15, not delivered as of 2026-09-17 |
| Feetech STS3032M 6 V | 4 | koala-bot, three neck + one spare | same order |

SO-ARM101 has its six. koala-bot must re-order at least four STS3215 before its limbs can
all be fitted (koala-bot OQ-16).

koala-bot's **knee is not a servo joint**: it is a wheel on a 12 V geared DC motor, and
the V1 leg ends there. A knee servo is designed for and deferred
(`koala-bot/docs/concept.md`, DEC-17), so it is not in the count of ten V1 limb joints.

The hexapod is the exception — 20 hobby servos on a **PCA9685** I²C PWM driver, inherited
from the Freenove kit. No feedback, no bus addressing. It works because a statically
stable walker can tolerate open-loop position control in a way a balancing robot cannot.

**STS3215 electrical, per servo** (vendor figures, checked 2026-09-07):

| Idle | No-load | **Stall** | Operating range | No-load speed |
|---|---|---|---|---|
| 30 mA | 200 mA | **2.7 A** | **6–14 V** | 0.22 s/60° @ 12 V |

Sizing is the count times the stall figure, because the fuse and the wiring have to
survive the fault case rather than the average: **six** on an SO-ARM101 is ~5–8 A in
realistic motion and **16.2 A** all-stalled; koala-bot's **ten** limb servos are 27 A.

**A 3S LiPo is the ceiling for STS3215.** A full 3S is 12.6 V, inside both the servo's
12 V rating and its 14 V absolute range; 4S at 16.8 V exceeds the range and destroys them.
This constrains the power architecture of any project using them.

**Torque and speed track the rail.** Both scale roughly with voltage, so a servo fed 9 V
delivers about three-quarters of its rated 30 kg·cm. A pack sagging toward its floor
therefore reads as a weakening arm, not as a tuning problem — worth knowing before chasing
the wrong fault.

### Drive motors, drivers and MCUs in hand

Two projects use 12 V geared DC motors with encoders rather than servos, and both drive
them with the same board — the **Pololu Dual TB9051FTG** (2.6 A continuous / 5 A peak per
channel, 4.5–28 V; chosen by koala-bot DEC-16, adopted by wk-devastator DEC-13). The
family holds more of both than any project needs. Allocated units are tabulated here;
**unallocated units — two surplus 37D motors, a spare driver and a Teensy 4.1 NE — are in
the owner's private stock list, [wk-inventory `docs/stock.md`](https://github.com/WayneKennedy/wk-inventory/blob/main/docs/stock.md)** (moved there 2026-09-17). A project that takes
one moves it into its own BOM and this table.

**Allocated, 2026-09-17:**

| Part | Qty | Where |
|---|---|---|
| 37D 12 V 122 rpm 38 kg·cm geared motor + encoder (Pi Hut; koala-bot's CAD models it as DFRobot FIT0403) | 2 | koala-bot, rear ankle drives (DEC-43) |
| Pololu Dual TB9051FTG | 1 | koala-bot (DEC-16) |
| same | 1 | wk-devastator — its own since 2026-09-11 (DEC-13, amended). It was koala-bot's board on loan from 2026-09-07; the loan is dissolved, not returned |
| Teensy 4.0 | 1 | **Bench logger, from 2026-09-18** — left koala-bot when its DEC-18 was amended to a 4.1 NE. Upstream micro-ROS lists the 4.0 "Not tested", so it is off every load-bearing path; the logger uses bare Teensyduino and no micro-ROS, and the 4.0's header kit suits a breadboard instrument ([`ideas.md`](ideas.md#a-correlated-bench-logger)) |
| Teensy 4.1 NE | 1 | **koala-bot (DEC-18 as amended, 2026-09-18) — to buy.** A third NE: one is in hand, one is on order for wk-devastator |
| Teensy 4.1, no-Ethernet variant | 1 | wk-devastator (DEC-10) — **ordered, not shipped**: RobotShop holds it with the back-ordered motors ([devastator `sourcing.md`](../projects/devastator/docs/sourcing.md)) |

wk-devastator's driver came on the same Pi Hut order (#1619429, 2026-09-10) as the
unallocated units.

### Configuring a servo — true for every STS project

The bus is a **single-wire half-duplex TTL UART**, 3-pin (V+, GND, signal), 1 Mbaud by
default. A generic USB-TTL cable has separate TX and RX and no direction switching, so it
will not drive these servos without a tri-state buffer — a purpose-made bus adapter is
required, not optional.

**Driving the bus from an MCU — open (2026-09-14).** The STS3215 has no PWM input: an MCU
drives the same half-duplex bus the USB adapters do, through one of two front ends. **(a)** The
**Waveshare Bus Servo Adapter (A) with its jumpers on channel A**, the MCU's UART on the board's
header: the board does the direction switching and keeps the 12 V power path, and moving the
jumpers back to B returns the bus to a PC. **(b)** The **MCU's own UART in single-wire
half-duplex mode** (Teensyduino offers one — to verify on a Teensy 4.x) through a
level-shifting buffer, with the chain powered straight from the supply. **Teensy 4.x pins are
3.3 V and not 5 V tolerant**, and neither the bus's idle signal level nor the Waveshare header's
logic level is recorded here — meter both before a Teensy is wired to either. Either way the bus
takes one master at a time: with the MCU on it, the PC tools cannot reach the servos. SO-ARM101
is the first to do this (its OQ-09); koala-bot's plan of one Teensy UART per voltage segment
(its DEC-22) faces the same choice.

**EEPROM writes need the servo's `Lock` register at 0 (proven on SO-ARM101, 2026-09-14).**
An STS3215 EEPROM register — ID, baud, homing offset, position limits — written while
`Lock` = 1 reads back correctly and is **lost at power-off**. LeRobot 0.6.1's
`enable_torque()` sets `Lock` = 1 and `disable_torque()` sets 0, so anything written while a
robot is holding under LeRobot is silently temporary. Write `Lock` = 0, write, read back,
restore `Lock` = 1; verify across a power cycle. Evidence:
[SO-ARM101 `test-log.md`](../projects/soarm101/docs/test-log.md) (OQ-12).

**Zero every servo when its ID is set, and assemble each joint at mid-travel (owner,
2026-09-14).** A factory STS3215 can sit anywhere on its encoder when it is bolted in, and the
servo can only be commanded within 0–4095 without crossing the wrap. On SO-ARM101 the elbow's
fold stop landed 21 counts from the wrap (the likely root of a −259° read), and the wrist roll's
travel ran 10–19° past it, so part of the roll's travel was uncommandable and a hand-turned roll
could be driven into its stop — fixed only by re-homing after assembly (an EEPROM write, with
its own pitfalls: see OQ-12 and the goal-adoption rule above). The practice: when the ID is set,
also centre the servo (command 2047, or write the homing offset so it reads 2047), then fit the
horn with the joint at the middle of its mechanical travel — so every joint's stops sit well
inside 0–4095 from day one. Evidence: [SO-ARM101 `test-log.md`](../projects/soarm101/docs/test-log.md).

**A joint's measured stop midpoint is a starting point, not its zero (SO-ARM101,
2026-09-14).** Upstream URDFs that put zero at mid-travel invite taking the midpoint of the
mechanical stops as the zero. On SO-ARM101 two of four joints were 2–5° off it — including the
elbow, whose travel matched the URDF's span exactly (equal span says the travel is the right
length, not that it is centred). What settled all four in minutes: hold the arm at the model's
zero pose, read each link with a phone spirit level (correcting for the desk's own tilt), and
cross-check against one tape-measured tool position. Method and numbers:
[SO-ARM101 `test-log.md`](../projects/soarm101/docs/test-log.md).

**Adapters in hand (2026-09-08):** a **Waveshare Bus Servo Adapter (A) v1.1** — the
"Motor Control Board" in the SO-ARM100 BOM, so it is the SO-ARM101 part — and a
**Feetech FE-URT-2**. Both came on Amazon 204-4524452-2059566, ordered and delivered
2026-09-07: a "Waveshare Serial Bus Servo Driver Board" (£9.99, taken to be the Adapter (A))
and a Stemedu listing for an **FE-URT-1** (£15.65). The board delivered is silkscreened
**FE-URT-2** (owner, 2026-09-17), so the listing named the wrong model
([SO-ARM101 `sourcing.md`](../projects/soarm101/docs/sourcing.md)). Those two are the family's only adapters: the RCmall STS3215 6-packs
were listed with an **FE-URT-1** each but shipped **without** (koala-bot `test-log.md`,
2026-09-12), and the STS3032M 4-pack ships passive 3-port connector boards and a link cable, not a
USB adapter. Both bring-ups therefore share the two boards. A further equivalent, if ever needed: the *Serial
Bus Servo Driver Board* (~€5, the part in the Open Duck Mini V2 BOM).

| Adapter | USB | Servo power in | Servo ports | Notes |
|---|---|---|---|---|
| Waveshare Bus Servo Adapter (A) | USB-C, **CH343** (`1a86:55d3`, verified 2026-09-09; `cdc_acm` → `/dev/ttyACM0`) | 5.5 × 2.1 mm barrel **or** screw terminals, 9–12.6 V / 5–8.4 V (pass-through, below) | 2 × 3-pin, either is the bus | **Both jumpers on channel B** for USB control (LeRobot docs) |
| Feetech FE-URT-2 | USB-C, **CH343** (vendor listing) | Two screw-terminal inputs: **DC 4.8–12 V for TTL** servos, **DC 12–24 V for RS485** servos | TTL bus header plus 2 × XH4 RS485 — check the silkscreen before plugging a 3-pin STS lead | 3.3 V / 5 V logic-level switch; also serves the SMS (RS485) family, which nothing here uses |

A CH343 enumerates under the kernel's `cdc_acm` driver as `/dev/ttyACM*`; the FTDI note
below does not apply to it. **On Windows** the same chip binds to the generic CDC serial
driver by default and gets a COM port; WCH's **VCP driver (CH343SER)** is a separate manual
install (Waveshare's wiki note, read 2026-09-12). Feetech's FD software found the servos on
2026-09-12 with the VCP driver installed **and its baud set to 1 000 000** — the 2026-09-09
"port but no servo" was the baud (FD defaults to 115200); whether the CDC driver would also
have worked at 1 Mbaud is untested. The chip's flow-control setting is irrelevant to the
servo bus, which uses no flow-control lines. Either board needs the user in the **`dialout`** group (or a
udev rule) before the port is writable without `sudo`. The Waveshare board **does not echo
transmitted bytes** back on RX (verified 2026-09-09) — a bus scanner need not strip them.

**Verified against a Waveshare ST3215 (2026-09-09):** factory state is **ID 1, 1 Mbaud**,
model number **777**; LeRobot 0.6.1's `FeetechMotorsBus.setup_motor()` and
`broadcast_ping()` work through the Waveshare board unmodified. `Present_Voltage` reads
the rail in 0.1 V units and is the quickest proof that a servo is actually powered.

**Every STS3215 on a bus must run the same firmware, and that firmware is 3.10 (verified
2026-09-12, SO-ARM101, six servos).** Units ship with **3.9** (the 2026-09-07 Waveshare pair
did) or **3.10** (the RCmall Feetech packs). Mixed, they collide: in a `sync_read` the servos
answer in the order asked, and a 3.10 unit starts its reply too early when the unit before it
is a 3.9 unit that was not the first responder — its header lands on the previous checksum
byte, the host sees `Incorrect status packet`, and `broadcast_ping()` loses IDs.
`Return_Delay_Time` does not help; ID placement can route around it but is fragile. **The
fix is the upgrade**, and it worked first time: Feetech **FD 1.9.8.3** on Windows (LeRobot's
[documented path](https://huggingface.co/docs/lerobot/main/feetech)), servo on the Waveshare
board, *Upgrade → Online → Upgrade*, one servo selected at a time, on a supply that will not
drop mid-write. Two pitfalls: Windows binds the board's CH343 to a generic CDC driver — install
WCH's **CH343SER** VCP driver — and FD defaults to **115200 baud; set 1 000 000** before
*Search* or it lists nothing. After the upgrade every read order passed 30/30 and broadcast
ping was complete. So: read `Firmware_Major_Version` / `Firmware_Minor_Version` at
commissioning, record it, and upgrade any 3.9 unit before it joins a bus. Full record:
[wk-soarm101 `test-log.md`](../projects/soarm101/docs/test-log.md)
2026-09-12, DEC-11.

**Three STS3215 behaviours that bit on 2026-09-12 (SO-ARM101, LeRobot 0.6.1):** writing
`Goal_Position` **turns torque on** regardless of `Torque_Enable`; servos **keep their last
goal across power and sessions**, and LeRobot's `connect()` re-enables torque without
resetting it, so joints lurch toward stale goals — write `Goal_Position := Present_Position`
before torque comes on; and LeRobot's `max_relative_target` clamps to *present ± step*, so
it follows a moving joint rather than holding it — not a safety net. Record and evidence:
[wk-soarm101 `servos.md`](../projects/soarm101/docs/servos.md)
and its `test-log.md`. These apply to every STS bus in the family.

**Home and travel limits are a separate, later step, and they live in the servo.** Setup
writes ID and baud only. LeRobot's `calibrate()` (after assembly) writes **`Homing_Offset`**
so the joint's mid-range reads 2047, then records the range you sweep by hand and writes
**`Min_Position_Limit` / `Max_Position_Limit`** — all three to servo EEPROM (LeRobot 0.6.1
`write_calibration`, read 2026-09-09), so the servo itself clamps any goal past them. The
limits are only as good as the sweep: stop just short of the hard stops. For a soft first
test, upstream's `SO-ARM100/Software/WEBUI_CALIBRATION.md` caps `Torque_Limit` (reg 48) at
30 %.

**The Waveshare Bus Servo Adapter (A) is a pass-through, confirmed 2026-09-07** — owner
read the Waveshare documentation (*"the input voltage must match the servo voltage"*,
stated twice) and confirmed against the board, which carries none of the inductor or bulk
electrolytics a switching converter would need. Its two input bands are the two pack
sizes, not a choice of supply: **9–12.6 V is the 3S window** for 12 V servos, **5–8.4 V
the 2S window** for 7.4 V ones. Consequences:

- **Feeding 9 V does not get you 12 V.** There is no boost. The servos see the pack.
- **The board supplies no regulation, bulk capacitance or protection of its own** — the
  bulk capacitance and fuse under [Power integrity](#power-integrity) are external to it,
  and are not optional.
- **Use the screw terminals, not the barrel jack**, for anything past bench testing: a
  5.5 × 2.1 mm jack is typically good for only ~3–5 A, in series with the whole bus.

Three constraints that apply on every project using these servos:

- **The adapter does not power the servo, and USB alone cannot.** Neither board routes
  USB 5 V onto the servo V+, and 5 V is below the STS3215's 6–14 V range anyway — the
  servo will not even answer a ping. The servo rail is fed separately, even for ID setup.
  LeRobot's setup writes ID and baud rate only and does not move the servo; Open Duck's
  script also drives it to zero so the horn can be fitted aligned, so needs working current.
- **Match the rail to the part.** STS3215 is 12 V, **STS3032M is 6 V**, and the adapter
  passes through whatever it is given. Same bus, same protocol, different rail.
- **One servo at a time, unplugged between each.** Every unit ships as **ID 1**, so IDs
  cannot be assigned on a shared bus.

**Scripted, not GUI.** Feetech's FD / SCServo Debug tool works, but leaves no record. The
one-time write is small enough to script and log: unlock EEPROM, mode 0, zero the
acceleration limits, write the PID coefficients, `change_id`. Open Duck Mini V2's
`scripts/configure_motor.py` (`pypot.feetech.FeetechSTS3215IO`) is a working reference;
LeRobot's SO-ARM setup command does the same job against the same SO-101 follower spec.

**Telemetry from a moving STS3215 is unreliable, and it is the servo, not the bus** (measured on
SO-ARM101, 2026-09-18; applies to every STS project). `Present_Position` comes from a magnetic
encoder; **temperature, voltage and current are measured by an ADC inside the servo**, and that ADC
is disturbed by the servo's own motor drive. Measured over every logged run: **0 impossible
position values in 82,260 readings, against 1.58 % implausible temperatures in 20,586** — same
bus, same `sync_read`, same checksum, same instants. By drive state: **0.00 % with torque off,
0.25 % holding still, 1.3–6 % moving.**

- **The frames are valid; the values are not.** LeRobot verifies the checksum, so nothing is
  detectable at the protocol layer — a corrupt reading looks exactly like a real one.
- **Nothing external fixes it.** Not baud rate, not `Return_Delay_Time`, not wiring, not bulk
  capacitance. It is internal to the servo.
- **Never guard on a single ADC sample.** Take a median across the servos on the rail (a real
  event moves all of them, a bad reading moves one), or reject physically impossible jumps — a
  servo cannot gain 40 °C in 50 ms. A two-sample debounce is **not** enough: at these rates two bad
  readings in a row is near-certain over a long run, and that has already caused a false
  over-temperature trip with every servo at 37 °C.
- **`min()` and `max()` select for the errors.** An extreme-value guard over six servos and a
  thousand samples has ~6000 chances a run to find a bad frame. On SO-ARM101 that manufactured a
  phantom "10.5 V rail sag" that survived four days and three supplies before it was caught.
- **Position is trustworthy**, so control loops and tracking guards built on it are sound. A
  reflex tier reading raw ADC telemetry at 200–1000 Hz would trip constantly; filter it there.

**The FTDI latency trap.** If a bus adapter presents as an FTDI device, its default
**16 ms latency timer** caps every bus round-trip — harmless during one-time ID setup,
fatal for a fast control loop later. The fix is a udev rule:

```
SUBSYSTEM=="usb-serial", DRIVER=="ftdi_sio", ATTR{latency_timer}="1"
```

(Sourced from the Open Duck Mini V2 runtime's Pi setup, which ships exactly this rule.
Neither adapter in hand is FTDI — both are CH343 — so this applies only to a future board;
check on first plug-in.)

---

## Compute: the two-tier split

The pattern koala-bot's architecture sets out, and the one any future balancing or
dynamic project should follow:

| Tier | Hardware | Band | Role | Status |
|---|---|---|---|---|
| **Reflex** | Real-time MCU (Teensy 4.0 leading; ESP32 / RP2040 candidates) | ~200–1000 Hz, deterministic | Motor and servo output, IMU read, balance loop, encoders, safety | **Decided** |
| **Intent** | On-robot Raspberry Pi 5 + ROS 2 | ~1–50 Hz, not real-time | Perception, SLAM, behaviour, LLM personality, networking | **Decided** |
| **Mission Planning** | Off-robot central machine | seconds | Shared world model, reasoning, fleet-level tasking | **Aspirational** — see [ideas.md](ideas.md#physical-ai-and-the-hive-mind) |

**The tiers are defined by one axis: control band.** Each is a loop that runs slower than
the one below it and hands the one below setpoints, and **each must stay useful when the
tier above it is unreachable** — the balance loop survives losing the Pi, the robot
survives losing the planner. Only the first two tiers are built or committed; the third is
recorded so the two below are designed with it in mind, not because it is planned.

**The load-bearing rule: the balance loop lives on the MCU, never on the Pi.** Linux is not
real-time and ROS 2 over USB adds jitter that destabilises an inverted pendulum. IMU → PID →
output closes on the MCU; the Pi sends setpoints and reads telemetry.

**The second rule: the reflex tier must recover from a telemetry fault, not latch on one**
(owner, 2026-09-18). A bench tool with a human watching may stop and hold; the reflex tier is the
layer that has to keep a robot safe when nobody is watching, so **losing a telemetry channel must
not mean losing the robot.** This is not hypothetical — the STS3215's ADC channels corrupt at
~1.58 % while driving ([above](#configuring-a-servo--true-for-every-sts-project)), and that rate
scales brutally with loop frequency:

| Loop rate | A bad ADC reading every | Two in a row every | Three in a row every |
|---|---|---|---|
| 20 Hz (today's host tools) | 3.2 s | 200 s | 3.5 h |
| 200 Hz | 0.3 s | 20 s | 21 min |
| 1000 Hz | 0.06 s | **4 s** | 4 min |

**Debouncing alone cannot work at reflex rates at any practical depth** — the two-sample debounce
that is adequate at 20 Hz would false-trip every four seconds at 1 kHz.

**Where the numbers apply.** The table is measured on **STS3215 servos**, which only **SO-ARM101**
and **koala-bot** (its limbs) use. **wk-devastator** has a reflex tier but no servos — two DC
motors on a driver, so its telemetry is encoders and driver current sense, whose error rates are
**unmeasured**; the rule applies to it, the figures do not. **wk-hexapod** drives hobby PWM servos
straight from its Pi and has no reflex tier, so neither applies. What a reflex tier needs, whatever
its telemetry:

- **Rank the sources by trustworthiness.** Position is encoder-derived and has never yet produced
  a bad value, so a tracking fault is authoritative and may act immediately. Every analogue
  channel — current, temperature, voltage — must be **confirmed before it is believed**: a median
  across the servos on the rail, a physical-plausibility bound, or a sustained trend.
- **Distinguish noise from signal rather than filtering both.** A genuine over-temperature rises
  and persists; a corrupt reading is isolated and returns to the trend. Filtering hard enough to
  hide the first is worse than the false trip it prevents.
- **Degrade rather than halt.** If a channel becomes unusable, fall back — a thermal estimate from
  duty cycle, a reduced envelope, a lower speed limit — and **report the degradation upward**, so
  the intent tier knows it is flying on reduced instruments.
- **Keep a latching path for real faults**, and make its threshold explicit. Recovery must not
  become a robot that ignores a genuine jam.

**Unresolved and deliberately not guessed at here:** the confirmation counts, the recovery
conditions, what escalates to the intent tier versus what the reflex tier handles alone, and
whether a fault should ever require a human to clear it. SO-ARM101 is the first project to face
this, under its OQ-09.

**What is *not* a tier: a smart sensor.** A camera that computes depth or runs a detector
on-board closes no control loop, takes no setpoints and offers no graceful degradation —
if it dies, the intent tier is blind wherever the depth was computed. It is a peripheral
of the intent tier, and where its work runs is a separate axis, covered under
[Perception placement](#perception-placement) below.

### Aircraft and the tiers

A flight controller is the reflex tier: it stabilises, holds position and recovers on its
own, at the reflex band, and it does so under a human pilot or under a computer alike.
**An aircraft is a family robot when an intent tier commands that flight controller.**
Where the intent tier runs is a second axis, and it decides what intent can be asked to do:

| Topology | Intent tier runs | Link to the flight controller | Latency | What intent can do | Instance |
|---|---|---|---|---|---|
| **Onboard** | Companion computer on the airframe | Wired serial / USB | ms | Reactive: obstacle response, visual servoing, local replanning | Holybro 10" ([wk-drones](https://github.com/WayneKennedy/wk-drones)) — see [projects.md](projects.md#holybro-10-wk-drones) |
| **Off-board** | A ground machine | Radio: ELRS MAVLink mode or a telemetry radio | 100s of ms to s | Tasking only: waypoints, modes, return-to-hold. The aircraft must self-stabilise and self-recover | Unbuilt — [ideas.md](ideas.md#roving-eyes-a-whoop-fleet) |

Off-board intent is the intent tier running at the mission-planning tier's latency: the
planner talks to the flight controller directly and the airframe carries no intent
hardware. **A human on the sticks is neither topology**, so an FPV aircraft is not a
robot however capable its flight controller, and an airframe can cross the line with no
physical change the day a ground machine holds the sticks instead. Both topologies need
two-way MAVLink from the flight controller, which means ArduPilot rather than iNav
([Bee35 DEC-06](https://github.com/WayneKennedy/wk-drones/blob/main/aircraft/bee35/docs/decisions.md)).
The rule applied to each aircraft in the fleet is
[wk-drones F-DEC-01](https://github.com/WayneKennedy/wk-drones/blob/main/fleet/decisions.md).
Decided 2026-09-13 (owner).

### ROS 2 installs are familial

**Owner's rule, 2026-09-19:** every ROS 2 host in the family is installed the same way,
as closely as the hardware allows; the **hexapod's `scripts/ubuntu-setup.sh`** is the
reference, and a deviation is either brought into line or recorded as a decision in that
host's project. What "the same way" means today, from that script:

| Item | Reference (hexapod) |
|---|---|
| OS | Ubuntu 24.04 (Server on robots), ROS 2 **Jazzy** from apt, nothing from source |
| apt source | the `ros2-apt-source_<latest>.noble_all.deb` from `ros-infrastructure/ros-apt-source`, not a hand-written keyring and list |
| Base packages | `ros-jazzy-ros-base ros-dev-tools python3-colcon-common-extensions python3-rosdep python3-vcstool`, with `--no-install-recommends`; robot-specific packages on top |
| Middleware | Fast DDS (`ros-jazzy-rmw-fastrtps-cpp` installed explicitly), `ROS_DOMAIN_ID=0` |
| rosdep | `rosdep init` once, `rosdep update` as the user; `rosdep install --from-paths src` before `colcon build` |
| Workspace | the project's `ros2_ws/` inside its repository or folder, built with `colcon build --symlink-install`; sourced as `/opt/ros/jazzy/setup.bash` then `install/setup.bash` |
| Not done | no ROS in `.bashrc` by default; launch scripts source what they need |

**Audit, open:** at the end of the current bring-up the three ROS 2 hosts — the hexapod,
the AI HAT+ 2 bench host and the Orin — are compared against this table and every
deviation is made deliberate and documented ([`status.md`](status.md)). Known deviations
on the bench host as installed 2026-09-19: base packages installed *with* recommends;
workspace at `~/ros2_ws` rather than inside the project folder (the package lives in
`projects/devastator/software/ros2/`, synced there); Fast DDS and domain 0 by Jazzy's
defaults rather than set explicitly. The Orin runs JetPack's Ubuntu 24.04 and may need
arm64 packages that differ; its session records what.

### micro-ROS: how the MCU joins the graph

ROS 2 is a Linux system — its transport is DDS, which assumes an OS, a network stack and
megabytes of RAM. **An MCU cannot run ROS 2.** micro-ROS is the ROS 2 client library for
microcontrollers: it replaces DDS with **DDS-XRCE** (*eXtremely Resource Constrained
Environments*), and the MCU speaks XRCE over serial to a **micro-ROS Agent** process on
the Linux host, which bridges it into the real DDS graph.

The MCU then *is* a ROS 2 node — it appears in `ros2 topic list`, RViz plots it, Nav2
drives it. The boundary between the tiers becomes the topic contract rather than a bespoke
serial protocol that has to be maintained, and re-diverges, per robot. The agent is a
container:

```bash
docker run -it --rm -v /dev:/dev --privileged --net=host \
  microros/micro-ros-agent:rolling serial --dev /dev/ttyACM0 -v6
```

**It requires a 32-bit target.** An 8-bit AVR (Arduino Uno/Nano) cannot run micro-ROS at
all — a constraint that decides MCU choice, not just MCU preference.

**Board support, from `micro-ROS/micro_ros_arduino` (checked 2026-09-07):** ESP32,
Teensy 3.2/3.6, **Teensy 4.1** and Arduino Portenta H7 are listed **Supported**;
**Teensy 4.0 is listed "Not tested"**, as is Teensy 3.5. RP2040 appears only as a
community-contributed entry. This matters because **koala-bot has already bought a Teensy
4.0** (DEC-18). The 4.0 and 4.1 share the same i.MX RT1062 core and the same Teensyduino
support, so it is *expected* to work — but that expectation is **unverified**, and proving
it on the bench is worth doing before the firmware is written rather than after.

**The family standardises on the Teensy 4.1 NE for every reflex tier** (owner, 2026-09-18).
The **4.0 is not used on a load-bearing path** — it is "Not tested" upstream, therefore in no
one's CI, so a release can break it silently; that is a standing risk rather than something a
bench test retires, and the two-tier rule needs the reflex tier boring and reliable. One board
across koala-bot, wk-devastator and SO-ARM101 also buys one toolchain and one set of quirks.

**Teensy 4.1 "NE" (no Ethernet) is the right variant for this family, and every unit bought
is NE** (2026-09-17). The standard 4.1 carries a DP83825 PHY on the board, but the RJ45
magjack is a separate purchase, so "with Ethernet" means board *plus* magjack *plus* cable;
the NE omits the PHY, which is soldered and not a retrofit
([PJRC](https://www.pjrc.com/store/teensy41.html)). The reason to skip it is architectural,
not the parts cost: **micro-ROS needs an agent host whatever the transport** — Ethernet does
not let an MCU speak ROS 2 natively, it only moves where the agent may sit. Under the
[two-tier split](#compute-the-two-tier-split) the reflex MCU always shares a robot with an
intent-tier Pi 5, a ~10 cm hop carrying setpoints at 10–100 Hz, and the rule that the reflex
loop survives losing the Pi means that link is not load-bearing. USB serial covers it, and it
is the transport the agent command above already uses. Two supporting points: the Arduino
native-Ethernet UDP transport arrived as a community contribution and carries a visible trail
of open issues, where serial is the well-trodden path; and on a mobile robot a cable is a
liability — the wireless answer is WiFi, which the Teensy has not got and the Pi has. The one
case that would change this is a **stationary wired node with no co-located host**, which no
project here plans, and where an ESP32 or Pi Zero would likely beat a Teensy anyway.

**Raspberry Pi 5 (8 GB) is the standard intent-tier host** — hexapod brain, koala-bot
cerebrum, and the printer's Klipper host. One board to know, one image to maintain.

### Perception placement

**Orthogonal to the tiers: where each stage of the perception pipeline runs.** Every
stage — image signal processing, stereo depth, detection and classification, feature
tracking, SLAM — can run in one of four places, and the choice is made per stage, not per
robot:

| Place | Examples | Costs the Pi |
|---|---|---|
| **In the sensor** | RealSense D4xx stereo ASIC; Sony IMX500 in the Raspberry Pi AI Camera; RealSense D555 Vision SoC V5 | Nothing but the bus |
| **Host accelerator** | Raspberry Pi AI HAT+ / AI HAT+ 2 (Hailo) on the Pi 5 PCIe connector | Competes with NVMe for the connector; sharing requires a [PCIe switch](#ai-hat-2-and-nvme) |
| **Pi CPU** | depth-to-laserscan, `slam_toolbox`, RTAB-Map, Nav2 — everything the hexapod runs today | The whole cost |
| **Off-robot** | GPU workstation | Ruled out for raw streams — see below |

**Why it matters here.** The hive-mind direction fixes one end: *share a world model, not
sensor streams* ([ideas.md](ideas.md#physical-ai-and-the-hive-mind)), so perception must
stay on the robot. The intent host is a Pi 5 on every project, so the Pi 5 is the
perception bottleneck, and moving stages into the sensor or an accelerator is the only
lever that does not change the host. The hexapod ran the D435i with all SLAM on the Pi,
and could not keep its loop rates (wk-hexapod OQ-02); the tank's camera is undecided
(`wk-devastator` OQ-09), and koala-bot's CSI camera-eyes are where an in-sensor module
would go.

**What justifies a depth camera (owner, 2026-09-18).** A D4xx earns its cost over a
standard camera by one thing: depth computed in the camera. Without a host that can use
that depth fully, a standard camera does the job for a fraction of the price. So the
family's one **D435i is banked as a pair with the Jetson Orin Nano**, whose GPU can use it
fully, and it left the hexapod ([wk-hexapod DEC-25]({HX})). **Where the pair goes is open**
(the Holybro 10" is a candidate; its at-risk cost is the objection) — see
[`status.md`](status.md).

**What the current products actually do on-device (checked 2026-09-09):**

- **RealSense D4xx (the family's D435i):** stereo disparity matching on the on-board
  ASIC; the host receives finished depth frames over USB 3. **No SLAM on-device** — the
  hexapod's `slam_toolbox` and RTAB-Map run on the Pi.
- **RealSense T265** was the only member that ran visual-inertial SLAM on-device and
  emitted pose. **Discontinued.** No current RealSense does on-device SLAM. librealsense
  removed its code at v2.54.1; the last validated release for it is v2.50.0
  ([release notes](https://github.com/IntelRealSense/librealsense/wiki/Release-Notes)), so
  using one means pinning a 2022-era driver. The family owns one, unused.
- **RealSense D555 PoE:** D450 optical module, IMU, and the new *Vision SoC V5* —
  disparity, motion estimation, a vision DSP and an ISP on-device; depth to 1280 × 720 at
  60 fps. Power and data over one Ethernet cable, and it **streams to ROS 2 directly
  over Ethernet with no host driver**. The biggest on-device offload in the family, and
  it takes the USB 3 bandwidth question off the table. Sources:
  [product page](https://www.realsenseai.com/products/d555-poe/),
  [datasheet v1.1](https://realsenseai.com/wp-content/uploads/2025/08/D555-Datasheet-v1.1.pdf).
- **Raspberry Pi AI Camera (Sony IMX500):** runs one int8 model, up to ~8 MB and a
  640 × 640 input tensor, on the sensor and returns output tensors and regions of interest
  as metadata alongside each frame. **Detection and classification only** — no depth, no
  SLAM. Source:
  [Raspberry Pi documentation](https://www.raspberrypi.com/documentation/accessories/ai-camera.html).
- **Raspberry Pi AI HAT+ (Hailo):** a host accelerator, not a sensor — the model runs
  on the HAT, the frames still cross to the Pi. PCIe/NVMe compatibility, including
  AI HAT+ 2, is recorded [below](#ai-hat-2-and-nvme).

**Rule of thumb:** put a stage in the sensor when the sensor's output is what the next
stage consumes anyway (depth for laserscan, detections for behaviour), and leave a stage
on the Pi when it needs the whole robot's state (SLAM, Nav2). The accelerator row has
its first result ([AI HAT+ 2 measurements](#first-measurements-on-the-ai-hat-2)); no
in-sensor stage has been tested.

**A three-way split, raised by the owner 2026-09-19, not decided or tested:** detection in
the sensor (an IMX500 AI Camera running one small model and emitting detections as
metadata), generative behaviour on the HAT (the Hailo-10H's 8 GB is for LLM/VLM work,
and a resident LLM would contend with detection for the same chip), SLAM and Nav2 on the
Pi CPU. Each stage on the part built for it. Caveats: no AI Camera is owned; it is a CSI
camera, so it brings the `libcamera`/`rpicam` stack that is awkward on Ubuntu and needs
Raspberry Pi's IMX500 support, unverified on 24.04; its one model is small (lower accuracy
than YOLOv8m on the HAT) and it cannot produce face embeddings; and the frames still cross
to the Pi if video is wanted.

### Depth: which kind, for which task

**Owner's observation, 2026-09-19:** depth keeps turning out to be the key component,
and depth cameras are expensive. The way out is that "depth" is three different needs,
and only one of them wants a depth *camera*. Prices are UK retail as remembered or seen
in passing, **unverified**; check before buying, and check stock first.

| Need | What actually serves it | Owned | Cheap route (unverified prices) |
|---|---|---|---|
| **Mapping and navigation** (hexapod, tank): a metric range scan for SLAM and Nav2 costmaps | A 2D lidar gives a 360° laserscan directly, which is what Nav2 consumes; the hexapod's depth camera only ever made a fake laserscan from one 10-pixel band | Nothing | LD19 / LDS-type lidar ~£80–100; RPLidar A1 ~£100. Arguably better value for this task than any depth camera |
| **Liveness / "is this surface flat?"** (door camera): coarse depth over a face-sized patch at 0.5–2 m | A few dozen range zones are enough; resolution is not the point | Dozens of HC-SR04 (one zone, no) | ST VL53L5CX / VL53L8CX 8×8-zone ToF module ~£15–25; or stereo from two cheap UVC cameras with OpenCV SGBM on the CPU, unsynchronised but fine for a still face |
| **Manipulation and scene depth** (the toy task, obstacle shape): dense metric depth, in-sensor | The D4xx class | **One D435i**, banked with the Orin | Arducam ToF (CSI, ~£40–50, 0.15–4 m, low resolution); Luxonis OAK-D Lite ~£100–150; the D435i itself is ~£430 ex VAT new |
| **Relative depth from one camera** (which is nearer, rough layout) | Monocular depth networks; the Hailo Model Zoo has them and `hailo-apps` ships a C++ example, so the HAT can produce it from the webcam | HAT + webcam | Free. **Not metric, and no use for liveness** — a photo of a face gets a face-shaped depth estimate |

Also owned and relevant: the SO-ARM101's pair of InnoMaker UVC cameras (allocated to the
arm) would do for a stereo experiment on the bench; the Pi 5's two CSI ports take two
Pi camera modules for a cheap stereo head. The RealSense T265 is pose-only and obsolete.

**Reading:** the two tasks that keep coming up, mapping and liveness, are the two that
do *not* need a depth camera. Spend the one D435i where dense depth is irreplaceable.

### AI HAT+ 2 and NVMe

**Documentation checked 2026-09-13; no hardware test.** Pi 5 exposes one PCIe lane on
one 16-pin FFC connector. Both official AI HATs use it; neither provides an NVMe socket
or downstream PCIe connector. An ordinary NVMe HAT and AI HAT+ 2 therefore cannot both
connect directly. GPIO stacking does not provide another PCIe connection; a passive
Y cable cannot replace an active PCIe switch. Sources:
[Pi connector description](https://www.raspberrypi.com/news/m-2-hat-on-sale-now-for-12/),
[AI HAT hardware and assembly](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html).

**Installed adapter identified by owner, 2026-09-13:**
[Pimoroni NVMe Base](https://thepihut.com/products/nvme-base-for-raspberry-pi-5-nvme-base)
(single-drive model). It mounts beneath the Pi and leaves its GPIO header free;
[Pimoroni's assembly guide](https://learn.pimoroni.com/article/getting-started-with-nvme-base)
explicitly accommodates a HAT above. This helps mechanical placement but does not remove
the PCIe conflict. Exact SSD models, cases and configured link speeds remain unknown.

**Base-specific cable constraint:** Pimoroni uses a 16-contact Pi end and an 18-contact
Base end, so a generic 16-to-16 ribbon is not a replacement. Its
[cable range](https://shop.pimoroni.com/products/pcie-flex-cable-for-nvme-base-and-raspberry-pi-5)
includes the stock 35 mm Pipe and a longer 50 mm Pipe. A switch-to-Base connection would
need the appropriate Pimoroni cable, with downstream socket orientation, reach and power
provision checked against the assembled stack. No cable/stack combination is validated.

**Candidate for retaining an existing NVMe HAT:**
[Waveshare PCIe TO 2-CH PCIe HAT](https://www.waveshare.com/product/modules/others/pcie-to-2-ch-pcie-hat.htm)
(SKU 30490) provides two downstream FFC connectors:

```text
Pi 5 PCIe → active switch ┬→ existing NVMe HAT → SSD
                         └→ AI HAT+ 2
```

- **Compatibility remains unverified for AI HAT+ 2.** The
  [vendor FAQ](https://www.waveshare.com/wiki/PCIe_TO_2-CH_PCIe_HAT) confirms Hailo-8,
  not Hailo-10H. The topology is a candidate, not a validated purchase combination.
- **Gen 2 x1 only, shared bandwidth.** The upstream link has a 500 MB/s ceiling per
  direction after line encoding, before PCIe transaction overhead. Both devices contend
  for it during simultaneous transfers; bandwidth is not permanently divided in half.
  Any current Gen 3 SSD setup would drop to Gen 2 with this switch. Pi 5's optional
  [Gen 3 mode is not certified](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#pcie-gen-3-0).
- **Before adopting:** establish exact SSD models, GPIO and power requirements,
  cable routing and heatsink clearance; verify cold boot from NVMe and concurrent SSD
  I/O plus Hailo inference on the intended OS/firmware. None has been tested here.

**The HAT needs the GPIO header, not just the ribbon (established 2026-09-18).** Raspberry
Pi's [PCIe connector standard](https://pip.raspberrypi.com/documents/RP-008298-DS-pcie-connector-standard.pdf)
rates the ribbon's 5 V pins at 500 mA each, 1 A total, and its detect pin makes the
bootloader probe PCIe without an ID EEPROM — so the original AI HAT+ (Hailo-8L, about
1.5 W) is reported to run on the ribbon alone
([forum](https://forums.raspberrypi.com/viewtopic.php?t=379842), no staff confirmation).
The AI HAT+ 2 does not fit that budget: a third-party review
([faceofit](https://www.faceofit.com/raspberry-pi-ai-hat-2-compatibility/), not Raspberry
Pi) gives 1.2 W idle, 3.5–4.5 W vision, 8 W peak on LLM loads and states it draws through
the header. No schematic or pin list for the HAT+ 2 is published, so which header pins it
uses beyond 5 V, ground and the ID EEPROM is unknown. Its socket carries pins that do not
protrude, so nothing stacks above it as supplied. **Consequence: any host whose header is
occupied cannot take it** — the hexapod's Freenove shield sits on the header on a
fixed-height riser, so the HAT is allocated to the Devastator
([status.md](status.md#ai-compute-purchase--ai-hat-2-jetson-or-dgx-spark)).

**Other routes:** a compatible USB 3 NVMe enclosure frees PCIe for the AI HAT+ 2, but
replaces the installed storage connection and consumes USB capacity
([Pi storage documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)).
**Tried on the hexapod, 2026-09-18, and abandoned:** a Realtek RTL9210B enclosure booted
Ubuntu 24.04 first time on UAS at 5 Gbps, but the bridge clears LBPME so the kernel
disables discard, and forcing `provisioning_mode=unmap` then `fstrim` hung the disk and
the host until power-cycled; the filesystems survived. Do not force unmap on that bridge
([wk-hexapod `test-log.md`](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/test-log.md)).
A dual-M.2 switch board with an M.2 accelerator can keep PCIe SSD storage while replacing
the existing HAT. [Seeed documents SSD + Hailo-8 operation](https://wiki.seeedstudio.com/raspberry_pi_5_uses_pcie_hat_dual_hat/);
that does not establish AI HAT+ 2 compatibility. The latter is a complete HAT, not an
M.2 module. Its Hailo-10H and 8 GB RAM add LLM/VLM support absent from Hailo-8;
[Raspberry Pi rates its vision performance as comparable to the 26-TOPS AI HAT+](https://www.raspberrypi.com/products/ai-hat-plus-2/).

#### Operating system for the HAT's Pi 5

**Checked 2026-09-18 against vendor and community pages; no hardware test here.** The
Hailo-10H needs the **HailoRT 5.x** stack (5.1–5.3 seen); the Hailo-8 era 4.x stack does
not drive it.

- **Raspberry Pi OS 64-bit, trixie, is the supported path** per
  [Raspberry Pi's AI documentation](https://www.raspberrypi.com/documentation/computers/ai.html):
  one meta-package, `hailo-h10-all` (runtime, PCIe kernel module, firmware, Python
  bindings, TAPPAS GStreamer plugins); PCIe Gen 3 is applied automatically for this HAT;
  `hailo-all` (AI Kit / AI HAT+) is incompatible and cannot co-exist with it; the
  bootloader must be current (`rpi-eeprom-update -a`). A **bookworm** install is not the
  supported base — third-party guides on bookworm exist, but the official page names
  trixie. **No Pi 5 board-revision restriction is stated**; rev 1.0 and 1.1 differ in
  16 GB addressing and NUMA tweaks, not in the PCIe connector
  ([revision codes](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/revision-codes.adoc),
  [forum](https://forums.raspberrypi.com/viewtopic.php?t=376730)). But **ROS 2 Jazzy has
  no binary packages for Debian**, so the family's intent-tier stack would be a source
  build or a container — the route the hexapod abandoned (its DEC-07).
- **Ubuntu 24.04 works and is the unsupported path:** Hailo publishes arm64 `.deb`s for
  HailoRT and the PCIe driver (DKMS, built against the running kernel) on its Developer
  Zone (login required); community reports on Pi 5 + Ubuntu 24.04 have `/dev/hailo0` and
  inference working, and at least one Hailo-10H LLM guide runs on Ubuntu Server 24.04.
  What does not come across: Raspberry Pi's `hailo-h10-all` packaging, `rpicam-apps` and
  the TAPPAS-based examples (reported not to build on Ubuntu without source changes).
  Sources: [Canonical's guide (Hailo-8L)](https://ubuntu.com/blog/hackers-guide-to-the-raspberry-pi-ai-kit-on-ubuntu),
  [Hailo community, Ubuntu 24.04 driver install](https://community.hailo.ai/t/hailort-driver-installation-issues-raspberry-pi-5-ubuntu-desktop-24-04-01-lts/12002),
  [Hailo-10H on Ubuntu Server 24.04](https://pudding-entertainment.medium.com/running-local-llms-on-raspberry-pi-5-and-hailo-ai-hat-2-b999fa240319),
  [Hailo-10H on Raspberry Pi OS](https://coreconduit.com/techlounge/guides/raspberry-pi/hailo-10h-setup.html).

- **A third option: Raspberry Pi OS host, ROS 2 Jazzy in a container.** The Hailo device
  is a host kernel driver exposing `/dev/hailo0`; a container sees it with
  `--device /dev/hailo0` and the HailoRT 5.x userland installed inside, **matching the
  host driver's version**. An Ubuntu 24.04 base image gets ROS 2 Jazzy from apt as usual.
  Both halves then sit on supported ground: Hailo on Raspberry Pi's packaging, ROS 2 on
  Ubuntu's. Costs: a USB serial reflex link and USB cameras pass through trivially, but
  the CSI camera stack (`libcamera`/`rpicam`) inside a container is awkward — a point for
  a USB or depth camera on any robot built this way (wk-devastator OQ-09); and the
  container must be rebuilt as a routine, with its Dockerfile in the robot's repo — the
  hexapod's container was built once and never rebuilt, which is why it went native
  (wk-hexapod DEC-07), an operational failure rather than a technical one. HailoRT inside
  a container on Raspberry Pi OS is **not verified here**; Hailo documents container use
  for its own tooling.

**Settled by test, 2026-09-19: Ubuntu 24.04 native works, with no Developer Zone
login.** Raspberry Pi's public apt archive carries the Hailo-10H packages, and two of
them install straight onto Ubuntu Server 24.04.5 arm64 from
`https://archive.raspberrypi.com/debian/pool/main/h/`:

- `h10-hailort-pcie-driver_5.1.1_all.deb` — DKMS source **plus the Hailo-10H firmware**
  (`/lib/firmware/hailo/hailo10h/`); needs `linux-headers-raspi`, `dkms`,
  `build-essential` first. Built cleanly against kernel `6.8.0-1064-raspi` as
  `hailo1x_pci` (the module name; `hailo_pci` is the Hailo-8 driver).
- `h10-hailort_5.1.1_arm64.deb` — the runtime and `hailortcli`; its dependencies are all
  in Ubuntu 24.04.

Result on the bench host: firmware 5.1.1 loaded in 2.7 s, `/dev/hailo0` present,
`hailortcli fw-control identify` → `Device Architecture: HAILO10H`, firmware
`5.1.1 (release,app)`. **Not installable on Ubuntu 24.04:** `python3-h10-hailort` (wants
Python 3.13) and `hailo-tappas-core` (trixie's OpenCV and Python); the Python API needs
Hailo's wheel for Python 3.12 from the Developer Zone, untested. So the ROS 2 host is
Ubuntu, native, and the container option above is not needed. Keep the two `.deb`s: a
kernel update rebuilds the module through DKMS, and a HailoRT update must move the driver
and runtime together.

#### First measurements on the AI HAT+ 2 (2026-09-19)

`hailortcli benchmark`, batch size 1, random input, 15 s per run, on the bench Pi 5 under
Ubuntu 24.04 with HailoRT 5.1.1; precompiled Hailo-10H models from the public Model Zoo
v5.4.0 (`https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/ModelZoo/Compiled/v5.4.0/hailo10h/<model>.hef`).
The PCIe link was already Gen 3 ×1 (`lspci`: `Speed 8GT/s, Width x1`) with no
`pciex1_gen` line in `config.txt`. Chip temperature 50–55 °C during the runs, Pi 48 °C;
power measurement is not supported through this driver.

| Model (640×640, COCO) | Measured FPS | Model Zoo FPS | Zoo mAP |
|---|---|---|---|
| YOLOv8n | 221–229 | 375 | 36.4 |
| YOLOv8s | 166.5 | 166 | 44.1 |
| YOLOv8m | 76.3 | 76.2 | 49.2 |

**Reading:** the two larger models hit the Zoo's figures exactly, so the chip is
delivering its rated compute; the smallest falls ~40 % short, so at that size the
Pi 5 side — one PCIe lane and the CPU's transfer and post-processing — is the limit,
not the accelerator. For a robot camera at 15–30 fps any of the three is far more than
enough, and YOLOv8m at 76 fps is the useful ceiling: the accuracy step from s to m is
free at robot frame rates. These are synthetic-input numbers; a live camera pipeline
adds capture, resize and post-processing on the CPU, unmeasured.

### AI compute — purchase comparison

**Researched 2026-09-13; none tested here.** Purchase state is tracked in
[status.md](status.md#ai-compute-purchase--ai-hat-2-jetson-or-dgx-spark).
Owner-quoted prices: **£192** for the HAT and **about £1,000** for the **Seeed
reComputer Super J401 NX Bundle with Orin NX 16 GB**
([SKU 100029661](https://www.seeedstudio.com/reComputer-Super-J401-NX-Bundle-p-6686.html)).
The **NVIDIA Jetson Orin Nano Super Developer Kit, 8 GB is £384 inc VAT**, verified on the
live RS listing — see *Buying the Nano developer kit in the UK* below.
The NX bundle includes a **256 GB NVMe SSD and Wi-Fi/Bluetooth module**. Do not substitute
the older J4012 Classic, which Seeed labels as not supporting Super mode. VAT, delivery
and the exact seller's remaining bundle contents are not independently checked.
At these prices NX costs about £616 more than Nano (~2.6x). The Nano/HAT £192 difference is
before the HAT's NVMe workaround and Jetson storage/accessories. The existing Pi is
already owned. NVIDIA's standard Nano kit
[includes a 19 V supply but requires storage](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/quick_start.html).

**A module swap is not a cheap route to 16 GB (checked 2026-09-15).** The Orin NX 16 GB
module alone lists at
[£995.99 inc VAT at Scan UK](https://www.scan.co.uk/products/nvidia-jetson-orin-nx-module-16gb-lpddr5-cortex-a78ae-1024-cuda-cores-157-ai-tops-1gbe-nvme-ampere)
(module only, 1–3 weeks), about the price of the whole Seeed bundle. Nano kit now plus an
NX module later is ~£1,380, more than the NX bundle outright; a later NX purchase adds a
second unit rather than upgrading the first. Whether the Nano developer-kit carrier
accepts an NX module, and in which power modes, is unverified here; RS's listing describes
the kit's carrier as accommodating all Orin Nano and Orin NX modules, but that is
distributor copy, not NVIDIA documentation.

**Buying the Nano developer kit in the UK (checked 2026-09-16; one ordered from RS on 2026-09-17, see [status](status.md#ai-compute-purchase--ai-hat-2-jetson-or-dgx-spark)).** The
suffix is a region/plug variant, not a hardware revision: **945-13766-0005-000 is the
EU/UK part**, -0000-000 is US/CA/CN/JP/PH, -0007-000 is IN/TW. All are the same Super
developer kit, and Super mode is software, so an older kit is the same hardware.
[RS UK 264-7384](https://uk.rs-online.com/web/p/processor-development-tools/2647384) is the
main UK route (OKdo is RS's own brand): **£320.00 ex VAT, £384.00 inc VAT**, and the
listing's manufacturer part number is 945-13766-0005-000 — both owner-checked on the live
page 2026-09-16. Cached search
snippets showing £215.84–£233.84 ex VAT were stale — distributors block automated fetches,
so their prices here are only trustworthy when a person has looked. Stock state at RS not
captured. Other stockists, unverified live:
[Scan](https://www.scan.co.uk/shop/computer-hardware/workstations-ai/nvidia-jetson-modules)
lists it as notify-me; The Pi Hut and Digi-Key UK do not list it; Farnell UK lists the
US-region -0000-000; [Silicon Highway](https://www.siliconhighwaydirect.com/product-p/945-13766-0005-000.htm)
ships from Ireland at €348 ex VAT on DAP terms, so UK import charges fall on the buyer;
Amazon UK carries only third-party kits. Broker listings (Enrgtech, Halltronics) are best
avoided. The kit still needs an NVMe SSD, and mains-lead provision varies by seller.

**Super mode** is a set of higher power modes (up to MAXN SUPER) from JetPack 6.2,
enabled by flashing with the Super configuration: software only, and the Nano developer
kit gets it by reflashing. Production carriers must handle the extra power and heat, which
is why Seeed marks its Classic J4012 (NX 16 GB) as not supporting it. Orin Nano 8 GB: GPU
625→1,020 MHz, CPU 1.5→1.7 GHz, **memory bandwidth 68→102 GB/s**, dense INT8 20→33 TOPS,
up to 25 W. Orin NX 16 GB: GPU 918→1,173 MHz, dense INT8 50→78 TOPS, up to 40 W;
bandwidth 102 GB/s either way. The Nano figures in the table below assume Super mode.
Source: [NVIDIA, JetPack 6.2 Super mode](https://developer.nvidia.com/blog/nvidia-jetpack-6-2-brings-super-mode-to-nvidia-jetson-orin-nano-and-jetson-orin-nx-modules/).

**JetPack for Orin (checked 2026-09-15; 7.2.1 flashed 2026-09-18, see [below](#the-jetson-orin-nano)).** Two maintained branches:

- **JetPack 7.2** ([2026-06-02](https://developer.nvidia.com/embedded/jetpack/downloads/archive-7.2);
  [7.2.1 on 2026-08-11](https://developer.nvidia.com/embedded/jetpack/downloads)) is the
  first 7.x release to support Orin. Ubuntu 24.04, kernel 6.8, CUDA 13.2.1, TensorRT 10.16.2.
  It matches the family's ROS 2 Jazzy on Ubuntu 24.04 (wk-hexapod DEC-07).
  [Isaac ROS 4.x](https://nvidia-isaac-ros.github.io/getting_started/index.html) supports
  Jazzy only, lists only JetPack 7.2 for Jetson, and offers Docker, venv or bare-metal installs.
  The Orin Nano developer kit now installs from a USB ISO, not an SD image, and needs UEFI
  firmware ≥ 36.0. Early reports in NVIDIA's
  [Orin Nano 7.2 thread](https://forums.developer.nvidia.com/t/jetpack-7-2-jetson-linux-r39-2-on-jetson-orin-nano-developer-kit-getting-started-and-feedback-thread/372151)
  (June 2026) cover firmware-update timeouts and MAXN SUPER missing after upgrade when a
  non-Super configuration was installed. DLA needs 7.2.1; see *DLA is conditional value* below.
- **JetPack 6.2.x**
  ([6.2.3, 2026-08-12](https://forums.developer.nvidia.com/t/jetpack-6-2-3-jetson-linux-36-5-2-is-now-live/379872))
  is Ubuntu 22.04 and kernel 5.15. NVIDIA's [FAQ](https://developer.nvidia.com/embedded/faq)
  calls it "sustaining mode"; no end-of-life date found. Ubuntu 22.04 is ROS 2 Humble's
  platform, not Jazzy's.

**Carrier vendors lag NVIDIA:** a third-party carrier needs its vendor's BSP for each
release. Seeed [promised 7.x for its Orin carriers](https://forum.seeedstudio.com/t/nvidia-has-officially-announced-jetpack-7-2-june-1-2026-any-plans-for-j401-agx-orin-32gb-support/295471)
on 2026-06-15 and reported J401 images by late June. Its
[reComputer Super](https://wiki.seeedstudio.com/recomputer_jetson_super_getting_started/) and
[Classic J401](https://wiki.seeedstudio.com/reComputer_J4012_Flash_Jetpack/) wikis list 6.2
and 7.2. The Robotics J401 ships with JetPack 6. The Classic J401 wiki says not to enable
MAXN SUPER with NX modules because the carrier's cooling is insufficient. NVIDIA lists
Orin Nano and NX modules as
[available through January 2032](https://developer.nvidia.com/embedded/lifecycle).

**Seeed Orin Nano 8 GB options** (checked 2026-09-15; none handled here). All use J401
carriers, which also take NX modules:

| Product | Form | Price seen |
|---|---|---|
| [J401 bundle](https://www.seeedstudio.com/Jetson-Orin-Classic-Bundle.html) | Classic J401 carrier + module; other contents not confirmed | $449.82 (NX 16 GB: $1,077.02) |
| [J401 Nano Bundle](https://openelab.io/products/seeed-studio-recomputer-j401-nano-bundle) | Carrier, 256 GB SSD, Wi-Fi, fan heatsink, 19 V adapter; listed as Super-capable | €899 inc VAT at a reseller; Seeed price not checked |
| [reComputer Super J3011](https://www.seeedstudio.com/reComputer-Super-J3011-p-6444.html) | Enclosed, dual GbE, 128 GB SSD | $769; [€668.90 inc VAT at Botland](https://botland.store/nvidia-modules/27336-recomputer-super-j3011-nvidia-jetson-orin-nano-8gb-ram-seeedstudio-114110312-5904422388546.html) |
| [reComputer Robotics J3011](https://www.seeedstudio.com/reComputer-Robotics-J3011-p-6503.html) | [Robotics J401](https://wiki.seeedstudio.com/recomputer_robotics_j401_getting_started/): 19–54 V XT30 input, 5 CAN, 2 GbE, 6 USB 3.2, optional 4-camera GMSL2; 115 × 115 × 38 mm, 1.1 kg; Wi-Fi sold separately | $789 |

The [Super J401 carrier](https://www.seeedstudio.com/reComputer-Super-J401-Carrier-Board-p-6642.html)
alone is $159 and supports Super MAXN mode for all four Orin Nano and NX modules.

The fourth candidate is **NVIDIA DGX Spark**, a desktop/ground compute option. NVIDIA's
[UK listing](https://marketplace.nvidia.com/en-gb/enterprise/personal-ai-supercomputers/dgx-spark/)
shows **£4,200 for 128 GB / 4 TB**, out of stock direct, checked 2026-09-13. This is a
current listing rather than an owner quote; partner pricing/availability may differ.

| Capability | Pi 5 + AI HAT+ 2 | Orin Nano Super developer kit | Super J401 NX 16 GB bundle | NVIDIA DGX Spark |
|---|---|---|---|---|
| Accelerator | Hailo-10H NPU; 40 INT4 / 20 INT8 TOPS | Ampere GPU, 1,024 CUDA cores / 32 Tensor cores | Same GPU core counts, higher clocks; adds two NVDLA engines and PVA | GB10 Grace Blackwell; 6,144 CUDA cores, fifth-generation Tensor cores and RT cores |
| GPU sparse INT8 / total sparse INT8 | Not applicable / precision differs | 67 / 67 TOPS | 77 / 157 TOPS; remaining 80 from DLAs | Advertised up to 1 PFLOP at sparse FP4; different metric |
| CPU | Pi 5 host | 6 Cortex-A78AE cores, up to 1.7 GHz | 8 Cortex-A78AE cores, up to 2 GHz | 20 Arm cores: 10 Cortex-X925 + 10 Cortex-A725 |
| Memory | Pi RAM plus separate 8 GB accelerator RAM; not one combined pool | 8 GB shared LPDDR5; 102 GB/s | 16 GB shared LPDDR5; 102.4 GB/s | 128 GB coherent shared LPDDR5x; 273 GB/s |
| Model deployment | Hailo compiled models/runtime; custom models depend on compiler support | CUDA, PyTorch and TensorRT; ARM64 builds, memory and versions constrain deployment | Same ecosystem; more memory headroom, DLA needs compatible models/software | CUDA on DGX OS; ARM64 and Blackwell-compatible builds required |
| NVMe | [Existing Base needs a switch or changed connection](#ai-hat-2-and-nvme) | Native M.2 2280 PCIe 3 x4 and M.2 2230 PCIe 3 x2 slots | Native NVMe, 256 GB SSD included; no AI accelerator/SSD connector conflict | 4 TB NVMe included in this configuration |
| Video encoding | HAT adds no encoder | CPU encoding; no NVENC | Hardware video encoder, including H.265 4K60 capability | NVENC and NVDEC |
| Power figures | Hailo quotes 2.5 W typical for the accelerator, not a complete Pi/HAT/SSD system | 7–25 W module modes | 10–40 W module modes; Super MAXN is separate; not whole-system draw | 140 W GB10 chip TDP; supplied 240 W PSU rating is not measured consumption |

Sources: [Hailo chip brief](https://hailo.ai/hailo-files/hailo-10h-product-brief-en/),
[AI HAT specification](https://www.raspberrypi.com/products/ai-hat-plus-2/),
[NVIDIA specifications](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/),
[dense/sparse figures and software](https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/),
[Jetson connectors](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html),
[Hailo custom-model workflow](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/GETTING_STARTED.rst),
[NVIDIA Orin module/compute comparison](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/),
[Spark hardware](https://docs.nvidia.com/dgx/dgx-spark/hardware.html),
[Spark software architecture](https://docs.nvidia.com/dgx/dgx-spark-porting-guide/overview.html).
**TOPS are not application benchmarks:** precision, sparsity, supported operations and
memory traffic prevent deriving a speed ratio from these figures.

**Published generation examples, not a matched benchmark:**

| Publisher/platform | Model | Tokens/s | Published conditions |
|---|---|---|---|
| Hailo GenAI model zoo / Hailo-10H | Qwen2.5-1.5B-Instruct | 7.35 | A8W4; compiled context limit 2,048; host/measurement conditions not fully specified in table |
| Hailo GenAI model zoo / Hailo-10H | Qwen3-1.7B-Instruct | 4.78 | A8W4; compiled context limit 2,048; same qualification |
| NVIDIA / Orin Nano Super | Llama 3.2 3B | 43.07 | INT4, MLC API; vendor benchmark published 2024-12-17 |
| NVIDIA / Orin Nano Super | Llama 3.1 8B | 19.14 | INT4, MLC API; same publication |

Sources: [Hailo models and performance](https://github.com/hailo-ai/hailo_model_zoo_genai/blob/main/docs/MODELS.rst),
[NVIDIA benchmarks](https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/).
Hailo's listed complete LLM/VLM examples are mainly 1–2B models; capacity claims alone
do not establish availability of a compiled model. Jetson can run selected quantised 7–8B
models, but Nano's 8 GB shared RAM leaves limited room for simultaneous robotics workloads and
long context. Hailo's separate RAM preserves host capacity. Raspberry Pi/Hailo identify
[encoding, prompt processing and short responses](https://www.raspberrypi.com/news/when-and-why-you-might-need-the-raspberry-pi-ai-hat-plus-2/)
as stronger HAT use cases than sustained text generation.

**NX buys capacity and concurrency more than GPU speed.** Its GPU peak is ~15% above
Nano's and memory bandwidth is essentially unchanged; 157/67 is not an LLM speed ratio.
The extra RAM allows larger model/context allocations or more resident workloads. As a
capacity estimate, 14B weights at 4 bits occupy ~7 GB before quantisation metadata, runtime
buffers and KV cache: selected 14B-class models become plausible on 16 GB, not a promise
of acceptable speed or of simultaneous full robotics and LLM pipelines. Rule of thumb,
unmeasured here: token-by-token generation is memory-bandwidth-bound, reading roughly the
whole weight set per token, so on the same 102 GB/s a model twice the size generates at
roughly half the rate. No matched
NX/Nano benchmark has been established here. For onboard voice + vision + mapping,
the RAM is the main reason to consider paying the premium. For learning or one modest
policy/detector, Nano remains the stronger value assessment.

**NX memory is shared across the whole system:** the CPU/OS, GPU and both DLA engines
draw from the same 16 GB LPDDR5 pool; it is not 16 GB per accelerator or a fixed equal
partition. Model weights, inference buffers and CPU applications all consume this budget
([NVIDIA Tegra memory architecture](https://docs.nvidia.com/cuda/cuda-for-tegra-appnote/index.html)).
Each Orin DLA also has 1 MiB of dedicated SRAM for local working data; its larger memory
requirements use system DRAM ([DLA memory pools](https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/dla-memory-pools.html)).
Offloading a detector to DLA can free GPU compute, but does not remove its system-memory
requirement or provide an independent DRAM bandwidth budget.

**DLA is conditional value.** It offloads supported CNN layers through TensorRT, not
arbitrary CUDA/LLM work. [JetPack 6.2 documents a DLA stack](https://developer.nvidia.com/embedded/jetpack-sdk-62).
JetPack 7.2 shipped without DLA: per
[NVIDIA staff on the forum](https://forums.developer.nvidia.com/t/dla-runtime-unavailable-on-jetpack-7-2-l4t-r39-2-cannot-create-dla-engine/373788)
(2026-06-22), its unified SBSA driver leaves DLA unavailable by default. NVIDIA announced
the fix as released on 2026-09-10; it needs **JetPack 7.2.1 + CUDA 13.4.1 + TensorRT
11.3.0 GA**. The [TensorRT guide](https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/work-with-dla.html)
still said 11.3 lacked DLA on 2026-09-08, two days before that announcement. Unverified on
hardware here, and whether Seeed's BSPs cover 7.2.1 is unchecked. Validate the exact
image/runtime before counting DLA capacity in a purchase justification.

**Spark buys a much larger local model tier.** It has eight times NX's RAM but only
~2.7 times its memory bandwidth; neither ratio predicts end-to-end performance. NVIDIA
[advertises inference up to 200B parameters](https://www.nvidia.com/en-us/products/workstations/dgx-spark/),
which is a capacity claim dependent on quantisation, context and runtime overhead. At
4 bits, 70B weights alone are ~35 GB and 200B ~100 GB before overhead. This opens models
far beyond the Jetsons' capacity, without establishing interactive speed for every model.
The sparse FP4 peak is not comparable to the Jetsons' INT8 totals or a guarantee of faster
small-model inference than the existing RTX workstation. No matched Spark/Jetson/RTX
benchmark has been established here.

For adaptation, NVIDIA publishes a [single-Spark NeMo 70B QLoRA recipe](https://build.nvidia.com/spark/nemo-fine-tune/instructions):
parameter-efficient fine-tuning, not full-weight training or pretraining a 70B model.
[Isaac Sim 6.0 lists DGX Spark support](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html)
on DGX OS 7, with cuRobo/cuMotion unsupported there at the checked date. Simulation and
synthetic-data development are candidates; supported execution does not establish useful
throughput for large parallel RL runs. ARM64 software compatibility still needs checking.

**Deployment assessment:** Spark is a ground/desk candidate: the
[manufacturer specifies 1.2 kg and 150 × 150 × 50.5 mm](https://www.nvidia.com/en-us/products/workstations/dgx-spark/),
before its external supply. An onboard companion can handle time-sensitive perception
while a ground workstation/Spark handles large-model reasoning, training and analysis.
Wireless transport adds variable latency and possible outages; ground inference is not a
substitute for a validated onboard response loop. Flight control remains with the flight
controller. Actual aircraft payload, power, cooling and latency budgets are unestablished.

**Purchase assessment:** start ground experiments on the already-owned
[RTX 5070 Ti workstation](#the-gpu-workstation). Spark becomes worth evaluating when a
specific workload exceeds 16 GB GPU memory or needs a dedicated large-memory host; no
evidence here justifies buying it merely for a speed increase. Nano remains the lower-cost
general onboard experiment; NX is the option for more memory/concurrency. Neither dev-kit
package is established as a suitable airborne installation without integration work.

**Assessment for this family:** Jetson is the stronger candidate for varied on-robot
AI experiments, LeRobot policy inference and GPU perception. NVIDIA documents
[LeRobot on Orin Nano Super](https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/),
[GPU visual SLAM](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_visual_slam/index.html)
and [mapping with nvblox](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_nvblox/index.html).
Existing CPU ROS nodes do not become GPU-accelerated merely by moving hosts. Choose a
supported JetPack/ROS/package combination; [Isaac ROS 4.6 added Orin/JetPack 7.2 support
on 2026-08-18](https://nvidia-isaac-ros.github.io/releases/index.html).
The HAT remains a candidate for a known supported inference pipeline where keeping the
Pi and minimising accelerator power matter most. Jetson adoption would require new
power/mounting and camera/GPIO compatibility work. Keep deterministic control on the MCU
and substantial training on the [GPU workstation](#the-gpu-workstation). This comparison
does not change the family's decided Pi intent-host architecture.

### Companion computers in hand — the Raspberry Pi 5 fleet

**Audited live over SSH, 2026-09-13 (owner); fifth unit 2026-09-15.** Five BCM2712
machines are owned, all in hand: four **8 GB Pi 5 Model B** boards and one **16 GB
Pi 500+** keyboard computer. RAM is soldered and non-upgradable on both. `MemTotal` varies
by ~100 MB between the Pi 5 units purely from each install's GPU/CMA reserve — not a
capacity difference. eth0 is present on every unit but unused (Wi-Fi only).

| Role | Board rev | OS (arm64) | Notes |
|---|---|---|---|
| **The AI HAT+ 2 bench host** (since 2026-09-18; the former desktop Pi, candidate drone intent computer) | Rev 1.0 (`d04170`) | **Ubuntu Server 24.04.5**, rebuilt 2026-09-19 (was Raspberry Pi OS bookworm, desktop, from 2024-03-27); bootloader updated to current the same day | Boots from its Kingston SNV2S500G 500 GB in a **USB 3 enclosure (SSK, USB ID `152d:0562`)** on a blue USB 3 port: the Pimoroni NVMe Base was removed to give the HAT the PCIe connector, where the Hailo-10H enumerates as `Hailo Technologies Ltd. Device 45c4`. The RTL9210B enclosure it first used is retired from this duty (below). **TRIM is on** since 2026-09-20, forced by a udev rule: the RTL9210B hang behind wk-hexapod DEC-23 does not apply to this bridge, which was tested first — [below](#trim-through-the-jmicron-152d0562-bridge). Root is `noatime` from the same date. The enclosure setup that finally booted is recorded [below](#booting-a-pi-5-from-a-usb-nvme-enclosure). |
| General-purpose desktop Pi | Rev 1.1 (`d04171`) | Ubuntu 24.04 LTS, desktop | |
| 3D-printer host | Rev 1.1 (`d04171`) | Raspberry Pi OS (Debian 12 bookworm), headless | |
| wk-hexapod brain | Rev 1.1 (`d04171`) | Ubuntu 24.04 LTS, desktop | Normally powered off. |
| Desktop computer, no role assigned | Pi 500+ Rev 1.0 (`e04190`) | Ubuntu 24.04 LTS, desktop | The only 16 GB unit. Keyboard form factor, so never an on-robot host. Boots from its internal 256 GB NVMe. Offline 2026-02-02 to 2026-09-15 and briefly recorded as a missing Pi 5; the desktop Pi 5 above was mistaken for it. |

**Purchases on invoice** (read 2026-09-17 ([how](../AGENTS.md#invoices-and-order-history)); which order became which board
is not recorded): Pi 5 8 GB — The Pi Hut #1164841, 2024-03-23, £78.00, with Amazon
202-8965289-9773916, 2024-03-26: Pimoroni NVMe Base £16.50 and Kingston SNV2S/500G £36.78,
matching the desktop Pi's parts; Amazon 026-1806556-5848369, 2025-12-28, £84.99; The Pi
Hut #1488946, 2026-01-05, £91.20, with a Raspberry Pi SSD 256 GB, 27 W PSU, Active Cooler
and NVMe Base case. Pi 500+ — The Pi Hut #1431072, 2025-09-29, £172.80. **The fourth Pi 5
has no purchase in the mail.**

**Identifiers are not kept here.** Hostnames, serials, MACs, LAN and tailnet addresses,
login users and SSH host-key fingerprints for every board — the data needed to recognise a
unit without re-auditing it — live in the private `wk-inventory` repo, `docs/pi5-fleet.md`.
This repository is public; see [What does not belong here](../AGENTS.md#what-does-not-belong-here).

### Never boot a Pi with another Ubuntu Pi's system disk attached

**Incident, 2026-09-18.** The general-purpose desktop Pi 5 was used as the bench for the
hexapod's SSD (in a USB 3 enclosure) to edit its `config.txt`, then rebooted with the
enclosure still attached. It came up with the hexapod's hostname: cloud-init's
`set_hostname` wrote it to `/etc/hostname`, and the Tailscale node renamed itself to
`<hexapod>-1`, so the desktop Pi vanished from the tailnet under its own name. The board,
disk and Tailscale node key were all the desktop Pi's — only the name had moved.

**Mechanism.** Every Ubuntu Pi image carries the same filesystem labels, `writable` and
`system-boot`; `/etc/fstab` mounts both by label, and cloud-init's NoCloud datasource
(`/etc/cloud/cloud.cfg.d/99-fake-cloud.cfg`, `fs_label: system-boot`) finds its seed by
that label. With a second Ubuntu Pi disk attached at boot there are two of each, and
which is picked is not under your control. The same machine had computed the hexapod's
hostname once before, on 2026-09-13, without writing it. The exact read path that yielded
the name (the cached datasource logged the NVMe seed) is not fully established.

**Rules.** Unplug another Pi's system disk before rebooting the host that edited it.
Where a Pi must keep its name regardless, set `preserve_hostname: true` in a
`/etc/cloud/cloud.cfg.d/` drop-in (done on the desktop Pi, 2026-09-18). Recovery is
`hostnamectl set-hostname <name>`, fix `127.0.1.1` in `/etc/hosts`, and
`tailscale set --hostname <name>` if the tailnet name does not follow within a minute.

### Booting a Pi 5 from a USB NVMe enclosure

**Measured 2026-09-18/19 on two Pi 5s with the same RTL9210B enclosure and Kingston
SNV2S500G.** Writing a 6.7 GB image to it from a Pi 5 failed at 1.5 GB with a USB device
reset and the SSD vanishing behind the bridge; booting a Pi 5 from it dropped the root
disk with I/O errors at about 300 s, on both a third-party and the official 27 W 5 A
supply. The same enclosure wrote and read back cleanly on the x86 workstation. It then
booted and ran on the Pi 5 with two settings added to the boot partition together, so
**which one mattered is not established**:

- `usb_max_current_enable=1` in `config.txt` — without it a Pi 5 caps its USB ports at
  600 mA total; the hexapod ran the same kind of enclosure for a day with this set.
- `usb-storage.quirks=0bda:9210:u` at the front of `cmdline.txt` — drives the RTL9210
  through the mass-storage path instead of UAS (`Quirks match for vid 0bda pid 9210` in
  `dmesg` confirms it took), at some cost in throughput.

**Then the bootloader update broke booting (2026-09-19).** After `rpi-eeprom-update -a`
took the bootloader from 2024-02-16 to 2025-12-08, the Pi stalled in the bootloader
while reading the enclosure on a USB 3 port (diagnostics screen: `boot: mode USB-MSD`,
`Read /config.txt` repeating; the old bootloader had booted the same disk twice). The
bootloader has its own USB stack, so the kernel quirk does not apply there. **Moving the
enclosure to a black USB 2 port fixed it**: it boots and runs at 480 Mb/s
(`lsusb -t`), which is adequate for a bench host.

**Rules:** image Pi disks from the workstation, not from a Pi; set both lines before the
first boot of any Pi 5 on this bridge; put the enclosure on a **USB 2 port** on a current
bootloader; and if it still drops, boot from microSD and keep the SSD off USB.

**Resolved the same day by changing the bridge.** The SSD moved into a second enclosure
the owner already had, USB ID `152d:0562` (its descriptor reads "JMicron JMS567 SATA
6Gb/s bridge", though it is bridging an NVMe drive — the exact JMicron part is
unverified). On a **blue USB 3 port**, current bootloader: boots first time, runs under
UAS at 5 Gb/s, and a 2 GiB write then read gave **220 MB/s and 346 MB/s** with no USB
errors and the HAT still present. So the RTL9210B was the whole problem, at both the
bootloader and the kernel stage, and it is retired from Pi 5 boot duty. The RTL9210
quirk in `cmdline.txt` is harmless and stays. Still open, now only as the tank's
question: the SSD back on PCIe through the Waveshare 2-channel switch (Devastator OQ-13).
A note for the record: a previous session recommended sourcing an RTL9210 enclosure; the
basis for that is not recorded, and the evidence here — two Pi 5s, two failure modes —
runs the other way.

### TRIM through the JMicron 152d:0562 bridge

**Verified 2026-09-20 on a spare enclosure, then applied to hailo (owner-approved).**
This bridge advertises `LBPU=1` and "Maximum unmap LBA count: unbounded" in its Logical
Block Provisioning VPD page, but clears `LBPME` in READ CAPACITY(16). The kernel
therefore leaves `provisioning_mode` at `full` and `discard_max_bytes` at 0, and
`fstrim` reports "the discard operation is not supported". **That is the same signature
as the RTL9210B, where forcing `unmap` hung the disk and the host** (wk-hexapod
[DEC-23](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/decisions.md),
superseded; the negative result is in that repo's `test-log.md`). So it was proved on a
spare before hailo was touched.

Forcing `provisioning_mode=unmap` yields `discard_max_bytes = 4294966784`. Two tests on a
second, identical SSK enclosure (held in the private `wk-inventory` repo, `docs/stock.md`):

- **Range correctness.** 256 MiB of random data at a 1 GiB offset, checksummed in 16 MiB
  chunks; `blkdiscard` of a 32 MiB middle range changed exactly those two chunks and left
  all fourteen others byte-identical.
- **Scattered `fstrim`.** ext4, 500 x 2 MiB files, every other one deleted; `fstrim`
  reported 915.3 GiB trimmed and all 250 survivors verified by SHA-256. The bridge's
  "Maximum unmap block descriptor count: 63" caused no collateral loss.

On hailo this trimmed 452.2 GiB on `/` and 409.4 MiB on `/boot/firmware`; 800 sampled
binaries verified unchanged afterwards, filesystem `clean`, no I/O errors. Persisted in
`/etc/udev/rules.d/10-ssk-nvme-trim.rules`:

```
ACTION=="add|change", SUBSYSTEM=="scsi_disk", ATTRS{idVendor}=="152d", ATTRS{idProduct}=="0562", ATTR{provisioning_mode}="unmap"
```

**This covers the JMicron bridge only. Do not force `unmap` on an RTL9210B.**

**Two traps in this bridge's identity, both of which have already misled a session:**

- `usb.ids` decodes `152d:0562` as "JMicron JMS567 SATA 6Gb/s bridge". That is wrong for
  this unit, which bridges NVMe — the drives are M-key M.2 2280, and an M-key card
  cannot seat in a SATA socket. **Do not infer the interface from `lsusb` output here.**
  The part is most likely a **JMS583**: `smartctl -d sntjmicron` is the one passthrough
  type whose opcode the bridge recognises (it returns a medium error, not "unsupported
  opcode"), and JMS583 firmware is distributed against this same PID. Unverified further.
- **Both SSK enclosures report the same bridge serial**, `DD564198838B8`. It identifies
  the bridge model, not the unit, so nothing may key on it — use the filesystem UUID.
  Identifiers live in the private `wk-inventory` repo, `docs/pi5-fleet.md`.

Drive identity is **not readable through this bridge**: SCSI INQUIRY returns vendor `SSK`
with an empty model field, `hdparm -I` is silent (NVMe has no ATA layer to answer it), and
every `smartctl` passthrough type fails. Record a drive's model while the card is out of
the enclosure; no software route exists once it is in. Firmware updating the bridge is
possible (JMicron OEM tooling, Windows-only, unofficial redistributions) but is **not
recommended**: these units report `bcdDevice 0209`, newer than the 2.0.8 in circulation,
and nothing is malfunctioning.

### The GPU workstation

**Established 2026-09-07.** A workstation with an **NVIDIA GeForce RTX 5070 Ti (16 GB,
driver 610.62)** is available, running **Ubuntu 24.04 LTS under WSL2** on a Windows
desktop. GPU passthrough is working (`/dev/dxg` present, CUDA libraries at
`/usr/lib/wsl/lib/`), and Docker is installed. **No ML stack is installed yet** — no
PyTorch, JAX, MuJoCo or `uv` as of that date.

It is the only GPU in the family, and it unlocks two things nothing else can: **RL
policy training** (MuJoCo Playground / MJX and anything else JAX- or PyTorch-based) and
**local LLM/VLM inference** for a reasoning tier.

Four constraints, all of which bite early:

- **Blackwell means `sm_120`.** The RTX 50-series needs **CUDA 12.8 or newer** and
  framework builds carrying `sm_120` kernels — PyTorch `cu128` wheels or later, a current
  `jax[cuda12]`. Older wheels fail outright or fall back silently to CPU, which on a
  300 M-step training run looks like "it works, but slowly" rather than like an error.
- **`nvidia-smi` is not on `PATH`.** It lives at `/usr/lib/wsl/lib/nvidia-smi`. A naive
  check therefore reports *no GPU* on a machine that has one.
- **WSL2 networking is NAT'd, not mirrored.** The LAN cannot open connections *into* the
  instance. This is the concrete reason **DDS multicast discovery will not reach it**, and
  why [Zenoh](ideas.md#physical-ai-and-the-hive-mind) rather than a networking workaround
  is the indicated route for any ROS 2 role. Unicast over the private overlay network
  works — that is how the machine is reached today.
- **It is a desktop, not a server.** Availability is not guaranteed: it may be powered
  off, or busy. Any role given to it must degrade gracefully when it is absent.

**16 GB of VRAM** is comfortable for MJX-scale RL training and for quantised models in the
7–14 B class; it is the binding limit on anything larger.

### The Jetson Orin Nano

**Flashed 2026-09-18.** One **Orin Nano Super Developer Kit, 8 GB** (module `3767-0005`) on
JetPack 7.2.1 / L4T R39.2.1, Ubuntu 24.04.4, desktop, root on a WD_BLACK SN850 1 TB in the
2280 slot. Default power mode is 25W; MAXN_SUPER is mode 2. Wi-Fi only; reached over
Tailscale SSH. Purchase and allocation are in [status.md](status.md#ai-compute-purchase--ai-hat-2-jetson-or-dgx-spark);
identifiers in the private `wk-inventory` repo, `docs/jetsons.md`.

#### Flashing a Jetson from a 24.04 host

Headless, over USB-C, no monitor or SD card. NVIDIA's r36 and r39 Quick Starts list only
Ubuntu 22.04 or 20.04 hosts, so on the 24.04 workstation the BSP runs in a **privileged
Ubuntu 22.04 Docker container** (`--privileged --net host -v /dev:/dev`). That worked on
the first real attempt once four host-side problems were fixed:

1. **Load `nfsd` on the host** (`modprobe nfsd`), then inside the container mount
   `/proc/fs/nfsd` and start `rpcbind`: `l4t_initrd_flash.sh` serves the images by NFS and
   otherwise stops at "NFS server is not running".
2. **Set `USER=root`** in the container: the image script tests `$USER`, not the UID, and
   Docker leaves it unset ("requires root privilege").
3. **Install `qemu-user-static` on the host**: `apply_binaries.sh` chroots into the aarch64
   rootfs, which needs binfmt registered in the host kernel.
4. **Check the archives** with `lbzip2 -t` before extracting: one 2 GB sample-rootfs
   download ended at 1.44 GB with curl reporting success. No published checksum was found.

Sequence (from `Linux_for_Tegra/`, as root in the container): `l4t_flash_prerequisites.sh`
(commit the container, or it is lost), `apply_binaries.sh`, `l4t_create_default_user.sh -u
<user> -p <pw> -n <host> --accept-license` (skips oem-config), then with the board in Force
Recovery (FC REC jumpered to GND, `lsusb` shows `0955:7523 NVIDIA Corp. APX`):

```
./l4t_initrd_flash.sh --external-device nvme0n1p1 \
  -c tools/kernel_flash/flash_l4t_t234_nvme.xml \
  --showlogs --erase-all jetson-orin-nano-devkit-super external
```

About five minutes; it rewrites QSPI and the whole SSD. "Backup GPT table is corrupt" and
"Not all of the space … used" in the log are expected; the root partition grows to fill
the disk on first boot. After boot the board enumerates as `0955:7020` and its USB network
comes up at `192.168.55.1`, but the host's `enx…` interface stays down until given an
address (`192.168.55.100/24`). **The Tegra kernel lacks `CONFIG_NETFILTER_XT_CONNMARK`**,
so Tailscale reports a connmark health warning; tailnet traffic and SSH work regardless.
A new node must carry the same ACL tag as the other personal machines before tailnet
policy admits SSH to it (tag named in `wk-inventory`).

### The topic contract

The vocabulary is shared deliberately: fix it once and every robot inherits it. Bodies
change; the spinal-cord protocol does not.

`/cmd_vel` · `/joint_commands` · `/joint_states` · `/imu` · `/wheel_odom` · `/telemetry`

The hexapod already speaks most of it — `/cmd_vel`, `/joint_commands`, `/joint_states`,
`/imu/data`, plus `/odom` for gait-integrated position and `/tf` for `odom`→`base_link`
(it has no wheels, so no `/wheel_odom`, and battery is `/battery/voltages` rather than
`/telemetry`) — which is what makes its navigation stack portable in principle.

---

## Collision awareness — open, family-wide

**Raised 2026-09-12 while watching SO-ARM101 cycle its joints**, which the owner treats as a
surrogate for industrial arms, where operating ranges are safety matters and "a box of
acceptable movement" is the basic tool: per-joint travel limits are
the only geometric protection any robot here has, and they cannot express "elbow past X is
fine unless the wrist is past Y", let alone another robot or a person in the same space.
LeRobot has no self-collision or world model at runtime (its policies inherit safety from the
human demonstrator); the Freenove hexapod stack has none; koala-bot's limbs will have the
same problem with more joints. **Nothing is decided.** What exists to draw on, and where it
would sit in the [two-tier split](#compute-the-two-tier-split):

| Layer | Mechanism | Tier | State here |
|---|---|---|---|
| Joint envelope | Per-joint limits **plus pairwise rules** (elbow vs wrist, shoulder vs elbow) fitted from hand-swept contact poses — cheap, MCU-sized, checks every goal before it is sent | Reflex | Not built. SO-ARM101 needs it first; the method is the calibration sweep applied to joint pairs |
| Effort reflex | Current / load / tracking-error thresholds that stop or back off a joint on unexpected resistance | Reflex | Only in bench tools (`extents_cycle.py`): stall, current, temperature stops |
| Self-collision model | URDF with collision meshes checked with FCL each control step — what MoveIt 2 does; upstream ships an SO-101 URDF and MuJoCo scene | Intent (ROS 2) | Not built; the meshes exist |
| World model | Depth camera → occupancy (octomap / voxel grid) → planning-scene obstacles; other robots publish their own poses into the same scene | Intent | Nothing; koala-bot's head camera and the hexapod's depth camera are the sensors that would feed it |
| Speed-and-separation | Slow down as anything approaches, stop inside a radius — the collaborative-robot rule (ISO/TS 15066 in industry) | Intent → reflex | Nothing |

The pattern that fits the family: the **reflex tier guarantees the arm cannot fold into
itself** (joint envelope + effort reflex, no perception needed, runs with the intent tier
dead), and the **intent tier keeps it out of the world** (geometric model + perception). A
policy or planner then commands only within what both allow. **SO-ARM101 is proving it
first (its DEC-14, 2026-09-14):** forward kinematics from upstream's URDF, a world keep-out
(plane minus cylinder), **self-collision between capsule hit boxes fitted to upstream's
collision meshes**, and a damped-least-squares IK, all host-side Python in its
`software/kinematics.py`, checked at every sample of a plan before a move is commanded
([roadmap](../projects/soarm101/docs/roadmap.md)). Capsules were chosen over meshes so the
same test can later run on the reflex-tier MCU. Whether MoveIt 2 or something lighter
carries the intent-tier check in the end is still open. **A split worth keeping (SO-ARM101,
2026-09-14, after its arm reached back into a wall):** physical clearance around the robot —
the sweep of the links nearest the base — is the *installer's* space, kept free by placement
and not by software; the software rule bounds where the *end-effector* may go. Industrial
practice draws the same line (ISO 10218's restricted space around the robot versus the
operating space its tool is allowed to use).

## Power integrity

Banked from an earlier InMoov build that stalled partly on this. A fully-loaded
servo/motor robot is a spiky, inductive load; bench PSUs have slow transient response and,
on a shared rail, dump that noise onto the logic — causing brownouts, servo jitter,
MCU/IMU resets and I²C corruption.

- **Prototype from a stiff, low-impedance source** — a LiPo pack, not a bench PSU. It is
  also the eventual onboard power, so there are no bench-to-battery surprises.
- **Isolate the logic rail.** MCU, Pi and IMU on their own regulator with local
  decoupling; never share the servo or motor feed points. The Pi 5 is power-hungry and
  brown-outs are a known failure mode.
- **Bulk capacitance** (~1000–2200 µF) across the servo/motor bus, to absorb transients
  and tame lead inductance.
- **Fuse the main pack lead.** LiPos deliver enormous fault current.

**The mechanism is source impedance, not "clean DC."** A bench PSU regulates through a
control loop with millisecond response; a servo stepping 200 mA → 2.7 A does it in
microseconds, and on a shared bus those dips overlap. A LiPo has milliohms of internal
resistance and no loop to settle. Lead resistance and inductance cause the same dip and
follow you between supplies — hence short, fat leads and the bulk capacitance above.

**Where a current-limited bench PSU is still the right tool** (scope note, 2026-09-07;
this does not weaken the rule above, which is about transient response *under load*):

- **First power-up and servo ID assignment.** A LiPo into a miswired bus delivers tens of
  amps without complaint; a supply limited to ~1 A turns a wiring error into a shrug. IDs
  are assigned one unplugged servo at a time, so there is no load to respond to.
- **Measuring draw**, which is where a project's power budget comes from.

Move to the pack the moment anything runs under load.

**One InMoov failure mode does not transfer.** InMoov ran PWM hobby servos, which jitter
both from brownout *and* from signal-path noise and deadband hunting. STS bus servos are
closed-loop, with their own magnetic encoder and a serial command — there is no pulse
width to misread. The brownout half still applies; the signal-side half does not.

**Nothing in this chain has a low-voltage cutoff.** Stop at ~10.5 V on a 3S (3.5 V/cell);
the adapter's 9 V floor is ~3.0 V/cell and already deep enough to hurt the pack.

### Bench power for servo robots — open

**Raised 2026-09-12.** A bench needs 12 V that behaves like a battery — stiff under a 2 A step,
no current-limit fold-back — but stays topped up from the mains. A plain brick sags or trips
on stalls; a bare LiPo must never be charged under load. What exists off the shelf, from a
first look (2026-09-12, specs partly unverified — check the port ratings before buying):

| Class | Example | 12 V out | UPS / charge-while-supplying | Verdict for a 6-servo bench |
|---|---|---|---|---|
| Portable power station (LiFePO₄) — **Bluetti AC70** | 768 Wh, 1 000 W AC, 10.2 kg, ~£419 UK (2026-09-12) | Car port **12 V / 10 A, stated "regulated"**; 2 × USB-C 100 W | **Yes**: pass-through stated; UPS 20 ms claimed, 14 ms measured (StorageReview) | **Recommended bench unit.** Everything confirmed; runs the Pi, a laptop and the iron as well; 768 Wh ≈ a day of arm work at ~1 A |
| Portable power station (LiFePO₄) — **EcoFlow River 3 Plus** | 286 Wh, 600 W AC, 4.2 kg, ~£219 UK | Car port **12.6 V / 10 A, 126 W** | UPS < 10 ms; **pass-through not confirmed** in the sources read | Value pick for the arm alone, if pass-through is confirmed on the spec sheet |
| Portable power station — EcoFlow Delta Pro 3 | ~4 kWh, house-backup class | **12.6 V / 30 A Anderson** | Yes | Only unit found with a > 10 A regulated 12 V port; far too big and dear for a bench |
| 12 V Li-ion pack with DC out | Talentcell YB1208300 (11.1 V nominal, 8.3 Ah, **6 A max**, 12.6 V/1.5 A charger) | 12 V barrel, 6 A | Pass-through is claimed for some Talentcell models; not verified per model | Marginal — 6 A is under the 10 A target; fine for one or two servos on a bench |
| "Mini DC UPS" for routers / CCTV | many, 12 V 2–5 A | Low | Yes | Too small |
| Automotive DC UPS | PowerStream DC-UPS-1212 (12 A pass-through, lead-acid, 0.8 A charge, ~$135) | 12 A | Yes, < 50 µs switch | Right current, wrong chemistry and needs a separate battery; not a desk unit |
| Build: 3S pack + BMS + power-path charger | — | whatever the pack gives | Yes if the charger has a load-sharing path | Exactly what a power station is; only worth it as a robot-mounted design, not for the desk |

A power station's DC port is a DC-DC converter fed from the battery, so it is battery DC in
the sense that matters (no mains ripple, no fold-back on transients) without being raw cell
voltage — which is better for the servos than a sagging pack. Every affordable unit tops out
at **10 A on 12 V** — the same 120 W ceiling as the brick recommendation, enough for realistic
motion (SO-ARM101 peaks ~2 A) and not for the all-stalled fault case, which is the fuse's job.
Nothing bought; whether the car-port rating holds at 10 A continuous is unverified.

### GPIO lines float when their process dies

Established on the hexapod, 2026-09-09, and true of any robot that drives a peripheral
straight from a Raspberry Pi GPIO: when the userspace process holding a line exits or is
killed, the kernel releases the line and it reverts to a **floating input**. An
active-high load on that pin — the hexapod's shield buzzer — then turns on and stays on
through a `reboot`. The fixes that worked, in layers: a firmware default in `config.txt`
(`gpio=<n>=op,dl`), a `systemd` service holding the line with `gpioset --mode=signal`,
and the software default off. Details in
[`wk-hexapod/docs/hardware.md`](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/hardware.md#the-buzzer-hazard).
This is one of the concrete arguments for the reflex tier: an MCU holds its pins through
a host crash; a Pi does not.

---

## Modelling and simulation

- **URDF + RViz** for serial kinematics — limbs, base yaw, head. It is the same file the
  robot's ROS 2 stack uses, so it is not a throwaway.
- **CAD motion study** for parallel mechanisms. *URDF cannot represent closed kinematic
  loops*, so anything parallel (koala-bot's torso and 3-RPS neck) is modelled in CAD or a
  loop-capable simulator.
- **Physics** — Gazebo (ROS 2-native), or PyBullet / MuJoCo for balance and gait.

---

## Documentation conventions

Every project in the family follows the same conventions, set out in each repo's
`AGENTS.md` — which is the provider-neutral entry point, with any harness-specific file
(`CLAUDE.md`, `GEMINI.md`) doing nothing but pointing at it.

- **Every repo stands alone.** A brand-new assistant, on a first read of that repository
  and nothing else, must be able to do useful work in it. This is the load-bearing rule;
  the rest follow from it.
- **The repository is the memory.** Per-harness memory holds *pointers* only — never a
  project fact, a measurement or a decision. Anything durable lands in a file.
- **Docs are written AI-first** — dense, factual, cross-referenced, greppable, on the
  assumption an AI assistant is the primary reader.
- **Every artefact meets the 4Cs** — Correct, Complete, Coherent, Concise. See
  [`AGENTS.md`](../AGENTS.md#the-4cs--the-standard-every-artefact-meets).
- **No project fact lives only in chat.** Durable decisions land in the repo.
- **Decided and open are kept apart** — a `decisions.md` for what is committed and the
  durable *why*; an `open-questions.md` for what is still unresolved. Items move between
  them as they resolve, and an open question is never stated as settled.
- **A test log records what actually happened**, including "no change needed" results.

## Licensing

Mixed hardware/software/docs projects use the standard open-hardware **tri-licence**:

| Area | Licence | SPDX |
|---|---|---|
| Hardware — CAD, mechanical, PCB, printable parts | CERN Open Hardware Licence v2, Strongly Reciprocal | `CERN-OHL-S-2.0` |
| Software — firmware, host software, tooling | MIT | `MIT` |
| Docs and media | Creative Commons Attribution-ShareAlike 4.0 | `CC-BY-SA-4.0` |

Source files carry an `SPDX-License-Identifier:` header. Full licence texts are included
verbatim in the repo rather than linked. Vendored third-party CAD keeps its own licence in
its own directory — SO-ARM100 reference CAD inside koala-bot is Apache-2.0.

This repository's index and `docs/` are documentation and are `CC-BY-SA-4.0` (root
`LICENSE`). Each folder under `projects/` is a project in its own right and carries the
tri-licence in its own `LICENSING.md` and `LICENSES/`; the root licence does not cover it.
