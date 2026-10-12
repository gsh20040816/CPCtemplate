"""Compare exact pre-change and current FPS code in fresh processes."""
from pathlib import Path
import hashlib
import json
import statistics
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
out = root / 'build/modint-normalization'
baseline = out / 'baseline'
revision = '00a4cf0'
paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', revision, 'src/compact'], text=True).splitlines()
paths += ['tests/fps_inverse_sqrt_benchmark.cpp', 'tests/fixtures/wida_montgomery_poly/12C.cpp']
for path in paths:
    dest = baseline / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(subprocess.check_output(['git', 'show', f'{revision}:{path}']))
for label, directory in [('before', baseline), ('after', root)]:
    subprocess.run([CXX, '-std=c++20', '-O2', str(directory / 'tests/fps_inverse_sqrt_benchmark.cpp'), '-o', str(out / label)], check=True)
rows = []
for n in [32768, 131072]:
    runs = []
    for repeat in range(5):
        order = ['before', 'after', 'original']
        if repeat % 2:
            order.reverse()
        for label in order:
            exe = out / ('after' if label == 'original' else label)
            mode = 'original' if label == 'original' else 'composition'
            seconds = float(subprocess.check_output([str(exe), str(n), mode], text=True, timeout=120))
            runs.append(dict(label=label, repeat=repeat, seconds=seconds))
    medians = {label: statistics.median(r['seconds'] for r in runs if r['label'] == label) for label in ['before', 'after', 'original']}
    rows.append(dict(n=n, runs=runs, medians=medians, after_over_before=medians['after']/medians['before'], after_over_original=medians['after']/medians['original']))
report = dict(scope='Local fresh-process FPS inverse square root, first call only, every output coefficient checked against 1-x. No OJ or SOTA claim.', baseline_revision=subprocess.check_output(['git', 'rev-parse', revision], text=True).strip(), compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0], rows=rows)
report['files'] = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths if (root/p).exists()}
report['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(out / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
(root / 'verification/modint-normalization-performance.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(rows, indent=2), flush=True)
