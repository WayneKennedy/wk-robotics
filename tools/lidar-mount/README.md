# lidar-mount — RPLIDAR C1 on the Raspberry Pi hole pattern

The plate from [wk-hexapod DEC-30](https://github.com/WayneKennedy/wk-hexapod/blob/main/docs/decisions.md):
one printed part that carries a Slamtec RPLIDAR C1 above any Pi-carrying robot's existing
standoffs, so one lidar moves between robots. Designed 2026-09-26 to the owner's brief:
HAT-style plate on the Pi holes, M2.5 clearance, 3 mm, rounded corners; printed standoffs
raising the lidar 10 mm, counterbored for M2.5×8 screws from below. **Unprinted.**

```sh
uv sync && uv run python mount.py     # checks, then build/lidar_mount.stl and .json
```

| | |
|---|---|
| Outline | 65 × 56 mm, R3.5 corners — the HAT+ spec board outline; the Pi's 58 × 49 mm pattern sits centred, Ø2.75 clearance |
| Plate | 3 mm |
| Lidar bosses | 4 × Ø9 × 10 mm on the C1's 43 × 43 mm pattern (datasheet v1.1 p. 18) |
| Lidar screws | 4 × **M2.5 × 8 socket cap from below**: Ø5.2 counterbore 8.5 mm deep leaves 4.5 mm under the lidar, so the screw engages **3.5 mm** — inside the datasheet's 4 mm limit. Do not use longer screws |
| Pi screws | 4 × M2.5 from above into the robot's standoffs |
| Cable | 14 × 8 mm closed slot in the plate under the lidar's connector side (−Y); the lead turns down through it in the 10 mm gap |
| Scan plane | plate top + 10 + 29.8 = **39.8 mm** above the plate's top face (C1 datasheet) |
| Mass | 12.2 cm³, ~15.5 g solid PETG |
| Print | plate face down, bosses up; the counterbores are blind holes from the bed. No supports. 100 % infill is cheap at this size and keeps the bosses solid |

**Orientation.** The C1's angular zero is the arrow on its base (the cable side). The plate puts
that side at −Y, with the Pi's USB/Ethernet edge at +X; on each robot the lidar's yaw relative
to `base_link` is whatever this comes to and belongs in that robot's URDF, not here.

**Checks the script makes:** screw engagement ≤ 4 mm, ≥ 3 mm of material under the head,
boss wall ≥ 1.2 mm (1.9), Pi holes clear of the bosses (8.1 mm centre-to-centre), one solid,
watertight STL.

**Labelled choices, unverified on a print:** Ø2.75 clearance in PETG; Ø5.2 counterbore for a
socket or pan head; the slot size against the C1's plug (~8 × 5 mm, not measured).
