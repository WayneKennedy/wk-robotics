#!/usr/bin/env python3
"""Cycle every joint through its saved travel, one joint at a time, until the pack is spent.

Usage: extents_cycle.py [--cycles N | until stopped] [--stop-volts 11.0] [--warn-volts 11.3]
                        [--margin-deg 3] [--speed 600] [--accel 30] [--settle 0.6]
                        [--stop-file software/.stop_cycle] [--log path]

Precondition: torque already ON and holding (hold_test.py --keep). This tool never toggles
torque. It first moves to the calibration mid pose (raw 2047 on every joint — the pose the
extents were swept from, so single-joint excursions from it replay the swept, collision-free
envelope), then for each joint: mid → upper limit − margin → lower limit + margin → mid,
gently (Goal_Velocity / Acceleration in RAM), and repeats. After every move it checks:
  tracking   |present − goal| ≤ --track counts once Moving clears, else STALL → park, stop
  current    any servo > --max-ma sustained across a step → park, stop
  temperature any servo > --max-temp °C → park, stop
  voltage    min servo rail < --stop-volts, judged only at the mid pose (unloaded; the rail
             sags ~0.9 V under a holding load) → park, stop; loaded readings warn below --warn-volts
  stop file  exists → park, stop
"Park" = command mid on all joints and leave torque ON. One CSV line per move in --log.
"""
import argparse
import csv
import sys
import time
from pathlib import Path

from lerobot.robots.so_follower import SOFollower, SOFollowerRobotConfig

HERE = Path(__file__).resolve().parent
ORDER = ["wrist_roll", "gripper", "wrist_flex", "elbow_flex", "shoulder_pan", "shoulder_lift"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", default="/dev/ttyACM0"); ap.add_argument("--id", default="wk_soarm101")
    ap.add_argument("--cycles", type=int, default=0, help="0 = until a stop condition")
    ap.add_argument("--stop-volts", type=float, default=11.0); ap.add_argument("--warn-volts", type=float, default=11.3)
    ap.add_argument("--margin-deg", type=float, default=3.0)
    ap.add_argument("--speed", type=int, default=600, help="Goal_Velocity, steps/s (4095 = one turn)")
    ap.add_argument("--accel", type=int, default=30, help="Acceleration register, 0..254")
    ap.add_argument("--settle", type=float, default=0.6); ap.add_argument("--move-timeout", type=float, default=8.0)
    ap.add_argument("--track", type=int, default=120, help="counts of tracking error tolerated after a move")
    ap.add_argument("--max-ma", type=float, default=900); ap.add_argument("--max-temp", type=int, default=60)
    ap.add_argument("--stop-file", default=str(HERE / ".stop_cycle"))
    ap.add_argument("--log", default=str(HERE / "logs" / f"extents_{time.strftime('%Y%m%d_%H%M%S')}.csv"))
    a = ap.parse_args()
    Path(a.log).parent.mkdir(exist_ok=True)
    stop_file = Path(a.stop_file); stop_file.unlink(missing_ok=True)

    r = SOFollower(SOFollowerRobotConfig(port=a.port, id=a.id, max_relative_target=None)); b = r.bus
    b.connect(handshake=False)
    margin = round(a.margin_deg / 360 * 4095)

    def tele():
        p = b.sync_read("Present_Position", normalize=False, num_retry=5)
        c = b.sync_read("Present_Current", normalize=False, num_retry=5)
        t = b.sync_read("Present_Temperature", normalize=False, num_retry=5)
        v = b.sync_read("Present_Voltage", normalize=False, num_retry=5)
        mv = b.sync_read("Moving", normalize=False, num_retry=5)
        return p, {m: c[m] * 6.5 for m in c}, t, {m: v[m] / 10 for m in v}, mv

    def park(reason):
        b.sync_write("Goal_Position", {m: 2047 for m in b.motors}, normalize=False)
        print(f"\n== {reason} → parked at mid, torque LEFT ON ==")

    try:
        if not r.is_calibrated:
            print("servos do not match saved calibration — refusing"); return 2
        te = {m: b.read("Torque_Enable", m, normalize=False, num_retry=5) for m in b.motors}
        if not all(v == 1 for v in te.values()):
            print(f"torque not on everywhere {te} — run hold_test.py --keep first"); return 2
        for m in b.motors:
            b.write("Acceleration", m, a.accel, num_retry=5)
            b.write("Goal_Velocity", m, a.speed, normalize=False, num_retry=5)
            b.write("Torque_Limit", m, 1000, normalize=False, num_retry=5)
        lim = {m: (c.range_min + margin, c.range_max - margin) for m, c in r.calibration.items()}
        lim["wrist_roll"] = (2047 - 1400, 2047 + 1400)          # full-turn joint: ±123°, keep cables sane
        print("targets (raw):", lim)

        log = open(a.log, "a", newline=""); w = csv.writer(log)
        if log.tell() == 0:
            w.writerow(["t", "cycle", "joint", "goal", "reached", "err", "peak_mA", "max_temp", "min_V", "dur_s"])

        def move(cycle, joint, goal_raw):
            goals = {m: 2047 for m in b.motors}; goals[joint] = goal_raw
            t0 = time.time(); peak = 0.0
            b.sync_write("Goal_Position", goals, normalize=False)
            while True:
                p, c, t, v, mv = tele()
                peak = max(peak, max(c.values()))
                done = abs(p[joint] - goal_raw) <= a.track and not any(mv.values())
                if done or time.time() - t0 > a.move_timeout:
                    break
                time.sleep(0.05)
            time.sleep(a.settle)
            p, c, t, v, mv = tele()
            err = p[joint] - goal_raw; dur = time.time() - t0
            w.writerow([round(time.time(), 1), cycle, joint, goal_raw, p[joint], err, round(peak), max(t.values()), min(v.values()), round(dur, 2)]); log.flush()
            print(f"c{cycle} {joint:13s} → {goal_raw:4d}  reached {p[joint]:4d} (err {err:+4d})  peak {peak:4.0f} mA  T {max(t.values())}°C  V {min(v.values()):.1f}  {dur:.1f}s")
            if abs(err) > a.track:
                park(f"STALL: {joint} err {err} after {dur:.1f}s"); return False
            if max(c.values()) > a.max_ma:
                park(f"CURRENT: {max(c, key=c.get)} {max(c.values()):.0f} mA sustained"); return False
            if max(t.values()) > a.max_temp:
                park(f"TEMPERATURE: {max(t, key=t.get)} {max(t.values())} °C"); return False
            # The rail sags ~0.9 V under a holding load (2026-09-12: 10.8 V loaded, 11.7 V at mid),
            # so the stop decision uses the reading at mid (all joints at 2047, ~0 mA); loaded
            # readings only warn.
            at_mid = goal_raw == 2047
            if at_mid and min(v.values()) < a.stop_volts:
                park(f"PACK LOW: {min(v.values()):.1f} V at rest < {a.stop_volts}"); return False
            if min(v.values()) < a.warn_volts:
                print(f"   warning: pack {min(v.values()):.1f} V{'' if at_mid else ' (loaded)'}")
            if stop_file.exists():
                park("stop file"); return False
            return True

        if not move(0, "shoulder_pan", 2047):      # go to mid first (all joints commanded to 2047)
            return 1
        cycle = 0
        while a.cycles == 0 or cycle < a.cycles:
            cycle += 1
            for j in ORDER:
                lo, hi = lim[j]
                for g in (hi, lo, 2047):
                    if not move(cycle, j, g):
                        return 1
        park(f"done: {cycle} cycles"); return 0
    except KeyboardInterrupt:
        park("interrupted"); return 1
    except Exception as e:
        try:
            park(f"error: {e}")
        finally:
            return 1
    finally:
        try:
            b.disconnect(disable_torque=False)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
