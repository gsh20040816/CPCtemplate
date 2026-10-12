#!/usr/bin/env python3
"""Exact source audit; sieve/trial division/Python integers are independent oracles."""
from pathlib import Path
import hashlib
import json
import os
import random
import subprocess
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/wida-factor'
OUT.mkdir(parents=True, exist_ok=True)
source = ROOT / 'tests/fixtures/wida_factor/factor.cpp'
blob = source.read_bytes()
assert hashlib.sha1(b'blob ' + str(len(blob)).encode() + b'\0' + blob).hexdigest() == 'e744206b3a512a31c8a7ba9f2141922433c7aebb'


def trial(n):
    result = []
    p = 2
    while p <= n // p:
        while n % p == 0:
            result.append(p)
            n //= p
        p += 1
    if n > 1:
        result.append(n)
    return result


def formatted(factors):
    return str(len(factors)) + ''.join(f' {p}' for p in factors)


inputs, expected = [], []
counts = {}


def add(kind, data, answer):
    inputs.append(data)
    expected.append(answer)
    counts[kind] = counts.get(kind, 0) + 1


limit = 50000
prime = [True] * (limit + 1)
prime[:2] = [False, False]
for p in range(2, limit + 1):
    if prime[p]:
        for k in range(p * p, limit + 1, p):
            prime[k] = False
    result = str(int(prime[p]))
    add('sieve_primality', f'p {p}', f'{result} {result}')
for n in [0, 1]:
    add('sieve_primality', f'p {n}', '0 0')

rng = random.Random(206130894)
cases = list(range(1, 10001)) + [rng.randrange(1, 10**8) for _ in range(150)]
cases += [10001, 10007**2, 10007 * 10009, 2**40, 3**25, 5**18]
for n in cases:
    answer = formatted(trial(n))
    add('trial_factorization', f'f {n}', f'{answer} | {answer}')

# Certify a false-positive directly: every factor is prime by trial division.
witness_factors = [149491, 747451, 34233211]
witness = 1
for p in witness_factors:
    assert trial(p) == [p]
    witness *= p
assert witness == 3825123056546413051
add('source_false_positive', f'p {witness}', '1 0')
add('source_composite_leaf', f'f {witness}', f'1 {witness} | {formatted(witness_factors)}')

# Replacement-only checks beyond signed i64; each full factor list is certified.
for factors in [[2] * 63, [3] * 40, [5] * 27, [3, 5, 17, 257, 641, 65537, 6700417]]:
    n = 1
    for p in factors:
        assert trial(p) == [p]
        n *= p
    assert n < 2**64
    add('unsigned_factorization', f'u {n}', formatted(factors))

for _ in range(400):
    m = rng.randrange(1, 2**63)
    a, b = rng.randrange(m), rng.randrange(m)
    add('python_modular_multiply', f'm {m} {a} {b}', f'{a*b%m} {a*b%m}')
    exponent = rng.randrange(2**63)
    answer = pow(a, exponent, m)
    add('python_modular_power', f'w {m} {a} {exponent}', f'{answer} {answer}')
for m in [1, 2, 2**63 - 1]:
    for a in [0, m - 1]:
        for b in [0, m - 1]:
            add('modular_endpoints', f'm {m} {a} {b}', f'{a*b%m} {a*b%m}')
            answer = pow(a, b, m)
            add('modular_endpoints', f'w {m} {a} {b}', f'{answer} {answer}')

paths = ['tests/wida_factor.cpp', 'tests/wida_factor.py',
         'tests/fixtures/wida_factor/factor.cpp', 'src/compact/number_theory.hpp',
         'src/compact/prime64.hpp', 'src/compact/mod64.hpp']
digests = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
report = dict(scope='Exact WIDA17 modular helpers, bounded primality and factorization, certified false-positive and unsigned replacement cases. No original application or new online AC.',
              cases=counts, witness=dict(n=witness, factors=witness_factors), files=digests, runs=[])
data = '\n'.join(inputs) + '\n'
answer = '\n'.join(expected) + '\n'
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for mode, flags in [('normal', ['-O2', '-DNDEBUG']),
                    ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = OUT / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(ROOT / 'tests/wida_factor.cpp'), '-o', str(exe)], check=True)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env=env, timeout=300)
    assert result.returncode == 0 and not result.stderr, (mode, result.returncode, result.stderr)
    if result.stdout != answer:
        actual = result.stdout.splitlines()
        for i, exp in enumerate(expected):
            assert i < len(actual) and actual[i] == exp, (mode, inputs[i], exp, actual[i:i+1])
        raise AssertionError('Unexpected extra output')
    report['runs'].append(dict(mode=mode, cases=len(inputs), passed=True,
                               output_sha256=hashlib.sha256(result.stdout.encode()).hexdigest()))
    print(mode, len(inputs), 'independent protocol cases PASS', flush=True)
assert digests == {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
(ROOT / 'verification/wida-factor.json').write_text(json.dumps(report, indent=2) + '\n')
