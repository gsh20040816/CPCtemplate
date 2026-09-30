"""Exact printed inverse programs; independent individual and output certificates."""
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

rng = random.Random(54312026)
small = []
primes = [3, 7, 101, 1000003, 998244353]
assert all(all(p % d for d in range(2, math.isqrt(p) + 1)) for p in primes)
for _ in range(160):
    p = rng.choice(primes)
    k = rng.randrange(2, p)
    a = [rng.randrange(1, p) for _ in range(rng.randrange(1, 300))]
    answer = sum(pow(k, i, p) * pow(x, -1, p) for i, x in enumerate(a, 1)) % p
    small.append((f'{len(a)} {p} {k}\n' + ' '.join(map(str, a)) + '\n', answer))
# Every nonzero residue, including k=p-1, repeated values and one-element inputs.
for p in [3, 7, 11, 31]:
    for k in [2, p - 1]:
        a = list(range(1, p))
        answer = sum(pow(k, i, p) * pow(x, -1, p) for i, x in enumerate(a, 1)) % p
        small.append((f'{len(a)} {p} {k}\n' + ' '.join(map(str, a)) + '\n', answer))
table_cases = [(1, 2), (2, 3), (100, 101), (1, 1009), (1008, 1009), (3000000, 10000019)]
assert all(10000019 % d for d in range(2, math.isqrt(10000019) + 1))
rows = {r['id']: r for r in records()}
for mode in ['normal', 'sanitizer']:
    flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    reports = []
    for ident in ['example-196', 'example-197', 'example-198']:
        row = rows[ident]
        source = root / ('build/inverse-' + ident + '.cpp')
        source.write_text(row['program'])
        exe = root / ('build/inverse-' + ident + '-' + mode)
        subprocess.run([CXX, '-std=c++20', *flags, str(source), '-o', str(exe)], check=True)
        observations = []
        def run(data):
            start = time.monotonic()
            result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
            assert not result.stderr, result.stderr
            observations.append(dict(seconds=round(time.monotonic()-start, 4), output_sha256=hashlib.sha256(result.stdout.encode()).hexdigest()))
            return result.stdout
        if ident == 'example-196':
            for n, p in table_cases:
                lines = run(f'{n} {p}\n').splitlines()
                assert len(lines) == n
                for i, line in enumerate(lines, 1):
                    x = int(line)
                    assert 0 < x < p and i*x % p == 1
            oracle = 'Every printed inverse certified by multiplication; primes independently trial-divided; n=3000000 complete output'
        else:
            for data, answer in small:
                assert run(data).splitlines() == [str(answer)]
            n, p, k = 5000000, 998244353, 2
            for value in [1, p - 1]:
                data = f'{n} {p} {k}\n' + (str(value)+' ') * n + '\n'
                answer = (pow(k, n+1, p)-k) * pow(k-1, -1, p) * pow(value, -1, p) % p
                assert run(data).splitlines() == [str(answer)]
            oracle = 'Python individual inverse weighted sums; all nonzero small residues; two n=5000000 geometric sums'
        reports.append(dict(usage=ident, program_sha256=row['program_sha256'], compiler=CXX, flags=flags, invocations=len(observations), oracle=oracle, observations=observations, new_online_ac=False))
        print(ident, mode, len(observations), 'invocations PASS', flush=True)
    report = dict(mode=mode, test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), programs=reports)
    (root / ('verification/inverse-usages-' + mode + '.json')).write_text(json.dumps(report, indent=2)+'\n')
