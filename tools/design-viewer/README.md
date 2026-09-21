# Design viewer

**A local 3D viewer for externally designed robots this family is studying.** It renders
upstream geometry as published — an assembly you can orbit, and every part laid out
separately so a single one can be inspected on its own.

It is the same instrument as koala-bot's
[`viewer.py`](https://github.com/WayneKennedy/koala-bot/blob/main/hardware/src/koala_hardware/viewer.py):
same encoding, same palette, same controls. The difference is the input. Koala's viewer
generates geometry from parametric build123d source that the repo owns; this one reads
meshes somebody else published, and owns none of them.

**What it is not.** An inspection aid, nothing more. It establishes nothing about fit,
clearance, printability, strength or whether a design works. Where it prints a number —
a bounding box, a bed-contact area, an overhang fraction — that number describes the mesh
as supplied, in the orientation as supplied, and a slicer may reorient the part.

## Running it

```sh
./viewer.py --fetch     # clone the upstream sources into upstream/ (gitignored)
./viewer.py             # build, serve on :8019, open a browser
./viewer.py --build     # regenerate build/ only
./viewer.py --serve     # serve an existing build/ without rebuilding
./viewer.py --design bimo
```

### Reaching it from another device

The reference workstation is headless, so `localhost` is only useful on the box itself. The pattern is
koala-bot's, and the server does not need rebinding: it stays on loopback and Tailscale
fronts it over HTTPS, tailnet only.

```sh
sudo tailscale serve --bg --https=8444 http://127.0.0.1:8019
```

koala's viewer holds 8443; this one takes 8444. No tailnet address or hostname appears in
this repo — it is public, and `AGENTS.md` bars them. `--host` exists on the script for the
rare case a direct bind is wanted, and defaults to loopback; prefer `tailscale serve`,
which adds HTTPS and does not put the page on any other interface.

[`systemd/design-viewer.service`](systemd/design-viewer.service) runs it across reboots,
with the same install steps and `ExecStartPre` rebuild that `koala-viewer.service` uses.

The script is a [PEP 723](https://peps.python.org/pep-0723/) single file: `uv` resolves
`numpy`, `trimesh` and `usd-core` on first run, and there is no project to install. Adding
`fast-simplification` to the environment enables decimation of bought-part meshes; without
it they are kept at full detail and `build/` is larger.

Neither `upstream/` nor `build/` is committed. The upstream checkouts are ~250 MB and
belong to their authors; the build output is derived. Only `viewer.py`, `viewer.html`,
`vendor/` and this file are in the repo.

## Controls

Drag to orbit, shift-drag or right-drag to pan, wheel to zoom. **Iso / Front / Side / Top**
snap the camera. In the sidebar, **click a part to solo it** and shift-click to hide it;
the search box filters the list and the scene together. The footer toggles servo bodies
and bought hardware independently, so a bracket can be seen with and without the servo it
wraps.

## The designs

### Open Duck Mini v2 — `apirrone/Open_Duck_Mini`, branch `v2`, Apache-2.0

The one on this page that can actually be built. See
[`docs/ideas.md`](../../docs/ideas.md#open-duck-mini-v2) for why it is parked and what
building it would cost.

- **Assembly** — 131 meshes placed from `mini_bdx/robots/open_duck_mini_v2/robot.urdf` at
  the zero pose, converted from metres to mm and stood on the floor. Joints are not
  driven, so nothing here shows clearance through travel. The zero pose holds the legs
  dead straight, which is not the crouch it walks in: it measures 430 mm to the head and
  518 mm to the antenna tips, against the ~42 cm upstream quotes.
- **Parts** — the 36 STLs in `print/`, in the orientation upstream ships them, with
  quantities and materials parsed out of `docs/print_guide.md` (51 pieces in total, one
  pair in TPU).
- **Servo bodies are called out separately.** The `wj-wk00-*` meshes are the three STS3215
  case shells — 45.22 × 24.72 mm, matching the Waveshare ST3215 drawing quoted in
  [`docs/common.md`](../../docs/common.md#actuators) — and there are 14 servos in the
  assembly. Toggling them off leaves the brackets that carry them.

### Bimo — `mekion/the-bimo-project`, Apache-2.0

**Read this before drawing conclusions from it.** Upstream publishes **no CAD**: no STL,
no STEP, no URDF, and its README still says CAD files are coming soon. The only geometry
in the repo is `IsaacLab/bimo/assets/Bimo.usd`, a simulation asset. Its shapes are
simplified for physics, they cannot be printed, and they should not be measured from.
What it is good for is seeing the arrangement — how an 8-DOF STS3215 biped carries its
servos.

Nine meshes, five distinct: the left and right bodies reuse one authored geometry, so the
parts tab lists each once with a quantity.

**A unit discrepancy worth knowing about.** The stage declares `metersPerUnit = 0.01`, but
the authored data is metric — the hip-to-foot translate is 0.4028 and the thigh mesh spans
0.22, on a robot upstream documents as 45 cm. Taking the declared unit produces a 5 mm
robot. The loader treats the numbers as metres and says so in a comment rather than trust
a header the asset contradicts. At that scale the default pose measures 506 mm tall, which
is more than the quoted 45 cm and is **unverified** — most likely a straight-legged pose
against a quoted standing height, the same gap the duck shows, but that has not been
confirmed.

## Adding a design

Add an entry to `SOURCES` and a builder function returning `{label, assembly, parts, meta}`,
then register it in `BUILDERS`. A builder's job is to produce `_item(...)` records; the
two existing ones show the two shapes that keep recurring — URDF plus mesh directory, and
a USD stage. `meta` carries the bed, the design rule and the notes the viewer prints
beneath a selection, including any warning that belongs on every part of that design.

## Vendored

`vendor/three-r128.min.js` is Three.js r128 from the cdnjs distribution, MIT, with its
licence alongside — the same copy koala-bot vendors, so the viewer works without CDN
access. It is copied into `build/` at build time.
