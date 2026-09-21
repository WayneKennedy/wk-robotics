#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Geometric section-property screen of the two long links (NOT FDM FEA).

Measures CAD-envelope A, Iy, Iz and section modulus from triangulated sections.
Treating either CAD solid as homogeneous would overstate sparse-print stiffness.
The compliance ratios concern only the altered middle span under pure bending.
"""
import argparse
import csv
import json
from pathlib import Path

import cadquery as cq
import numpy as np
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
import trimesh

from generate import HERE, load_part


def mesh(shape):
    vertices, faces = shape.tessellate(.025, .08)
    return trimesh.Trimesh([v.toTuple() for v in vertices], faces, process=True)


def properties(m, x):
    section = m.section(plane_origin=[x,0,0], plane_normal=[1,0,0])
    region = Polygon()
    for loop in section.discrete:
        p = Polygon(loop[:,1:3])
        if not p.is_valid:
            p = p.buffer(0)
        region = region.symmetric_difference(p)
    polygons = [region] if region.geom_type == "Polygon" else list(region.geoms)
    area = sy = sz = iyy = izz = 0
    for polygon in polygons:
        polygon = orient(polygon)
        for ring in [polygon.exterior, *polygon.interiors]:
            yz = np.array(ring.coords)
            y, z = yz[:-1].T
            yy, zz = yz[1:].T
            cross = y*zz-yy*z
            area += cross.sum()/2
            sy += ((y+yy)*cross).sum()/6
            sz += ((z+zz)*cross).sum()/6
            izz += ((y*y+y*yy+yy*yy)*cross).sum()/12
            iyy += ((z*z+z*zz+zz*zz)*cross).sum()/12
    cy, cz = sy/area, sz/area
    iy, iz = iyy-area*cz**2, izz-area*cy**2
    ymin,zmin,ymax,zmax = region.bounds
    return dict(area_mm2=area, Iy_mm4=iy, Iz_mm4=iz,
                Zy_mm3=iy/max(zmax-cz,cz-zmin), Zz_mm3=iz/max(ymax-cy,cy-ymin))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--cad-dir", type=Path, default=HERE)
    args = ap.parse_args()
    rows = []
    summaries = {}
    for name in ["Upper_arm_SO101", "Under_arm_SO101"]:
        original = mesh(load_part(Path(args.upstream)/"STEP/SO101"/(name+".step")))
        candidate = mesh(load_part(args.cad_dir/"step"/(name+".step")))
        xs = np.arange(-27.5,54,1)
        a = [properties(original,x) for x in xs]
        b = [properties(candidate,x) for x in xs]
        summary = {}
        for axis in ["y","z"]:
            key = "I"+axis+"_mm4"
            ratio = np.array([v[key]/u[key] for u,v in zip(a,b)])
            summary[f"minimum_I{axis}_ratio"] = float(ratio.min())
            summary[f"minimum_I{axis}_at_x_mm"] = float(xs[np.argmin(ratio)])
            summary[f"middle_span_pure_bending_compliance_{axis}_ratio"] = float(
                sum(1/v[key] for v in b)/sum(1/u[key] for u in a))
            summary[f"minimum_candidate_Z{axis}_mm3"] = float(min(v[f"Z{axis}_mm3"] for v in b))
            summary[f"nominal_solid_stress_3Nm_about_{axis}_MPa"] = 3000/summary[f"minimum_candidate_Z{axis}_mm3"]
        summaries[name] = summary
        for x,u,v in zip(xs,a,b):
            rows.append(dict(part=name,x_mm=x,**{"original_"+k:w for k,w in u.items()},**{"candidate_"+k:w for k,w in v.items()}))
        print(name,summary,flush=True)
    with (args.cad_dir/"analysis/sections.csv").open("w") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (args.cad_dir/"analysis/sections.json").write_text(json.dumps(dict(
        method="1 mm stations across x=-27.5..53.5 mm; OpenCASCADE relative linear deflection 0.025, angular tolerance 0.08 rad; homogeneous envelope only",
        limitations="No raster/layer anisotropy, notch stress, contact, creep, fatigue, fastener failure or torsion. Nominal stresses are NOT FDM strength predictions.",
        parts=summaries),indent=2)+"\n")


if __name__ == "__main__":
    main()
