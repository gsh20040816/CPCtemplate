#!/usr/bin/env python3
"""Check all coefficients of three distinct convolution adapters."""
import os
from pathlib import Path
import random
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
p = 998244353
rng = random.Random(982143)
for problem, op in [('convolution_mod', '+'), ('bitwise_and_convolution', '&'), ('bitwise_xor_convolution', '^')]:
    exe = root / ('build/lc-' + problem)
    subprocess.run([CXX, *flags, str(root / ('verify/library_checker/' + problem + '.compact.cpp')), '-o', str(exe)], check=True)
    def check(a, b, expected):
        n, m = len(a), len(b)
        first = f'{n} {m}' if op == '+' else str(n.bit_length()-1)
        data = first+'\n'+' '.join(map(str, a))+'\n'+' '.join(map(str, b))+'\n'
        r = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=60)
        assert not r.stderr, r.stderr
        actual = list(map(int, r.stdout.split()))
        assert actual == expected, (problem, n, m)
    for _ in range(40):
        n = rng.randrange(1, 40) if op == '+' else 1 << rng.randrange(0, 6)
        m = rng.randrange(1, 40) if op == '+' else n
        a = [rng.randrange(p) for _ in range(n)]
        b = [rng.randrange(p) for _ in range(m)]
        expected = [0]*(n+m-1 if op == '+' else n)
        for i in range(n):
            for j in range(m):
                k = i+j if op == '+' else (i&j if op == '&' else i^j)
                expected[k] = (expected[k]+a[i]*b[j])%p
        check(a, b, expected)
    # Maximal legal inputs. Constant arrays admit exact independent counts.
    if op == '+':
        n = 1 << 19
        expected = [min(i+1, 2*n-1-i) for i in range(2*n-1)]
        check([p-1]*n, [p-1]*n, expected)
        # Highly unequal lengths, zero polynomial and modular sign boundary.
        check([p-1], list(range(n)), [(-i)%p for i in range(n)])
        check([0]*n, [p-1], [0]*n)
    else:
        n = 1 << 20
        expected = [pow(3, 20-i.bit_count(), p) for i in range(n)] if op == '&' else [n]*n
        check([p-1]*n, [p-1]*n, expected)
        # A unit impulse exposes the AND identity index or XOR permutation.
        at = n-1 if op == '&' else 731
        a = [0]*n
        a[at] = 1
        b = list(range(n))
        expected = b if op == '&' else [i^at for i in range(n)]
        check(a, b, expected)
print('LC convolution drivers: schoolbook and direct bitwise oracles, maximum constant counts, impulses and modular signs PASS')
