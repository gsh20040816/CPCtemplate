"""Verify P1972 bundles against sets and an optional million-item periodic case."""
from pathlib import Path
import random
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
rng = random.Random(1972)
cases = []
for _ in range(12):
    n = rng.randrange(1, 70)
    a = [rng.randrange(1, 20) for _ in range(n)]
    queries = []
    for _ in range(200):
        l = rng.randrange(1, n + 1)
        r = rng.randrange(l, n + 1)
        queries.append((l, r))
    text = f'{n}\n' + ' '.join(map(str, a)) + f'\n{len(queries)}\n'
    text += ''.join(f'{l} {r}\n' for l, r in queries)
    cases.append((text, [len(set(a[l - 1:r])) for l, r in queries]))
if '--scale' in sys.argv:
    n, period = 1000000, 100003
    queries = [(1, n), (1, 1), (n, n)]
    for _ in range(100):
        l = rng.randrange(1, n + 1)
        r = rng.randrange(l, n + 1)
        queries.append((l, r))
    text = f'{n}\n' + ' '.join(str(i % period + 1) for i in range(n)) + f'\n{len(queries)}\n'
    text += ''.join(f'{l} {r}\n' for l, r in queries)
    cases.append((text, [min(period, r - l + 1) for l, r in queries]))
for style in ['compact']:
    source = root / f'build/P1972.{style}.cpp'
    exe = root / f'build/P1972.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P1972.{style}.cpp'), str(source)], check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(source), '-o', str(exe)], check=True)
    for text, expected in cases:
        got = list(map(int, subprocess.check_output([str(exe)], input=text.encode()).split()))
        assert got == expected
    label = 'set oracle and million-item periodic case' if '--scale' in sys.argv else 'set oracle'
    print(f'P1972 {style} bundled driver / {label} PASS')
