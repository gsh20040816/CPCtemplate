"""Exact printed programs: trial-factor quotient, Korselt, big-int matrix."""
from compiler_config import CXX
from pathlib import Path
import hashlib
import json
import math
import random
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import records

rng = random.Random(1593293)

def sigma(a, b):
    answer, p, mod = 1, 2, 9901
    while p <= a // p:
        if a % p == 0:
            e = 0
            while a % p == 0:
                a //= p
                e += 1
            n = e * b + 1
            term = n % mod if p % mod == 1 else (pow(p, n, mod) - 1) * pow((p - 1) % mod, -1, mod) % mod
            answer = answer * term % mod
        p += 1
    if a > 1:
        term = (b + 1) % mod if a % mod == 1 else (pow(a, b + 1, mod) - 1) * pow((a - 1) % mod, -1, mod) % mod
        answer = answer * term % mod
    return answer

def geometric(a, n, mod):
    def mul(x, y):
        return [[sum(x[i][k] * y[k][j] for k in range(2)) % mod
                 for j in range(2)] for i in range(2)]
    x, y = [[a % mod, 1 % mod], [0, 1 % mod]], [[1 % mod, 0], [0, 1 % mod]]
    while n:
        if n & 1:
            y = mul(y, x)
        x = mul(x, x)
        n //= 2
    return y[0][1]

prime_one = next(p for p in range(9902, 50000001, 9901)
                 if all(p % d for d in range(2, math.isqrt(p) + 1)))
ab = [(1, 0), (1, 50000000), (50000000, 0), (50000000, 50000000),
      (9901, 50000000), (prime_one, 50000000)]
ab += [(a, b) for a in range(1, 31) for b in range(5)]
ab += [(rng.randint(1, 50000000), rng.randint(0, 50000000)) for _ in range(300)]
p1593 = [(f'{a} {b}\n', str(sigma(a, b))) for a, b in ab]
spf = list(range(65000))
for p in range(2, 65000):
    if spf[p] == p:
        for x in range(p * p, 65000, p):
            if spf[x] == x:
                spf[x] = p
expected = []
for n in range(3, 65000):
    good, x = spf[n] != n, n
    while x > 1:
        p = spf[x]
        x //= p
        if x % p == 0 or (n - 1) % (p - 1):
            good = False
        while x % p == 0:
            x //= p
    expected.append(f'The number {n} is a Carmichael number.' if good else f'{n} is normal.')
uva = [(''.join(f'{n}\n' for n in range(3, 65000)) + '0\n', '\n'.join(expected)), ('0\n', '')]
axm = [(3, 4, 7), (8, 10, 9), (10**9, 10**12, 998244353)]
axm += [(a, x, m) for a in [1, 2, 10**9] for x in [1, 2, 10**12]
        for m in [1, 2, 6, 10**9]]
axm += [(rng.randint(1, 10**9), rng.randint(1, 10**12), rng.randint(1, 10**9)) for _ in range(300)]
abc = [(f'{a} {x} {m}\n', str(geometric(a, x, m))) for a, x, m in axm]
checks = {'example-191': p1593, 'example-192': uva, 'example-193': abc}
for mode in ['normal', 'sanitizer']:
    flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    report = {'mode': mode, 'compiler': CXX, 'flags': flags, 'online_ac': False, 'examples': [],
              'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    for row in records():
        if row['id'] not in checks:
            continue
        source = root / f"build/math-usage-{row['id']}-{mode}.cpp"
        source.write_text(row['program'])
        exe = source.with_suffix('')
        subprocess.run([CXX, '-std=c++20', *flags, str(source), '-o', str(exe)], check=True)
        for data, answer in checks[row['id']]:
            result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
            assert not result.stderr, result.stderr
            assert result.stdout.strip() == answer, (row['id'], data[:100], result.stdout[:100], answer[:100])
        report['examples'].append({'id': row['id'], 'program_sha256': row['program_sha256'],
                                   'invocations': len(checks[row['id']]),
                                   'legal_n_checked': 64997 if row['id'] == 'example-192' else None})
        print(mode, row['id'], len(checks[row['id']]), 'PASS', flush=True)
    (root / f'verification/math-usages-{mode}.json').write_text(json.dumps(report, indent=2) + '\n')
