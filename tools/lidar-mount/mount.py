"""RPLIDAR C1 mount: a HAT-outline plate on the Raspberry Pi hole pattern, with four printed
standoffs that raise the lidar and take M2.5x8 screws from below (wk-hexapod DEC-30).

    uv run python mount.py          # checks, then STL to build/

Frame: X, Y in the plate; Z up. Origin at the centre of the Pi hole pattern; the plate's top
face is Z = PLATE_T. The Pi's USB/Ethernet edge is +X (HAT convention: holes 3.5 mm in from
the -X and +-Y edges of a 65 x 56 board). Every dimension has its source beside it.
"""
import json
import pathlib
from build123d import *   # noqa: F403

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"

# ---- Raspberry Pi / HAT (Raspberry Pi HAT+ specification, mechanical) -------------------------
PI_HOLE_X, PI_HOLE_Y = 58.0, 49.0     # [SPEC] Pi mounting-hole pitch
HAT_L, HAT_W = 65.0, 56.0             # [SPEC] HAT board outline
HAT_R = 3.5                           # [SPEC] HAT corner radius (holes are 3.5 mm in from three edges)
M25_CLEAR = 2.75                      # [CHOICE] M2.5 clearance in printed PETG; 2.7 nominal "close", +0.05 for print shrink
PLATE_T = 3.0                         # [OWNER 2026-09-26]

# ---- RPLIDAR C1 (datasheet v1.1 p.18, read 2026-09-23) ----------------------------------------
C1_HOLE = 43.0                        # [DATASHEET] 4 x M2.5 on a 43 x 43 square, tapped in the base
C1_TAP_MAX = 4.0                      # [DATASHEET] "depth of 4*M2.5 screws in the bottom should be no longer than 4mm"
C1_BASE = 55.6                        # [DATASHEET] base footprint, square
C1_CABLE_SIDE = -1                    # [DATASHEET drawing] cable leaves the base on the side marked with the arrow; here -Y

# ---- Standoffs and screws ---------------------------------------------------------------------
STANDOFF_H = 10.0                     # [OWNER 2026-09-26] lidar base 10 mm above the plate top
STANDOFF_D = 9.0                     # [CHOICE] boss diameter; 1.9 mm wall around the counterbore
SCREW_L = 8.0                         # [OWNER] M2.5 x 8 from below
HEAD_D, HEAD_H = 4.5, 2.5             # [ISO 4762] M2.5 socket head cap: d_k 4.5, k 2.5
CBORE_D = 5.2                         # [CHOICE] head clearance (a pan head, 5.0, also fits)
ENGAGE = 3.5                          # [CHOICE] thread engagement in the lidar, <= C1_TAP_MAX
THROUGH = SCREW_L - ENGAGE            # material between screw head seat and lidar base = 4.5 mm
STACK = PLATE_T + STANDOFF_H          # 13 mm
CBORE_DEPTH = STACK - THROUGH         # 8.5 mm, from the plate's underside

# ---- Cable slot --------------------------------------------------------------------------------
SLOT_W, SLOT_L = 8.0, 14.0            # [CHOICE] for the C1's 4-wire lead and JST-style plug (~8 x 5 mm, unverified)
SLOT_Y = C1_CABLE_SIDE * (C1_BASE / 2 - 6.0)   # closed slot under the lidar base, cable side; the lead turns down in the 10 mm gap


def checks():
    assert ENGAGE <= C1_TAP_MAX, "screw would bottom in the lidar"
    assert THROUGH >= 3.0, "too little material under the head"
    assert CBORE_DEPTH + HEAD_H < STACK, "counterbore breaks through"
    wall = (STANDOFF_D - CBORE_D) / 2
    assert wall >= 1.2, f"boss wall {wall} mm"
    # Pi holes vs lidar bosses: centre distance must exceed boss radius + Pi hole radius + 1 mm
    import math
    d = min(math.hypot(px - lx, py - ly) for px in (PI_HOLE_X / 2, -PI_HOLE_X / 2) for py in (PI_HOLE_Y / 2, -PI_HOLE_Y / 2)
            for lx in (C1_HOLE / 2, -C1_HOLE / 2) for ly in (C1_HOLE / 2, -C1_HOLE / 2))
    assert d > STANDOFF_D / 2 + M25_CLEAR / 2 + 1.0, f"Pi hole to boss {d:.1f} mm"
    return dict(engage_mm=ENGAGE, through_mm=THROUGH, cbore_depth_mm=CBORE_DEPTH, boss_wall_mm=wall, pi_hole_to_boss_mm=round(d, 2))


def build():
    with BuildPart() as p:
        # plate: HAT outline, holes 3.5 mm in from -X and both Y edges (HAT convention), so the
        # pattern is offset +X of the outline centre by (HAT_L - PI_HOLE_X)/2 - HAT_R = 0
        with BuildSketch():
            RectangleRounded(HAT_L, HAT_W, HAT_R)
        extrude(amount=PLATE_T)
        # lidar standoffs
        with BuildSketch(Plane.XY.offset(PLATE_T)):
            with GridLocations(C1_HOLE, C1_HOLE, 2, 2):
                Circle(STANDOFF_D / 2)
        extrude(amount=STANDOFF_H)
        # Pi mounting holes, M2.5 clearance, through the plate
        with BuildSketch():
            with GridLocations(PI_HOLE_X, PI_HOLE_Y, 2, 2):
                Circle(M25_CLEAR / 2)
        extrude(amount=STACK, mode=Mode.SUBTRACT)
        # lidar screws: through hole up the boss, counterbore from below
        with BuildSketch():
            with GridLocations(C1_HOLE, C1_HOLE, 2, 2):
                Circle(M25_CLEAR / 2)
        extrude(amount=STACK, mode=Mode.SUBTRACT)
        with BuildSketch():
            with GridLocations(C1_HOLE, C1_HOLE, 2, 2):
                Circle(CBORE_D / 2)
        extrude(amount=CBORE_DEPTH, mode=Mode.SUBTRACT)
        # cable slot on the lidar's connector side
        with BuildSketch():
            with Locations((0, SLOT_Y)):
                SlotOverall(SLOT_L, SLOT_W)
        extrude(amount=PLATE_T, mode=Mode.SUBTRACT)
    return p.part


def export(part):
    BUILD.mkdir(exist_ok=True)
    out = BUILD / "lidar_mount.stl"
    export_stl(part, str(out), tolerance=0.02, angular_tolerance=0.1)
    import trimesh
    m = trimesh.load(str(out))
    assert m.is_watertight and m.volume > 0, "STL not watertight"
    bb = m.bounds[1] - m.bounds[0]
    return out, m.volume / 1000.0, bb


if __name__ == "__main__":
    c = checks()
    part = build()
    assert len(part.solids()) == 1, "not one solid"
    out, vol, bb = export(part)
    info = dict(checks=c, volume_cm3=round(vol, 2), bbox_mm=[round(x, 1) for x in bb],
                mass_g_petg_solid=round(vol * 1.27, 1),
                print="plate face down, standoffs up; counterbores print as blind holes from the bed, no supports",
                screws="4 x M2.5 x 8 socket cap from below into the lidar (3.5 mm engagement); 4 x M2.5 into the Pi standoffs from above")
    json.dump(info, open(BUILD / "lidar_mount.json", "w"), indent=1)
    print(json.dumps(info, indent=1))
    print("wrote", out)
