#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Summarise a bench-record.sh capture: fps, per-stage latency, CPU/GPU load, temperatures, power."""
import json
import re
import statistics as st
import sys
from pathlib import Path

out = Path(sys.argv[1])
rows = [json.loads(l) for l in (out / 'stats.jsonl').read_text().splitlines() if l.startswith('{')]
rows = [r for r in rows if r.get('frames_done', 0) > 0][3:]  # drop warm-up seconds
print(open(out / 'host.txt').read().strip())
print(open(out / 'nvpmodel.txt').read().strip())
if rows:
    print(f'samples {len(rows)}  fps_out mean {st.mean(r["fps_out"] for r in rows):.1f} '
          f'min {min(r["fps_out"] for r in rows):.1f} max {max(r["fps_out"] for r in rows):.1f}')
    for k in rows[-1]['stages']:
        m = [r['stages'][k]['mean_ms'] for r in rows if k in r['stages']]
        p = [r['stages'][k]['p95_ms'] for r in rows if k in r['stages']]
        print(f'  {k:16s} mean {st.mean(m):7.2f} ms   p95 {st.mean(p):7.2f} ms')
# tegrastats: "RAM 2345/7620MB ... CPU [12%@1510,8%@1510,...] ... GR3D_FREQ 45% ... cpu@45.5C soc2@44C ... gpu@44C ... VDD_IN 5432mW/5432mW VDD_CPU_GPU_CV 1234mW/1234mW VDD_SOC 1234mW/..."
cpu, gpu, temps, power = [], [], {}, {}
for line in (out / 'tegrastats.log').read_text().splitlines():
    m = re.search(r'CPU \[([^\]]*)\]', line)
    if m:
        cores = [int(c.split('%')[0]) for c in m.group(1).split(',') if c and c[0].isdigit()]
        if cores:
            cpu.append(sum(cores) / len(cores))
    m = re.search(r'GR3D_FREQ (\d+)%', line)
    if m:
        gpu.append(int(m.group(1)))
    for name, val in re.findall(r'(\w+)@([\d.]+)C', line):
        temps.setdefault(name, []).append(float(val))
    for name, val in re.findall(r'(VDD_\w+) (\d+)mW', line):
        power.setdefault(name, []).append(int(val))
if cpu:
    print(f'CPU mean {st.mean(cpu):.0f}%  GPU (GR3D) mean {st.mean(gpu):.0f}% max {max(gpu)}%')
    print('temps max: ' + ' '.join(f'{k}={max(v):.1f}C' for k, v in sorted(temps.items())))
    print('power mean: ' + ' '.join(f'{k}={st.mean(v):.0f}mW' for k, v in sorted(power.items())))
