# Hardware

What exists for this build, and its state. Print jobs and slicer settings are in the
family's private `3d-printing` repo; only their **results** are recorded here.

## Printed parts — SO-101 follower, 11 parts

All in **white eSUN PLA+** (DEC-05), on the family's Ender-5 S1. Upstream STLs, unmodified.
State as of **2026-09-09**:

| Part | State | Note |
|---|---|---|
| `Base` | **Usable** | Printed 2026-09-07 alone, 87 mm tall, no supports. STS3215 is a solid press fit in the pocket |
| `Base_motor_holder` | **Usable** | Plate 1, 2026-09-07 |
| `Motor_holder_Base` | **Usable** | Clean reprint on plate 1, 2026-09-07. A first copy (2026-09-06, supports everywhere) had support welded in the servo pocket and was superseded; it doubled as the first press-fit gauge |
| `Motor_holder_Wrist` | **Usable** | Plate 1, 2026-09-07 |
| `WaveShare_Mounting_Plate` | **Usable, cosmetic defect** | Plate 1, 2026-09-07. Delaminated at its raised boss; judged cosmetic 2026-09-07 and kept — mates correctly with a servo fitted |
| `Rotation_Pitch` | **Usable** | 2026-09-08, printed rotated 90° about X, which cut support from 5.4 g to 0.1 g |
| `Upper_arm` | **Usable** | Plate 3, 2026-09-08 |
| `Under_arm` | **Usable** | Plate 3, 2026-09-08 |
| `Wrist_Roll_Pitch` | **No usable copy yet** (OQ-05) | Attempt 1 (plate 3, flipped, bed-only support): fork face extruded into air. Attempt 2 (2026-09-08, supports everywhere): support welded to both fork faces. Attempt 3 (2026-09-09, organic support from the bed): **complete, not yet inspected** |
| `Wrist_Roll_Follower` | **Printed, not yet inspected** | Plate 4, 2026-09-09 |
| `Moving_Jaw` | **Printed, not yet inspected** | Plate 4, 2026-09-09, with a 5 mm brim |

The gauges from upstream `STL/Gauges/` (`Gauge_0`, `Gauge_tight_1`) were printed
2026-09-06: the servo is a tight friction fit in `Gauge_0`, the intended press fit. That
and the `Base` result established the family finding that PLA+ at these settings is
dimensionally correct with no elephant-foot compensation
([wk-robotics `common.md`](../../../docs/common.md#press-fits-and-supports)).

**Nothing is assembled.** No part has been fastened to another; servos have only been
test-fitted into pockets.

**The two M3 hex-nut recesses in `Wrist_Roll_Follower` are the wrist-camera provision**
(nuts installed 2026-09-12). They take upstream's *Hex-Nut Recess Wrist Camera Adapter*,
`Optional/SO101_Wrist_Cam_Hex-Nut_Mount_32x32_UVC_Module/stl/SO-ARM101_camera_wrist_mount.stl`
— an add-on, not part of the base print list, which is why it was not printed with the
eleven. Upstream prints it as oriented with tree supports and 40 % infill; it needs two
M3 × 8 screws into those nuts and four of the servos' M2 screws for the camera board.
Alternatives in the same folder: a one-piece `Wrist_Roll` replacement carrying the camera,
a plug-on variant, and RealSense D405/D435 mounts. An overhead mount that keys into the
arm's base is there too. All assume a **32 × 32 mm USB UVC camera module**. **Two
InnoMaker UVC boards are on order (2026-09-14, [`sourcing.md`](sourcing.md))** — one for
this wrist provision, one for a workspace view; the mount is not printed yet, and the
boards' hole pattern against the 32 × 32 mm assumption is checked when they arrive.

## Electronics in hand

| Item | Qty | Since | Note |
|---|---|---|---|
| Waveshare **ST3215 12 V** bus servo (Feetech STS3215 rebadge, 1/345), firmware **3.10** (shipped 3.9, upgraded 2026-09-12, DEC-11) | 2 | 2026-09-07 | Amazon. Bought as koala-bot's test-fit pair; now this arm's `shoulder_pan` and `shoulder_lift` ([`servos.md`](servos.md)). Box contained M3 horn screws and M2×5 self-tapping case screws |
| Feetech **STS3215 12 V** bus servo (1/345), firmware 3.10 | 4 | 2026-09-12 | From koala-bot's RCmall packs (DEC-09), **permanently since 2026-09-14** — a backfill 6-pack is ordered for koala-bot; this arm's IDs 3–6 ([`servos.md`](servos.md)). Each box: two metal horns, M3×6 horn screws, M2×6 case screws |
| Waveshare **Bus Servo Adapter (A)** v1.1 | 1 | 2026-09-07 | Upstream's "Motor Control Board" (DEC-03). CH343 USB-C. Both jumpers on **B** for USB |
| Feetech **FE-URT-2** | 1 | 2026-09-08 | Spare / bench bus adapter. Not needed for the arm |
| USB webcam, bench observation | 1 | 2026-09-12 | On this host as `/dev/video0` (1280 × 720 via V4L2). Lets the assistant see the arm during bring-up; not a LeRobot policy camera. Host user needs the `video` group (added 2026-09-12; ACL granted for the session). Placement and settings: [Bench](#bench) below |

Adapter behaviour, pinouts and power rules are family facts:
[wk-robotics `common.md` → Configuring a servo](../../../docs/common.md#configuring-a-servo--true-for-every-sts-project).

**Not in hand:** a decided 12 V supply (OQ-03), the
M2×6 and M3×6 fasteners upstream's guide calls for (OQ-07). The 12 V source used on the
bench on 2026-09-09 read 12.3–12.4 V at the servo and is otherwise **unrecorded**; on
2026-09-12 it was a **3S LiPo**, not fully charged, reading 11.7–11.9 V; a second, fuller 3S pack
read 12.2–12.4 V for the afternoon's calibration. From 2026-09-14 the bench source is an **Eventek KPS3010D**
bench supply (30 V / 10 A class) at 12.0 V, 11.9–12.1 V at the servos idle.

## Bench

The arm's physical situation since 2026-09-14 (owner). Anything that plans a motion — the
bench tools, and the geometry work under
[wk-robotics `common.md` → Collision awareness](../../../docs/common.md#collision-awareness--open-family-wide) —
takes these as world constraints.

- **Mount:** base clamped to a desk edge, free air in front of and below the base. The desk
  surface and whatever is on it lie behind.
- **Keep-out (owner's rule, 2026-09-14): nothing on the arm goes behind the vertical plane
  that rises from the base along the desk edge.** The plane is fixed in the world, not in
  the pan frame — at ±90° pan the arm runs along it. **The desk edge is 25 mm ahead of the
  pan axis** (owner's tape, 2026-09-14), so in the URDF base frame the plane is at
  x = 0.0638 m (`kinematics.DESK_EDGE_X`). The upper arm's root straddles that plane in
  every pose by construction of the mount; the check ignores a 50 mm region around the
  shoulder pivot. **Open (owner to say): whether the rule means the link *bodies* stay
  ahead of the edge (a 30 mm capsule margin — a vertical upper arm then overhangs by ~13 mm
  and is refused; the arm must lean ≥14° forward) or the link *centrelines* do (a vertical
  upper arm is allowed, its rear face ~2 cm over the desk).** The tools default to bodies. At the calibrated mid pose (all joints
  2047) the upper arm leans ~20° *forward* into free air with the wrist and gripper above
  and ahead of the base (owner, confirmed on the bench camera 2026-09-14), so the park pose
  and the extents cycle stay clear of the plane. **No tool enforces the rule yet**; a
  geometric check before every goal is the first job of the collision-awareness work.
- **Camera:** on the arm's left, looking side-on, mounted in portrait. The raw frame is
  **not mirrored**: `software/snap.py` rotates it 90° counter-clockwise and nothing else,
  giving an upright view with the arm's front (free air, over the black floor mat) on the
  **left** and the desk behind the base on the **right**. Established 2026-09-14 from the
  hand-set zero pose, whose forearm points forward by definition; an earlier guess that the
  frame was mirrored (and a flip added on it) was wrong and is reverted. Do not take the
  floor mat for the desk: the desk is the furniture behind the base. Auto-exposure blows out against the garage
  roof; manual exposure 40 (V4L2 absolute units) gives a usable frame in daytime — the
  garage's light swings widely, so expect to retune
  ([wk-robotics `common.md` → Environment](../../../docs/common.md#environment)).
- **Supply:** Eventek KPS3010D bench supply at 12.0 V, above.

