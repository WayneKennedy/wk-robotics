#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "trimesh", "usd-core"]
# ///
"""Local 3D viewer for externally designed robots this family is studying.

    ./viewer.py --fetch          # clone/update the upstream sources
    ./viewer.py                  # build, serve, open a browser
    ./viewer.py --build          # regenerate build/ only
    ./viewer.py --serve          # serve an existing build/
    ./viewer.py --design bimo    # one design instead of all

Reads upstream geometry as published and writes build/scene-<design>.json for
a checked-in viewer.html, in the same encoding koala-bot's viewer uses
(base64 float32 positions, uint32 indices), so the two look and drive alike.

This is an inspection aid for design study. It renders geometry exactly as
upstream ships it. It establishes nothing about fit, clearance, printability
or strength, and for Bimo the geometry is a simulation asset rather than
manufacturing CAD. See README.md.
"""
import argparse
import base64
import http.server
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import webbrowser
import xml.etree.ElementTree as ET

import numpy as np
import trimesh

ROOT = pathlib.Path(__file__).resolve().parent
UPSTREAM = ROOT / "upstream"
OUT = ROOT / "build"
VENDOR = ROOT / "vendor"

# The printer and the design rule both come from wk-robotics docs/common.md:
# an Ender-5 S1 at 220x220x280, and koala-bot's stricter every-part-under-200
# rule, which is the one to design to.
BED = (220.0, 220.0)
BED_Z = 280.0
DESIGN_RULE_MM = 200.0
GRID_STEP = 20.0     # mm, viewer floor grid
HARDWARE_FACE_BUDGET = 6000   # triangles kept per bought/servo mesh
PART_GAP = 15.0      # mm between parts in the layout
LAYOUT_W = 620.0     # mm; wrap width, wide enough to read as a grid

PART_COLOURS = ["#8fb4d9", "#d9d08f", "#d9a48f", "#c98fd9", "#8fd9c9",
                "#b4d98f", "#d98f9e", "#8f9ed9", "#d9c48f", "#9ed98f"]
SERVO_COLOUR = "#e0663f"      # STS3215 bodies, so they read at a glance
HARDWARE_COLOUR = "#7d8794"   # boards, cells, bought parts

SOURCES = {
    "openduck": {
        "label": "Open Duck Mini v2",
        "repo": "https://github.com/apirrone/Open_Duck_Mini.git",
        "branch": "v2",
        "dir": "Open_Duck_Mini",
        "licence": "Apache-2.0",
    },
    "bimo": {
        "label": "Bimo",
        "repo": "https://github.com/mekion/the-bimo-project.git",
        "branch": None,
        "dir": "the-bimo-project",
        "licence": "Apache-2.0",
    },
}

# Names that are a servo body rather than a printed or bought part. wj-wk00-*
# are the three STS3215 case shells (45.22 x 24.72 mm, matching the Waveshare
# ST3215 drawing quoted in docs/common.md); sg90 is the 9 g antenna servo.
SERVO_PAT = re.compile(r"wj-wk00|sts\d|st\d{4}|servo|sg90", re.I)


# --------------------------------------------------------------------------
# geometry encoding - identical schema to koala-bot's viewer
# --------------------------------------------------------------------------
def decimate(mesh: trimesh.Trimesh, budget: int) -> trimesh.Trimesh:
    """Thin a bought-part mesh that is far denser than inspecting it needs.

    Applied only to servo bodies and bought hardware, never to a printed part:
    the duck repeats one 102k-triangle STS3215 shell fourteen times, which is
    most of the scene for none of the information.
    """
    if len(mesh.faces) <= budget:
        return mesh
    try:
        return mesh.simplify_quadric_decimation(face_count=budget)
    except Exception:
        return mesh          # no simplifier available; full detail is correct


def _item(name: str, mesh: trimesh.Trimesh, colour: str, **extra) -> dict:
    v = np.asarray(mesh.vertices, dtype=np.float32)
    f = np.asarray(mesh.faces, dtype=np.uint32)
    lo, hi = mesh.bounds
    return {
        "name": name,
        "colour": colour,
        "tris": int(len(f)),
        "size": [round(float(x), 2) for x in (hi - lo)],
        "pos": base64.b64encode(v.tobytes()).decode(),
        "idx": base64.b64encode(f.tobytes()).decode(),
        **extra,
    }


# Surface-only print screen, same conventions as koala-bot's printability.py:
# `angle` is measured from straight down, so a horizontal ceiling is 0 deg and
# a vertical wall 90 deg. The 45 deg threshold is a heuristic. It neither finds
# every floating start nor says anything about strength.
SELF_SUPPORT_DEG = 45.0
BED_TOL = 0.05   # mm - a face this close to the lowest point counts as on the bed


def print_metrics(mesh: trimesh.Trimesh) -> dict:
    n = mesh.face_normals
    a = mesh.area_faces
    face_max_z = mesh.triangles[:, :, 2].max(axis=1)
    z_min = mesh.bounds[0][2]
    on_bed = (face_max_z <= z_min + BED_TOL) & (n[:, 2] < -0.9)
    overhang = (n[:, 2] < -np.cos(np.radians(SELF_SUPPORT_DEG))) & ~on_bed
    return {
        "bed_area": round(float(a[on_bed].sum()), 1),
        "overhang_area": round(float(a[overhang].sum()), 1),
        "overhang_frac": round(float(a[overhang].sum() / max(a.sum(), 1e-9)), 4),
    }


def size_flags(size) -> dict:
    """Bed and design-rule fit for a part in the orientation as supplied."""
    w, d, h = sorted(size[:2], reverse=True) + [size[2]]
    return {
        "fits_bed": bool(w <= BED[0] and d <= BED[1] and h <= BED_Z),
        "fits_rule": bool(w <= DESIGN_RULE_MM and d <= DESIGN_RULE_MM),
        "largest_xy": round(float(w), 2),
    }


def layout(entries):
    """Row-wrap parts across the floor so they read as a grid, not a column.

    A size and shape comparison, not a build plate: the bed square is drawn
    alongside purely as a scale reference.
    """
    placed, x, y, row_h = [], PART_GAP, PART_GAP, 0.0
    for entry in entries:
        mesh = entry["mesh"]
        mesh.apply_translation(-mesh.bounds[0])       # sit on the floor
        w, d = mesh.extents[0], mesh.extents[1]
        if x + w > LAYOUT_W and x > PART_GAP:
            x, y, row_h = PART_GAP, y + row_h + PART_GAP, 0.0
        mesh.apply_translation([x, y, 0])
        placed.append(entry)
        x += w + PART_GAP
        row_h = max(row_h, d)
    return placed


# --------------------------------------------------------------------------
# Open Duck Mini v2 - URDF assembly plus the published print/ STLs
# --------------------------------------------------------------------------
def _rpy(rpy) -> np.ndarray:
    r, p, y = rpy
    cr, sr, cp, sp, cy, sy = (np.cos(r), np.sin(r), np.cos(p),
                              np.sin(p), np.cos(y), np.sin(y))
    return np.array([
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp,     cp * sr,                cp * cr],
    ])


def _origin(elem) -> np.ndarray:
    T = np.eye(4)
    if elem is None:
        return T
    xyz = [float(v) for v in elem.get("xyz", "0 0 0").split()]
    rpy = [float(v) for v in elem.get("rpy", "0 0 0").split()]
    T[:3, :3] = _rpy(rpy)
    T[:3, 3] = xyz
    return T


def _colour(visual) -> str | None:
    material = visual.find("material")
    rgba = material.find("color") if material is not None else None
    if rgba is None:
        return None
    r, g, b, _a = [float(v) for v in rgba.get("rgba").split()]
    return "#%02x%02x%02x" % tuple(int(round(255 * c)) for c in (r, g, b))


def openduck(src: pathlib.Path) -> dict:
    robot_dir = src / "mini_bdx/robots/open_duck_mini_v2"
    urdf = robot_dir / "robot.urdf"
    print_dir = src / "print"
    if not urdf.exists():
        sys.exit(f"missing {urdf} - run --fetch first")

    printed_names = {p.stem for p in print_dir.glob("*.stl")}

    # ---- assembly, at the URDF zero pose ----
    root = ET.parse(urdf).getroot()
    parent_of = {}
    joint_kind = {}
    for j in root.findall("joint"):
        child = j.find("child").get("link")
        parent_of[child] = (j.find("parent").get("link"),
                            _origin(j.find("origin")), j.get("name"))
        joint_kind[j.get("name")] = j.get("type")

    def world(link):
        """T_world_link with every revolute joint at zero, plus its joint chain."""
        T, chain, cur = np.eye(4), [], link
        while cur in parent_of:
            parent, origin, joint = parent_of[cur]
            T = origin @ T
            if joint_kind.get(joint) == "revolute":
                chain.append(joint)
            cur = parent
        return T, list(reversed(chain))

    cache, items = {}, []
    for link in root.findall("link"):
        T_link, chain = world(link.get("name"))
        for visual in link.findall("visual"):
            mesh_el = visual.find("geometry/mesh")
            if mesh_el is None:
                continue
            stem = pathlib.Path(mesh_el.get("filename").split("/")[-1]).stem
            path = robot_dir / f"{stem}.stl"
            if not path.exists():
                continue
            if path not in cache:
                cache[path] = trimesh.load(path, force="mesh")
            mesh = cache[path].copy()
            mesh.apply_transform(T_link @ _origin(visual.find("origin")))
            mesh.apply_scale(1000.0)        # URDF/mesh metres -> mm
            servo = bool(SERVO_PAT.search(stem))
            kind = ("servo" if servo else
                    "printed" if stem in printed_names else "hardware")
            if kind != "printed":
                mesh = decimate(mesh, HARDWARE_FACE_BUDGET)
            items.append(_item(
                stem, mesh,
                SERVO_COLOUR if servo else
                HARDWARE_COLOUR if kind == "hardware" else
                (_colour(visual) or PART_COLOURS[len(items) % len(PART_COLOURS)]),
                # One link can carry several copies of the same mesh, so the
                # name is not unique; solo and hide key off id instead.
                id=f"{stem}#{len(items)}", sub=link.get("name"),
                kind=kind, link=link.get("name"),
                joint=chain[-1] if chain else None,
                chain=" › ".join(chain) if chain else "fixed to trunk"))

    # Stand the robot on the grid rather than on the URDF's arbitrary origin.
    if items:
        floor = min(min(np.frombuffer(base64.b64decode(i["pos"]),
                                      dtype=np.float32)[2::3])
                    for i in items)
        for i in items:
            v = np.frombuffer(base64.b64decode(i["pos"]),
                              dtype=np.float32).copy().reshape(-1, 3)
            v[:, 2] -= floor
            i["pos"] = base64.b64encode(v.tobytes()).decode()

    # ---- printed parts, in the orientation upstream ships them ----
    guide = {}
    guide_file = src / "docs/print_guide.md"
    if guide_file.exists():
        for line in guide_file.read_text().splitlines():
            m = re.match(r"^\s*-\s*(\S+\.stl)\s*x(\d+)(.*)$", line)
            if m:
                guide[m.group(1)] = (int(m.group(2)),
                                     "TPU" if "TPU" in m.group(3).upper() else "PLA")

    entries = []
    for path in sorted(print_dir.glob("*.stl")):
        mesh = trimesh.load(path, force="mesh")
        qty, material = guide.get(path.name, (1, "PLA"))
        entries.append({"mesh": mesh, "name": path.stem, "qty": qty,
                        "material": material,
                        "in_guide": path.name in guide})

    parts = []
    for n, entry in enumerate(layout(entries)):
        mesh = entry["mesh"]
        size = mesh.extents
        parts.append(_item(
            entry["name"], mesh, PART_COLOURS[n % len(PART_COLOURS)],
            id=entry["name"], kind="printed",
            qty=entry["qty"], material=entry["material"],
            watertight=bool(mesh.is_watertight),
            volume_cm3=round(float(mesh.volume) / 1000.0, 2)
            if mesh.is_watertight else None,
            metrics=print_metrics(mesh), **size_flags(size),
            notes="" if entry["in_guide"] else
                  "Not listed in upstream's print guide; quantity assumed 1."))

    return {
        "label": SOURCES["openduck"]["label"],
        "assembly": items,
        "parts": parts,
        "meta": {
            "bed": list(BED), "bed_z": BED_Z, "rule": DESIGN_RULE_MM,
            "grid": GRID_STEP, "parts_are_printable": True,
            "source": "apirrone/Open_Duck_Mini branch v2, Apache-2.0",
            "assembly_note": "URDF zero pose. Joints are not driven here; "
                             "nothing about clearance through travel is shown.",
            "parts_note": "Upstream print/ STLs in the orientation as supplied. "
                          "Quantities and materials are read from "
                          "docs/print_guide.md. Bed and design-rule flags use "
                          "that orientation; a slicer may reorient a part.",
        },
    }


# --------------------------------------------------------------------------
# Bimo - the Isaac Lab simulation asset, the only geometry published
# --------------------------------------------------------------------------
def bimo(src: pathlib.Path) -> dict:
    from pxr import Usd, UsdGeom

    asset = src / "IsaacLab/bimo/assets/Bimo.usd"
    if not asset.exists():
        sys.exit(f"missing {asset} - run --fetch first")

    stage = Usd.Stage.Open(str(asset))
    # The stage declares metersPerUnit 0.01, but the authored data is metric:
    # the hip-to-foot translate is 0.4028 and the thigh mesh spans 0.22, on a
    # robot upstream documents as 45 cm. Taking the declared unit yields a
    # 5 mm robot. Treat the numbers as metres and say so rather than trust a
    # header the asset contradicts.
    scale = 1000.0

    def to_mesh(prim, world=True):
        geom = UsdGeom.Mesh(prim)
        pts = np.asarray(geom.GetPointsAttr().Get(), dtype=np.float64)
        counts = np.asarray(geom.GetFaceVertexCountsAttr().Get())
        idx = np.asarray(geom.GetFaceVertexIndicesAttr().Get())
        faces, at = [], 0
        for c in counts:                       # fan-triangulate any n-gons
            fan = idx[at:at + c]
            faces.extend([[fan[0], fan[i], fan[i + 1]] for i in range(1, c - 1)])
            at += c
        if world:
            M = np.array(UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(
                Usd.TimeCode.Default()))       # USD is row-vector: v' = v @ M
            pts = np.column_stack([pts, np.ones(len(pts))]) @ M
            pts = pts[:, :3]
        return trimesh.Trimesh(vertices=pts * scale, faces=np.array(faces),
                               process=False)

    prims = [p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)]

    items = []
    for n, prim in enumerate(prims):
        mesh = to_mesh(prim)
        parts_path = prim.GetPath().pathString.split("/")
        body = parts_path[3] if len(parts_path) > 3 else prim.GetName()
        items.append(_item(body, mesh, PART_COLOURS[n % len(PART_COLOURS)],
                           id=f"{body}#{n}", sub=prim.GetName(),
                           kind="sim", link=body,
                           chain=prim.GetPath().pathString))
    if items:
        floor = min(min(np.frombuffer(base64.b64decode(i["pos"]),
                                      dtype=np.float32)[2::3]) for i in items)
        for i in items:
            v = np.frombuffer(base64.b64decode(i["pos"]),
                              dtype=np.float32).copy().reshape(-1, 3)
            v[:, 2] -= floor
            i["pos"] = base64.b64encode(v.tobytes()).decode()

    # One entry per distinct source mesh: the left and right bodies reference
    # the same authored geometry, so showing both twice would be noise.
    unique, seen = [], {}
    for prim in prims:
        stem = prim.GetName()
        if stem in seen:
            seen[stem]["qty"] += 1
            continue
        entry = {"mesh": to_mesh(prim, world=False), "name": stem, "qty": 1}
        seen[stem] = entry
        unique.append(entry)

    parts = []
    for n, entry in enumerate(layout(unique)):
        mesh = entry["mesh"]
        parts.append(_item(
            entry["name"], mesh, PART_COLOURS[n % len(PART_COLOURS)],
            id=entry["name"], kind="sim", qty=entry["qty"], material="unknown",
            watertight=bool(mesh.is_watertight),
            volume_cm3=round(float(mesh.volume) / 1000.0, 2)
            if mesh.is_watertight else None,
            **size_flags(mesh.extents),
            notes="Simulation mesh in its authored orientation. Upstream "
                  "publishes no print orientation, so no print screen is run."))

    return {
        "label": SOURCES["bimo"]["label"],
        "assembly": items,
        "parts": parts,
        "meta": {
            "bed": list(BED), "bed_z": BED_Z, "rule": DESIGN_RULE_MM,
            "grid": GRID_STEP, "parts_are_printable": False,
            "source": "mekion/the-bimo-project, IsaacLab/bimo/assets/Bimo.usd, "
                      "Apache-2.0",
            "warning": "Simulation asset, not manufacturing CAD. Upstream "
                       "publishes no STL, STEP or URDF - its README still says "
                       "CAD files are coming soon. Shapes are simplified for "
                       "physics and cannot be printed or measured from.",
            "assembly_note": "Default pose as authored in the USD stage.",
            "parts_note": "One entry per distinct authored mesh; the left and "
                          "right bodies reuse the same geometry.",
        },
    }


BUILDERS = {"openduck": openduck, "bimo": bimo}


# --------------------------------------------------------------------------
def fetch(names) -> None:
    UPSTREAM.mkdir(parents=True, exist_ok=True)
    for name in names:
        s = SOURCES[name]
        dest = UPSTREAM / s["dir"]
        if dest.exists():
            print(f"{name}: updating {dest.name}")
            subprocess.run(["git", "-C", str(dest), "pull", "--ff-only"],
                           check=False)
            continue
        cmd = ["git", "clone", "--depth", "1"]
        if s["branch"]:
            cmd += ["--branch", s["branch"]]
        cmd += [s["repo"], str(dest)]
        print(f"{name}: cloning {s['repo']}")
        subprocess.run(cmd, check=True)


def build(names) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for name in names:
        src = UPSTREAM / SOURCES[name]["dir"]
        if not src.exists():
            print(f"{name}: no checkout at {src}; skipping (run --fetch)")
            continue
        scene = BUILDERS[name](src)
        path = OUT / f"scene-{name}.json"
        path.write_text(json.dumps(scene))
        tris = sum(i["tris"] for i in scene["assembly"] + scene["parts"])
        print(f"{name}: {len(scene['assembly'])} assembly + "
              f"{len(scene['parts'])} parts, {tris:,} triangles, "
              f"{path.stat().st_size / 1e6:.1f} MB")
        index.append({"id": name, "label": scene["label"],
                      "licence": SOURCES[name]["licence"],
                      "parts": len(scene["parts"])})
    (OUT / "designs.json").write_text(json.dumps({"designs": index}))
    shutil.copy(ROOT / "viewer.html", OUT / "index.html")
    for f in VENDOR.iterdir():
        if f.is_file():
            shutil.copy(f, OUT / f.name)


def serve(port: int, open_browser: bool, host: str = "127.0.0.1") -> None:
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(OUT), **k)
    shown = "localhost" if host in ("127.0.0.1", "") else host
    url = f"http://{shown}:{port}/"
    with http.server.ThreadingHTTPServer((host, port), handler) as httpd:
        print(f"serving {url}  (ctrl-c to stop)")
        if open_browser:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--design", choices=[*SOURCES, "all"], default="all")
    ap.add_argument("--fetch", action="store_true",
                    help="clone or update the upstream checkouts, then exit")
    ap.add_argument("--build", action="store_true",
                    help="regenerate build/ and exit, do not serve")
    ap.add_argument("--serve", action="store_true",
                    help="serve the existing build/ without rebuilding")
    ap.add_argument("--port", type=int, default=8019)
    ap.add_argument("--host", default="127.0.0.1",
                    help="address to bind. Default is loopback only. Pass this "
                         "machine's tailnet address to reach it from another "
                         "device; it is deliberately not defaulted or recorded "
                         "here, because this repo is public")
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    names = list(SOURCES) if args.design == "all" else [args.design]
    if args.fetch:
        fetch(names)
        return
    if not args.serve:
        build(names)
    if not args.build:
        serve(args.port, not args.no_open and args.host == "127.0.0.1",
              args.host)


if __name__ == "__main__":
    main()
