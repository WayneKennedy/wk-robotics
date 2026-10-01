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
MODEL = {'kind': 'reference', 'name': 'Motor_holder_SO101_Base', 'variant': 'lightweight-v1', 'source': '../lightweight-v1/step/Motor_holder_SO101_Base.step', 'source_sha256': 'fb2ef4603324ddea53ab655f6ecd48c7f5a72dd7603e57e92c60c0a8e67a9083', 'upstream_path': 'STEP/SO101/Motor_holder_SO101_Base.step', 'upstream_identical': True, 'role': 'printed', 'slug': 'lightweight-v1__step__Motor_holder_SO101_Base'}

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
