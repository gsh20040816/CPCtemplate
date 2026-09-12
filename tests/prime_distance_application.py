"""POJ 2689 / UVa 10140 complete-program oracle, including first tied pair."""
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]

def prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11):
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 7, 61):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True

def answer(l, r):
    ps = [x for x in range(l, r + 1) if prime(x)]
    if len(ps) < 2:
        return 'There are no adjacent primes.'
    pairs = list(zip(ps, ps[1:]))
    a, b = min(pairs, key=lambda pair: pair[1] - pair[0])
    c, d = max(pairs, key=lambda pair: pair[1] - pair[0])
    return f'{a},{b} are closest, {c},{d} are most distant.'

rng = random.Random(2689)
cases = [(2, 17), (14, 17), (1, 2), (1, 3), (3, 13), (24, 28),
         (2147483646, 2147483647), (2147483647 - 1000000, 2147483647)]
for _ in range(200):
    l = rng.randrange(1, 2147480000)
    cases.append((l, l + rng.randrange(1, 1000)))
expected = [answer(l, r) for l, r in cases]
assert expected[:2] == ['2,3 are closest, 7,11 are most distant.',
                       'There are no adjacent primes.']
data = ''.join(f'{l} {r}\n' for l, r in cases)
for style in ['compact', 'classic']:
    bundle = root / f'build/2689.{style}.cpp'
    exe = root / f'build/2689.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/poj/2689.{style}.cpp', str(bundle)], cwd=root, check=True)
    flags = ['-O2']
    if os.environ.get('SANITIZE') == '1':
        flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    subprocess.run([os.environ.get('CXX', '/opt/homebrew/bin/g++-16'), '-std=c++20', *flags, str(bundle), '-o', str(exe)], check=True)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
    assert result.stdout.splitlines() == expected
    assert not result.stderr, result.stderr
    print(f'Prime Distance {style}: 208 EOF datasets, tied pairs, empty pairs and million-wide INT_MAX interval PASS')
