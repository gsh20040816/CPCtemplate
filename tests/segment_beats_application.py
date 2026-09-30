"""Copied full LC driver vs independent vectors and maximum closed-form cases."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
mode = 'san' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-std=c++20', '-O2'] if mode == 'normal' else [
    '-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
source = root / f'build/segment-beats-driver-{mode}.cpp'
source.parent.mkdir(exist_ok=True)
subprocess.run(['python3', str(root / 'tools/bundle.py'), str(root / 'verify/library_checker/range_chmin_chmax_add_range_sum.compact.cpp'), str(source)], check=True)
exe = source.with_suffix('')
subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)


def run(a, queries, answers):
    data = f'{len(a)} {len(queries)}\n' + ' '.join(map(str, a)) + '\n'
    data += ''.join(' '.join(map(str, q)) + '\n' for q in queries)
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=90)
    assert not p.stderr, p.stderr
    assert p.stdout.split() == list(map(str, answers))


rng = random.Random(2026093004)
for case in range(160):
    n = rng.randrange(1, 101)
    a = [rng.randrange(-100, 101) for _ in range(n)]
    if case % 3 == 0:
        a = [7] * n
    if case % 3 == 1:
        a = [(-1)**i * 10**12 for i in range(n)]
    b, queries, answers = a[:], [], []
    for step in range(300):
        l = rng.randrange(n)
        r = rng.randrange(l + 1, n + 1)
        if step % 7 == 0:
            l, r = 0, n
        kind = rng.randrange(4)
        if kind == 3:
            queries.append((3, l, r))
            answers.append(sum(b[l:r]))
            continue
        x = rng.choice(b) if step % 4 == 0 else rng.randrange(-1000, 1001)
        if kind == 2:
            x = max(-10**12 - min(b[l:r]), min(x, 10**12 - max(b[l:r])))
        queries.append((kind, l, r, x))
        for i in range(l, r):
            b[i] = min(b[i], x) if kind == 0 else max(b[i], x) if kind == 1 else b[i] + x
    queries.extend((3, i, i + 1) for i in range(n))
    answers.extend(b)
    run(a, queries, answers)

# Maximum N=Q, uniform alternating clips/adds: every answer is closed form.
n = 200000
for sign in (-1, 1):
    queries = []
    for _ in range((n - 2) // 2):
        queries.append((2, 0, n, sign * 10**12))
        queries.append((0 if sign > 0 else 1, 0, n, 0))
    queries.extend([(3, 1, n - 1), (3, n // 2, n // 2 + 1)])
    run([0] * n, queries, [0, 0])

# Two values; clipping exactly to the second extrema forces correct descent.
a = [i % 2 for i in range(n)]
queries, answers = [], []
for step in range(n // 4):
    queries.extend([(0, 0, n, 0), (2, 0, n, 1), (1, 0, n, 2), (3, step, n - step)])
    answers.append(2 * (n - 2 * step))
run(a, queries, answers)
print('SegmentBeats full driver PASS: 160 vector-oracle inputs; 3 N=Q=200000 closed-form inputs')
