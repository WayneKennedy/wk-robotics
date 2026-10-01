# SPDX-License-Identifier: MIT
"""Rebuild this exact model in FreeCAD from the frozen builder in
sources/2eb48b4dd85eb3ac44a9bdac5ce36aba55de7b5d2c1e8cbb565f6bcfff38fc95/. Run with ./freecad-run PATH, or in FreeCAD's Python console:
    p = r"<absolute path to this file>"
    exec(compile(open(p).read(), p, "exec"), {"__name__": "__main__", "__file__": p})
It creates a new document and never closes or overwrites an existing one.
"""
from pathlib import Path
import sys

SOURCE_REVISION = '2eb48b4dd85eb3ac44a9bdac5ce36aba55de7b5d2c1e8cbb565f6bcfff38fc95'
MODEL = {'kind': 'reference', 'name': 'WaveShare_Mounting_Plate_SO101', 'variant': 'lightweight-v1', 'source': '../lightweight-v1/step/WaveShare_Mounting_Plate_SO101.step', 'source_sha256': '9531e7ff46908473217ad314e9a5bd63fb043fae2603c61f9170bbdca28c8ef1', 'upstream_path': 'STEP/SO101/WaveShare_Mounting_Plate_SO101.step', 'upstream_identical': False, 'role': 'prototype', 'slug': 'lightweight-v1__step__WaveShare_Mounting_Plate_SO101'}

if __name__ == "__main__":
    here = Path(__file__).resolve()
    root = next(p for p in here.parents if (p / "sources" / SOURCE_REVISION).is_dir())
    sys.modules.pop("so101_freecad", None)   # FreeCAD's interpreter persists between runs
    sys.path.insert(0, str(root / "sources" / SOURCE_REVISION))
    try:
        from so101_freecad import replay
    finally:
        sys.path.pop(0)
    replay(here, MODEL)
