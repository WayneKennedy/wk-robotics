#!/usr/bin/env python3
"""Stepwise SO-101 follower calibration — LeRobot's `SOFollower.calibrate()` split into steps.

LeRobot's wizard needs one terminal with the arm being moved between Enter presses. Over
SSH with the arm moved by someone else, run the same writes as separate commands instead:

  calibrate.py home                  arm held at the MIDDLE of every joint's range.
                                     Torque off, Operating_Mode POSITION, then
                                     set_half_turn_homings(): Homing_Offset written so the
                                     current pose reads 2047 on every servo.
  calibrate.py sweep-start           begins recording min/max of every joint except
                                     wrist_roll in the background; move each joint to just
                                     short of both hard stops, then
  calibrate.py sweep-stop            stops recording, writes Min/Max_Position_Limit to the
                                     servos, saves LeRobot's calibration JSON for --id.
  calibrate.py status                what the servos hold now, and what the JSON holds.

Everything written is identical to lerobot-calibrate (0.6.1): homing_offset, range_min,
range_max, drive_mode 0; wrist_roll is a full-turn joint with range 0..4095. State between
steps lives in --state (default: alongside this script, git-ignored).
"""
import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

from lerobot.motors import MotorCalibration
from lerobot.motors.feetech import OperatingMode
from lerobot.robots.so_follower import SOFollower, SOFollowerRobotConfig

FULL_TURN = "wrist_roll"
HERE = Path(__file__).resolve().parent


def make_robot(a):
    cfg = SOFollowerRobotConfig(port=a.port, id=a.id)
    r = SOFollower(cfg)
    r.bus.connect(handshake=False)
    return r


def cmd_home(a):
    r = make_robot(a)
    try:
        r.bus.disable_torque()
        for m in r.bus.motors:
            r.bus.write("Operating_Mode", m, OperatingMode.POSITION.value)
        before = r.bus.sync_read("Present_Position", normalize=False, num_retry=5)
        offsets = r.bus.set_half_turn_homings()
        after = r.bus.sync_read("Present_Position", normalize=False, num_retry=5)
        state = {"homing_offsets": offsets, "raw_before": before, "raw_after": after, "t": time.time()}
        Path(a.state).write_text(json.dumps(state, indent=2))
        print("| Joint | Raw before | Homing_Offset written | Reads now |\n|---|---|---|---|")
        for m in r.bus.motors:
            print(f"| `{m}` | {before[m]} | {offsets[m]} | {after[m]} |")
    finally:
        _quiet_disconnect(r)


def cmd_sweep_start(a):
    st = json.loads(Path(a.state).read_text())
    if "homing_offsets" not in st:
        sys.exit("run `home` first")
    pid = os.fork()
    if pid:  # parent
        st["sweep_pid"] = pid
        Path(a.state).write_text(json.dumps(st, indent=2))
        print(f"recording in background, pid {pid}. Move every joint except {FULL_TURN} to just short of both stops.")
        return
    # child: record until SIGTERM
    r = make_robot(a)
    motors = [m for m in r.bus.motors if m != FULL_TURN]
    pos = r.bus.sync_read("Present_Position", motors, normalize=False, num_retry=5)
    mins, maxes = dict(pos), dict(pos)
    stop = {"flag": False}
    signal.signal(signal.SIGTERM, lambda *_: stop.update(flag=True))
    live = Path(a.state).with_suffix(".sweep.json")
    n = 0
    try:
        while not stop["flag"]:
            try:
                pos = r.bus.sync_read("Present_Position", motors, normalize=False, num_retry=5)
            except ConnectionError:
                continue
            for m in motors:
                mins[m] = min(mins[m], pos[m]); maxes[m] = max(maxes[m], pos[m])
            n += 1
            if n % 10 == 0:
                live.write_text(json.dumps({"mins": mins, "maxes": maxes, "pos": pos, "samples": n}, indent=2))
            time.sleep(0.02)
    finally:
        live.write_text(json.dumps({"mins": mins, "maxes": maxes, "pos": pos, "samples": n, "done": True}, indent=2))
        _quiet_disconnect(r)
    os._exit(0)


def cmd_sweep_stop(a):
    st = json.loads(Path(a.state).read_text())
    live = Path(a.state).with_suffix(".sweep.json")
    pid = st.get("sweep_pid")
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            for _ in range(100):
                try:
                    os.kill(pid, 0); time.sleep(0.05)
                except ProcessLookupError:
                    break
        except ProcessLookupError:
            pass
    for _ in range(50):
        sw = json.loads(live.read_text())
        if sw.get("done"):
            break
        time.sleep(0.05)
    mins, maxes = sw["mins"], sw["maxes"]
    same = [m for m in mins if mins[m] == maxes[m]]
    if same and not a.force:
        sys.exit(f"these joints were not moved: {same} — sweep again, or --force to accept")
    mins[FULL_TURN], maxes[FULL_TURN] = 0, 4095
    r = make_robot(a)
    try:
        r.calibration = {
            m: MotorCalibration(id=mm.id, drive_mode=0, homing_offset=st["homing_offsets"][m],
                                range_min=mins[m], range_max=maxes[m])
            for m, mm in r.bus.motors.items()
        }
        r.bus.disable_torque()                 # writes Lock = 0: EEPROM writes made with Lock 1 are lost at power-off (OQ-12)
        r.bus.write_calibration(r.calibration)
        r._save_calibration()
        print(f"calibration written to servos and saved to {r.calibration_fpath} ({sw['samples']} samples)")
        _print_status(r)
    finally:
        _quiet_disconnect(r)


def cmd_status(a):
    r = make_robot(a)
    try:
        _print_status(r)
    finally:
        _quiet_disconnect(r)


def _print_status(r):
    ho = r.bus.sync_read("Homing_Offset", normalize=False, num_retry=5)
    lo = r.bus.sync_read("Min_Position_Limit", normalize=False, num_retry=5)
    hi = r.bus.sync_read("Max_Position_Limit", normalize=False, num_retry=5)
    pos = r.bus.sync_read("Present_Position", normalize=False, num_retry=5)
    print("| Joint | Homing_Offset | Min_Position_Limit | Max_Position_Limit | Present (raw) |\n|---|---|---|---|---|")
    for m in r.bus.motors:
        print(f"| `{m}` | {ho[m]} | {lo[m]} | {hi[m]} | {pos[m]} |")
    print(f"JSON: {r.calibration_fpath} {'exists' if r.calibration_fpath.is_file() else 'absent'}")


def _quiet_disconnect(r):
    try:
        r.bus.disconnect(disable_torque=False)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["home", "sweep-start", "sweep-stop", "status"])
    ap.add_argument("--port", default="/dev/ttyACM0")
    ap.add_argument("--id", default="wk_soarm101", help="LeRobot robot id; names the calibration JSON")
    ap.add_argument("--state", default=str(HERE / ".calibration_state.json"))
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    {"home": cmd_home, "sweep-start": cmd_sweep_start, "sweep-stop": cmd_sweep_stop, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    main()
