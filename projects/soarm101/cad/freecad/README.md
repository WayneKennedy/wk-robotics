# SO-101 in FreeCAD

**Every SO-101 CAD file this project holds, as a FreeCAD document, and the follower arm as
a posable FreeCAD assembly.** Built 2026-10-01 with FreeCAD 1.1.3 (OCCT 7.8.1), by the
approach koala-bot uses for its STEP references
([its `docs/freecad.md`](https://github.com/WayneKennedy/koala-bot/blob/main/docs/freecad.md)):
Python is the source of truth, each `.FCStd` is generated and paired with a replay script,
and a manifest carries the hashes. FreeCAD is how the family views and designs
([`common.md`](../../../../docs/common.md#cad-and-viewing-freecad)); there is no other viewer
for this arm.

- [`INDEX.md`](INDEX.md) — every document and its replay script (generated).
- [`manifest.json`](manifest.json) — the same, with hashes, solid counts, volumes, bounds.
- [`evidence.json`](evidence.json) — the two checks under [Evidence](#evidence).
- [Decision](../../docs/decisions.md) — DEC-16.

## What is here

| Kind | Count | What |
|---|---:|---|
| Assembly | 2 | `so101-follower`: all upstream parts, the design the commissioned arm was printed from. `so101-follower-lightweight-v1`: the same with the [lightweight study](../lightweight-v1/README.md)'s base and board plate, drawn orange — **unprinted prototypes** |
| STEP reference | 14 | The study's eleven STEP files (nine are byte-identical upstream copies, two are modified), upstream's originals of those two, and upstream's STS3215 servo model |

**A reference is one imported solid.** STEP carries no feature history, so none is
recovered and none is invented; each object's `SO101` properties record its source file,
its SHA-256, the upstream path and whether it is upstream's byte for byte.

**An assembly is upstream's URDF, drawn with those solids.** Each URDF link is an
`App::Part` nested in its parent, so the model tree is the kinematic chain. The six servos
are links to one hidden master solid.

## Open and pose

Open an assembly from [`INDEX.md`](INDEX.md). It opens at upstream's URDF zero pose: pan
straight ahead, upper arm vertical, forearm horizontal.

**To pose the arm, edit column B of the `Joints` spreadsheet** (degrees) and recompute.
Each revolute joint's angle is bound to its cell. Columns C and D show the URDF's limits;
**nothing enforces them**, and this arm's measured limits are in
[`software/kinematics.py`](../../software/kinematics.py), not here. Posing a released file
and saving it changes its hash, and `--check` will then reject it: save a posed copy under
another name.

## Rebuild, check, replay

FreeCAD is a Flatpak on the machine this was built on, and it cannot read the host's
`/tmp`: keep every path under the checkout.

```sh
./freecad-run so101_freecad.py --check     # sources, scripts and documents against the manifest
./freecad-run so101_freecad.py             # rebuild everything, headless
./freecad-run references/<hash>/<name>.py  # replay one model into <name>.rebuilt.FCStd
```

**Release builds are made inside the FreeCAD GUI**, where colours and the camera are saved
natively; through the FreeCAD MCP or the Python console:

```python
import runpy; runpy.run_path("<absolute path>/so101_freecad.py", run_name="__main__")
```

A headless build has the same geometry and visibility and no colours. A build takes about
40 s on the GUI thread, during which FreeCAD does not repaint
([what the desktop then does](../../../../docs/common.md#cad-and-viewing-freecad)).

A build writes `sources/<sha256>/so101_freecad.py`, the builder frozen at that revision;
replay scripts import it from there, so an old revision replays after the builder changes.
Assemblies are stored under the first 16 digits of that revision and references under the
first 16 of their STEP file's hash. Old revisions are kept; nothing prunes them.

## Inputs

| Input | Where | Held how |
|---|---|---|
| The study's eleven STEP files | [`../lightweight-v1/step/`](../lightweight-v1/step/) | Read in place and hash-checked; not copied |
| Upstream `Base_SO101.step`, `WaveShare_Mounting_Plate_SO101.step` | `reference-sources/<sha256>/` | Frozen copies; hashes equal the study's [`source-lock.json`](../lightweight-v1/source-lock.json) |
| Upstream `STEP/SO100/STS3215_03a.step` | `reference-sources/<sha256>/` | Frozen copy; the same file koala-bot vendors |
| Upstream `Simulation/SO101/so101_new_calib.urdf` | `reference-sources/<sha256>/` | Frozen copy: link frames, visual origins, joint origins, axes and limits |

All upstream inputs are from
[TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100/tree/eecbe3e0a9ebb23e25ad7b2759b03884c6660903)
at the revision the study pins. **Upstream remains the design authority**; the frozen
copies exist so a replay needs no sibling checkout. Licence: [`NOTICE`](NOTICE).

## Evidence

`./freecad-run verify.py SIMULATION_DIR` writes [`evidence.json`](evidence.json);
`SIMULATION_DIR` is upstream's `Simulation/SO101` at the pinned revision. Run 2026-10-01:

1. **The STEP solids are in the URDF meshes' frames**, which is what lets the URDF place
   them. 400 vertices of each mesh, in millimetres, against the STEP solid: for the 13
   unmodified pairings the greatest distance is 0.0077 mm and the greatest bounding-box
   difference 0.0053 mm. The study's base differs by up to 9.2 mm, at the windows it cut.
2. **The assemblies' joint frames equal `software/kinematics.py`'s**, which reads the same
   URDF with its own code: all seven frames, at the zero pose and at a test pose, within
   3 × 10⁻¹³ mm and 2 × 10⁻¹⁵ in every rotation-matrix element.
3. **Every document reopens, recomputes and matches** its recorded solid count, volume and
   bounds (`--check`, 16 of 16).

## Limits

- **An inspection assembly, not a solver.** Nothing checks interference, clearance, fit,
  cable routing or strength, at any pose.
- **It is upstream's nominal geometry**, not this arm's: printed-part tolerances, horn
  seating and the measured joint zeros (`software/kinematics.py`, `JOINT_ZERO`) are not in it.
- **One servo is drawn with a horn it does not have**: upstream's mesh for the servo in
  `wrist_link` has no horn, and the STEP model has one. The object carries a note.
- **No screws, bearings, horns as separate parts, cables or electronics**: the URDF has none.
- **The masses in the URDF are not used.** A solid's volume here says nothing about a
  printed part's mass; the study's slicing figures do ([report](../lightweight-v1/report.md)).
