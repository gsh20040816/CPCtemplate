#!/usr/bin/env python3
"""Full arbitrary-point driver checked without polynomial division or NTT.

Small/medium references use Python integer Horner evaluation. Maximum-size
references use a finite geometric sum or explicitly sparse coefficients.
These are local tests, not online AC or evidence of an OJ time limit.
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

ROOT = Path(__file__).resolve().parents[1]
MOD = 998244353
LIMIT = 131072
SEED = 21120261002
DRIVER = 'verify/library_checker/multipoint_evaluation.compact.cpp'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def horner(coefficients, points):
    answer = []
    for x in points:
        value = 0
        for coefficient in reversed(coefficients):
            value = (value * x + coefficient) % MOD
        answer.append(value)
    return answer


def cases():
    rng = random.Random(SEED)
    # Exercise dimensions independently, including both sides of tree/NTT splits.
    sizes = [1, 2, 3, 7, 8, 9, 15, 16, 17, 31, 32, 33, 63, 64, 65]
    for i, n in enumerate(sizes):
        for j, m in enumerate(sizes):
            f = [rng.randrange(MOD) for _ in range(n)]
            x = [rng.randrange(MOD) for _ in range(m)]
            if (i + j) % 3 == 0:
                x = [0, 1, MOD - 1, 1, 0, MOD - 1] * ((m + 5) // 6)
                x = x[:m]
            if (i + j) % 5 == 0:
                f[n // 2:] = [0] * (n - n // 2)
            yield f'boundary-{n}-{m}', f, x, None, 'integer Horner'
    for trial in range(180):
        n, m = rng.randrange(1, 181), rng.randrange(1, 181)
        f = [rng.randrange(MOD) for _ in range(n)]
        x = [rng.randrange(MOD) for _ in range(m)]
        if trial % 6 == 0:
            f = [0] * n
        elif trial % 6 == 1:
            f = [MOD - 1] * n
        elif trial % 6 == 2:
            # A reproducible trailing-zero suffix with no degree assumption.
            cut = rng.randrange(n)
            f[cut:] = [0] * (n - cut)
        if trial % 5 == 0:
            x = [rng.choice([0, 1, MOD - 1])] * m
        elif trial % 5 == 1:
            x = [rng.choice([0, 1, MOD - 1, 17, 123456789]) for _ in range(m)]
        yield f'random-{trial:03d}', f, x, None, 'integer Horner'
    for n, m in [(1, 4097), (4097, 1), (2, 4096), (4096, 2),
                 (127, 1025), (1025, 127), (257, 513), (513, 257)]:
        f = [rng.randrange(MOD) for _ in range(n)]
        x = [rng.randrange(MOD) for _ in range(m)]
        x[:min(m, 3)] = [0, 1, MOD - 1][:min(m, 3)]
        yield f'unbalanced-{n}-{m}', f, x, None, 'integer Horner'
    # Empty inputs are a driver/API extension, outside the official problem.
    for n, m in [(0, 0), (0, 7), (7, 0)]:
        yield f'empty-extension-{n}-{m}', [3] * n, [0, 1, MOD - 1, 2, 2, 7, 9][:m], None, 'integer Horner; outside official constraints'
    x = [0, 1, MOD - 1] + [rng.randrange(MOD) for _ in range(LIMIT - 3)]
    # All coefficients are one: sum(x^i)=(x^n-1)/(x-1), with x=1 separate.
    want = [LIMIT if a == 1 else (pow(a, LIMIT, MOD) - 1) * pow((a - 1) % MOD, MOD - 2, MOD) % MOD for a in x]
    yield 'maximum-dense-geometric-sum', [1] * LIMIT, x, want, 'finite geometric sum, x=1 separately'
    terms = [(0, MOD - 1), (1, 7), (LIMIT // 2, 123456789), (LIMIT - 1, MOD - 2)]
    f = [0] * LIMIT
    for exponent, coefficient in terms:
        f[exponent] = coefficient
    want = [sum(coefficient * pow(a, exponent, MOD) for exponent, coefficient in terms) % MOD for a in x]
    yield 'maximum-sparse-powers', f, x, want, 'four sparse terms and modular exponentiation'
    f = [rng.randrange(MOD) for _ in range(LIMIT)]
    specials = [0, 1, MOD - 1]
    values = horner(f, specials)
    x = [specials[i % 3] for i in range(LIMIT)]
    yield 'maximum-dense-repeated-points', f, x, [values[i % 3] for i in range(LIMIT)], 'integer Horner at 0, 1, -1; repetitions retain order'
    yield 'maximum-zero-polynomial', [0] * LIMIT, x, [0] * LIMIT, 'zero polynomial'
    yield 'maximum-points-constant', [MOD - 1], x, [MOD - 1] * LIMIT, 'constant polynomial'
    yield 'maximum-degree-one-point', f, [17], horner(f, [17]), 'integer Horner'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sanitize', action='store_true')
    ap.add_argument('--usage', help='Compile the exact registered printed program')
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    sanitizer = args.sanitize or os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1'
    mode = 'sanitizer' if sanitizer else 'normal'
    work = ROOT / 'build/multipoint-application' / (mode + ('-usage' if args.usage else ''))
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
        # This environment cannot reliably run LeakSanitizer. No leak claim.
        options = [option for option in env.get('ASAN_OPTIONS', '').split(':') if option and not option.startswith('detect_leaks=')]
        env['ASAN_OPTIONS'] = ':'.join(options + ['detect_leaks=0'])
        env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
    results = []
    for name, f, x, expected, oracle in cases():
        if expected is None:
            expected = horner(f, x)
        data = (f'{len(f)} {len(x)}\n' + ' '.join(map(str, f)) + '\n' + ' '.join(map(str, x)) + '\n').encode()
        start = time.monotonic()
        run = subprocess.run([str(executable)], input=data, capture_output=True, env=env, timeout=180)
        assert run.returncode == 0, (name, run.returncode, run.stderr.decode())
        assert not run.stderr, (name, run.stderr.decode())
        actual = list(map(int, run.stdout.split()))
        assert actual == expected, (name, next(((i, a, b) for i, (a, b) in enumerate(zip(actual, expected)) if a != b), None), len(actual), len(expected))
        results.append(dict(case=name, n=len(f), m=len(x), oracle=oracle, input_sha256=digest(data), expected_sha256=digest((' '.join(map(str, expected)) + '\n').encode()), output_sha256=digest(run.stdout), elapsed_seconds=round(time.monotonic() - start, 5), verdict='independent_oracle_accepted'))
    report = dict(problem='multipoint_evaluation', scope='Local independent full-driver tests only; not online AC, an OJ speed ranking, or leak detection', modulus=MOD, official_maximum_n=LIMIT, official_maximum_m=LIMIT, driver=DRIVER, usage=args.usage, program_sha256=digest(source.read_bytes()), test_script_sha256=digest(Path(__file__).read_bytes()), compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0], flags=flags, sanitizer=sanitizer, sanitizer_environment={key: env.get(key) for key in ['ASAN_OPTIONS', 'UBSAN_OPTIONS']} if sanitizer else {}, seed=SEED, recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=results)
    destination = args.report or ROOT / f'verification/multipoint-application-{mode}{"-usage" if args.usage else ""}.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(f'multipoint_evaluation: {len(results)} independent full-driver cases PASS; sanitizer={sanitizer}; usage={args.usage}; not online AC', flush=True)


if __name__ == '__main__':
    main()
