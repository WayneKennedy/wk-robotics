#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Slice matched originals/candidates locally; save material mass and deposited COM.

Does not connect to a printer. G-code is temporary analysis output, never production
G-code. Requires a locally runnable PrusaSlicer CLI; --slicer selects its executable.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile

import cadquery as cq
import numpy as np

from generate import HERE, load_part, sha, print_mesh


def read_extrusion(path):
    role = "unknown"
    xyz = np.zeros(3)
    roles = {}
    weighted = np.zeros(3)
    part_e = 0.0
    # comparison.ini requires relative E, absolute XYZ, no arcs/custom G-code.
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith(";TYPE:"):
            role = line[6:].strip()
        if not line.startswith(("G0 ", "G1 ")):
            continue
        args = {k: float(v) for k, v in re.findall(r"\b([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))", line.split(";")[0])}
        after = xyz.copy()
        for i, key in enumerate("XYZ"):
            if key in args:
                after[i] = args[key]
        # Ignore pure-E unretractions; deposited extrusions have an XY move.
        extrusion = args.get("E", 0)
        if extrusion > 0 and ("X" in args or "Y" in args) and np.linalg.norm(after[:2]-xyz[:2]) > 1e-8:
            roles[role] = roles.get(role, 0.0) + extrusion
            if not role.lower().startswith(("support", "skirt", "brim", "wipe")):
                if role == "unknown":
                    raise ValueError("Extrusion without role")
                weighted += extrusion * ((xyz+after)/2 - [0, 0, 0.1])
                part_e += extrusion
        xyz = after
    conversion = math.pi*(1.75/2)**2 * 1.24 / 1000
    return dict(part_mass_g=part_e*conversion,
                total_mass_g=sum(roles.values())*conversion,
                support_mass_g=sum(v for k, v in roles.items() if k.lower().startswith("support"))*conversion,
                roles_mass_g={k: v*conversion for k, v in roles.items()},
                deposited_center_gcode_mm=(weighted/part_e).tolist())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream", type=Path, required=True)
    ap.add_argument("--slicer", required=True)
    ap.add_argument("--work", type=Path, default=Path(tempfile.gettempdir())/"so101-slicing")
    ap.add_argument("--perimeters", type=int, default=3)
    ap.add_argument("--cad-dir", type=Path, default=HERE)
    args = ap.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    geometry = json.loads((args.cad_dir/"analysis/geometry.json").read_text())
    orientations = json.loads((HERE/"orientations.json").read_text())
    tasks = []
    for row in geometry["parts"]:
        name = row["part"]
        p = args.upstream/row["source"]
        if sha(p) != row["source_sha256"]:
            raise ValueError(f"Source hash mismatch: {p}")
        R = np.array(orientations[name]["rotation"])
        original, shift = print_mesh(load_part(p), R, args.upstream/"STL/SO101/Individual"/(name+".stl"))
        original_stl = args.work/(name+"_original.stl")
        original.export(original_stl)
        for variant, stl in [("original", original_stl), ("candidate", args.cad_dir/"stl"/(name+".stl"))]:
            tasks.append((name, variant, stl, R, shift if variant == "original" else np.array(row["print_translation_mm"])))

    def run(task):
        name, variant, stl, R, shift = task
        gcode = args.work/f"{name}_{variant}_p{args.perimeters}.gcode"
        command = [args.slicer, "--load", str(HERE/"comparison.ini"), "--perimeters", str(args.perimeters),
                   "--export-gcode", "--center", "110,110", "--output", str(gcode), str(stl)]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode or not gcode.exists():
            raise RuntimeError(f"{name} {variant}: {result.stdout}\n{result.stderr}")
        data = read_extrusion(gcode)
        footer = re.search(r"; filament used \[g\] = ([\d.]+)", gcode.read_text())
        if footer is None or abs(data["total_mass_g"]-float(footer.group(1))) > .1:
            raise ValueError(f"Extrusion accounting disagrees with slicer footer: {gcode}")
        data["footer_total_mass_g"] = float(footer.group(1))
        data["deposited_center_cad_mm"] = ((np.array(data.pop("deposited_center_gcode_mm"))-[110,110,0]-shift)@R).tolist()
        data["gcode_sha256"] = sha(gcode)
        data["stl_sha256"] = sha(stl)
        data["slicer_warnings"] = result.stderr.strip()
        print(f"{name} {variant}: part {data['part_mass_g']:.2f} g; support {data['support_mass_g']:.2f} g", flush=True)
        return name, variant, data

    rows = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        for name, variant, data in pool.map(run, tasks):
            rows.setdefault(name, {})[variant] = data
    version = subprocess.run([args.slicer, "--help"], capture_output=True, text=True).stdout.splitlines()[0]
    meta = dict(slicer=version, profile_sha256=sha(HERE/"comparison.ini"),
                perimeters=args.perimeters, layer_height_mm=0.2, density_g_cm3=1.24,
                notes="Toolpath estimate, not weighed mass. Support excluded from part mass. COM assumes uniform extrusion along each line.",
                parts=rows)
    (args.cad_dir/"analysis"/f"slices-p{args.perimeters}.json").write_text(json.dumps(meta, indent=2)+"\n")
    with (args.cad_dir/"analysis"/f"mass-p{args.perimeters}.csv").open("w") as f:
        w = csv.writer(f)
        w.writerow(["part", "original_g", "candidate_g", "saved_g", "saved_percent"])
        for name, data in rows.items():
            a, b = data["original"]["part_mass_g"], data["candidate"]["part_mass_g"]
            w.writerow([name, a, b, a-b, 100*(1-b/a)])
    a = sum(r["original"]["part_mass_g"] for r in rows.values())
    b = sum(r["candidate"]["part_mass_g"] for r in rows.values())
    print(f"TOTAL {a:.2f} -> {b:.2f} g; saving {a-b:.2f} g ({100*(1-b/a):.2f}%)")


if __name__ == "__main__":
    main()
