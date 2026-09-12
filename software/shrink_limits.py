#!/usr/bin/env python3
"""Pull every recorded travel limit in by a fraction of its span, at both ends.

Usage: shrink_limits.py [--fraction 0.10] [--port /dev/ttyACM0] [--id wk_soarm101] [--dry-run]

Reads the saved LeRobot calibration for --id, computes new range_min/range_max
(min + f*span, max - f*span) for every joint except wrist_roll (full turn), writes them to the
servos' Min/Max_Position_Limit and back to the JSON, and mirrors the JSON into
software/calibration/. Homing offsets are untouched. Owner's rule 2026-09-12: 10 % each end.
"""
import argparse
import json
import shutil
from pathlib import Path

from lerobot.robots.so_follower import SOFollower, SOFollowerRobotConfig

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fraction", type=float, default=0.10)
    ap.add_argument("--port", default="/dev/ttyACM0")
    ap.add_argument("--id", default="wk_soarm101")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    r = SOFollower(SOFollowerRobotConfig(port=a.port, id=a.id))
    if not r.calibration:
        raise SystemExit(f"no calibration for id {a.id}")
    print(f"| Joint | Old min | Old max | New min | New max | Span → |\n|---|---|---|---|---|---|")
    for m, c in r.calibration.items():
        if m == "wrist_roll":
            print(f"| `{m}` | {c.range_min} | {c.range_max} | {c.range_min} | {c.range_max} | full turn, untouched |")
            continue
        span = c.range_max - c.range_min
        nmin, nmax = round(c.range_min + a.fraction * span), round(c.range_max - a.fraction * span)
        print(f"| `{m}` | {c.range_min} | {c.range_max} | {nmin} | {nmax} | {span} → {nmax-nmin} |")
        c.range_min, c.range_max = nmin, nmax
    if a.dry_run:
        return
    r.bus.connect(handshake=False)
    try:
        r.bus.write_calibration(r.calibration)
        lo = r.bus.sync_read("Min_Position_Limit", normalize=False, num_retry=5)
        hi = r.bus.sync_read("Max_Position_Limit", normalize=False, num_retry=5)
        ok = all(lo[m] == c.range_min and hi[m] == c.range_max for m, c in r.calibration.items())
        print("servos read back:", "match" if ok else f"MISMATCH {lo} {hi}")
    finally:
        try:
            r.bus.disconnect(disable_torque=False)
        except Exception:
            pass
    r._save_calibration()
    shutil.copy(r.calibration_fpath, HERE / "calibration" / r.calibration_fpath.name)
    print("saved", r.calibration_fpath, "and mirrored to software/calibration/")


if __name__ == "__main__":
    main()
