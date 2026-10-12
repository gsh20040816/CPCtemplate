from pathlib import Path
import hashlib
import json
import statistics
import subprocess
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/mod-reduction'
OUT.mkdir(parents=True, exist_ok=True)
baseline_commit = 'd390956'
baseline_path = 'src/compact/dynamic_modint.hpp'
baseline = subprocess.check_output(['git', 'show', baseline_commit + ':' + baseline_path], cwd=ROOT)
(OUT / 'mint-before.hpp').write_bytes(baseline)
exe = OUT / 'benchmark'
subprocess.run([CXX, '-std=c++20', '-O2', '-I' + str(OUT),
                str(ROOT / 'tests/barrett32_benchmark.cpp'), '-o', str(exe)], check=True)
rows = []
for mod in [1, 12, 998244353, 2147483647]:
    runs = {mode: [] for mode in ['before', 'after']}
    values = []
    for repeat in range(3):
        modes = ['before', 'after'] if repeat % 2 == 0 else ['after', 'before']
        for mode in modes:
            answer, elapsed = subprocess.check_output(
                [str(exe), str(mod), '3000000', mode], text=True, timeout=30).split()
            values.append(answer)
            runs[mode].append(float(elapsed))
    assert len(set(values)) == 1
    medians = {mode: statistics.median(values) for mode, values in runs.items()}
    rows.append(dict(mod=mod, iterations=3000000, runs_seconds=runs,
                     median_seconds=medians, after_over_before=medians['after'] / medians['before']))
report = dict(scope='Same local machine, GCC16 C++20 O2, alternating 3 runs of dependent multiply-add chain; not OJ timing or universal speed claim.',
              baseline_commit=baseline_commit, baseline_path=baseline_path,
              baseline_sha256=hashlib.sha256(baseline).hexdigest(), runs=rows)
report['files'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in [
    'tests/barrett32_benchmark.cpp', 'tests/barrett32_benchmark.py',
    'src/compact/barrett32.hpp', 'src/compact/dynamic_modint.hpp']}
(ROOT / 'verification/barrett32-performance.json').write_text(json.dumps(report, indent=2) + '\n')
for row in rows:
    print(row['mod'], row['after_over_before'], flush=True)
