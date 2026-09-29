"""Check P4720's actual submission bundles against Python exact combinations."""
from compiler_config import CXX
from pathlib import Path
import math
import random
import os
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(4720)
cases = [(5, 3, 3), (666, 233, 123456), (10**18, 3, 10**6), (10**18, 10**18, 999983), (132, 66, 999983)]
for _ in range(75):
    n = rng.randrange(1, 10000)
    k = rng.randrange(1, n + 1)
    cases.append((n, k, rng.randrange(2, 10001)))
for p in [2, 8, 27, 72, 524288, 531441, 999983, 1000000]:
    for k in [1, 2, 63, 127]:
        cases.append((10**18, k, p))
        cases.append((10**18, 10**18-k, p))
for style in ['compact']:
    source = root / f'build/P4720.{style}.cpp'
    exe = root / f'build/P4720.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P4720.{style}.cpp'), str(source)], check=True)
    flags = ['-std=c++20', '-O2']
    if os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1':
        flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)
    for n, k, p in cases:
        result = subprocess.run([str(exe)], input=f'{n} {k} {p}\n', text=True, capture_output=True, check=True, timeout=120)
        assert not result.stderr, result.stderr
        got = int(result.stdout)
        assert got == math.comb(n, k) % p
    print(f'P4720 {style}: {len(cases)} cases, bundled driver / Python exact combinations PASS')
