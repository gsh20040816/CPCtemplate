#!/usr/bin/env python3
"""Independent tests of the existing Garner + three-prime NTT usage.

Python exact-integer schoolbook and closed forms supply convolution answers;
Python arbitrary-precision direct CRT sums supply generic Garner answers.
No convolution_i64 or library convolution is used as a reference. Timings are
local observations, not online acceptance or an OJ performance guarantee.
"""
from compiler_config import CXX
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
DRIVER = 'verify/library_checker/convolution_mod_1000000007.garner.compact.cpp'
CORE = 'tests/garner_convolution_core.cpp'
MOD = 1000000007
LIMIT = 524288
PRIMES = (167772161, 469762049, 1224736769)
SEED = 21320261002


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(values):
    return (' '.join(map(str, values)) + '\n').encode()


def schoolbook(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return [x % MOD for x in result]


def constants(n, m, a, b):
    return [min(k + 1, n, m, n + m - 1 - k) * a * b % MOD
            for k in range(n + m - 1)]


def sparse(n, m, left, right):
    a, b, result = [0] * n, [0] * m, [0] * (n + m - 1)
    for i, x in left:
        a[i] = x
    for j, y in right:
        b[j] = y
    for i, x in left:
        for j, y in right:
            result[i + j] = (result[i + j] + x * y) % MOD
    return a, b, result


def cases(section):
    rng = random.Random(SEED)
    if section in ('all', 'small'):
        fixed = [([0], [0]), ([MOD - 1], [MOD - 1]),
                 ([1, 2, 3, 4], [5, 6, 7, 8, 9]),
                 ([PRIMES[0], PRIMES[1]], [MOD - 1, 0, 1]),
                 ([0, 0, 0], [1, MOD - 1]),
                 ([0, MOD - 1, 0], [0, MOD - 1, 0, 0])]
        for i, (a, b) in enumerate(fixed):
            yield f'fixed-{i}', a, b, schoolbook(a, b), 'Python exact-integer schoolbook'
        # Exhaust all pairs of nonempty binary arrays of lengths 1..3.
        arrays = [[(mask >> i) & 1 for i in range(n)] for n in range(1, 4)
                  for mask in range(1 << n)]
        for i, a in enumerate(arrays):
            for j, b in enumerate(arrays):
                yield f'binary-{i}-{j}', a, b, schoolbook(a, b), 'Python exact-integer schoolbook'
        special = [0, 1, 2, MOD - 1, MOD - 2, PRIMES[0], PRIMES[1]]
        for trial in range(160):
            n, m = rng.randrange(1, 81), rng.randrange(1, 81)
            a = [rng.choice(special) if trial % 3 == 0 else rng.randrange(MOD) for _ in range(n)]
            b = [rng.choice(special) if trial % 3 == 0 else rng.randrange(MOD) for _ in range(m)]
            yield f'random-{trial:03}', a, b, schoolbook(a, b), 'Python exact-integer schoolbook'
    if section in ('all', 'boundary'):
        # Cross each transform rounding boundary through the largest permitted
        # output. True coefficients are computed before reducing modulo MOD.
        for exponent in range(1, 20):
            for delta in (-1, 0, 1):
                size = (1 << exponent) + delta
                n = (size + 1) // 2
                m = size + 1 - n
                yield f'boundary-2^{exponent}{delta:+}', [MOD - 1] * n, [MOD - 2] * m, constants(n, m, MOD - 1, MOD - 2), 'constant arrays; triangular/trapezoidal overlap'
    if section in ('all', 'max'):
        n = LIMIT
        yield 'maximum-constant-high', [MOD - 1] * n, [MOD - 1] * n, constants(n, n, MOD - 1, MOD - 1), 'maximal true coefficient and triangular overlap'
        yield 'maximum-constant-asymmetric', [MOD - 2] * n, [MOD - 1] * (n - 1), constants(n, n - 1, MOD - 2, MOD - 1), 'unequal maximum-adjacent lengths; trapezoidal overlap'
        a = [rng.randrange(MOD) for _ in range(n)]
        yield 'maximum-zero-dense', [0] * n, a, [0] * (2 * n - 1), 'zero times independently random dense array'
        a, b, want = sparse(n, n, [(0, MOD - 1), (n // 2, PRIMES[0]), (n - 1, MOD - 2)], [(0, 1), (n // 3, PRIMES[1]), (n - 1, MOD - 1)])
        yield 'maximum-sparse-impulses', a, b, want, 'nine explicit impulse products'
        a = [rng.randrange(MOD) for _ in range(n)]
        yield 'maximum-left-scalar', [MOD - 1], a, [(-x) % MOD for x in a], 'one-element left input; independent scalar multiplication'
        yield 'maximum-right-scalar', a, [MOD - 2], [(-2 * x) % MOD for x in a], 'one-element right input; independent scalar multiplication'
        position = n // 3
        b = [0] * n
        b[position] = MOD - 1
        yield 'maximum-shifted-dense', a, b, [0] * position + [(-x) % MOD for x in a] + [0] * (n - 1 - position), 'dense array shifted by an interior impulse'


def generic_cases():
    rng = random.Random(SEED + 1)
    bound = LIMIT * (MOD - 1) ** 2
    for target in (1, 2, 7, MOD, PRIMES[0], (1 << 63) - 1):
        yield f'empty-target-{target}', [], [], target
        yield f'max-coefficient-target-{target}', [bound % p for p in PRIMES], list(PRIMES), target
    for values in ([-(1 << 63)] * 3, [(1 << 63) - 1] * 3, [-1, 0, 1]):
        for target in (1, MOD, (1 << 63) - 1):
            yield f'extremes-{values[0]}-{target}', values, [(1 << 63) - 1, (1 << 63) - 2, 1], target
    for trial in range(400):
        moduli = []
        while len(moduli) < trial % 13:
            p = rng.randrange(1, 100 if trial % 2 else (1 << 63))
            if all(math.gcd(p, m) == 1 for m in moduli):
                moduli.append(p)
        residues = [rng.randrange(-(1 << 63), 1 << 63) for _ in moduli]
        target = (1, MOD, (1 << 63) - 1, moduli[-1] if moduli else 1)[trial % 4]
        yield f'random-coprime-{trial:03}', residues, moduli, target
    primes = []
    candidate = 2
    while len(primes) < 1000:
        if all(candidate % p for p in primes if p * p <= candidate):
            primes.append(candidate)
        candidate += 1
    yield '1000-moduli-huge-period', [rng.randrange(-(1 << 63), 1 << 63) for _ in primes], primes, (1 << 63) - 1
    for moduli in ([2, 4], [7, 7], [6, 10, 15]):
        for target in (1, MOD):
            yield f'noncoprime-{moduli}-{target}', [0] * len(moduli), moduli, target


def crt_oracle(b, moduli, target):
    if any(math.gcd(a, c) != 1 for i, a in enumerate(moduli) for c in moduli[i + 1:]):
        return None, None
    period = math.prod(moduli)
    # Direct CRT sum, not Garner's mixed-radix recurrence.
    solution = sum(value * (period // m) * pow(period // m, -1, m)
                   for value, m in zip(b, moduli)) % period
    digits, rest = [], solution
    for m in moduli:
        rest, digit = divmod(rest, m)
        digits.append(digit)
    assert rest == 0
    rebuilt, place = 0, 1
    for digit, m in zip(digits, moduli):
        rebuilt += place * digit
        place *= m
    assert rebuilt == solution
    assert all(solution % m == value % m for value, m in zip(b, moduli))
    return [solution % target, *digits], period.bit_length()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sanitize', action='store_true')
    ap.add_argument('--sanitizer-profile', choices=('default', 'bounded'), default='default')
    ap.add_argument('--usage', help='Compile the exact registered printed program')
    ap.add_argument('--section', choices=('all', 'small', 'boundary', 'max', 'core'), default='all')
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    mode = 'sanitizer' if args.sanitize else 'normal'
    suffix = ('-usage' if args.usage else '') + ('' if args.section == 'all' else '-' + args.section)
    work = ROOT / 'build/garner-convolution' / (mode + suffix + '-' + args.sanitizer_profile)
    work.mkdir(parents=True, exist_ok=True)
    source, executable = work / 'main.cpp', work / 'main'
    sys.path.insert(0, str(ROOT / 'tools'))
    from usage_examples import expand
    if args.usage:
        from usage_examples import records
        row = next(r for r in records() if r['id'] == args.usage)
        assert row['driver'] == DRIVER
        program = row['program']
    else:
        program = expand((ROOT / DRIVER).read_text(), (ROOT / DRIVER).parent, set())
    source.write_text(program)
    flags = ['-std=c++20', '-O2', '-Wall', '-Wextra', '-Wshadow']
    if args.sanitize:
        flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-Wall', '-Wextra', '-Wshadow']
    env = os.environ.copy()
    env.pop('ASAN_OPTIONS', None)
    env.pop('UBSAN_OPTIONS', None)
    if args.sanitize:
        env['ASAN_OPTIONS'] = 'detect_leaks=0:halt_on_error=1'
        if args.sanitizer_profile == 'bounded':
            env['ASAN_OPTIONS'] += ':quarantine_size_mb=32:thread_local_quarantine_size_kb=128'
        env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
    destination = args.report or ROOT / f'verification/garner-convolution-{mode}{suffix}.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    dependencies = {}
    def collect(path):
        import re
        path = path.resolve()
        key = str(path.relative_to(ROOT))
        if key in dependencies:
            return
        dependencies[key] = digest(path.read_bytes())
        for name in re.findall(r'^#include "([^"]+)"', path.read_text(), re.M):
            collect(path.parent / name)
    collect(ROOT / DRIVER)
    report = dict(problem='convolution_mod_1000000007', scope='Local independent tests; not online AC, OJ performance acceptance, or leak detection', driver=DRIVER, usage=args.usage, program_sha256=digest(source.read_bytes()), dependencies_sha256=dependencies, test_script_sha256=digest(Path(__file__).read_bytes()), core_harness_sha256=digest((ROOT / CORE).read_bytes()), compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0], flags=flags, sanitizer=args.sanitize, sanitizer_profile=args.sanitizer_profile if args.sanitize else None, sanitizer_environment={k: env[k] for k in ('ASAN_OPTIONS', 'UBSAN_OPTIONS')} if args.sanitize else {}, leak_sanitizer_excluded=args.sanitize, seed=SEED, section=args.section, per_process_timeout_seconds=180, rss_measurement='wait4 lifetime peak may include inherited pre-exec memory; candidate VmHWM samples every 10ms exclude pre-exec and are a lower bound, not exact peak', recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), status='running', cases=[], generic_core_cases=[])
    def checkpoint():
        destination.write_text(json.dumps(report, indent=2) + '\n')
    def run_program(exe, data, name):
        input_file, output_file, error_file = work / 'active.in', work / 'active.out', work / 'active.err'
        input_file.write_bytes(data)
        start = time.monotonic()
        with input_file.open('rb') as inp, output_file.open('wb') as out, error_file.open('wb') as err:
            process = subprocess.Popen([str(exe)], stdin=inp, stdout=out, stderr=err, env=env, close_fds=False)
            sampled_peak = None
            deadline = start + 180
            while True:
                pid, status, usage = os.wait4(process.pid, os.WNOHANG)
                if pid:
                    process.returncode = os.waitstatus_to_exitcode(status)
                    break
                try:
                    # Exclude the parent image inherited before exec. VmHWM is
                    # candidate-local but sampled, so it is a lower bound.
                    if Path(f'/proc/{process.pid}/exe').resolve() == exe.resolve():
                        status_text = Path(f'/proc/{process.pid}/status').read_text()
                        rss = next(int(line.split()[1]) for line in status_text.splitlines() if line.startswith('VmHWM:'))
                        sampled_peak = max(sampled_peak or 0, rss)
                except (OSError, StopIteration):
                    pass
                if time.monotonic() >= deadline:
                    process.kill()
                    _, status, usage = os.wait4(process.pid, 0)
                    process.returncode = os.waitstatus_to_exitcode(status)
                    raise TimeoutError(f'{name} exceeded 180 seconds; active input/output/error retained in {work}')
                time.sleep(.01)
        output, errors = output_file.read_bytes(), error_file.read_bytes()
        stats = dict(exit_code=process.returncode, elapsed_seconds=round(time.monotonic() - start, 5), subprocess_lifetime_max_rss_kib=usage.ru_maxrss, candidate_peak_rss_sampled_kib=sampled_peak, output_sha256=digest(output), stderr=errors.decode(errors='replace'))
        report['active_process'] = stats
        checkpoint()
        assert process.returncode == 0, (name, stats)
        assert not errors, (name, errors.decode(errors='replace'))
        return output, stats
    checkpoint()
    try:
        # Check the arithmetic preconditions independently in Python.
        factors = ((2, 5), (2, 7), (2, 73))
        for p, divisors in zip(PRIMES, factors):
            assert all(p % d for d in range(2, math.isqrt(p) + 1))
            assert all(pow(3, (p - 1) // q, p) != 1 for q in divisors)
        product, bound = math.prod(PRIMES), LIMIT * (MOD - 1) ** 2
        assert bound < product
        assert (bound + product) % MOD != bound % MOD
        report['bounds'] = dict(input_limit=LIMIT, coefficient_bound=str(bound), crt_product=str(product), prime_transform_caps=[(p - 1) & -(p - 1) for p in PRIMES], common_transform_cap=1 << 24, maximum_needed_transform=1 << 20, arithmetic_checks='trial-division primality and factor-order primitive-root tests; coefficient bound; alias counterexample')
        if args.section != 'core':
            subprocess.run([CXX, *flags, str(source), '-o', str(executable)], check=True, timeout=180, capture_output=True)
            report['binary_sha256'] = digest(executable.read_bytes())
            for name, a, b, expected, oracle in cases(args.section):
                assert 1 <= len(a) <= LIMIT and 1 <= len(b) <= LIMIT
                assert len(expected) == len(a) + len(b) - 1
                data = f'{len(a)} {len(b)}\n'.encode() + encode(a) + encode(b)
                report['active_case'] = name
                checkpoint()
                output, stats = run_program(executable, data, name)
                want = encode(expected)
                assert output == want, (name, 'exact output mismatch', len(output), len(want))
                report['cases'].append(dict(case=name, n=len(a), m=len(b), oracle=oracle, input_sha256=digest(data), expected_sha256=digest(want), verdict='independent_oracle_accepted', **stats))
                report.pop('active_process', None)
                checkpoint()
                if max(len(a), len(b)) == LIMIT:
                    print(f'{mode}: {name}: {stats["elapsed_seconds"]:.3f}s, {stats["candidate_peak_rss_sampled_kib"]} KiB sampled candidate RSS PASS', flush=True)
        if args.section in ('all', 'core'):
            core_source, core_exe = work / 'core.cpp', work / 'core'
            core_source.write_text(expand((ROOT / CORE).read_text(), (ROOT / CORE).parent, set()))
            subprocess.run([CXX, *flags, str(core_source), '-o', str(core_exe)], check=True, timeout=180, capture_output=True)
            report['core_program_sha256'] = digest(core_source.read_bytes())
            report['core_binary_sha256'] = digest(core_exe.read_bytes())
            rows = list(generic_cases())
            data = f'{len(rows)}\n'.encode()
            expected_lines = []
            for name, b, moduli, target in rows:
                expected, bits = crt_oracle(b, moduli, target)
                data += f'{len(b)} {target}\n'.encode() + encode(b) + encode(moduli)
                expected_lines.append(b'INVALID\n' if expected is None else encode(expected))
                report['generic_core_cases'].append(dict(case=name, modulus_count=len(moduli), target=target, product_bits=bits, oracle='Python arbitrary-precision direct CRT sum plus divmod mixed-radix digits' if expected is not None else 'pairwise-gcd rejection, including consistent residues', expected_sha256=digest(expected_lines[-1])))
            report['active_case'] = 'generic-garner-batch'
            checkpoint()
            output, stats = run_program(core_exe, data, 'generic-garner-batch')
            expected = b''.join(expected_lines)
            assert output == expected, 'generic Garner result/digits differ from direct CRT oracle'
            report['generic_core_run'] = dict(input_sha256=digest(data), expected_sha256=digest(expected), verdict='independent_oracle_accepted', **stats)
    except BaseException:
        report['status'] = 'failed'
        report['failure'] = traceback.format_exc()
        report['failure_artifacts'] = str(work.relative_to(ROOT)) + '/active.{in,out,err}'
        checkpoint()
        raise
    for key in ('active_case', 'active_process'):
        report.pop(key, None)
    report['status'] = 'passed'
    report['case_count'] = len(report['cases'])
    report['generic_core_case_count'] = len(report['generic_core_cases'])
    checkpoint()
    print(f'Garner convolution: {report["case_count"]} full-driver cases and {report["generic_core_case_count"]} generic Garner cases PASS; {mode}; usage={args.usage}; not online AC', flush=True)


if __name__ == '__main__':
    main()
