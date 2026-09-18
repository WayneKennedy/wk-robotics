#!/usr/bin/env python3
"""Trace a shape with the gripper tip, on a loop, under IK and the keep-out.

Usage:  shapes.py --shape square-yz|square-xy|square-xz|cube [--size 0.20] [--centre 0.24,0,0.06]
                  [--pitch 45] [--loops 3 | 0 = until stop file] [--tool-speed 5 (cm/s)] [--dry-run]
                  [--corner-speed 2] [--tool-accel 50] [--goal-velocity 800] [--acceleration 30]
                  [--port /dev/ttyACM0] [--id wk_soarm101] [--stop-file software/.stop_shapes]

--centre is relative to the pan axis: metres forward, left, above the base plate. Every 1 cm
along the shape is solved by IK (position + pitch, warm-started from the previous point) and must
converge within 3 mm, sit inside the URDF and servo limits, clear the bench keep-out
(kinematics.keepout_clear: nothing behind the desk edge outside the cylinder), be free of
self-collision between the capsule hit boxes (kinematics.self_collisions) and move no joint
more than 10° from the previous point; one failure anywhere and nothing moves. The arm first
travels from its present pose to the shape's start on a guarded joint-space line (guarded_move.plan),
then streams the loop at --rate Hz. Guards as
guarded_move.py; on a trip, or the stop file, or Ctrl-C, the goal is rewritten to the present
position and the arm holds, torque on. Precondition: torque ON and holding (hold_test.py --keep).

The loop is time-parameterised, not step-quantised (2026-09-17). The waypoints get a speed
profile — --tool-speed along an edge, easing to --corner-speed through any direction change
over --corner-deg at --tool-accel — which is integrated to a time for each waypoint and then
sampled at --rate. Asking for a speed the rate cannot carry no longer rounds silently: the
profile is honoured in time and the requested rate is held to a deadline, with overruns
counted and reported.

--goal-velocity (reg 46, counts/s) and --acceleration (reg 41) are the servos' own SRAM
limits, exposed here because they were the first suspects for the speed ceiling. **They are
not it** (test-log, 2026-09-17): the cube trips the tracking guard at the same lag, at the
same point, with Goal_Velocity 800 or 2000 and Acceleration 30 or 150, at 104–202 mA. The
ceiling is the servos' position loop — P_Coefficient 16, I_Coefficient 0, both factory
defaults in EEPROM — whose proportional following error rises with speed and has no integral
term to cancel it.

Two telemetry columns serve supply questions: max_mA is the worst single servo (the --max-ma
guard), sum_mA is what the supply actually sees. --min-v trips on a sagging rail; the servos'
own Min_Voltage_Limit is 4.0 V, far below the point where a run misbehaves.
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics as K
from guarded_move import plan as joint_plan, NAMES, MOVING

HERE = Path(__file__).resolve().parent


def shape_segments(shape, c, s):
    c = np.asarray(c, float); h = s / 2
    if shape.startswith("square"):
        pl = shape.split("-")[1]
        P = {"yz": [c + [0, -h, -h], c + [0, h, -h], c + [0, h, h], c + [0, -h, h]],
             "xy": [c + [-h, -h, 0], c + [h, -h, 0], c + [h, h, 0], c + [-h, h, 0]],
             "xz": [c + [-h, 0, -h], c + [h, 0, -h], c + [h, 0, h], c + [-h, 0, h]]}[pl]
        return [(P[i], P[(i + 1) % 4]) for i in range(4)]
    if shape == "cube":
        b = [c + [-h, -h, -h], c + [h, -h, -h], c + [h, h, -h], c + [-h, h, -h]]
        t = [p + [0, 0, s] for p in b]
        path = [b[0], b[1], b[2], b[3], b[0], t[0], t[1], b[1], t[1], t[2], b[2], t[2], t[3], b[3], t[3], t[0], b[0]]
        return list(zip(path, path[1:]))
    raise SystemExit(f"unknown shape {shape}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shape", required=True); ap.add_argument("--size", type=float, default=0.20)
    ap.add_argument("--centre", default="0.24,0,0.06"); ap.add_argument("--pitch", type=float, default=45)
    ap.add_argument("--loops", type=int, default=3); ap.add_argument("--tool-speed", type=float, default=5.0)
    ap.add_argument("--rate", type=float, default=20); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--corner-speed", type=float, help="cm/s through a direction change; default = --tool-speed, i.e. no easing")
    ap.add_argument("--corner-deg", type=float, default=20.0, help="a direction change past this counts as a corner")
    ap.add_argument("--tool-accel", type=float, default=50.0, help="cm/s^2 on the ramps into and out of a corner")
    ap.add_argument("--goal-velocity", type=int, default=800, help="servo slew cap, counts/s (reg 46); ~3000 is the STS3215's free run at 12 V")
    ap.add_argument("--acceleration", type=int, default=30, help="servo acceleration register (reg 41), 0..254")
    ap.add_argument("--max-joint-speed", type=float, default=0.0, help="cap every joint at this many counts/s by stretching the profile in time; 0 = off. Tool-space easing cannot see a joint reversal that the Jacobian makes sharp")
    ap.add_argument("--jaw-cycle", action="store_true", help="drive the gripper closed -> open -> closed across every edge of the path")
    ap.add_argument("--jaw-open-pct", type=float, default=50.0, help="with --jaw-cycle: opening at the middle of an edge, %% of commandable jaw TRAVEL (not gap)")
    ap.add_argument("--track", type=int, default=150); ap.add_argument("--max-ma", type=float, default=900); ap.add_argument("--max-temp", type=int, default=60)
    ap.add_argument("--min-v", type=float, default=10.0, help="trip if the rail sags below this (V); the servos' own fault level is 4.0 V, far too low to protect a run")
    ap.add_argument("--port", default="/dev/ttyACM0"); ap.add_argument("--id", default="wk_soarm101")
    ap.add_argument("--stop-file", default=str(HERE / ".stop_shapes"))
    ap.add_argument("--start-raw", help="dry-run only: pretend the arm is at these six raw counts")
    a = ap.parse_args()
    joints = K.load_urdf(); cal = json.load(open(HERE / "calibration" / f"{a.id}.json"))
    dx, dy, dz = (float(v) for v in a.centre.split(","))
    centre = (K.PAN_AXIS_X + dx, dy, dz)
    stop_file = Path(a.stop_file); stop_file.unlink(missing_ok=True)

    # --- solve the shape
    segs = shape_segments(a.shape, centre, a.size); pts = []; along = []
    for si, (p0, p1) in enumerate(segs):
        n = max(1, int(np.ceil(np.linalg.norm(p1 - p0) / 0.01)))
        ts = np.linspace(0, 1, n + 1)[:-1]
        for k, t in enumerate(ts):
            # the fraction runs 0..1 across the samples this edge OWNS (its last sample, not the
            # shared corner, which belongs to the next edge) so the jaw shuts exactly on it
            pts.append(p0 + (p1 - p0) * t)
            along.append((si, (k / (len(ts) - 1)) if len(ts) > 1 else 0.0))
    pts.append(segs[-1][1]); along.append((len(segs) - 1, 1.0))

    # --- the jaw cycle: closed -> --jaw-open-pct -> closed on every edge, as a triangle in edge fraction.
    # Closed is the lowest commandable opening (servo limit + the 3° planning margin), which
    # calibration/gripper_gap.json records as raw 1357; open is the same margin at the top.
    mrg = round(3 / 360 * 4095)
    jaw_lo = cal["gripper"]["range_min"] + mrg
    jaw_hi = cal["gripper"]["range_max"] - mrg
    jaw_mid = jaw_lo + (jaw_hi - jaw_lo) * max(0.0, min(1.0, a.jaw_open_pct / 100.0))
    # an edge's 1 cm samples straddle its midpoint rather than landing on it, so the raw triangle
    # peaks below the asked-for opening (45.5% instead of 50% on a 12-sample edge). Normalise per
    # edge by the peak its own samples can reach, so --jaw-open-pct is what actually gets commanded.
    _tri = lambda f: 1.0 - abs(2.0 * f - 1.0)
    _peak = {}
    for si, f in along:
        _peak[si] = max(_peak.get(si, 0.0), _tri(f))
    def jaw_at(i):
        if not a.jaw_cycle: return None
        si, f = along[i]
        scale = _tri(f) / _peak[si] if _peak[si] > 0 else 0.0
        return int(round(jaw_lo + (jaw_mid - jaw_lo) * scale))

    q0 = None; sols = []; worst = 0.0; rear = 9; jaw_rear = 9
    for i, p in enumerate(pts):
        r = K.solve(joints, p, pitch=np.radians(a.pitch), q0=q0)
        if r is None or r["err"] > 0.003 or not r["ok"]:
            print(f"point {i} at {np.round(p, 3)}: " + ("no solution" if r is None else f"err {r['err']*1000:.1f} mm limits {r['limits_ok']} keep-out {r['clear']} self-collision {[(a, b, round(c*1000)) for a, b, c in r['self_hits']]}") + " — refused"); return 1
        m = 3 / 360 * 4095
        if not all(cal[j]["range_min"] + m <= r["raw"][j] <= cal[j]["range_max"] - m for j in MOVING):
            print(f"point {i}: outside the servos' saved limits {r['raw']} — refused"); return 1
        if q0 and max(abs(r["q"][j] - q0[j]) for j in MOVING) > np.radians(10):
            print(f"point {i}: joint jump > 10° from the previous point — refused"); return 1
        # K.solve holds the gripper at URDF 0 — its closed stop — so a cycling jaw is a link the
        # path check has never seen. Re-run the capsule and keep-out checks at the jaw angle this
        # point will actually be commanded to, changing nothing else about the accepted solution.
        if a.jaw_cycle:
            jr = jaw_at(i)
            if not (cal["gripper"]["range_min"] + mrg <= jr <= cal["gripper"]["range_max"] - mrg):
                print(f"point {i}: jaw {jr} outside the gripper's saved limits — refused"); return 1
            qj = dict(r["q"]); qj["gripper"] = K.raw_to_rad({"gripper": jr})["gripper"]
            fj = K.fk(joints, qj); hits = K.self_collisions(fj); clr, rj, _ = K.keepout_clear(fj)
            if hits or not clr:
                print(f"point {i} (edge {along[i][0]}, jaw {jr}): " + ("keep-out breached" if not clr else "")
                      + "; ".join(f"{x}–{y} {z*1000:+.0f} mm" for x, y, z in hits) + " — refused"); return 1
            r["jaw"] = jr; jaw_rear = min(jaw_rear, rj)
        q0 = dict(r["q"]); sols.append(r); worst = max(worst, r["err"]); rear = min(rear, r["rear_x"])
    print(f"{a.shape} {a.size*100:.0f} cm, centre {np.round(centre,3)}, pitch {a.pitch}°: {len(pts)} points solved, worst {worst*1000:.1f} mm, rearmost point outside the cylinder x {rear:+.3f} m")
    if a.jaw_cycle:
        print(f"jaw cycle: closed {jaw_lo} -> {int(round(jaw_mid))} ({a.jaw_open_pct:.0f}% of travel) -> closed on each of {len(segs)} edges; "
              f"capsules and keep-out re-checked at every point's own jaw angle, rearmost x {jaw_rear:+.3f} m. "
              f"NOTE gap in mm is calibrated only to raw 1591 = 37 mm, so the opening here is unmeasured")
    first = sols[0]["raw"]

    # --- speed profile over the waypoints, integrated to a time for each (see the docstring)
    n = len(pts)
    vmax = a.tool_speed / 100.0                                     # m/s
    vcor = max((a.corner_speed if a.corner_speed is not None else a.tool_speed) / 100.0, 1e-4)
    acc = max(a.tool_accel / 100.0, 1e-4)                           # m/s²
    seg = [max(float(np.linalg.norm(pts[i + 1] - pts[i])), 1e-9) for i in range(n - 1)]
    dirs = [(pts[i + 1] - pts[i]) / seg[i] for i in range(n - 1)]
    turn = [0.0] * n                                                # the path's corners are its own, not the shape's
    for i in range(1, n - 1):
        turn[i] = float(np.degrees(np.arccos(np.clip(float(np.dot(dirs[i - 1], dirs[i])), -1.0, 1.0))))
    vlim = [vcor if (i in (0, n - 1) or turn[i] > a.corner_deg) else vmax for i in range(n)]
    for i in range(n - 2, -1, -1):                                  # backward: slow enough to make the corner ahead
        vlim[i] = min(vlim[i], float(np.sqrt(vlim[i + 1] ** 2 + 2 * acc * seg[i])))
    for i in range(n - 1):                                          # forward: slow enough to have reached it
        vlim[i + 1] = min(vlim[i + 1], float(np.sqrt(vlim[i] ** 2 + 2 * acc * seg[i])))
    tw = [0.0]
    for i in range(n - 1):
        tw.append(tw[-1] + 2 * seg[i] / (vlim[i] + vlim[i + 1]))
    # A tool-space profile says nothing about joint speed: near some poses the Jacobian turns a
    # gentle tool corner into a hard joint reversal, which is what actually trips the tracking
    # guard (2026-09-18, shoulder_lift reversing at a cube corner). Stretch any segment whose
    # joint delta would exceed the cap.
    slowed = 0
    if a.max_joint_speed > 0:
        jd = [max(abs(sols[i + 1]["raw"][m] - sols[i]["raw"][m]) for m in MOVING) for i in range(n - 1)]
        tw2 = [0.0]
        for i in range(n - 1):
            want = jd[i] / a.max_joint_speed
            have = tw[i + 1] - tw[i]
            if want > have: slowed += 1
            tw2.append(tw2[-1] + max(have, want))
        print(f"joint-speed cap {a.max_joint_speed:.0f} counts/s: {slowed} of {n-1} segments stretched, "
              f"loop {tw[-1]:.1f} s -> {tw2[-1]:.1f} s (mean tool speed {sum(seg)*100/tw2[-1]:.1f} cm/s)")
        tw = tw2
    corners = sum(1 for i in range(1, n - 1) if turn[i] > a.corner_deg)
    print(f"profile: {corners} corners over {a.corner_deg:.0f}°, {min(vlim)*100:.1f}–{max(vlim)*100:.1f} cm/s, "
          f"{a.tool_accel:.0f} cm/s² ramps, Goal_Velocity {a.goal_velocity}; one loop {tw[-1]:.1f} s "
          f"at {a.rate:.0f} Hz = {int(np.ceil(tw[-1]*a.rate))} steps")

    # --- bus
    from lerobot.motors import Motor, MotorNormMode
    from lerobot.motors.feetech import FeetechMotorsBus
    b = None
    if a.start_raw and a.dry_run:
        present = dict(zip(NAMES, (int(x) for x in a.start_raw.split(","))))
    else:
        b = FeetechMotorsBus(a.port, {n: Motor(i + 1, "sts3215", MotorNormMode.RANGE_M100_100) for i, n in enumerate(NAMES)})
        b.connect(handshake=False)
        present = b.sync_read("Present_Position", normalize=False, num_retry=5)
        if not a.dry_run:
            te = {m: b.read("Torque_Enable", m, normalize=False, num_retry=5) for m in NAMES}
            goal = b.sync_read("Goal_Position", normalize=False, num_retry=5)
            # stale goals from an earlier session differ by hundreds of counts; gravity lag under a horizontal forearm is ~30–40
            off = {m: goal[m] - present[m] for m in NAMES if abs(goal[m] - present[m]) > 60}
            if not all(v == 1 for v in te.values()) or off:
                print(f"torque {te}, targets off present {off} — run hold_test.py --keep first"); return 2
    approach, rows, ok = joint_plan(joints, cal, present, first, 1.5)
    print(f"approach to the start: {len(approach)-1} steps, {'OK' if ok else 'REFUSED'}")
    if not ok:
        for k, raw, verdict, r_ in rows:
            if verdict != "ok": print(f"  step {k}: {verdict}"); break
        return 1
    if a.dry_run:
        print("dry run — nothing moved"); return 0

    # --- execute
    for m in NAMES:
        b.write("Acceleration", m, a.acceleration, num_retry=5); b.write("Goal_Velocity", m, a.goal_velocity, normalize=False, num_retry=5)
    DRIVE = MOVING + ["gripper"] if a.jaw_cycle else MOVING          # the approach keeps MOVING: the jaw stays put on the way in
    log = open(HERE / "logs" / f"shapes_{time.strftime('%Y%m%d_%H%M%S')}.csv", "w", newline=""); w = csv.writer(log)
    w.writerow(["t", "loop", "point", *DRIVE, *[m + "_p" for m in DRIVE], "max_mA", "sum_mA", "max_T", "min_V",
                *[m + "_V" for m in NAMES]])
    dt = 1 / a.rate; t0 = time.time(); peak = 0.0

    # ~1.5-2.4% of telemetry reads come back corrupted on this bus — measured across every run
    # since 2026-09-14, not an occasional freak (test-log 2026-09-18). Two bad ones in a row is
    # therefore common, so debouncing alone cannot protect a guard. A servo cannot change
    # temperature by more than a degree or two in one 50 ms step, so reject any sample that does
    # and carry the last good one; a real rise still trips, it just has to be physical.
    warm = {}
    bad_reads = {"n": 0}

    def tele():
        p = b.sync_read("Present_Position", normalize=False, num_retry=5)
        c = b.sync_read("Present_Current", normalize=False, num_retry=5)
        t = b.sync_read("Present_Temperature", normalize=False, num_retry=5)
        v = b.sync_read("Present_Voltage", normalize=False, num_retry=5)
        for m, x in t.items():
            if m in warm and abs(x - warm[m]) > 5:
                bad_reads["n"] += 1; t[m] = warm[m]         # implausible jump: keep the last good
            else:
                warm[m] = x
        # max_mA is the worst single servo — the per-servo guard. sum_mA is what the SUPPLY sees,
        # and is the number that matters for sizing a brick or hunting a brownout (2026-09-17).
        # per-servo volts are kept, not just the minimum: the joints that are NOT moving share the
        # rail with the ones that are, so comparing them separates a real drop in the leads from a
        # servo measuring its own commutation dip (OQ-03, 2026-09-18).
        # The GUARD uses the MEDIAN of the six, not the minimum. A real sag pulls every servo on the
        # shared rail down together; a corrupt frame moves one. min() over six servos and a thousand
        # samples is ~6000 chances to catch a bad frame, which is exactly what produced the phantom
        # "10.5 V rail sag" in every run from 2026-09-14 to 2026-09-18 (OQ-03, closed). The raw
        # minimum is still logged in min_V, and every servo's own reading in the per-servo columns.
        vs = sorted(x / 10 for x in v.values())
        return p, max(c.values()) * 6.5, max(t.values()), (vs[2] + vs[3]) / 2, sum(c.values()) * 6.5, v, vs[0]

    def hold_here(reason):
        p = b.sync_read("Present_Position", normalize=False, num_retry=5)
        b.sync_write("Goal_Position", p, normalize=False)
        print(f"\n== {reason} → holding, torque LEFT ON ==")

    over = {"ma": 0, "T": 0, "V": 0}     # a single bad sample is a corrupted read (130 °C after 38 °C, 2026-09-14): trip on two in a row

    # the period is held to a deadline, so the rate asked for is the rate flown; tele() runs inside it
    clock = {"next": None, "late": 0, "lag": 0, "sum": 0.0, "v": 99.0}

    def step(raw, loop, i, dt_, keys=None):
        nonlocal peak
        keys = keys or MOVING
        b.sync_write("Goal_Position", {m: raw[m] for m in keys}, normalize=False)
        now = time.time()
        clock["next"] = (now + dt_) if clock["next"] is None else (clock["next"] + dt_)
        if clock["next"] > now:
            time.sleep(clock["next"] - now)
        else:
            clock["late"] += 1; clock["next"] = now
        p, ma, T, V, sm, vall, vmin = tele()
        w.writerow([f"{time.time()-t0:.3f}", loop, i, *[raw.get(m, p[m]) for m in DRIVE], *[p[m] for m in DRIVE], f"{ma:.0f}", f"{sm:.0f}", T, f"{vmin:.1f}",
                    *[f"{vall[m]/10:.1f}" for m in NAMES]])
        lag = max(abs(p[m] - raw[m]) for m in keys)
        clock["lag"] = max(clock["lag"], lag); clock["sum"] = max(clock["sum"], sm); clock["v"] = min(clock["v"], V)
        if lag > a.track: hold_here(f"TRACKING lag {lag} at loop {loop} point {i}"); return False
        over["ma"] = over["ma"] + 1 if ma > a.max_ma else 0
        over["T"] = over["T"] + 1 if T > a.max_temp else 0
        over["V"] = over["V"] + 1 if V < a.min_v else 0
        if over["ma"] < 2: peak = max(peak, ma) if ma <= a.max_ma else peak
        if over["ma"] >= 2: hold_here(f"CURRENT {ma:.0f} mA at loop {loop} point {i}"); return False
        if over["T"] >= 2: hold_here(f"TEMPERATURE {T} °C"); return False
        if over["V"] >= 2: hold_here(f"RAIL median {V:.1f} V (below --min-v {a.min_v}) at loop {loop} point {i}, sum {sm:.0f} mA"); return False
        if stop_file.exists(): hold_here("stop file"); return False
        return True

    try:
        for i, raw in enumerate(approach):             # the approach keeps its own safe rate whatever --rate is
            if not step({**present, **raw}, 0, i, 1 / 20): return 1
        if a.jaw_cycle:
            # the jaw may be anywhere (it is not in the approach plan); walk it to the cycle's
            # start at <= 1.5 deg a step rather than jumping, which would trip the tracking guard
            g0, g1 = present["gripper"], sols[0]["jaw"]
            nsg = max(1, int(np.ceil(abs(g1 - g0) / 17)))
            base = {**present, **approach[-1]}
            print(f"jaw to the cycle start: {g0} -> {g1} in {nsg} steps")
            for k in range(1, nsg + 1):
                cmd = dict(base); cmd["gripper"] = int(round(g0 + (g1 - g0) * k / nsg))
                if not step(cmd, 0, i + k, 1 / 20, DRIVE): return 1
        time.sleep(0.5); clock["next"] = None
        T_loop = tw[-1]; nst = max(1, int(np.ceil(T_loop / dt)))
        loop = 0
        while a.loops == 0 or loop < a.loops:
            loop += 1; j = 0; clock["lag"] = 0
            for k in range(1, nst + 1):                # sample the profile in time, not per waypoint
                tk = min(T_loop, k * dt)
                while j < len(tw) - 2 and tw[j + 1] < tk: j += 1
                span = tw[j + 1] - tw[j]
                u = 0.0 if span <= 0 else (tk - tw[j]) / span
                r0, r1 = sols[j]["raw"], sols[j + 1]["raw"]
                cmd = {m: int(round(r0[m] + (r1[m] - r0[m]) * u)) for m in MOVING}
                if a.jaw_cycle:
                    j0, j1 = sols[j]["jaw"], sols[j + 1]["jaw"]
                    # at an edge join the triangle resets 1 -> 0; interpolating across it would
                    # command a half-open jaw that belongs to neither edge, so take the new edge's value
                    cmd["gripper"] = int(round(j0 + (j1 - j0) * u)) if along[j][0] == along[j + 1][0] else j1
                if not step(cmd, loop, j, dt, DRIVE): return 1
            p, ma, T, V, sm, _v, _vm = tele()
            print(f"loop {loop} done  {time.time()-t0:.1f} s  peak {peak:.0f} mA  max lag {clock['lag']} of {a.track}  {T} °C  rail min {clock['v']:.1f} V  sum peak {clock['sum']:.0f} mA"
                  + (f"  LATE {clock['late']}" if clock["late"] else ""))
        p, ma, T, V, sm, _v, _vm = tele(); tcp = K.fk(joints, K.raw_to_rad(p))["gripper_frame_joint"][:3, 3]
        el = time.time() - t0
        # {V} here is the closing sample, not a minimum — labelling it "V min" understated the rail
        # sag by over a volt in every run logged before 2026-09-17. The true minimum is clock["v"].
        print(f"\ndone: {loop} loops, peak {peak:.0f} mA, {T} °C; rail {clock['v']:.1f} V min, {V:.1f} V at rest, "
              f"sum peak {clock['sum']:.0f} mA; tool at {np.round(tcp,3)}; holding at the shape start, torque ON")
        print(f"telemetry: {bad_reads['n']} implausible temperature samples rejected of {loop*nst+len(approach)}")
        print(f"rate: asked {a.rate:.0f} Hz, flew {(loop*nst+len(approach))/el:.1f} Hz over {el:.1f} s, {clock['late']} deadlines missed")
        return 0
    except KeyboardInterrupt:
        hold_here("interrupted"); return 1
    finally:
        log.close()
        try: b.disconnect(disable_torque=False)
        except Exception: pass


if __name__ == "__main__":
    sys.exit(main())
