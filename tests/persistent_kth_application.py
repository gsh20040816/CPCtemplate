"""Check actual P3834 bundles against sorted slices, including signed endpoints."""
from pathlib import Path
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(3834)
cases = []
for trial in range(25):
    n = rng.randrange(1, 70)
    a = [rng.choice([-(1 << 63), (1 << 63) - 1, -5, 0, 5, rng.randrange(-100, 101)])
         for _ in range(n)]
    queries = []
    for _ in range(150):
        l = rng.randrange(1, n + 1)
        r = rng.randrange(l, n + 1)
        k = rng.randrange(1, r - l + 2)
        queries.append((l, r, k))
    cases.append((a, queries))
for style in ['compact']:
    source = root / f'build/P3834.{style}.cpp'
    exe = root / f'build/P3834.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P3834.{style}.cpp'), str(source)], check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(source), '-o', str(exe)], check=True)
    for a, queries in cases:
        text = f'{len(a)} {len(queries)}\n' + ' '.join(map(str, a)) + '\n'
        text += ''.join(f'{l} {r} {k}\n' for l, r, k in queries)
        got = list(map(int, subprocess.check_output([str(exe)], input=text.encode()).split()))
        assert got == [sorted(a[l - 1:r])[k - 1] for l, r, k in queries]
    print(f'P3834 {style} bundled driver / sorted-slice oracle with int64 endpoints PASS')
