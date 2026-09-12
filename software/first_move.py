#!/usr/bin/env python3
"""First move under torque: hold the current pose, then nudge one joint at a time and return.

Usage: first_move.py [--port /dev/ttyACM0] [--id wk_soarm101] [--delta 5] [--dwell 1.0] [--joints a,b]

Connects as LeRobot's so101_follower with the saved calibration (connect-time configure():
position mode, PID 16/0/32, gripper torque capped at 50 %). Joints in degrees, gripper in
0..100. Default order: wrist_roll, wrist_flex, gripper, elbow_flex, shoulder_lift,
shoulder_pan. Torque is released at the end, so start it at a pose the arm can rest in.

Guards, added after 2026-09-12's first attempt drove the elbow into its stop off a bad read:
  * every present-position read is retried and must lie inside the saved range and within
    --max-jump of the previous read for that joint, or the run aborts with torque still
    holding the last good pose;
  * commanded goals are clamped to the saved range less --margin degrees, not just stepped;
  * start from a pose where no joint is in contact — the folded rest pose is not one.
"""
import argparse
import time

from lerobot.robots.so_follower import SOFollower, SOFollowerRobotConfig

ORDER = ["wrist_roll", "wrist_flex", "gripper", "elbow_flex", "shoulder_lift", "shoulder_pan"]


def raw_to_norm(r, m, raw):
    c = r.calibration[m]
    if m == "gripper":
        return (raw - c.range_min) / (c.range_max - c.range_min) * 100
    return (raw - 2047) / 4095 * 360


def limits_norm(r, m, margin):
    c = r.calibration[m]
    lo, hi = raw_to_norm(r, m, c.range_min), raw_to_norm(r, m, c.range_max)
    if m == "wrist_roll":
        return -180 + margin, 180 - margin
    return lo + margin, hi - margin


def read_checked(r, prev, max_jump):
    obs = {k: v for k, v in r.get_observation().items() if k.endswith(".pos")}
    raw = r.bus.sync_read("Present_Position", normalize=False, num_retry=5)
    for m in r.bus.motors:
        c = r.calibration[m]
        if not (0 <= raw[m] <= 4095):
            raise RuntimeError(f"{m}: raw position {raw[m]} out of encoder range — refusing to act")
        if m != "wrist_roll" and not (c.range_min - 200 <= raw[m] <= c.range_max + 200):
            raise RuntimeError(f"{m}: raw {raw[m]} outside saved range {c.range_min}..{c.range_max} — refusing to act")
        if prev is not None and abs(obs[m + ".pos"] - prev[m + ".pos"]) > max_jump:
            raise RuntimeError(f"{m}: jumped {prev[m+'.pos']:.1f} → {obs[m+'.pos']:.1f} between reads — refusing to act")
    return obs, raw


def readings(r):
    cur = r.bus.sync_read("Present_Current", normalize=False, num_retry=5)
    tmp = r.bus.sync_read("Present_Temperature", normalize=False, num_retry=5)
    load = r.bus.sync_read("Present_Load", normalize=False, num_retry=5)
    return cur, tmp, load


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", default="/dev/ttyACM0")
    ap.add_argument("--id", default="wk_soarm101")
    ap.add_argument("--delta", type=float, default=5.0)
    ap.add_argument("--dwell", type=float, default=1.0)
    ap.add_argument("--margin", type=float, default=5.0, help="degrees kept clear of the saved range ends")
    ap.add_argument("--max-jump", type=float, default=30.0, help="degrees a joint may differ between consecutive reads")
    ap.add_argument("--joints", default=",".join(ORDER))
    a = ap.parse_args()
    joints = [j for j in a.joints.split(",") if j]

    r = SOFollower(SOFollowerRobotConfig(port=a.port, id=a.id, max_relative_target=a.delta))
    r.connect(calibrate=True)                      # torque ON after configure()
    held = None
    try:
        start, raw = read_checked(r, None, a.max_jump)
        cur, tmp, load = readings(r)
        print("| Joint | Start | Raw | Range (norm) | Current (mA) | Load | °C |\n|---|---|---|---|---|---|---|")
        for m in r.bus.motors:
            lo, hi = limits_norm(r, m, a.margin)
            print(f"| `{m}` | {start[m+'.pos']:.1f} | {raw[m]} | {lo:.0f}..{hi:.0f} | {cur[m]*6.5:.0f} | {load[m]} | {tmp[m]} |")
        r.send_action(dict(start)); held = dict(start); time.sleep(a.dwell)
        prev = start

        print("\n| Joint | Command | Reached | Δ | Current (mA) | Load | °C |\n|---|---|---|---|---|---|---|")
        for m in joints:
            key = m + ".pos"
            lo, hi = limits_norm(r, m, a.margin)
            for sign in (+1, -1, 0):
                target = dict(start)
                target[key] = min(max(start[key] + sign * a.delta, lo), hi)
                r.send_action(target); held = target; time.sleep(a.dwell)
                obs, _ = read_checked(r, prev, a.max_jump); prev = obs
                cur, tmp, load = readings(r)
                print(f"| `{m}` | {target[key]:.1f} | {obs[key]:.1f} | {obs[key]-target[key]:+.1f} | {cur[m]*6.5:.0f} | {load[m]} | {tmp[m]} |")
        r.send_action(dict(start)); held = dict(start); time.sleep(a.dwell)
        end, _ = read_checked(r, prev, a.max_jump)
        print("\nback at start, max |Δ| = %.1f → torque off" % max(abs(end[k] - start[k]) for k in start))
    except Exception as e:
        print(f"\nABORTED: {e}\nTorque left ON holding the last commanded pose {held}. Run release_torque.py when the arm is supported.")
        raise SystemExit(1)
    else:
        r.disconnect()


if __name__ == "__main__":
    main()
