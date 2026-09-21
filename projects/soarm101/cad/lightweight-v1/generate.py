#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Reproducible subtractive SO-101 follower prototype. All dimensions in mm.

See README.md for scope, provenance, limitations and reproduction commands.
Upstream CAD is Apache-2.0; this script does not change its coordinate systems.
"""
import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
REVISION = "eecbe3e0a9ebb23e25ad7b2759b03884c6660903"


def box(bounds):
    x0, x1, y0, y1, z0, z1 = bounds
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def rounded_box(bounds, axis, radius):
    return cq.Workplane(obj=box(bounds)).edges("|" + axis).fillet(radius).val()


def designs(experimental_links=False):
    """Explicit removed regions and independently named protected interfaces.

    Keep complete end blocks, not just bolt axes. Protection is applied before
    cutting and its original volume is compared with the exported/reloaded part.
    """
    d = {}
    for name, y in [("Upper_arm_SO101", 0), ("Under_arm_SO101", -44)]:
        d[name] = dict(
            cuts=[
                ([-10, 10, y-5, y+30, -14, 14], "Y", 5),
                ([-25, -15, y+6, y+18, -45, 45], "Z", 4),
                ([17, 49, y+6, y+18, -45, 45], "Z", 5),
            ],
            protected={
                "servo_seat_and_case_screws": [-90, -28, y-10, y+40, -50, 50],
                "horns_bores_and_end_faces": [54, 90, y-10, y+40, -50, 50],
                "cable_clip_and_root": [34, 54, y-5, y+30, -45, -27],
            },
        )
    d["Base_SO101"] = dict(
        cuts=[
            ([19, 40, -5, 23, 6, 52], "Y", 7),
            ([-40, -19, -5, 23, 6, 52], "Y", 7),
        ],
        protected={
            "servo_pocket_and_cable_provisions": [-23, 23, 18, 80, -25, 40],
            "central_base_and_attachment": [-18, 18, -5, 80, -25, 80],
            "lower_mounting_bolts_and_foot": [-65, 65, -5, 25, -25, 3],
            "upper_mounting_bolts": [-45, 45, -5, 25, 54, 80],
        },
    )
    d["Rotation_Pitch_SO101"] = dict(
        cuts=[([-65, -30, 18, 38, -12, 12], "X", 5)],
        protected={
            "lower_horn_and_root": [-70, 5, -5, 15, -30, 30],
            "upper_horn_and_root": [-70, 5, 41, 59, -30, 30],
            "case_attachment": [-70, 5, 59, 90, -30, 30],
        },
    )
    d["WaveShare_Mounting_Plate_SO101"] = dict(
        cuts=[
            ([-11, 11, 12, 18, -2, 10], "Z", 2),
            ([-11, 11, -18, -12, -2, 10], "Z", 2),
            ([12, 21, -7, 7, -2, 10], "Z", 3),
            ([-21, -12, -7, 7, -2, 10], "Z", 3),
        ],
        protected={
            "mounting_boss": [-11, 11, -11, 11, -3, 11],
            "upper_left_screw": [-27, -12, 8, 23, -3, 11],
            "upper_right_screw": [12, 27, 8, 23, -3, 11],
            "lower_left_screw": [-27, -12, -23, -8, -3, 11],
            "lower_right_screw": [12, 27, -23, -8, -3, 11],
        },
    )
    return d if experimental_links else {k:v for k,v in d.items() if k in ["Base_SO101", "WaveShare_Mounting_Plate_SO101"]}


def load_part(path):
    # Some upstream files contain empty assembly nodes before their solid.
    solids = cq.importers.importStep(str(path)).solids().vals()
    if len(solids) != 1 or not solids[0].isValid():
        raise ValueError(f"Expected one valid solid: {path}")
    return solids[0]


def bbox(s):
    b = s.BoundingBox()
    return [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]


def volume(s):
    return sum(abs(x.Volume()) for x in s.Solids())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rotate_part(shape, matrix):
    # Use a rigid OCC transform, not a rounded general affine matrix.
    vector = Rotation.from_matrix(matrix).as_rotvec()
    angle = np.linalg.norm(vector)
    return shape.rotate((0, 0, 0), tuple(vector), math.degrees(angle)) if angle > 1e-12 else shape


def print_mesh(shape, rotation, source_stl=None):
    """Use proven upstream meshes for unchanged parts; tessellate modifications.

    A 0.0001 mm vertex weld removes binary STL seam round-off. No hole filling,
    geometry smoothing or removal of small components is performed. The moving
    jaw contains an intentional closed internal cavity (negative-volume shell).
    """
    if source_stl:
        m = trimesh.load(source_stl)
    else:
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        BRepMesh_IncrementalMesh(shape.wrapped, .03, False, .1, True)
        vertices, faces = shape.tessellate(.03, .1)
        m = trimesh.Trimesh([v.toTuple() for v in vertices], faces, process=True)
    m.merge_vertices(digits_vertex=4)
    m.update_faces(m.unique_faces())
    m.update_faces(m.nondegenerate_faces())
    m.remove_unreferenced_vertices()
    if not m.is_watertight or not m.is_winding_consistent:
        raise ValueError("Print mesh has open/nonmanifold edges or inconsistent winding")
    R = Rotation.from_matrix(rotation).as_matrix()
    m.vertices = m.vertices@R.T
    b = m.bounds
    shift = np.array([-(b[0,0]+b[1,0])/2, -(b[0,1]+b[1,1])/2, -b[0,2]])
    m.vertices += shift
    return m, shift


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=HERE)
    ap.add_argument("--part", help="Build only this STEP stem (development)")
    ap.add_argument("--experimental-links", action="store_true", help="Reproduce rejected link windows; do not use for the release set")
    args = ap.parse_args()
    if args.part and args.output.resolve() == HERE:
        ap.error("--part requires --output to a separate development directory")
    src = args.upstream / "STEP" / "SO101"
    files = sorted(p for p in src.rglob("*.step")
                   if "Assembly" not in p.name and "Leader_Specific" not in str(p)
                   and "Seeedstudio" not in p.name)
    if len(files) != 11:
        raise ValueError(f"Expected eleven follower source files; got {len(files)}")
    settings = designs(args.experimental_links)
    out = args.output
    for sub in ["step", "stl", "analysis"]:
        (out / sub).mkdir(parents=True, exist_ok=True)
    orientations = json.loads((HERE / "orientations.json").read_text())
    lock_path = HERE / "source-lock.json"
    lock = json.loads(lock_path.read_text()) if lock_path.exists() else None
    rows = []
    for p in files:
        if args.part and p.stem != args.part:
            continue
        digest = sha(p)
        if lock and digest != lock["files"][str(p.relative_to(args.upstream))]:
            raise ValueError(f"Upstream hash mismatch: {p}; do not silently change geometry")
        original = load_part(p)
        spec = settings.get(p.stem, {"cuts": [], "protected": {}})
        guards = {n: box(b) for n, b in spec["protected"].items()}
        result = original
        for bounds, axis, radius in spec["cuts"]:
            cutter = rounded_box(bounds, axis, radius)
            for guard in guards.values():
                cutter = cutter.cut(guard)
            result = result.cut(cutter)
        if not result.isValid() or len(result.Solids()) != 1:
            raise ValueError(f"Invalid/disconnected result: {p.stem}")
        output_step = out / "step" / p.name
        if spec["cuts"]:
            cq.exporters.export(result, str(output_step))
        else:
            # Byte identity is stronger than a coincident-surface Boolean test.
            shutil.copyfile(p, output_step)
        reloaded = load_part(output_step)
        # Do coincident-face Booleans on the native shapes. STEP re-import
        # reparameterises splines, which makes OCC's coincident-face Boolean
        # unreliable on this upstream model. Check serialization separately.
        added = volume(result.cut(original)) if spec["cuts"] else 0.0
        guard_loss = {n: volume(original.intersect(g).cut(result)) for n, g in guards.items()}
        extent_error = max(abs(a-b) for a, b in zip(bbox(original), bbox(reloaded)))
        roundtrip_error = abs(volume(result)-volume(reloaded))
        av = np.array([v.Center().toTuple() for v in result.Vertices()])
        bv = np.array([v.Center().toTuple() for v in reloaded.Vertices()])
        vertex_error = max(cKDTree(av).query(bv)[0].max(), cKDTree(bv).query(av)[0].max())
        topology_equal = all(len(getattr(result, x)()) == len(getattr(reloaded, x)()) for x in ["Faces", "Edges", "Vertices"])
        if added > 1e-4 or any(v > 1e-4 for v in guard_loss.values()) or extent_error > 1e-5 or roundtrip_error > max(1e-4, volume(result)*1e-5) or vertex_error > 1e-5 or not topology_equal:
            raise ValueError(f"Geometry verification failed: {p.stem}: added={added}, guard_loss={guard_loss}, extent_error={extent_error}, roundtrip_error={roundtrip_error}")
        R = orientations[p.stem]["rotation"]
        output_stl = out / "stl" / (p.stem + ".stl")
        source_stl = args.upstream/"STL/SO101/Individual"/(p.stem+".stl")
        if lock and sha(source_stl) != lock["files"][str(source_stl.relative_to(args.upstream))]:
            raise ValueError(f"Upstream STL hash mismatch: {source_stl}")
        m, shift = print_mesh(reloaded, R, source_stl if not spec["cuts"] else None)
        m.export(output_stl)
        row = dict(part=p.stem, modified=bool(spec["cuts"]), quantity=1,
                   source=str(p.relative_to(args.upstream)), source_sha256=digest,
                   step_sha256=sha(output_step), stl_sha256=sha(output_stl),
                   print_translation_mm=shift.tolist(),
                   mesh_watertight=True, mesh_consistent_winding=True,
                   mesh_volume_mm3=float(m.volume),
                   original_volume_mm3=volume(original), candidate_volume_mm3=volume(reloaded),
                   original_centroid_mm=list(original.Center().toTuple()),
                   candidate_centroid_mm=list(reloaded.Center().toTuple()),
                   removed_volume_mm3=volume(original)-volume(reloaded),
                   bounds_mm=bbox(reloaded), cuts=spec["cuts"], protected_regions=spec["protected"],
                   validation=dict(valid_solid=True, solids=1, native_added_volume_mm3=added,
                                   native_protected_region_loss_mm3=guard_loss,
                                   max_bounds_error_mm=extent_error,
                                   step_roundtrip_vertex_error_mm=float(vertex_error),
                                   step_roundtrip_topology_counts_equal=topology_equal,
                                   step_roundtrip_volume_error_mm3=roundtrip_error))
        rows.append(row)
        print(f"{p.stem}: {100*(1-volume(reloaded)/volume(original)):.1f}% CAD volume removed", flush=True)
    (out / "analysis" / "geometry.json").write_text(json.dumps(dict(
        upstream_revision=REVISION, cadquery_version=cq.__version__, experimental_links=args.experimental_links, parts=rows), indent=2)+"\n")


if __name__ == "__main__":
    main()
