#!/usr/bin/env python3
"""Official HDU protocols and exact submitted/copy-source correspondence."""
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import records
from audit_copy_context import candidate, extract_components
build = root / 'build/hdu-source-completion'
components = {r['symbol']: r for r in extract_components(json.loads((root / 'docs/catalog.json').read_text()))}
rows = {r['id']: r for r in records()}
rng = random.Random(20261012)
chain = [('2\n3\n2 0 0\n0 1 0\n0 1 1\n5\n3 0 0\n0 1 0\n0 0 1\n0 2 2\n3 3 3\n', '2 1\n3 2\n')]
for case in range(100):
    n = case % 40 + 1
    points = set()
    while len(points) < n:
        points.add(tuple(rng.choice([0, 1, 2, 3, 1 << 30]) for _ in range(3)))
    points = sorted(points)
    length, ways = [], []
    for i, v in enumerate(points):
        length.append(1)
        ways.append(1)
        for j, u in enumerate(points[:i]):
            if not all(u[d] <= v[d] for d in range(3)):
                continue
            if length[j] + 1 > length[i]:
                length[i], ways[i] = length[j] + 1, ways[j]
            elif length[j] + 1 == length[i]:
                ways[i] = (ways[i] + ways[j]) % (1 << 30)
    best = max(length)
    count = sum(w for l, w in zip(length, ways) if l == best) % (1 << 30)
    rng.shuffle(points)
    chain.append(('1\n' + str(n) + '\n' + ''.join(' '.join(map(str, p)) + '\n' for p in points), f'{best} {count}\n'))
# Three maximum-size official cases: chain, antichain, and equality on two axes.
n = 100000
chain.append(('3\n' + ''.join(str(n) + '\n' + ''.join(f'{i} {i if mode == 0 else n - i if mode == 1 else 0} {i if mode == 0 else 0}\n' for i in range(n)) for mode in range(3)), f'{n} 1\n1 {n}\n{n} 1\n'))
shift = [('2 1 2 3\n0 1\n', '4\n7\n')]
p = 1000003
for case in range(100):
    n = case % 35 + 1
    b, c, d = [rng.randint(1, 1000000) for _ in range(3)]
    a = [rng.randint(0, 1000000) for _ in range(n)]
    ans = []
    for k in range(n):
        x = (b * pow(c, 2 * k, p) + d) % p
        value = 0
        for v in reversed(a):
            value = (value * x + v) % p
        ans.append(value)
    shift.append((f'{n} {b} {c} {d}\n' + ' '.join(map(str, a)) + '\n', ''.join(f'{v}\n' for v in ans)))
a = [rng.randint(0, 1000000) for _ in range(100000)]
value = 0
for v in reversed(a):
    value = (value * 1000000 + v) % p
shift.append(('100000 1 1 999999\n' + ' '.join(map(str, a)) + '\n', f'{value}\n' * 100000))
report = {'checked_at': '2026-10-12', 'scope': 'Official-domain protocols plus archived minimal-copy identity; no inferred compiler flags for HDU.', 'runs': []}
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for pid, rid, cases in [('4742', 'example-273', chain), ('4656', 'example-347', shift)]:
    source = root / f'verification/submitted/HDU{pid}.compact.cpp'
    row = rows[rid]
    assert source.read_text() == candidate(row, row['requires'], components)['program']
    for mode in ('normal', 'sanitizer'):
        exe = build / f'official-{pid}-{mode}'
        flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=all']
        subprocess.run([CXX, '-std=c++20', *flags, str(source), '-o', str(exe)], check=True)
        for raw, expected in cases:
            result = subprocess.run([str(exe)], input=raw, capture_output=True, text=True, env=env, timeout=60)
            assert result.returncode == 0 and result.stdout == expected and not result.stderr, (pid, mode, result.stderr)
        report['runs'].append({'problem': pid, 'mode': mode, 'program_invocations': len(cases), 'submitted_sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
        print(pid, mode, len(cases), 'PASS', flush=True)
report['runner_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(root / 'verification/hdu-source-completion-local.json').write_text(json.dumps(report, indent=2) + '\n')
