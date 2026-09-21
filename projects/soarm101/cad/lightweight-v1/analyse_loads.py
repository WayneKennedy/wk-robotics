#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Static gravity screen, deliberately separate from structural qualification.

No bus access or hardware writes. Uses the existing measured travel limits and
upstream geometry, never the URDF's generic effort=10 as a servo specification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]/"software"))
import kinematics as kin

G = 9.80665
RATED = 10*G/100
STALL = 30*G/100


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream", type=Path, required=True)
    args = ap.parse_args()
    urdf = args.upstream/"Simulation/SO101/so101_new_calib.urdf"
    root = ET.parse(urdf).getroot()
    joints = kin.load_urdf(urdf)
    slices = json.loads((HERE/"analysis/slices-p3.json").read_text())["parts"]
    lookup = {n.lower(): n for n in slices}
    pitch = ["shoulder_lift", "elbow_flex", "wrist_flex"]

    def pose(a):
        return dict(zip(pitch, a)) | {"shoulder_pan": 0.0, "wrist_roll": 0.0, "gripper": 0.0}

    def objective(a):
        f = kin.fk(joints, pose(a))
        return -(f["gripper_frame_joint"][0,3]-f["shoulder_lift"][0,3])

    solution = minimize(objective, [1.3, -1.2, -.1], method="L-BFGS-B",
                        bounds=[joints[j]["limit"] for j in pitch], options={"ftol": 1e-14, "gtol": 1e-10})
    if not solution.success:
        raise RuntimeError(solution.message)
    q = pose(solution.x)
    frames = kin.fk(joints, q)
    link_T = {"base_link": np.eye(4)} | {joints[j]["child"]: T for j,T in frames.items()}
    children = {}
    for j in joints.values():
        children.setdefault(j["parent"], []).append(j["child"])

    def descendants(link):
        return {link}.union(*(descendants(c) for c in children.get(link, [])))

    def transform(origin):
        T = np.eye(4)
        if origin is not None:
            T[:3,:3] = kin._rpy(*map(float, origin.get("rpy", "0 0 0").split()))
            T[:3,3] = list(map(float, origin.get("xyz", "0 0 0").split()))
        return T

    bodies = {v: [] for v in ["urdf", "original", "candidate", "half_print_mass"]}
    part_locations = []
    for link in root.findall("link"):
        lname = link.get("name")
        T = link_T[lname]
        inertial = link.find("inertial")
        if inertial is not None:
            m = float(inertial.find("mass").get("value"))
            p = (T@transform(inertial.find("origin")))[:3,3]
            bodies["urdf"].append((lname, m, p))
        for visual in link.findall("visual"):
            mesh = visual.find("geometry/mesh")
            if mesh is None:
                continue
            stem = Path(mesh.get("filename")).stem
            V = T@transform(visual.find("origin"))
            if stem.startswith("sts3215"):
                # Nominal 55 g at CAD case origin; internal mass distribution
                # and whether the quoted mass includes horns are not measured.
                for variant in ["original", "candidate", "half_print_mass"]:
                    bodies[variant].append((lname, .055, V[:3,3]))
                continue
            name = lookup[re.sub(r"_v\d+$", "", stem)]
            for variant in ["original", "candidate", "half_print_mass"]:
                data = slices[name]["candidate" if variant == "candidate" else "original"]
                mass = data["part_mass_g"] / 1000 * (.5 if variant == "half_print_mass" else 1)
                p = (V@np.r_[np.array(data["deposited_center_cad_mm"])/1000, 1])[:3]
                bodies[variant].append((lname, mass, p))
            part_locations.append(dict(part=name, link=lname, world_center_m=p.tolist()))

    def torque(body_list, joint):
        j = joints[joint]
        p = frames[joint][:3,3]
        axis = frames[joint][:3,:3]@j["axis"]
        downstream = descendants(j["child"])
        return sum(float(np.cross(pos-p, [0,0,-mass*G])@axis)
                   for link, mass, pos in body_list if link in downstream)

    tool = frames["gripper_frame_joint"][:3,3]
    fingertip = tool + frames["gripper_frame_joint"][:3,:3]@np.array([0,0,kin.GRIPPER_TIP])
    data = {}
    for variant, bb in bodies.items():
        torques = {j: torque(bb, j) for j in ["shoulder_pan", *pitch, "wrist_roll"]}
        empty = abs(torques["shoulder_lift"])
        payload_tool_per_kg = abs(torque([("gripper_link",1,tool)], "shoulder_lift"))
        payload_tip_per_kg = abs(torque([("gripper_link",1,fingertip)], "shoulder_lift"))
        data[variant] = dict(total_model_mass_g=sum(m for _,m,_ in bb)*1000,
            gravity_torque_Nm=torques,
            shoulder_payload_tool_Nm_per_kg=payload_tool_per_kg,
            shoulder_payload_tip_Nm_per_kg=payload_tip_per_kg,
            shoulder_torque_by_payload_Nm={str(g): empty+g/1000*payload_tool_per_kg for g in [0,100,250,500]},
            optimistic_rated_static_payload_tool_g=max(0,(RATED-empty)/payload_tool_per_kg*1000),
            optimistic_stall_static_payload_tool_g=max(0,(STALL-empty)/payload_tool_per_kg*1000))
    total_print = sum(s["original"]["part_mass_g"] for s in slices.values())
    residual = 810-330-total_print
    shoulder = frames["shoulder_lift"][:3,3]
    output = dict(
        input_sha256={
            "so101_new_calib.urdf": hashlib.sha256(urdf.read_bytes()).hexdigest(),
            "software/kinematics.py": hashlib.sha256(Path(kin.__file__).read_bytes()).hexdigest(),
            "software/calibration/wk_soarm101.json": hashlib.sha256(kin.CALIBRATION_JSON.read_bytes()).hexdigest(),
            "slices-p3.json": hashlib.sha256((HERE/"analysis/slices-p3.json").read_bytes()).hexdigest(),
        },
        pitch_limits_radians={j:list(joints[j]["limit"]) for j in pitch},
        gravity_m_s2=G, nominal_servo_mass_g=55, servos=6,
        rated_torque_Nm=RATED, stall_torque_Nm=STALL,
        pose_degrees={n:float(np.degrees(x)) for n,x in q.items()},
        shoulder_to_tool_m=float(np.linalg.norm(tool-shoulder)),
        shoulder_to_fingertip_m=float(np.linalg.norm(fingertip-shoulder)),
        horizontal_tool_lever_m=float(tool[0]-shoulder[0]),
        unexplained_mass_vs_810_g=residual,
        residual_at_tool_adds_shoulder_Nm=max(0,residual)/1000*data["original"]["shoulder_payload_tool_Nm_per_kg"],
        assumptions=["CAD joint geometry with existing measured travel limits; pose maximises forward tool reach.",
                     "Static gravity only: no acceleration, cable loads, impacts, heating or control margin.",
                     "Print COM from toolpaths; six 55 g servos located at CAD case origins.",
                     "Unallocated hardware/wiring/mass discrepancy excluded; payload ceilings are optimistic model calculations, NOT arm ratings.",
                     "Half-print-mass case is a hypothetical scaling of every original print, not a design."],
        models=data)
    (HERE/"analysis/loads.json").write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
