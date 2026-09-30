"""P5668 exact printed source, independent complete roots and large certificates."""
from compiler_config import CXX
from pathlib import Path
import hashlib
import json
import math
import random
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import records

rng = random.Random(56682026)
small = []
for m in range(1, 181):
    for n in range(1, 9):
        buckets = [[] for _ in range(m)]
        for x in range(m):
            buckets[pow(x, n, m)].append(x)
        small.extend((n, m, k, a) for k, a in enumerate(buckets))
for _ in range(400):
    m, n = rng.randint(1, 5000), rng.randint(1, 10**9)
    k = rng.randrange(m)
    small.append((n, m, k, [x for x in range(m) if pow(x, n, m) == k]))
for m in [1, 2, 4, 8, 16, 27, 81, 125, 180]:
    for n in [999999999, 10**9]:
        for k in range(m):
            small.append((n, m, k, [x for x in range(m) if pow(x, n, m) == k]))

# Prime known by trial division; order of 3 certified from complete factorization.
p = 998244353
assert all(p % d for d in range(2, math.isqrt(p) + 1))
assert pow(3, p - 1, p) == 1
assert all(pow(3, (p - 1) // d, p) != 1 for d in [2, 7, 17])
large = []
for n in [1, 2, 7, 17, 1024, 10**9]:
    x = rng.randrange(1, p)
    d = math.gcd(n, p - 1)
    ratio = pow(3, (p - 1) // d, p)
    values, current = [], x
    for _ in range(d):
        values.append(current)
        current = current * ratio % p
    large.append((n, p, pow(x, n, p), sorted(values)))
large.append((2, p, 3, []))
large.append((2, p, 0, [0]))
q = 1 << 29
x = 1234567
large.append((2, q, pow(x, 2, q), sorted({x, q-x, (x+q//2)%q, (q//2-x)%q})))
large.append((2, q, 0, list(range(0, q, 1 << 15))))
# Zero-root valuation oracle independent of group logarithms / CRT.
large.append((3, 3**18, 0, list(range(0, 3**18, 3**6))))
large.append((3, 10**9, 0, list(range(0, 10**9, 1000))))
large.append((1, 10**9, 999999999, [999999999]))
# Multiprime CRT reference: all local square roots enumerated before combination.
moduli = [64, 81, 125, 7, 11]
m = math.prod(moduli)
x = 42
k = pow(x, 2, m)
values, product = [0], 1
for q in moduli:
    local = [r for r in range(q) if pow(r, 2, q) == k % q]
    values = [a + product * ((b-a) * pow(product, -1, q) % q)
              for a in values for b in local]
    product *= q
large.append((2, m, k, sorted(values)))

# Both complete input cases from the public Luogu sample.
for n, m, k in [(3, 531441, 330750), (5, 304128, 1)]:
    large.append((n, m, k, [x for x in range(m) if pow(x, n, m) == k]))

# Keep every invocation within T<=100 and sum(root counts)<=1e6.
groups = [small[i:i+100] for i in range(0, len(small), 100)]
groups += [[x] for x in large]
# Maximum T with large prime moduli, independently planted roots.
worst = []
for _ in range(100):
    n = 10**9
    x = rng.randrange(1, p)
    d = math.gcd(n, p-1)
    r = pow(3, (p-1)//d, p)
    a, current = [], x
    for _ in range(d):
        a.append(current)
        current = current*r%p
    worst.append((n, p, pow(x, n, p), sorted(a)))
groups.append(worst)

row = next(x for x in records() if x['id'] == 'example-194')
for mode in ['normal', 'sanitizer']:
    flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    source = root / f'build/nth-roots-usage-{mode}.cpp'
    source.write_text(row['program'])
    exe = source.with_suffix('')
    subprocess.run([CXX, '-std=c++20', *flags, str(source), '-o', str(exe)], check=True)
    report = {'usage': row['id'], 'program_sha256': row['program_sha256'],
              'mode': mode, 'compiler': CXX, 'flags': flags, 'online_ac': False,
              'oracle': 'full modular-power buckets, cyclic prime certificates, zero valuations and independent CRT',
              'cases': len(small)+len(large)+100, 'invocations': len(groups),
              'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'large_cases': []}
    started = time.monotonic()
    for i, group in enumerate(groups):
        assert 1 <= len(group) <= 100
        assert sum(len(a) for n, m, k, a in group) <= 10**6
        data = str(len(group))+'\n'+''.join(f'{n} {m} {k}\n' for n,m,k,a in group)
        start = time.monotonic()
        result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=60)
        assert not result.stderr, result.stderr
        lines = iter(result.stdout.splitlines())
        for n, m, k, expected in group:
            assert int(next(lines)) == len(expected), (mode, n, m, k)
            if expected:
                got = list(map(int, next(lines).split()))
                assert got == expected, (mode, n, m, k, got[:10], expected[:10])
        assert next(lines, None) is None
        if i >= (len(small)+99)//100:
            report['large_cases'].append({'inputs': [[n,m,k] for n,m,k,a in group],
                                          'roots': sum(len(a) for n,m,k,a in group),
                                          'seconds': round(time.monotonic()-start,4),
                                          'stdout_sha256': hashlib.sha256(result.stdout.encode()).hexdigest()})
    report['seconds'] = round(time.monotonic()-started,4)
    (root/f'verification/nth-roots-usages-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
    print(mode, report['cases'], 'cases', report['invocations'], 'invocations PASS', flush=True)
