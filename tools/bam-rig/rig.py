# SPDX-License-Identifier: CERN-OHL-S-2.0
"""BAM identification rig for the 12 V Feetech STS3215 (family tooling).

Parametric build123d model of a pendulum test bench in the form Rhoban's BAM
asks for (bam/docs/identification/setup.rst): a bracket that holds the servo
rigidly, rigid arms of two lengths, a load seat, and +/-90 degrees of clear
swing about the hanging position. Run it:

    uv run python rig.py            # builds, checks, exports build/*.stl, prints the parts table

Frame (the koala-bot servo frame, koala-bot/hardware/src/koala_hardware/servo_iface.py):
X = output axis (+X toward the drive horn, "Front"), Y = case width ("Sides"),
Z = case length with the servo's Bottom at Z=0 and the output axis at Z=AXIS_Z.
In the rig the servo LIES ON A SIDE: -Y is down, the bench top is the plane
Y = -PLATE_Y1 and the bench edge is the plane X = 0, with the drive side and
the arm hanging beyond it. Every part is exported in its print orientation
with +Z up and its lowest face at Z = 0.

Provenance tags follow koala-bot params.py: [STEP] [SPEC] [MEASURED date]
[SUPPLIED date] [DESIGN] [VERIFY] (best available, confirm on the part) and
[GUESS] (chosen here without a source; confirm before relying on it).
"""
from __future__ import annotations
import argparse
import json
import math
import pathlib
import sys

import numpy as np
import trimesh
from build123d import (Align, Box, Cylinder, Face, Line, Part, Plane, Polygon, Pos,
                       RectangleRounded, Rot, ThreePointArc, extrude, export_stl, make_face)

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"

# --- STS3215 case and horn: COPIED from koala-bot, which is canonical -------
# Source: koala-bot/hardware/src/koala_hardware/params.py (constant names in
# comments) and servo_iface.py (saddle(), case_boxes(), socket_reference()).
# If koala-bot changes a value, change it here too: check_koala() compares
# every one against that file when koala-bot is checked out beside wk-robotics.
CASE_X = 34.9          # SOCKET_CASE_X [STEP] pocket across the output axis (calipers ~34.8)
CASE_Y = 24.7          # SOCKET_CASE_Y [STEP] case width, Side to Side
CASE_L = 45.23         # SOCKET_CASE_L [SPEC] case length, Bottom to Top
SERVO_AXIS_X = 12.5    # SERVO_AXIS_X [SPEC] output axis from the case length centre
AXIS_Z = CASE_L / 2 + SERVO_AXIS_X   # SOCKET_AXIS_Z = 35.115, Bottom to output axis
EAR_X = 31.8           # SOCKET_EAR_X [MEASURED 2026-09-08] faces carrying the M2 lug holes
HORN_SEAT_X = 28.8     # SOCKET_HORN_SEAT_X [MEASURED 2026-09-08] faces the horns sit on
SEAT_OFFSET = 0.5      # SOCKET_SEAT_OFFSET [MEASURED 2026-09-08] seat mid-plane is +0.5 toward the drive side
IDLER_T = 3.1          # SOCKET_IDLER_T [MEASURED 2026-09-08]
IDLER_FACE = SEAT_OFFSET - (HORN_SEAT_X / 2 + IDLER_T)   # SOCKET_IDLER_FACE = -17.0
HORN_SPAN = 36.4       # SOCKET_HORN_SPAN [MEASURED 2026-09-08] drive horn outer face to idler outer face
DRIVE_FACE = IDLER_FACE + HORN_SPAN                      # SOCKET_DRIVE_FACE = 19.4, the arm's contact plane
HORN_DIA = 20.0        # SOCKET_HORN_DIA [STEP]
DRIVE_SQ = 9.9         # SERVO_DRIVE_SQ [STEP] horn hole pattern, tapped M3 (koala test-log 2026-09-08 row 2)
HORN_SCREW_HEAD_DIA = 5.2   # [SUPPLIED 2026-09-08] M3x6 pan head in the Waveshare box
HORN_SCREW_HEAD_H = 2.0     # [SUPPLIED 2026-09-08]
IDLER_BOSS_DIA = 8.0        # SOCKET_BOSS_DIA [VERIFY]
IDLER_BOSS_PROUD = 0.7      # SOCKET_IDLER_BOSS_PROUD [MEASURED 2026-09-08]
REGION_Z = (5.3, 18.8)      # SOCKET_REGION_Z [MEASURED 2026-09-08 Back] ear|widest, widest|seat
DRIVE_PAD_TOP = 25.55       # SOCKET_DRIVE_PAD_TOP [STEP envelope]
DRIVE_SLOT_Y = 14.0         # SOCKET_DRIVE_SLOT_Y [STEP 2026-09-11] SO-101 Upper_arm recess widths
IDLER_SLOT_Y = 18.5         # SOCKET_IDLER_SLOT_Y
IDLER_SLOT_Z = 5.0          # SOCKET_IDLER_SLOT_Z
LUG_BACK_Z = 2.25           # SOCKET_LUG_BACK_Z [STEP] SO-101 printed holes
LUG_DRIVE_Z = 5.8           # SOCKET_LUG_DRIVE_Z [STEP]
LUG_Y = 10.25               # SOCKET_LUG_Y [STEP][SPEC]
M2_CLEAR = 2.0              # SOCKET_M2_CLEAR [STEP] print clearance for the supplied M2x5 self-tappers
M2_SEAT = 2.2               # SOCKET_M2_SEAT [STEP] plastic under the M2 head
M2_HEAD = 4.0               # SOCKET_M2_HEAD [VERIFY] head pocket
# SO-101 socket, the fit that is proven on this printer:
SOCKET_CLEAR = 0.0          # SOCKET_CLEAR [MEASURED 2026-09-07] SO-101 fits PLA+/PETG at zero clearance
WALL = 5.0                  # SOCKET_WALL [DESIGN] SO-101 nominal >= 4.8
DEPTH = 17.0                # SOCKET_DEPTH [STEP] SO-101 rear-case capture depth
SHELF = 5.0                 # SOCKET_SHELF [DESIGN] floor under the servo's Bottom
CLEAR_HOLE_M3 = 3.4         # CLEAR_HOLE_M3 [MEASURED 2026-09-01] coupon: 3.4 slides free
HEAD_CLEAR = 6.4            # SOCKET_HEAD_CLEAR [DESIGN DEC-43] pocket for the pan head
WEB_T = 3.5                 # SOCKET_PLATE_T [STEP] plastic under the horn screw heads: M3x6 leaves 2.5 mm in the horn

# --- Rig choices [DESIGN] unless tagged ------------------------------------
ARM_LENGTHS_MM = (100.0, 150.0)   # axis to load-bolt axis; BAM `length` = 0.10 / 0.15 m (docs/common.md)
ARM_W = 25.0        # bar width, in the swing plane; also the hub pad diameter
ARM_T = 6.0         # bar thickness along the output axis
ARM_CLEAR = 2.0     # bar inner face beyond the bracket's drive wall (the wall the arm sweeps past at -90 deg)
PAD_R = ARM_W / 2   # hub pad radius about the output axis; must stay under WALL_REACH (checked)
ARM_END = ARM_W / 2 # material beyond the load-bolt axis and beyond the output axis
LOAD_BOLT_DIA = 8.4 # [GUESS] M8 clearance in print; koala measured M3 at nominal+0.4, this is nominal+0.4 too
HEAD_RELIEF_DIA = HORN_SCREW_HEAD_DIA + 0.6   # koala clevis_plate(): pan-head relief
HEAD_RELIEF_H = HORN_SCREW_HEAD_H + 0.4
PLATE_T = 6.0       # bench plate thickness (vertical in print)
PLATE_REACH = 70.0  # bench plate inboard of the bench edge
PLATE_Z = (-SHELF, 50.0)   # plate extent along the case axis; longer than the saddle for clamp room
LIP_T, LIP_H = 6.0, 15.0   # rib hooking over the bench edge at X = 0
RIB = 6.0           # 45-degree prism at the plate / back-wall junction
PLATE_HOLE_DIA = 5.0       # [GUESS] for M4 or No.8 wood screws; a G-clamp works without them
PLATE_HOLES = tuple((x, z) for x in (-40.0, -75.0) for z in (8.0, 37.0))   # (X, Z) on the plate
POT_OD, POT_H, POT_WALL, POT_FLOOR = 70.0, 50.0, 2.5, 3.0   # load pot
LID_T, LID_SPIGOT_H, LID_SPIGOT_CLEAR = 3.0, 3.0, 0.3
DENSITY_G_CM3 = 1.24   # [VERIFY] generic PLA; eSUN PLA+ not measured. Print at 100 % infill; the scale wins.
OVERHANG_DEG = 45.0    # self-support limit, as koala printability.py (a heuristic)
BED_MM = 200.0         # docs/common.md: every part <= 200 x 200 mm

WALL_OUT = CASE_X / 2 + SOCKET_CLEAR + WALL      # 22.45, drive wall outer face
WALL_REACH = AXIS_Z - DEPTH                      # 18.1, nearest bracket point to the output axis
ARM_X0 = WALL_OUT + ARM_CLEAR                    # 24.45, bar inner face
ARM_X1 = ARM_X0 + ARM_T                          # 30.45, bar outer face; the load sits beyond
PLATE_Y1 = CASE_Y / 2 + 2.0                      # 14.35, saddle outer half-width = plate top (koala saddle: y += 2)
BENCH_TOP_Y = -(PLATE_Y1 + PLATE_T)              # the bench surface, in the rig frame


# --- primitives ---------------------------------------------------------------
def box(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def teardrop(d: float) -> Face:
    """Circle of diameter d with a 45-degree roof toward sketch +Y: a horizontal
    hole that prints without support. One wire (two lines and an arc through
    the tangent points), not a boolean: tangent unions leave OCC slivers."""
    r = d / 2
    s = r * math.sqrt(0.5)
    apex = (0, r * math.sqrt(2))
    return make_face(Line((-s, s), apex) + Line(apex, (s, s)) + ThreePointArc((s, s), (0, -r), (-s, s)))


def x_hole(x0, x1, y, z, d) -> Part:
    """Teardrop hole along +X from x0 to x1, roof toward +Z (print up)."""
    solid = extrude(Rot(Z=90) * teardrop(d), amount=x1 - x0)   # apex -> sketch -X
    return Pos(x0, y, z) * Rot(Y=90) * solid                     # sketch -X -> +Z, extrusion -> +X


def y_hole(x, y0, y1, z, d) -> Part:
    """Teardrop hole along +Y from y0 to y1, roof toward +Z."""
    solid = extrude(Rot(Z=180) * teardrop(d), amount=y1 - y0)  # apex -> sketch -Y
    return Pos(x, y0, z) * Rot(X=-90) * solid                    # sketch -Y -> +Z, extrusion -> +Y


def z_cyl(x, y, z0, z1, d) -> Part:
    return Pos(x, y, z0) * Cylinder(d / 2, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def _check_primitives():
    h = x_hole(0, 10, 0, 0, 4)
    bb = h.bounding_box()
    assert abs(bb.min.X) < 1e-6 and abs(bb.max.X - 10) < 1e-6, bb
    assert abs(bb.max.Z - 2 * math.sqrt(2)) < 1e-6 and abs(bb.min.Z + 2) < 1e-6, bb
    h = y_hole(0, 0, 10, 0, 4)
    bb = h.bounding_box()
    assert abs(bb.min.Y) < 1e-6 and abs(bb.max.Y - 10) < 1e-6, bb
    assert abs(bb.max.Z - 2 * math.sqrt(2)) < 1e-6 and abs(bb.min.Z + 2) < 1e-6, bb


# --- the servo, as an obstacle (koala servo_iface.case_boxes + socket_reference) --
def ear_face(side: str) -> float:
    return SEAT_OFFSET + (1 if side == "drive" else -1) * EAR_X / 2


def servo_obstacle() -> Part:
    """Conservative case envelope plus both horns and the drive centre screw head."""
    y, off = CASE_Y / 2, SEAT_OFFSET
    seat_f, seat_b = off + HORN_SEAT_X / 2, off - HORN_SEAT_X / 2
    ear_f, ear_b = ear_face("drive"), ear_face("idler")
    wide, (za, zb) = CASE_X / 2, REGION_Z
    front, back = DRIVE_SLOT_Y / 2, IDLER_SLOT_Y / 2
    part = box(ear_b, ear_f, -y, y, 0, zb)
    part += box(seat_f, wide, -front, front, 0, DRIVE_PAD_TOP)
    part += box(-wide, ear_b, -back, back, za, zb)
    part += box(seat_b, seat_f, -y, y, zb, CASE_L)
    part += Pos(seat_f, 0, AXIS_Z) * Rot(Y=90) * Cylinder(HORN_DIA / 2, DRIVE_FACE - seat_f, align=(Align.CENTER, Align.CENTER, Align.MIN))
    part += Pos(DRIVE_FACE, 0, AXIS_Z) * Rot(Y=90) * Cylinder(HORN_SCREW_HEAD_DIA / 2, HORN_SCREW_HEAD_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    part += Pos(IDLER_FACE, 0, AXIS_Z) * Rot(Y=90) * Cylinder(HORN_DIA / 2, seat_b - IDLER_FACE, align=(Align.CENTER, Align.CENTER, Align.MIN))
    part += Pos(IDLER_FACE - IDLER_BOSS_PROUD, 0, AXIS_Z) * Rot(Y=90) * Cylinder(IDLER_BOSS_DIA / 2, IDLER_BOSS_PROUD, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return part


# --- parts ---------------------------------------------------------------------
def saddle() -> Part:
    """koala-bot servo_iface.saddle() re-expressed: the SO-101 four-ear pocket,
    17 mm capture, unequal drive/idler recesses, 2 mm Side returns, rounded
    outline; M2 holes and head pockets as teardrops so the walls print
    without support. Same datums, same fit."""
    x = CASE_X / 2 + SOCKET_CLEAR
    y = PLATE_Y1
    part = box(-x - WALL, x + WALL, -y, y, -SHELF, 0)
    for side, sign in (("drive", 1), ("idler", -1)):
        a, b = (x, x + WALL) if sign == 1 else (-x - WALL, -x)
        wall = box(a, b, -y, y, -SHELF, DEPTH)
        face = ear_face(side)
        edge = (DRIVE_SLOT_Y if side == "drive" else IDLER_SLOT_Y) / 2
        for sy in (-1, 1):
            ya, yb = (edge, y) if sy == 1 else (-y, -edge)
            lo, hi = (face, x + WALL) if sign == 1 else (-x - WALL, face)
            wall += box(lo, hi, ya, yb, 0, DEPTH)
        if side == "idler":
            wall += box(-x - WALL, face, -y, y, 0, IDLER_SLOT_Z)
        part += wall
    for sign in (-1, 1):
        a, b = (CASE_Y / 2, y) if sign == 1 else (-y, -CASE_Y / 2)
        part += box(-x, x, a, b, -SHELF, DEPTH)
    outside = Pos(0, 0, -SHELF) * extrude(RectangleRounded(2 * (x + WALL), 2 * y, 2), amount=DEPTH + SHELF)
    return part & outside


def ear_cuts() -> list[Part]:
    """The four M2 self-tapper holes: through-bore of the screw's own wall, and
    a head pocket from the outer face to the 2.2 mm seat, both teardrop (apex
    +Z). koala cuts the bore through both walls; here it stops at the pocket
    face, because across the pocket it would graze the opposite wall's slot
    edge and leave the mesh non-manifold."""
    cuts = []
    for side in ("drive", "idler"):
        face = ear_face(side)
        z = LUG_DRIVE_Z if side == "drive" else LUG_BACK_Z
        for y in (-LUG_Y, LUG_Y):
            if side == "drive":
                cuts.append(x_hole(face - 1, 40, y, z, M2_CLEAR))
            else:
                cuts.append(x_hole(-40, face + 1, y, z, M2_CLEAR))
            if side == "drive":
                cuts.append(x_hole(face + M2_SEAT, 40, y, z, M2_HEAD))
            else:
                cuts.append(x_hole(-40, face - M2_SEAT, y, z, M2_HEAD))
    return cuts


def bracket() -> Part:
    """Saddle on a bench plate. Print as modelled: saddle floor on the bed,
    pocket opening up, plate standing on its long edge, lip and rib run the
    full print height so nothing overhangs."""
    part = saddle()
    x_out = WALL_OUT
    z0, z1 = PLATE_Z
    part += box(-PLATE_REACH, x_out, -PLATE_Y1 - PLATE_T, -PLATE_Y1, z0, z1)      # plate
    part += box(-LIP_T, 0, -PLATE_Y1 - PLATE_T - LIP_H, -PLATE_Y1 - PLATE_T, z0, z1)  # bench-edge lip
    rib = extrude(Polygon((-x_out, -PLATE_Y1), (-x_out - RIB, -PLATE_Y1), (-x_out, -PLATE_Y1 + RIB), align=None), amount=DEPTH + SHELF, dir=(0, 0, 1))
    part += Pos(0, 0, -SHELF) * rib                                                  # 45-degree rib, back wall to plate
    for cut in ear_cuts():
        part -= cut
    for x, z in PLATE_HOLES:
        part -= y_hole(x, -PLATE_Y1 - PLATE_T - 1, -PLATE_Y1 + 1, z, PLATE_HOLE_DIA)
    return part


def pad_outline() -> Face:
    """Hub pad in the swing plane (sketch X = along the bar, sketch Y = bar width):
    a disc of PAD_R whose lower rim is replaced by 45-degree flats down to the
    bar's edge, so that edge is the bed in the on-edge print."""
    r = PAD_R
    s = r * math.sqrt(0.5)
    w = s - (r - s)                       # where the 45-degree tangents meet the bar edge
    return make_face(Line((-w, -r), (w, -r)) + Line((w, -r), (s, -s))
                     + ThreePointArc((s, -s), (0, r), (-s, -s)) + Line((-s, -s), (-w, -r)))


def arm(length_mm: float) -> Part:
    """Pendulum arm, modelled hanging (-Y) from the output axis in the rig frame.

    Hub pad on the horn face (X = DRIVE_FACE), 3.5 mm web under the four M3x6
    pan heads, head pockets open on the outer face; the bar runs in a plane
    ARM_CLEAR beyond the bracket's drive wall so the -90 degree position clears
    it. Load bolt axis parallel to the output axis at `length_mm`.
    Printed on edge: the bar's -Z edge (rig frame) is the bed, so the swing
    plane is vertical and every hole is a horizontal teardrop."""
    L = length_mm
    half = ARM_W / 2
    bar = box(ARM_X0, ARM_X1, -(L + ARM_END), ARM_END, AXIS_Z - half, AXIS_Z + half)
    # pad_outline() is drawn in a plane whose sketch Y must become rig Z (bar width) and
    # sketch X rig -Y (along the bar): place it on the YZ plane and extrude along +X.
    pad = extrude(Plane.YZ * pad_outline(), amount=ARM_X0 - DRIVE_FACE, dir=(1, 0, 0))
    pad = Pos(DRIVE_FACE, 0, AXIS_Z) * pad
    part = bar + pad
    part -= x_hole(DRIVE_FACE - 1, DRIVE_FACE + HEAD_RELIEF_H, 0, AXIS_Z, HEAD_RELIEF_DIA)  # drive centre pan head
    for a in (-DRIVE_SQ / 2, DRIVE_SQ / 2):
        for b in (-DRIVE_SQ / 2, DRIVE_SQ / 2):
            part -= x_hole(DRIVE_FACE - 1, ARM_X1 + 1, a, AXIS_Z + b, CLEAR_HOLE_M3)
            part -= x_hole(DRIVE_FACE + WEB_T, ARM_X1 + 1, a, AXIS_Z + b, HEAD_CLEAR)
    part -= x_hole(ARM_X0 - 1, ARM_X1 + 1, -L, AXIS_Z, LOAD_BOLT_DIA)
    return part


def pot() -> Part:
    """Load pot: open cup with the M8 bolt through its floor. Fill with anything
    dense and loose (lead or steel shot, sand, loose steel hardware, coins),
    fit the lid, clamp with the nut, weigh the whole thing. Print floor down."""
    cup = z_cyl(0, 0, 0, POT_H, POT_OD)
    cup -= z_cyl(0, 0, POT_FLOOR, POT_H + 1, POT_OD - 2 * POT_WALL)
    cup -= z_cyl(0, 0, -1, POT_FLOOR + 1, LOAD_BOLT_DIA)
    return cup


def lid() -> Part:
    """Pot lid: disc with a locating spigot. Print disc down, spigot up."""
    part = z_cyl(0, 0, 0, LID_T, POT_OD)
    part += z_cyl(0, 0, LID_T, LID_T + LID_SPIGOT_H, POT_OD - 2 * POT_WALL - 2 * LID_SPIGOT_CLEAR)
    part -= z_cyl(0, 0, -1, LID_T + LID_SPIGOT_H + 1, LOAD_BOLT_DIA)
    return part


# --- checks -----------------------------------------------------------------------
def bench_obstacle() -> Part:
    """The bench: everything inboard of the edge and below its top surface."""
    return box(-400, 0, -400, BENCH_TOP_Y, -200, 300)


def swing(part: Part, deg: float) -> Part:
    """Rotate a part about the output axis (the line Y=0, Z=AXIS_Z, along X)."""
    return Pos(0, 0, AXIS_Z) * Rot(X=deg) * Pos(0, 0, -AXIS_Z) * part


def load_stack(length_mm: float) -> Part:
    """What hangs on the load bolt at the arm's tip: bolt head inboard, pot(s)
    and lid outboard, modelled as envelopes for the clearance sweep."""
    head = Pos(ARM_X0 - 5.3, 0, 0) * Rot(Y=90) * Cylinder(13.0 / math.sqrt(3), 5.3, align=(Align.CENTER, Align.CENTER, Align.MIN))  # M8 hex head [STD-ish]
    pots = Pos(ARM_X1, 0, 0) * Rot(Y=90) * Cylinder(POT_OD / 2, 2 * POT_H + LID_T + 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(0, -length_mm, AXIS_Z) * (head + pots)


def clearance_sweep(bracket_part: Part, length_mm: float, step: float = 10.0) -> float:
    """Largest intersection volume (mm^3) of arm + load with bracket, servo and
    bench over -90..+90 degrees. Must be 0."""
    obstacles = bracket_part + servo_obstacle() + bench_obstacle()
    moving = arm(length_mm) + load_stack(length_mm)
    worst = 0.0
    angles = np.arange(-90.0, 90.0 + step / 2, step)
    for deg in angles:
        hit = swing(moving, float(deg)) & obstacles
        v = hit.volume if hit.solids() else 0.0
        worst = max(worst, v)
    return worst


def export_mesh(part: Part, path: pathlib.Path) -> trimesh.Trimesh:
    """koala-bot meshing.export_mesh, condensed: export, merge round-off
    vertices, drop collapsed triangles, refuse anything not closed."""
    export_stl(part, str(path))
    raw = trimesh.load(path, force="mesh", process=False)
    mesh = trimesh.load(path, force="mesh")
    merged = len(np.unique(raw.vertices, axis=0)) != len(mesh.vertices)
    keep = np.all(np.diff(np.sort(mesh.faces, axis=1), axis=1) != 0, axis=1)
    if not np.all(keep):
        mesh.update_faces(keep)
        mesh.remove_unreferenced_vertices()
    if not mesh.is_watertight or mesh.volume <= 0:
        raise ValueError(f"{path}: STL is not a closed positive-volume mesh")
    if merged or not np.all(keep):
        mesh.export(str(path), file_type="stl")
    return mesh


def overhang_area(mesh: trimesh.Trimesh, tol_deg: float = 0.5) -> float:
    """Area of down-facing faces steeper than the self-support limit that are
    not on the bed (koala printability.metrics). 45-degree teardrop roofs and
    chamfers sit exactly on the limit, hence the tolerance."""
    n = mesh.face_normals
    face_max_z = mesh.triangles[:, :, 2].max(axis=1)
    on_bed = (face_max_z <= mesh.bounds[0][2] + 0.05) & (n[:, 2] < -0.9)
    limit = -math.cos(math.radians(OVERHANG_DEG - tol_deg))   # flag only faces steeper than 44.5 deg
    return float(mesh.area_faces[(n[:, 2] < limit) & ~on_bed].sum())


def to_bed(part: Part) -> Part:
    bb = part.bounding_box()
    return Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * part


def arm_inertia_from_mesh(mesh: trimesh.Trimesh, length_mm: float) -> dict:
    """Mesh in rig frame (hanging along -Y, axis through Y=0, Z=AXIS_Z)."""
    rho = DENSITY_G_CM3 * 1e-3 * 1e-3   # kg per mm^3
    m = mesh.volume * rho
    I_com = mesh.moment_inertia * rho    # about CoM, kg*mm^2, mesh frame axes
    c = mesh.center_mass
    d2 = (c[1] - 0.0) ** 2 + (c[2] - AXIS_Z) ** 2      # CoM distance^2 from the X axis line
    I_axis = (I_com[0][0] + m * d2) * 1e-6              # kg*m^2 about the output axis
    L = length_mm * 1e-3
    x_com = -c[1] * 1e-3
    return dict(mass_kg=m, x_com_m=x_com, I_axis_kgm2=I_axis,
                arm_mass_gravity_equiv_kg=2 * m * x_com / L,
                arm_mass_inertia_equiv_kg=3 * I_axis / L ** 2)


KOALA_PARAMS = HERE.parents[2] / "koala-bot" / "hardware" / "src" / "koala_hardware" / "params.py"
KOALA_NAMES = {   # this file's name -> koala params.py name
    "CASE_X": "SOCKET_CASE_X", "CASE_Y": "SOCKET_CASE_Y", "CASE_L": "SOCKET_CASE_L", "SERVO_AXIS_X": "SERVO_AXIS_X",
    "AXIS_Z": "SOCKET_AXIS_Z", "EAR_X": "SOCKET_EAR_X", "HORN_SEAT_X": "SOCKET_HORN_SEAT_X",
    "SEAT_OFFSET": "SOCKET_SEAT_OFFSET", "IDLER_T": "SOCKET_IDLER_T", "IDLER_FACE": "SOCKET_IDLER_FACE",
    "HORN_SPAN": "SOCKET_HORN_SPAN", "DRIVE_FACE": "SOCKET_DRIVE_FACE", "HORN_DIA": "SOCKET_HORN_DIA",
    "DRIVE_SQ": "SERVO_DRIVE_SQ", "HORN_SCREW_HEAD_DIA": "HORN_SCREW_HEAD_DIA", "HORN_SCREW_HEAD_H": "HORN_SCREW_HEAD_H",
    "IDLER_BOSS_DIA": "SOCKET_BOSS_DIA", "IDLER_BOSS_PROUD": "SOCKET_IDLER_BOSS_PROUD", "REGION_Z": "SOCKET_REGION_Z",
    "DRIVE_PAD_TOP": "SOCKET_DRIVE_PAD_TOP", "DRIVE_SLOT_Y": "SOCKET_DRIVE_SLOT_Y", "IDLER_SLOT_Y": "SOCKET_IDLER_SLOT_Y",
    "IDLER_SLOT_Z": "SOCKET_IDLER_SLOT_Z", "LUG_BACK_Z": "SOCKET_LUG_BACK_Z", "LUG_DRIVE_Z": "SOCKET_LUG_DRIVE_Z",
    "LUG_Y": "SOCKET_LUG_Y", "M2_CLEAR": "SOCKET_M2_CLEAR", "M2_SEAT": "SOCKET_M2_SEAT", "M2_HEAD": "SOCKET_M2_HEAD",
    "SOCKET_CLEAR": "SOCKET_CLEAR", "WALL": "SOCKET_WALL", "DEPTH": "SOCKET_DEPTH", "SHELF": "SOCKET_SHELF",
    "CLEAR_HOLE_M3": "CLEAR_HOLE_M3", "HEAD_CLEAR": "SOCKET_HEAD_CLEAR", "WEB_T": "SOCKET_PLATE_T",
}


def check_koala() -> str:
    """Compare every copied constant with koala-bot's params.py if that repo is
    checked out beside wk-robotics (params.py imports nothing, so it loads
    standalone). Raises on any mismatch: koala is canonical."""
    if not KOALA_PARAMS.exists():
        return f"koala-bot params.py not found at {KOALA_PARAMS}; copied constants unchecked this run"
    import importlib.util
    spec = importlib.util.spec_from_file_location("koala_params", KOALA_PARAMS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    bad = []
    for mine, theirs in KOALA_NAMES.items():
        a, b = globals()[mine], getattr(mod, theirs)
        if not np.allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float)):
            bad.append(f"{mine}={a} vs koala {theirs}={b}")
    if bad:
        raise SystemExit("copied constants drifted from koala-bot params.py:\n  " + "\n  ".join(bad))
    return f"{len(KOALA_NAMES)} copied constants match koala-bot params.py ({KOALA_PARAMS})"


# --- build ----------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-sweep", action="store_true", help="skip the +/-90 degree clearance sweep")
    ap.add_argument("--sweep-step", type=float, default=10.0, help="degrees between sweep samples")
    args = ap.parse_args(argv)
    _check_primitives()
    BUILD.mkdir(exist_ok=True)

    b = bracket()
    parts = [
        ("bracket", 1, b, "as exported: saddle floor on the bed, pocket up, plate on its long edge; lip and rib to the bed",
         "PLA+ or PETG"),
    ]
    for L in ARM_LENGTHS_MM:
        parts.append((f"arm_{int(L)}", 1, arm(L),
                      "as exported: on edge, bar's long edge on the bed, horn face vertical; all holes are teardrops", "PLA+"))
    parts.append(("pot", 2, pot(), "as exported: floor on the bed, open end up", "PLA+"))
    parts.append(("lid", 2, lid(), "as exported: disc on the bed, spigot up", "PLA+"))

    rows, failures, report = [], [], {"parts": {}, "arms": {}, "sweep_mm3": {}}
    for name, count, part, orient, material in parts:
        assert part.is_valid, name
        assert len(part.solids()) == 1, f"{name}: {len(part.solids())} solids"
        placed = to_bed(part)
        path = BUILD / f"{name}.stl"
        mesh = export_mesh(placed, path)
        size = mesh.bounds[1] - mesh.bounds[0]
        oh = overhang_area(mesh)
        fits = size[0] <= BED_MM and size[1] <= BED_MM
        support_free = oh < 1.0
        if not fits:
            failures.append(f"{name}: {size[0]:.0f} x {size[1]:.0f} mm exceeds {BED_MM:.0f} mm bed")
        if not support_free:
            failures.append(f"{name}: {oh:.0f} mm^2 of unsupported overhang in its print orientation")
        rows.append((name, count, orient, "yes" if support_free else f"NO ({oh:.0f} mm^2)",
                     f"{size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f}", mesh.volume * 1e-3, material))
        report["parts"][name] = dict(count=count, orientation=orient, support_free=support_free,
                                     overhang_mm2=oh, bbox_mm=[float(s) for s in size],
                                     volume_cm3=mesh.volume * 1e-3, mass_est_g=mesh.volume * 1e-3 * DENSITY_G_CM3,
                                     watertight=True, material=material)

    # Arm mass properties, in the rig frame (not the bed-placed mesh).
    for L in ARM_LENGTHS_MM:
        tmp = BUILD / f"_arm_{int(L)}_rigframe.stl"
        mesh = export_mesh(arm(L), tmp)
        tmp.unlink()
        report["arms"][int(L)] = arm_inertia_from_mesh(mesh, L)

    # Geometry invariants the design rests on.
    print(check_koala())
    fit = servo_obstacle() & b
    assert not fit.solids() or fit.volume < 1e-6, f"servo envelope intersects the bracket pocket by {fit.volume:.1f} mm^3"
    assert PAD_R * 1.1 < WALL_REACH, "hub pad would sweep into the bracket's drive wall"
    assert ARM_X0 - 5.3 > 0 + 1.0, "M8 bolt head would reach the bench edge"
    if not args.no_sweep:
        for L in ARM_LENGTHS_MM:
            v = clearance_sweep(b, L, args.sweep_step)
            report["sweep_mm3"][int(L)] = v
            if v > 1e-6:
                failures.append(f"arm_{int(L)}: swing intersects bracket/servo/bench by {v:.1f} mm^3")

    (BUILD / "report.json").write_text(json.dumps(report, indent=2) + "\n")

    print("Printed parts (print orientation = as exported, +Z up)")
    print("| part | count | orientation | support-free | bbox X x Y x Z (mm) | volume (cm3) | material |")
    print("|---|---|---|---|---|---|---|")
    for name, count, orient, sf, bbox, vol, material in rows:
        print(f"| {name} | {count} | {orient} | {sf} | {bbox} | {vol:.1f} | {material} |")
    print()
    print(f"Modelled arm properties at {DENSITY_G_CM3} g/cm3, 100 % infill (estimates; the scale wins):")
    for L, d in report["arms"].items():
        print(f"  arm_{L}: mass {d['mass_kg']*1e3:.1f} g, CoM {d['x_com_m']*1e3:.1f} mm below the axis, "
              f"I_axis {d['I_axis_kgm2']*1e6:.0f} g*cm2 -> BAM arm_mass: gravity-equivalent "
              f"{d['arm_mass_gravity_equiv_kg']*1e3:.1f} g, inertia-equivalent {d['arm_mass_inertia_equiv_kg']*1e3:.1f} g")
    if not args.no_sweep:
        print("Clearance sweep -90..+90 deg (arm + load vs bracket, servo, bench), worst intersection:",
              {k: f"{v:.3g} mm3" for k, v in report["sweep_mm3"].items()})
    print(f"Datums: horn face X={DRIVE_FACE}, bar X={ARM_X0:.2f}..{ARM_X1:.2f}, drive wall outer X={WALL_OUT}, "
          f"nearest bracket point to axis {WALL_REACH:.1f} mm, axis {AXIS_Z + PLATE_Y1 + PLATE_T:.1f} mm above the bench top")
    if failures:
        print("FAIL:\n  " + "\n  ".join(failures))
        return 1
    print(f"PASS: {len(rows)} parts, all single solids, watertight STLs in {BUILD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
