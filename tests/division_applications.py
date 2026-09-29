"""P3834 division-tree driver vs independent sorting and maximum-size formulas."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
mode = 'san' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-std=c++20', '-O2'] if mode == 'normal' else ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
source = root / f'build/division-P3834-{mode}.cpp'
exe = source.with_suffix('')
subprocess.run(['python3', str(root / 'tools/bundle.py'), str(root / 'verify/luogu/P3834.division.compact.cpp'), str(source)], check=True)
subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)


def check(a, qs, answers):
    data = f'{len(a)} {len(qs)}\n' + ' '.join(map(str, a)) + '\n'
    data += ''.join(f'{l + 1} {r} {k + 1}\n' for l, r, k in qs)
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=90)
    assert not p.stderr, p.stderr
    assert p.stdout.split() == list(map(str, answers))


rng = random.Random(2026093004)
for t in range(240):
    n = rng.randrange(1, 100)
    a = [rng.randrange(4) if t % 2 else rng.randrange(10**9 + 1) for _ in range(n)]
    qs, answers = [], []
    for _ in range(60):
        l = rng.randrange(n)
        r = rng.randrange(l + 1, n + 1)
        k = rng.randrange(r - l)
        qs.append((l, r, k))
        answers.append(sorted(a[l:r])[k])
    check(a, qs, answers)
for mode in range(3):
    n = 200000
    a = list(range(n)) if mode == 0 else list(reversed(range(n))) if mode == 1 else [10**9] * n
    qs, answers = [], []
    for _ in range(n):
        l = rng.randrange(n)
        r = rng.randrange(l + 1, n + 1)
        k = rng.randrange(r - l)
        qs.append((l, r, k))
        answers.append(a[l + k] if mode == 0 else a[r - 1 - k] if mode == 1 else 10**9)
    check(a, qs, answers)
print('Division P3834 PASS: 240 independent sorting inputs; three N=Q=200000 increasing/decreasing/equal inputs')
