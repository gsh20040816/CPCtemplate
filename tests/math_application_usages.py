"""Exact printed frog/prime applications against motion and trial-division oracles.

Run with --mode normal, sanitizer or both (default). All generated programs,
complete input/answer fixtures and source-bound reports stay under build/.
"""
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import math
import os
import platform
import random
import shutil
import subprocess
import sys
import time

from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records

EXAMPLES = {'example-207': 'verify/luogu/P1516.compact.cpp',
            'example-208': 'verify/poj/2689.compact.cpp'}
HEADERS = {'extended_gcd': 'src/compact/extended_gcd.hpp',
           'linear_congruence': 'src/compact/linear_congruence.hpp',
           'segmented_primes': 'src/compact/segmented_sieve.hpp'}
SOURCES = ['docs/usage-examples.json', 'docs/catalog.json',
           'tests/math_application_usages.py', 'tests/usage_examples.py',
           'tests/compiler_config.py', 'tools/usage_examples.py',
           *EXAMPLES.values(), *HEADERS.values()]
INT_MAX = 2147483647


def digest(data):
    return hashlib.sha256(data).hexdigest()


def source_hashes():
    return {path: digest((ROOT / path).read_bytes()) for path in SOURCES}


def copied_program(row):
    """Paste only the named regions, in the order actually taught in the book."""
    code = ['#include <bits/stdc++.h>\nusing namespace std;\n']
    for symbol in row['requires']:
        text = (ROOT / HEADERS[symbol]).read_text()
        begin, end = '// BEGIN ' + symbol + '\n', '// END ' + symbol
        assert text.count(begin) == text.count(end) == 1
        code.append(text.split(begin, 1)[1].split(end, 1)[0])
    return '\n'.join(code) + row['snippet']


def frog_answer(case):
    """Visit the two positions at every time in one full circumference cycle."""
    x, y, m, n, length = case
    for t in range(length):
        if (x + m * t) % length == (y + n * t) % length:
            return str(t)
    return 'Impossible'


def frog_cases():
    cases = []

    def add(case, answer, group):
        x, y, m, n, length = case
        assert all(1 <= value <= 2000000000 for value in (x, y, m, n))
        assert x != y and 1 <= length <= 2100000000
        cases.append(dict(group=group, datasets=1, scope='P1516 statement range',
                          input=' '.join(map(str, case)) + '\n', expected=answer + '\n'))

    # Exhaust all these literal inputs, including negative/equal speed differences
    # and initially equal positions modulo L despite the required x != y.
    for length in range(1, 7):
        for x, y, m, n in itertools.product(range(1, 5), repeat=4):
            if x != y:
                case = (x, y, m, n, length)
                add(case, frog_answer(case), 'exhaustive_L_1_to_6_xy_mn_1_to_4')
    rng = random.Random(207208)
    for _ in range(160):
        x, y = rng.sample(range(1, 2000000001), 2)
        case = (x, y, rng.randint(1, 2000000000),
                rng.randint(1, 2000000000), rng.randint(1, 200))
        add(case, frog_answer(case), 'small_L_full_range_positions_and_speeds')
    boundary = [
        ((1, 2, 3, 4, 5), '4'),
        ((1, 2, 4, 3, 5), '1'),
        ((1, 5, 3, 1, 10), '2'),  # first time 2, period 5
        ((5, 1, 1, 3, 10), '2'),
        ((1, 2, 3, 1, 10), 'Impossible'),
        ((1, 2, 2000000000, 2000000000, 2100000000), 'Impossible'),
        ((1, 2, 2000000000, 2000000000, 1), '0'),
        ((2, 1, 2, 1, 2100000000), '2099999999'),
        ((1, 2, 1, 2, 2100000000), '2099999999'),
        ((1, 2000000000, 2, 1, 2100000000), '1999999999'),
        ((1, 2000000000, 1, 2, 2100000000), '100000001'),
        ((2000000000, 1, 2000000000, 1, 2100000000), '2099999999'),
    ]
    for case, answer in boundary:
        if answer != 'Impossible':
            x, y, m, n, length = case
            assert (x + m * int(answer) - y - n * int(answer)) % length == 0
        if case[-1] <= 10:
            assert answer == frog_answer(case)
        add(case, answer, 'fixed_sign_gcd_zero_and_statement_maxima')
    # In the final fixed case a=b; gcd=1 proves the first time is L-1.
    assert math.gcd(1999999999, 2100000000) == 1
    # Odd speed differences are invertible modulo 2^30. Therefore the planted
    # time in [0,L) is unique there and is the minimum, without an inverse oracle.
    length = 1 << 30
    for _ in range(40):
        difference = 2 * rng.randrange(1000000000) + 1
        t = rng.randint(1, length - 1)
        y = (1 + difference * t) % length or length
        assert y != 1 and math.gcd(difference, length) == 1
        add((1, y, difference + 1, 1, length), str(t), 'planted_unique_time_and_swapped_frogs')
        add((y, 1, 1, difference + 1, length), str(t), 'planted_unique_time_and_swapped_frogs')
    return cases


def trial_divisors():
    """Prepare primes by trial division, never by marking any sieve interval."""
    primes = []
    for n in range(2, math.isqrt(INT_MAX) + 1):
        for p in primes:
            if p * p > n:
                primes.append(n)
                break
            if n % p == 0:
                break
        else:
            primes.append(n)
    return [(p, p * p) for p in primes]


def prime_cases():
    divisors = trial_divisors()

    def prime(n):
        if n < 2:
            return False
        for p, square in divisors:
            if square > n:
                return True
            if n % p == 0:
                return False
        return True

    @lru_cache(maxsize=None)
    def answer(left, right):
        ps = [n for n in range(left, right + 1) if prime(n)]
        if len(ps) < 2:
            return 'There are no adjacent primes.'
        # Tuple ordering implements first-in-increasing-order ties independently
        # of the driver's strict-update scan.
        triples = [(b - a, a, b) for a, b in zip(ps, ps[1:])]
        _, a, b = min(triples)
        _, c, d = min(triples, key=lambda triple: (-triple[0], triple[1]))
        return f'{a},{b} are closest, {c},{d} are most distant.'

    cases = []

    def add(intervals, group, extension=False, ending='\n'):
        assert all(0 <= left <= right <= INT_MAX and right - left <= 1000000
                   for left, right in intervals)
        if not extension:
            assert all(1 <= left < right for left, right in intervals)
        data = ''.join(f'{left} {right}\n' for left, right in intervals)
        if data:
            data = data.rstrip('\n') + ending
        cases.append(dict(group=group, datasets=len(intervals),
                          scope='Extra library contract, outside UVA statement' if extension
                                else 'UVA10140 reviewed statement range; POJ limits not rechecked',
                          input=data, expected=''.join(answer(left, right) + '\n'
                                                      for left, right in intervals)))

    assert answer(2, 17) == '2,3 are closest, 7,11 are most distant.'
    assert answer(14, 17) == 'There are no adjacent primes.'
    assert answer(3, 13) == '3,5 are closest, 7,11 are most distant.'
    assert answer(2, 7) == '2,3 are closest, 3,5 are most distant.'
    add([(2, 17), (14, 17)], 'official_UVA_sample')
    add([(left, right) for left in range(1, 41) for right in range(left + 1, 41)],
        'all_legal_intervals_inside_1_to_40')
    add([(left, right) for left in range(13) for right in range(left, 13)]
        + [(INT_MAX, INT_MAX)], 'extra_zero_one_singleton_contract', extension=True)
    add([(1, 2), (1, 3), (2, 7), (3, 13), (24, 28), (INT_MAX - 1, INT_MAX)],
        'prime_endpoints_empty_one_pair_and_first_ties')
    add([(p * p - 2, p * p + 2) for p in (2, 3, 5, 7, 31, 997, 46337)],
        'prime_squares')
    rng = random.Random(208207)
    intervals = []
    for _ in range(160):
        left = rng.randint(1, INT_MAX - 1000)
        intervals.append((left, left + rng.randint(1, 1000)))
    add(intervals, 'seeded_high_range_trial_division')
    add([(1, 1000001), (1, 3), (INT_MAX - 1000000, INT_MAX),
         (14, 17), (2, 17)], 'million_difference_then_small_EOF_reset', ending='')
    add([], 'empty_EOF')
    cases.append(dict(group='whitespace_EOF', datasets=0,
                      scope='Input termination', input='\n \t\n', expected=''))
    return cases


def main():
    assert __debug__, 'Run without python -O so every check remains active'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('normal', 'sanitizer', 'both'), default='both')
    args = parser.parse_args()
    modes = ('normal', 'sanitizer') if args.mode == 'both' else (args.mode,)
    before = source_hashes()
    rows = {row['id']: row for row in records() if row['id'] in EXAMPLES}
    assert set(rows) == set(EXAMPLES), 'Register examples 207 and 208 first'
    for ident, row in rows.items():
        assert row['driver'] == EXAMPLES[ident] and row['kind'] == 'application'
    compiler = Path(shutil.which(CXX)).resolve()
    compiler_version = subprocess.check_output([str(compiler), '--version'], text=True).splitlines()[0]
    print('Preparing complete motion/trial-division oracle cases', flush=True)
    checks = {'example-207': frog_cases(), 'example-208': prime_cases()}
    for mode in modes:
        work = ROOT / 'build' / 'math-application-usages' / mode
        work.mkdir(parents=True, exist_ok=True)
        report_path = work / 'report.json'
        report_path.unlink(missing_ok=True)
        flags = ['-O2'] if mode == 'normal' else [
            '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                   UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        results = []
        for ident, row in rows.items():
            case_text = ''.join(json.dumps(case, ensure_ascii=False) + '\n' for case in checks[ident])
            fixtures = work / (ident + '.cases.jsonl')
            fixtures.write_text(case_text)
            programs = {'registered': row['program'], 'named_dependencies': copied_program(row)}
            executions = []
            for form, program in programs.items():
                source = work / f'{ident}-{form}.cpp'
                exe = source.with_suffix('')
                source.write_text(program)
                command = [str(compiler), '-std=c++20', *flags, str(source), '-o', str(exe)]
                subprocess.run(command, cwd=ROOT, check=True)
                start = time.monotonic()
                actual = hashlib.sha256()
                for index, case in enumerate(checks[ident]):
                    result = subprocess.run([str(exe)], input=case['input'], text=True,
                                            capture_output=True, check=True, timeout=30, env=env)
                    assert not result.stderr, (ident, form, index, result.stderr)
                    assert result.stdout == case['expected'], (
                        ident, form, index, case['group'], case['input'][:300],
                        result.stdout[:300], case['expected'][:300])
                    # JSON preserves invocation boundaries, including empty output.
                    actual.update((json.dumps(result.stdout) + '\n').encode())
                executions.append(dict(form=form, program_sha256=digest(program.encode()),
                                       executable_sha256=digest(exe.read_bytes()), compile_command=command,
                                       invocations=len(checks[ident]), output_sha256=actual.hexdigest(),
                                       seconds=round(time.monotonic() - start, 6)))
            assert executions[0]['program_sha256'] == row['program_sha256']
            assert executions[0]['output_sha256'] == executions[1]['output_sha256']
            datasets_by_group = Counter()
            for case in checks[ident]:
                datasets_by_group[case['group']] += case['datasets']
            results.append(dict(id=ident, driver=row['driver'], kind=row['kind'],
                                program_sha256=row['program_sha256'],
                                cases_file=str(fixtures.relative_to(ROOT)),
                                cases_sha256=digest(case_text.encode()),
                                invocations_per_program=len(checks[ident]),
                                datasets_per_program=sum(case['datasets'] for case in checks[ident]),
                                groups=dict(Counter(case['group'] for case in checks[ident])),
                                datasets_by_group=dict(datasets_by_group),
                                executions=executions))
            print(mode, ident, len(checks[ident]), 'inputs x 2 exact/copy programs PASS', flush=True)
        assert source_hashes() == before, 'Inputs changed during testing; discard this run'
        report = dict(mode=mode, passed=True, checked_at=datetime.now(timezone.utc).isoformat(),
                      compiler=str(compiler), compiler_version=compiler_version,
                      compiler_sha256=digest(compiler.read_bytes()), platform=platform.platform(),
                      source_sha256=before, programs=results,
                      sanitizer_options={key: env[key] for key in ('ASAN_OPTIONS', 'UBSAN_OPTIONS')},
                      oracle='Literal frog positions over all t in [0,L) for small L; large unique '
                             'planted times modulo 2^30 and explicit boundary equations. Prime '
                             'divisors and each candidate use exact trial division, not a sieve '
                             'or probabilistic primality; adjacent pairs ranked with tuple keys.',
                      scope='Local exact printed programs and named dependency-only copies; '
                            'selected full-range/full-width inputs. Extra zero/singleton prime '
                            'inputs are separately labelled outside the reviewed UVA statement. '
                            'POJ source unavailable. No full-suite, online AC, timing-rank or '
                            'LeakSanitizer claim. Does not directly verify the returned frog period.')
        report_path.write_text(json.dumps(report, indent=2) + '\n')
        print('Report:', report_path.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
