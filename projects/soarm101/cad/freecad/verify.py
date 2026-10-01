#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Evidence for the SO-101 FreeCAD assemblies. Writes evidence.json beside this file.

1. Frames: each STEP solid against upstream's URDF mesh of the same part, in the mesh's own
   frame (metres -> mm). Agreement is what allows the URDF's visual origins to place the
   STEP solids. The two parts the lightweight study modified differ where it cut windows.
2. Kinematics: every joint frame of the released assembly against software/kinematics.py,
   which reads the same URDF with its own code, at the zero pose and at a test pose.

Usage: ./freecad-run verify.py SIMULATION_DIR
SIMULATION_DIR is upstream's Simulation/SO101 at the pinned revision (the URDF and assets/),
from a checkout or downloaded under this repository; FreeCAD's Flatpak cannot read /tmp.
"""
import importlib.util
import json
import math
import random
import sys
from pathlib import Path

import FreeCAD as App
import Mesh
import numpy as np
import Part

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import so101_freecad as build  # noqa: E402

SAMPLES = 400
TEST_POSE = dict(shoulder_pan=0.5, shoulder_lift=-0.7, elbow_flex=0.9, wrist_flex=0.4,
                 wrist_roll=-1.1, gripper=0.6)


def frames(simulation):
    if build.sha(simulation / "so101_new_calib.urdf") != build.URDF[1]:
        raise SystemExit("SIMULATION_DIR holds a different URDF from the frozen one")
    sources = {(m["name"], m["variant"]): m for m in build.reference_models(build.ARCHIVE)}
    rows, rng = [], random.Random(1)
    for mesh_name, part in sorted(build.MESH_PART.items()):
        mesh = Mesh.Mesh(str(simulation / "assets" / f"{mesh_name}.stl"))
        for variant in ("upstream", build.STUDY):
            meta = sources.get((part, variant))
            if meta is None or (variant == build.STUDY and meta["upstream_identical"]
                                and (part, "upstream") in sources):
                continue
            shape = build.read_step(build.ARCHIVE, meta["source"], meta["source_sha256"])
            points = rng.sample(list(mesh.Points), min(SAMPLES, mesh.CountPoints))
            distances = sorted(Part.Vertex(App.Vector(p.x * 1000, p.y * 1000, p.z * 1000)).distToShape(shape)[0]
                               for p in points)
            box, mbox = shape.optimalBoundingBox(False, False), mesh.BoundBox
            bounds = max(abs(getattr(box, k) - getattr(mbox, k) * 1000)
                         for k in ("XMin", "YMin", "ZMin", "XMax", "YMax", "ZMax"))
            rows.append(dict(
                mesh=mesh_name, part=part, source=meta["source"], modified=not meta["upstream_identical"],
                samples=len(points), bounds_difference_mm=round(bounds, 4),
                distance_mm=dict(median=round(distances[len(distances) // 2], 4),
                                 p95=round(distances[int(len(distances) * 0.95)], 4),
                                 max=round(distances[-1], 4)),
                volume_cm3=dict(step=round(shape.Volume / 1000, 2), mesh=round(mesh.Volume * 1e6, 2))))
            print(f"{part:32s} {variant:14s} max {distances[-1]:.4f} mm", flush=True)
    return rows


def global_placement(obj):
    placement = obj.Placement
    while True:
        parents = [p for p in obj.InList if p.TypeId == "App::Part"]
        if not parents:
            return placement
        obj = parents[0]
        placement = obj.Placement.multiply(placement)


def kinematics():
    path = HERE.parents[1] / "software" / "kinematics.py"
    spec = importlib.util.spec_from_file_location("kinematics", path)
    kin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kin)
    joints = kin.load_urdf(build.frozen(build.ARCHIVE, *build.URDF))
    index = json.loads((HERE / "manifest.json").read_text())
    rows = []
    for item in (m for m in index["models"] if m["kind"] == "assembly"):
        doc = App.openDocument(str(HERE / item["fcstd"]), True)
        try:
            sheet = doc.getObject("Joints")
            names = [sheet.get(f"A{r}") for r in range(2, 8)]
            for label, pose in (("zero", dict.fromkeys(names, 0.0)), ("test", TEST_POSE)):
                for row, name in enumerate(names, start=2):
                    sheet.set(f"B{row}", f"={math.degrees(pose[name])!r} deg")
                doc.recompute()
                expected = kin.fk(joints, pose)
                worst_mm = worst_rotation = 0.0
                for joint, matrix in expected.items():
                    child = [c for c in doc.getObject("J_" + joint).Group if c.TypeId == "App::Part"][0]
                    got = global_placement(child)
                    m = got.Rotation.Matrix
                    rotation = np.array([[m.A11, m.A12, m.A13], [m.A21, m.A22, m.A23], [m.A31, m.A32, m.A33]])
                    worst_mm = max(worst_mm, float(np.linalg.norm(np.array(matrix)[:3, 3] * 1000 - np.array(got.Base))))
                    worst_rotation = max(worst_rotation, float(np.abs(rotation - np.array(matrix)[:3, :3]).max()))
                invalid = [o.Name for o in doc.Objects if not o.isValid()]
                rows.append(dict(assembly=item["name"], pose=label, joint_frames=len(expected),
                                 max_origin_difference_mm=worst_mm, max_rotation_element_difference=worst_rotation,
                                 invalid_objects=invalid))
                print(f"{item['name']:32s} {label:5s} {worst_mm:.2e} mm", flush=True)
        finally:
            App.closeDocument(doc.Name)   # opened hidden; the released file is not saved
    return rows


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    result = dict(
        upstream_revision=build.UPSTREAM_REVISION, freecad_version=".".join(App.Version()[:3]),
        test_pose_rad=TEST_POSE, frames=frames(Path(sys.argv[1]).resolve()), kinematics=kinematics())
    (HERE / "evidence.json").write_text(json.dumps(result, indent=1) + "\n")
    print("wrote evidence.json")
