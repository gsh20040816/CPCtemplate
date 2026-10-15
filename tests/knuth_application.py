#!/usr/bin/env python3
"""AtCoder awc0100_o driver versus exhaustive circular merge orders; official samples; maximum-size timing."""
import os
import random
import subprocess
import time
from functools import lru_cache
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
exe = root / 'build/awc0100_o'
flags = ['-std=c++20', '-O2']
if os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
subprocess.run([CXX, *flags, str(root / 'verify/atcoder/awc0100_o.compact.cpp'), '-o', str(exe)], check=True)


def run(a):
    text = f'{len(a)}\n' + ' '.join(map(str, a)) + '\n'
    return int(subprocess.run([str(exe)], input=text, capture_output=True, text=True, check=True).stdout)


@lru_cache(maxsize=None)
def brute(a):
    # Merge any two circularly adjacent tablets; the circle keeps its order.
    if len(a) == 1:
        return 0
    best = None
    n = len(a)
    for i in range(n):
        j = (i + 1) % n
        merged = a[i] + a[j]
        if j == 0:
            b = (merged,) + a[1:n - 1]
        else:
            b = a[:i] + (merged,) + a[j + 1:]
        value = merged + brute(b)
        best = value if best is None else min(best, value)
    return best


samples = [([3, 1, 4, 1], 18), ([10, 20, 30], 90), ([7, 2, 9, 4, 6, 3, 8, 5], 132),
           ([12, 45, 7, 23, 89, 34, 56, 78, 11, 90, 5, 67, 38, 42, 19, 73, 61, 29, 84, 16, 50, 99, 3, 27, 64, 8, 71, 36, 14, 52], 6201),
           ([10 ** 9, 10 ** 9], 2 * 10 ** 9)]
for a, want in samples:
    assert run(a) == want, a
rng = random.Random(100)
for case in range(300):
    n = rng.randint(2, 8)
    a = [rng.randint(1, 30) for _ in range(n)]
    assert run(a) == brute(tuple(a)), (case, a)
if os.environ.get('CPC_SANITIZE') != '1':
    for a in ([10 ** 9] * 3000, [rng.randint(1, 10 ** 9) for _ in range(3000)]):
        start = time.monotonic()
        value = run(a)
        assert 0 < value < 2 ** 62 and time.monotonic() - start < 3
print('awc0100_o driver: 5 official samples, 300 random circles vs all merge orders, n=3000 within 3s PASS', flush=True)
