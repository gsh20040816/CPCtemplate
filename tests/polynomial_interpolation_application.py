#!/usr/bin/env python3
"""Check the entire arbitrary-point interpolation driver using independent algebra.

Arbitrary small samples are solved by modular Vandermonde elimination. Other
inputs are integer-Horner samples of known coefficients, or analytic samples at
maximum size. Neither the C++ multipoint evaluator nor NTT supplies an oracle.
These are local tests, not online AC or an OJ time-limit measurement.
"""
from compiler_config import CXX
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import random
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
MOD = 998244353
LIMIT = 131072
SEED = 21220261002
DRIVER = 'verify/library_checker/polynomial_interpolation.compact.cpp'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def horner(coefficients, points):
    return [horner_one(coefficients, x) for x in points]


def horner_one(coefficients, x):
    value = 0
    for coefficient in reversed(coefficients):
        value = (value * x + coefficient) % MOD
    return value


def vandermonde(points, values):
    """Solve an augmented dense linear system, without polynomial algorithms."""
    n = len(points)
    matrix = []
    for x, y in zip(points, values):
        row, power = [], 1
        for _ in range(n):
            row.append(power)
            power = power * x % MOD
        matrix.append(row + [y])
    for col in range(n):
        pivot = next(row for row in range(col, n) if matrix[row][col])
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        inverse = pow(matrix[col][col], MOD - 2, MOD)
        matrix[col] = [value * inverse % MOD for value in matrix[col]]
        for row in range(n):
            if row != col:
                factor = matrix[row][col]
                matrix[row] = [(a - factor * b) % MOD for a, b in zip(matrix[row], matrix[col])]
    return [matrix[row][n] for row in range(n)]


def distinct_points(rng, n, kind):
    """Vary the points independently from the polynomial degree/coefficients."""
    if kind % 4 == 0:
        # Arbitrary nonconsecutive points, including exceptional field values.
        points = [0, 1, MOD - 1][:n]
        used = set(points)
        while len(points) < n:
            x = rng.randrange(MOD)
            if x not in used:
                points.append(x)
                used.add(x)
    elif kind % 4 == 1:
        points = list(range(n))
    elif kind % 4 == 2:
        # A random affine permutation of consecutive indices modulo the field.
        offset, step = rng.randrange(MOD), rng.randrange(1, MOD)
        points = [(offset + i * step) % MOD for i in range(n)]
    else:
        # A primitive root has order MOD-1, safely greater than every test n.
        points, x = [], 1
        for _ in range(n):
            points.append(x)
            x = x * 3 % MOD
    rng.shuffle(points)
    assert len(points) == len(set(points)) == n
    return points


def cases():
    rng = random.Random(SEED)
    for n in range(1, 13):
        for kind in range(4):
            for trial in range(2):
                x = distinct_points(rng, n, kind)
                y = [rng.randrange(MOD) for _ in range(n)]
                yield f'vandermonde-{n}-{kind}-{trial}', x, y, vandermonde(x, y), 'modular Vandermonde Gaussian elimination'
    sizes = [1, 2, 3, 7, 8, 9, 15, 16, 17, 31, 32, 33, 63, 64, 65,
             127, 128, 129, 255, 256, 257, 511, 512, 513, 1023, 1024, 1025]
    for n in sizes:
        for kind in range(4):
            coefficients = [rng.randrange(MOD) for _ in range(n)]
            if kind == 1:
                coefficients[n // 2:] = [0] * (n - n // 2)
            elif kind == 2:
                coefficients = [0] * n
                coefficients[rng.randrange(n)] = rng.randrange(1, MOD)
            x = distinct_points(rng, n, kind)
            yield f'known-coefficients-{n}-{kind}', x, horner(coefficients, x), coefficients, 'known coefficients sampled by Python integer Horner'
    for trial in range(120):
        n = rng.randrange(1, 201)
        degree_bound = rng.randrange(n + 1)
        coefficients = [rng.randrange(MOD) for _ in range(degree_bound)] + [0] * (n - degree_bound)
        x = distinct_points(rng, n, trial)
        yield f'random-degree-points-{trial:03d}', x, horner(coefficients, x), coefficients, 'independent coefficient length and point distribution; integer Horner'
    yield 'empty-driver-extension', [], [], [], 'empty extension outside official constraints'
    for n in [2047, 2048, 2049, 4095, 4096, 4097, 65535, 65536, 65537, LIMIT]:
        x = distinct_points(rng, n, 0)
        y = [n if a == 1 else (pow(a, n, MOD) - 1) * pow((a - 1) % MOD, MOD - 2, MOD) % MOD for a in x]
        yield f'dense-geometric-{n}', x, y, [1] * n, 'finite geometric sum; x=1 separately'
    n = LIMIT
    x = distinct_points(rng, n, 0)
    terms = [(0, MOD - 1), (1, 7), (n // 2, 123456789), (n - 1, MOD - 2)]
    coefficients = [0] * n
    for exponent, coefficient in terms:
        coefficients[exponent] = coefficient
    y = [sum(coefficient * pow(a, exponent, MOD) for exponent, coefficient in terms) % MOD for a in x]
    yield 'maximum-sparse-powers', x, y, coefficients, 'four explicit sparse terms and modular exponentiation'
    # Dense (x-1)^(n-1), with coefficients obtained by a linear binomial recurrence.
    inverse = [0, 1] + [0] * (n - 2)
    for i in range(2, n):
        inverse[i] = MOD - (MOD // i) * inverse[MOD % i] % MOD
    coefficients = [MOD - 1]
    for i in range(1, n):
        coefficients.append(-coefficients[-1] * (n - i) * inverse[i] % MOD)
    yield 'maximum-dense-binomial', x, [pow((a - 1) % MOD, n - 1, MOD) for a in x], coefficients, '(x-1)^(n-1); binomial coefficients and modular exponentiation'
    yield 'maximum-high-monomial', distinct_points(rng, n, 2), None, [0] * (n - 1) + [MOD - 1], 'highest monomial; modular exponentiation'
    yield 'maximum-zero-high-zero-preservation', x, [0] * n, [0] * n, 'zero polynomial; all n zero coefficients must be emitted'
    yield 'maximum-constant-high-zero-preservation', distinct_points(rng, n, 1), [MOD - 1] * n, [MOD - 1] + [0] * (n - 1), 'constant polynomial; n-1 high zero coefficients must be emitted'
    y = [(7 * a + MOD - 1) % MOD for a in x]
    yield 'maximum-linear-high-zero-preservation', x, y, [MOD - 1, 7] + [0] * (n - 2), 'linear polynomial; n-2 high zero coefficients must be emitted'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sanitize', action='store_true')
    ap.add_argument('--usage', help='Compile the exact registered printed program')
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    sanitizer = args.sanitize or os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1'
    mode = 'sanitizer' if sanitizer else 'normal'
    suffix = '-usage' if args.usage else ''
    work = ROOT / 'build/interpolation-application' / (mode + suffix)
    work.mkdir(parents=True, exist_ok=True)
    source, executable = work / 'main.cpp', work / 'main'
    if args.usage:
        sys.path.insert(0, str(ROOT / 'tools'))
        from usage_examples import records
        row = next(r for r in records() if r['id'] == args.usage)
        assert row['driver'] == DRIVER, 'Usage belongs to another driver'
        source.write_text(row['program'])
        assert digest(source.read_bytes()) == row['program_sha256']
    else:
        subprocess.run([sys.executable, str(ROOT / 'tools/bundle.py'), DRIVER, str(source)], cwd=ROOT, check=True)
    flags = ['-std=c++20', '-O2']
    if sanitizer:
        flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    subprocess.run([CXX, *flags, str(source), '-o', str(executable)], check=True)
    env = os.environ.copy()
    if sanitizer:
        # LeakSanitizer is excluded in this environment; no leak-detection claim.
        options = [option for option in env.get('ASAN_OPTIONS', '').split(':') if option and not option.startswith('detect_leaks=')]
        env['ASAN_OPTIONS'] = ':'.join(options + ['detect_leaks=0'])
        env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
    report = dict(problem='polynomial_interpolation', scope='Local independent full-driver tests only; not online AC, OJ speed ranking, or leak detection', modulus=MOD, official_maximum_n=LIMIT, driver=DRIVER, usage=args.usage, program_sha256=digest(source.read_bytes()), driver_sha256=digest((ROOT / DRIVER).read_bytes()), header_sha256=digest((ROOT / 'src/compact/polynomial_interpolation.hpp').read_bytes()), test_script_sha256=digest(Path(__file__).read_bytes()), compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0], flags=flags, sanitizer=sanitizer, sanitizer_environment={key: env.get(key) for key in ['ASAN_OPTIONS', 'UBSAN_OPTIONS']} if sanitizer else {}, leak_sanitizer_excluded=sanitizer, seed=SEED, recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), status='running', cases=[])
    destination = args.report or ROOT / f'verification/interpolation-application-{mode}{suffix}.json'
    destination.parent.mkdir(parents=True, exist_ok=True)

    def checkpoint():
        destination.write_text(json.dumps(report, indent=2) + '\n')

    checkpoint()
    try:
        for name, x, y, expected, oracle in cases():
            if y is None:
                assert name == 'maximum-high-monomial'
                y = [-pow(a, len(x) - 1, MOD) % MOD for a in x]
            assert len(x) == len(y) == len(expected)
            assert len(x) == len(set(x))
            data = (f'{len(x)}\n' + ' '.join(map(str, x)) + '\n' + ' '.join(map(str, y)) + '\n').encode()
            report['active_case'] = name
            checkpoint()
            start = time.monotonic()
            run = subprocess.run([str(executable)], input=data, capture_output=True, env=env, timeout=240)
            assert run.returncode == 0, (name, run.returncode, run.stderr.decode())
            assert not run.stderr, (name, run.stderr.decode())
            actual = list(map(int, run.stdout.split()))
            assert actual == expected, (name, next(((i, a, b) for i, (a, b) in enumerate(zip(actual, expected)) if a != b), None), len(actual), len(expected))
            report['cases'].append(dict(case=name, n=len(x), oracle=oracle, high_zero_coefficients=len(expected) - next((i + 1 for i in range(len(expected) - 1, -1, -1) if expected[i]), 0), input_sha256=digest(data), expected_sha256=digest((' '.join(map(str, expected)) + '\n').encode()), output_sha256=digest(run.stdout), elapsed_seconds=round(time.monotonic() - start, 5), verdict='independent_oracle_accepted'))
            checkpoint()
    except BaseException:
        report['status'] = 'failed'
        report['failure'] = traceback.format_exc()
        checkpoint()
        raise
    report.pop('active_case', None)
    report['status'] = 'passed'
    report['case_count'] = len(report['cases'])
    checkpoint()
    print(f'polynomial_interpolation: {len(report["cases"])} independent full-driver cases PASS; sanitizer={sanitizer}; usage={args.usage}; not online AC', flush=True)


if __name__ == '__main__':
    main()
