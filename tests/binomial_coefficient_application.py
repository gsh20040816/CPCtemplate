#!/usr/bin/env python3
"""Independent P1313 checks of registered, standalone and minimal-copy programs.

Defaults to one normal profile; SANITIZE=1 or CPC_SANITIZE=1 selects ASan/UBSan.
Use --mode both explicitly for serial execution. Runtime artifacts stay in build/;
source-bound reports (including partial failures) are saved in verification/.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import re
import shutil
import subprocess
import sys
import time

from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import expand, records

MOD = 10007
DRIVER = 'verify/luogu/P1313.compact.cpp'
DRIVER_SHA = '3d813d04128e6bc1b0ae54cd3f561b67ddfea5c5b6f7730e2b494312a100159e'
PROGRAM_SHA = '966e0009c4da1f035bfeaebe805dae0725d34f70b94a994297f55af7cd8bafe3'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    return sha(Path(path).read_bytes())


def polynomial_row(a, b, k):
    """Literally multiply by by+ax k times; no binomial or factorial formula."""
    row = [1]
    for _ in range(k):
        nxt = [0] * (len(row) + 1)
        for x_degree, coefficient in enumerate(row):
            nxt[x_degree] = (nxt[x_degree] + b * coefficient) % MOD
            nxt[x_degree + 1] = (nxt[x_degree + 1] + a * coefficient) % MOD
        row = nxt
    return row


def cases():
    result = []

    def add(a, b, k, n, want, group):
        m = k - n
        assert 0 <= a <= 10**6 and 0 <= b <= 10**6
        assert 0 <= n <= k <= 1000 and 0 <= m <= k
        result.append(dict(group=group, input=f'{a} {b} {k} {n} {m}\n',
                           expected=f'{want}\n'))

    for a in range(4):
        for b in range(4):
            for k in range(9):
                for n, want in enumerate(polynomial_row(a, b, k)):
                    add(a, b, k, n, want, 'exhaustive_literal_bases_0_to_3_k_0_to_8')
    # Includes zero bases with zero exponents, both endpoints, residues zero/one,
    # largest legal inputs, and bases just below/above the modulus.
    bases = (0, 1, MOD - 1, MOD, MOD + 1, 99 * MOD, 10**6)
    for a in bases:
        for b in bases:
            for k in (0, 1, 2, 10, 999, 1000):
                for n in sorted({0, k // 2, k}):
                    want = math.comb(k, n) * pow(a, n, MOD) * pow(b, k-n, MOD) % MOD
                    add(a, b, k, n, want, 'zero_one_modulus_maximum_boundaries')
    rng = random.Random(1313216)
    for _ in range(200):
        a, b = rng.randrange(10**6 + 1), rng.randrange(10**6 + 1)
        k = rng.randrange(1001)
        n = rng.randrange(k + 1)
        want = math.comb(k, n) * pow(a, n, MOD) * pow(b, k-n, MOD) % MOD
        add(a, b, k, n, want, 'seeded_full_statement_bounds_exact_comb')
    # Entire maximum row: addition-only Pascal recurrence, cross-checked against
    # Python exact integer combinatorics, neither sharing modular inversion.
    row = polynomial_row(1, 1, 1000)
    for n, want in enumerate(row):
        assert want == math.comb(1000, n) % MOD
        add(1, 1, 1000, n, want, 'complete_k1000_pascal_row')
    add(1, 1, 3, 1, 3, 'canonical_hand_checked_not_claimed_official_sample')
    return result


def minimal_program(row):
    """Same start-to-next-top-level-struct selection rule as the book builder."""
    path = 'src/compact/number_theory.hpp'
    lines = (ROOT / path).read_text().splitlines()
    starts = []
    for i, line in enumerate(lines):
        match = re.match(r'^(?:template.*?\s+)?struct\s+(\w+)', line)
        if match:
            starts.append((i, match[1]))
    regions = []
    code = ['#include <cassert>\n#include <iostream>\n#include <vector>\n#include <optional>\n#include <utility>\nusing namespace std;\n']
    assert row['requires'] == ['ModInt', 'Binomial']
    for symbol in row['requires']:
        idx = next(i for i, item in enumerate(starts) if item[1] == symbol)
        start = starts[idx][0]
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        if start and lines[start - 1].startswith('template'):
            start -= 1
        if end and lines[end - 1].startswith('template'):
            end -= 1
        region = '\n'.join(lines[start:end]) + '\n'
        assert re.findall(r'^(?:template.*?\s+)?struct\s+(\w+)', region, re.M) == [symbol]
        code.append(region)
        regions.append(dict(symbol=symbol, path=path, start_line=start+1,
                            end_line=end, region_sha256=sha(region.encode())))
    code.append(row['snippet'])
    return '\n'.join(code), regions


def main():
    assert __debug__, 'Run without python -O'
    parser = argparse.ArgumentParser(description=__doc__)
    default = 'sanitizer' if any(os.getenv(key) == '1' for key in ('SANITIZE', 'CPC_SANITIZE')) else 'normal'
    parser.add_argument('--mode', choices=('normal', 'sanitizer', 'both'), default=default)
    args = parser.parse_args()
    modes = ('normal', 'sanitizer') if args.mode == 'both' else (args.mode,)
    assert MOD > 1 and all(MOD % d for d in range(2, math.isqrt(MOD)+1))
    assert 1000 < MOD
    row = next(r for r in records() if r['id'] == 'example-216')
    assert row['driver'] == DRIVER and row['kind'] == 'application'
    assert file_sha(ROOT / DRIVER) == DRIVER_SHA
    assert row['program_sha256'] == PROGRAM_SHA
    driver = (ROOT / DRIVER).read_text()
    assert row['snippet'] == driver[driver.index('int main()'):]
    included = set()
    standalone = expand(driver, (ROOT / DRIVER).parent, included)
    minimal, regions = minimal_program(row)
    dependencies = sorted(str(p.relative_to(ROOT)) for p in included)
    programs = {'registered_expanded_context': row['program'],
                'standalone_expanded_driver': standalone,
                'minimal_declared_regions': minimal}
    source_paths = sorted({DRIVER, 'tests/binomial_coefficient_application.py',
                           'tests/compiler_config.py', 'tools/usage_examples.py', *dependencies})
    source_hashes = {p: file_sha(ROOT / p) for p in source_paths}
    # Hash only the selected registration; unrelated metadata can change in parallel.
    registration = {k: v for k, v in row.items() if k not in ('program', 'snippet')}
    compiler = Path(shutil.which(CXX)).resolve()
    compiler_version = subprocess.check_output([str(compiler), '--version'], text=True)
    checks = cases()
    fixture_text = ''.join(json.dumps(c, sort_keys=True) + '\n' for c in checks)
    for mode in modes:
        work = ROOT / 'build' / 'binomial-coefficient' / mode
        work.mkdir(parents=True, exist_ok=True)
        fixture = work / 'cases.jsonl'
        fixture.write_text(fixture_text)
        report_path = ROOT / 'verification' / f'binomial-coefficient-{mode}.json'
        flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        env = dict(os.environ)
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                   UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        report = dict(mode=mode, passed=False, checked_at=datetime.now(timezone.utc).isoformat(),
                      compiler=str(compiler), compiler_version=compiler_version,
                      compiler_sha256=file_sha(compiler), platform=platform.platform(),
                      source_sha256=source_hashes, registration=registration,
                      registration_sha256=sha(json.dumps(registration, sort_keys=True).encode()),
                      fixtures=str(fixture.relative_to(ROOT)), fixtures_sha256=sha(fixture_text.encode()),
                      invocations_per_form=len(checks), groups=dict(Counter(c['group'] for c in checks)),
                      sanitizer_options={k: env[k] for k in ('ASAN_OPTIONS', 'UBSAN_OPTIONS')},
                      quarantine='ASan default; no overrides',
                      statement_source='https://www.luogu.com.cn/problem/P1313',
                      statement_reviewed='2026-10-02', modulus_prime_by_trial_division=True,
                      oracle='Literal polynomial multiplication for exhaustive small cases; exact math.comb '
                             'and Python modular powers for boundaries/random cases; complete k=1000 '
                             'Pascal row cross-checked with exact math.comb. No C++ factorial/inverse oracle.',
                      scope='Single legal P1313 instance per invocation, exact one-line output. '
                            'Local checks only; no online AC, full-suite, performance or LSan claim. '
                            'Canonical 1 1 3 1 2 is hand-checked, not asserted to be an official sample.',
                      executions=[])
        try:
            for form, program in programs.items():
                source = work / (form + '.cpp')
                binary = work / form
                source.write_text(program)
                command = [str(compiler), '-std=c++20', *flags, str(source), '-o', str(binary)]
                execution = dict(form=form, source=str(source.relative_to(ROOT)),
                                 program_sha256=sha(program.encode()), compile_command=command,
                                 project_dependencies=[DRIVER, *dependencies] if form != 'minimal_declared_regions'
                                 else [DRIVER, 'src/compact/number_theory.hpp'],
                                 copied_regions=regions if form == 'minimal_declared_regions' else [], cases=[])
                report['executions'].append(execution)
                compiled = subprocess.run(command, capture_output=True, text=True, cwd=ROOT, timeout=120)
                execution['compile'] = dict(exit_code=compiled.returncode, stdout=compiled.stdout, stderr=compiled.stderr)
                assert compiled.returncode == 0, f'{form} compilation failed'
                execution['binary_sha256'] = file_sha(binary)
                start = time.monotonic()
                for index, case in enumerate(checks):
                    entry = dict(index=index, group=case['group'], input_sha256=sha(case['input'].encode()),
                                 expected_sha256=sha(case['expected'].encode()))
                    execution['cases'].append(entry)
                    try:
                        ran = subprocess.run([str(binary)], input=case['input'], capture_output=True,
                                             text=True, env=env, timeout=10)
                    except subprocess.TimeoutExpired as error:
                        entry.update(exit_code=None, timeout=True, stderr=str(error))
                        raise
                    entry.update(exit_code=ran.returncode, stderr=ran.stderr,
                                 actual_sha256=sha(ran.stdout.encode()),
                                 passed=ran.returncode == 0 and ran.stderr == '' and ran.stdout == case['expected'])
                    if not entry['passed']:
                        entry.update(input=case['input'], expected=case['expected'], actual=ran.stdout)
                    assert entry['passed'], f'{mode} {form} case {index}: {entry}'
                execution.update(passed=True, seconds=round(time.monotonic() - start, 6))
                print(mode, form, len(checks), 'PASS', flush=True)
            assert source_hashes == {p: file_sha(ROOT / p) for p in source_paths}, 'Test dependencies changed during run'
            report['passed'] = True
        except BaseException as error:
            report['failure'] = f'{type(error).__name__}: {error}'
            raise
        finally:
            report['finished_at'] = datetime.now(timezone.utc).isoformat()
            report_path.write_text(json.dumps(report, indent=2) + '\n')
            (work / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print('Report:', report_path.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
