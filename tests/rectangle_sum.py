"""Full rectangle_sum protocol: independent scan oracle, boundaries and sanitizers."""
from pathlib import Path
import hashlib
import json
import os
import random
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
out = root / 'build/rectangle-sum'
out.mkdir(exist_ok=True)
driver = 'verify/library_checker/rectangle_sum.compact.cpp'
source = out / 'submission.cpp'
subprocess.run(['python3', 'tools/bundle.py', driver, str(source)], cwd=root, check=True)
rng = random.Random(432)
cases = []
for trial in range(240):
    points = [(rng.choice([0, 1, 2, 10**9, rng.randrange(10**9)]),
               rng.choice([0, 1, 2, 10**9, rng.randrange(10**9)]),
               rng.choice([0, 10**9, rng.randrange(10**9)]))
              for _ in range(rng.randrange(1, 70))]
    queries = [(0, 0, 10**9, 10**9), (0, 0, 1, 1)]
    for _ in range(100):
        l, r = sorted(rng.sample([0, 1, 2, 3, 10**9 - 1, 10**9], 2))
        d, u = sorted(rng.sample([0, 1, 2, 3, 10**9 - 1, 10**9], 2))
        queries.append((l, d, r, u))
    expected = [sum(w for x, y, w in points if l <= x < r and d <= y < u)
                for l, d, r, u in queries]
    data = f'{len(points)} {len(queries)}\n'
    data += ''.join(' '.join(map(str, p)) + '\n' for p in points + queries)
    cases.append((data, expected))
# Maximum sum and duplicate coordinates; last-coordinate points are excluded.
cases.append(('200000 2\n' + '0 0 1000000000\n' * 199999 +
              '1000000000 1000000000 1000000000\n0 0 1 1\n0 0 1000000000 1000000000\n',
              [199999000000000, 199999000000000]))
results = {}
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    exe = out / mode
    subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)
    for data, expected in cases:
        run = subprocess.run([str(exe)], input=data, text=True, capture_output=True,
                             env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                                      UBSAN_OPTIONS='halt_on_error=1'), timeout=30)
        assert run.returncode == 0 and not run.stderr, run.stderr
        assert list(map(int, run.stdout.split())) == expected
    results[mode] = {'protocols': len(cases), 'flags': flags}
    print(mode, len(cases), 'protocols PASS', flush=True)
report = {'driver': driver, 'bundle_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'scope': 'Independent full-protocol local tests, not online verdict', 'runs': results}
(root / 'verification/rectangle-sum.json').write_text(json.dumps(report, indent=2) + '\n')
