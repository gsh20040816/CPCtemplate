"""Check P4720's actual submission bundles against Python exact combinations."""
from compiler_config import CXX
from pathlib import Path
import math
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(4720)
cases = [(10**18, 3, 10**6), (10**18, 10**18, 999983), (132, 66, 999983)]
for _ in range(75):
    n = rng.randrange(1, 10000)
    k = rng.randrange(1, n + 1)
    cases.append((n, k, rng.randrange(2, 10001)))
for style in ['compact']:
    source = root / f'build/P4720.{style}.cpp'
    exe = root / f'build/P4720.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P4720.{style}.cpp'), str(source)], check=True)
    subprocess.run([CXX, '-std=c++20', '-O2', str(source), '-o', str(exe)], check=True)
    for n, k, p in cases:
        got = int(subprocess.check_output([str(exe)], input=f'{n} {k} {p}\n'.encode()))
        assert got == math.comb(n, k) % p
    print(f'P4720 {style} bundled driver / Python exact combinations PASS')
