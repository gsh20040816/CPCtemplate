#!/usr/bin/env python3
"""Independent P2158 application verification; one mode by default, --mode both optional.

Reports remain in a fresh build directory, including failures. ASan/UBSan uses the
compiler's default PIE behavior and quarantine; LSan alone is disabled for ptrace.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import shutil
import subprocess
import sys
import tempfile
import time

SELF = Path(__file__).resolve()
ROOT = next(p for p in SELF.parents if (p / 'tests/compiler_config.py').is_file()
            and (p / 'tools/usage_examples.py').is_file())
sys.path.insert(0, str(ROOT / 'tests'))
sys.path.insert(0, str(ROOT / 'tools'))
from compiler_config import CXX
from usage_examples import expand, records

DRIVER = ROOT / 'verify/luogu/P2158.compact.cpp'
CONTRACT = ROOT / 'tests/fixtures/totient-lattice/contract.json'
USAGE = 'example-218'
MAX = 40000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    return sha(path.read_bytes())


def canonical_hash(value):
    return sha(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())


def registration():
    row = next(r for r in records() if r['id'] == USAGE)
    assert row['driver'] == str(DRIVER.relative_to(ROOT))
    assert row['symbol'] == 'LinearSieve' and row['requires'] == ['LinearSieve']
    assert row['kind'] == 'application'
    return row


def registration_snapshot(row):
    # Include derived program/snippet hashes, without coupling to unrelated rows.
    return {k: (sha(v.encode()) if k in ('program', 'snippet') else v) for k, v in row.items()}


def trial_phi(n):
    result, value, p = n, n, 2
    while p * p <= value:
        if value % p == 0:
            result -= result // p
            while value % p == 0:
                value //= p
        p += 1
    if value > 1:
        result -= result // value
    return result


def cases(contract):
    # Eratosthenes prime-multiple updates, not production's linear recurrence.
    phi = list(range(MAX + 1))
    for p in range(2, MAX + 1):
        if phi[p] == p:
            for j in range(p, MAX + 1, p):
                phi[j] -= phi[j] // p
    assert all(phi[n] == trial_phi(n) for n in range(1, MAX + 1))
    answers = [0] * (MAX + 1)
    prefix = 0
    for n in range(2, MAX + 1):
        prefix += phi[n - 1]
        answers[n] = 1 + 2 * prefix
    for n in range(1, 101):
        visible = sum(math.gcd(x, y) == 1 for x in range(n) for y in range(n))
        assert answers[n] == visible
    assert contract['url'] == 'https://www.luogu.com.cn/problem/P2158'
    assert contract['pid'] == 'P2158' and contract['samples'] == [['4', '9']]
    assert answers[1] == 0 and answers[4] == 9
    rng = random.Random(2158)
    values = sorted(set(range(1, 101)) | {127, 128, 129, 255, 256, 257, 999, 1000, 1001,
                    32767, 32768, 32769, 39998, 39999, 40000} |
                    {rng.randint(101, MAX) for _ in range(100)})
    result = [{'group': 'literal_gcd' if n <= 100 else 'independent_phi_reference',
               'input': f'{n}\n', 'expected': f'{answers[n]}\n'} for n in values]
    return result, phi


def main():
    assert __debug__, 'Run without python -O'
    parser = argparse.ArgumentParser(description=__doc__)
    default = 'sanitizer' if any(os.getenv(k) == '1' for k in ('SANITIZE', 'CPC_SANITIZE')) else 'normal'
    parser.add_argument('--mode', choices=('normal', 'sanitizer', 'both'), default=default)
    parser.add_argument('--output', type=Path, help='New, previously nonexistent directory under build/')
    args = parser.parse_args()
    modes = ('normal', 'sanitizer') if args.mode == 'both' else (args.mode,)
    if args.output:
        out = args.output.resolve()
        assert out.is_relative_to(ROOT / 'build'), 'Output must stay under build/'
        out.mkdir(parents=True, exist_ok=False)
    else:
        out = Path(tempfile.mkdtemp(prefix='totient-lattice-', dir=ROOT / 'build'))
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    row = registration()
    initial_registration = registration_snapshot(row)
    driver = DRIVER.read_text()
    snippet = driver[driver.index('int main()'):]
    assert row['snippet'] == snippet
    dependencies = set()
    standalone = expand(driver, DRIVER.parent, dependencies)
    header = ROOT / 'src/compact/number_theory.hpp'
    source = header.read_text()
    block = source[source.index('struct LinearSieve\n'):source.index('template <int mod> struct ModInt')].rstrip()
    assert block.count('struct ') == 1
    minimal_prefix = '#include <iostream>\n#include <vector>\nusing namespace std;\n\n' + block + '\n\n'
    programs = {'registered': row['program'], 'standalone': standalone, 'minimal-copy': minimal_prefix + snippet}
    phi_program = minimal_prefix + 'int main() { LinearSieve s(40000); for (int n=1;n<=40000;n++) cout << s.phi[n] << "\\n"; }\n'
    tracked = sorted({DRIVER, SELF, header, ROOT / 'tests/compiler_config.py', ROOT / 'tools/usage_examples.py', CONTRACT, *dependencies})
    initial_hashes = {str(p.relative_to(ROOT)): file_sha(p) for p in tracked}
    initial_compiler_hash = file_sha(compiler)
    compiler_version = subprocess.check_output([str(compiler), '--version'], text=True)
    checks, phi = cases(json.loads(CONTRACT.read_text()))
    fixture = out / 'cases.jsonl'
    fixture.write_text(''.join(json.dumps(c, sort_keys=True) + '\n' for c in checks))
    phi_fixture = out / 'phi-reference.txt'
    phi_fixture.write_text(''.join(f'{v}\n' for v in phi[1:]))
    fixture_hashes = {str(p.relative_to(ROOT)): file_sha(p) for p in (fixture, phi_fixture)}
    for mode in modes:
        work = out / mode
        work.mkdir()
        flags = ['-std=c++20', '-Wall', '-Wextra'] + (['-O2'] if mode == 'normal' else
                  ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'])
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                   UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        # No inherited LSan/ASan quarantine tweaks or suppression file options.
        env.pop('LSAN_OPTIONS', None)
        report = dict(passed=False, mode=mode, started_at=datetime.now(timezone.utc).isoformat(),
                      compiler=str(compiler), compiler_sha256=initial_compiler_hash, compiler_version=compiler_version,
                      source_sha256=initial_hashes, selected_registration=initial_registration,
                      selected_registration_sha256=canonical_hash(initial_registration), fixture_sha256=fixture_hashes,
                      platform=platform.platform(), flags=flags,
                      sanitizer_options={k: env[k] for k in ('ASAN_OPTIONS', 'UBSAN_OPTIONS')},
                      quarantine='ASan default; no override', pie='compiler default; no override',
                      scope='Actual phi-consumption application; not formal template verification. No OJ/CI/full-suite/LSan claim. Other prime/lp/mu APIs not independently verified.',
                      source_url='https://www.luogu.com.cn/problem/P2158', sample=['4', '9'], n1=0,
                      n1_provenance='Derived from corner-origin diagram/model; not an official sample',
                      oracles={'literal_gcd_n':[1,100], 'eratosthenes_phi_n':[1,MAX], 'trial_division_phi_n':[1,MAX]},
                      application_cases_per_form=len(checks), application_executions=[], phi_harness=None)
        failure = None
        try:
            for name, program in [*programs.items(), ('phi-check', phi_program)]:
                generated = work / (name + '.cpp')
                binary = work / name
                generated.write_text(program)
                command = [str(compiler), *flags, str(generated), '-o', str(binary)]
                execution = dict(form=name, program_sha256=sha(program.encode()), compile_command=command, cases=[])
                if name == 'phi-check':
                    report['phi_harness'] = execution
                else:
                    report['application_executions'].append(execution)
                compiled = subprocess.run(command, capture_output=True, text=True, timeout=120)
                execution['compile'] = dict(exit_code=compiled.returncode, stdout=compiled.stdout, stderr=compiled.stderr)
                assert compiled.returncode == 0, f'{name} compile failure'
                execution['binary_sha256'] = file_sha(binary)
                selected = [{'input':'', 'expected':phi_fixture.read_text(), 'group':'all_phi_entries'}] if name == 'phi-check' else checks
                started = time.monotonic()
                for index, case in enumerate(selected):
                    entry = dict(index=index, group=case['group'], input_sha256=sha(case['input'].encode()), expected_sha256=sha(case['expected'].encode()))
                    execution['cases'].append(entry)
                    ran = subprocess.run([str(binary)], input=case['input'], capture_output=True, text=True, env=env, timeout=10)
                    entry.update(exit_code=ran.returncode, stderr=ran.stderr, actual_sha256=sha(ran.stdout.encode()),
                                 passed=ran.returncode == 0 and not ran.stderr and ran.stdout == case['expected'])
                    if not entry['passed']:
                        entry.update(input=case['input'], expected=case['expected'], actual=ran.stdout)
                    assert entry['passed'], f'{mode} {name} case {index} failed'
                assert file_sha(binary) == execution['binary_sha256'], 'Binary changed during execution'
                assert file_sha(generated) == execution['program_sha256'], 'Generated source changed during execution'
                execution.update(passed=True, seconds=round(time.monotonic()-started, 6))
                print(mode, name, len(selected), 'PASS', flush=True)
        except BaseException as error:
            failure = error
            report['failure'] = f'{type(error).__name__}: {error}'
        finally:
            try:
                current_hashes = {str(p.relative_to(ROOT)): file_sha(p) for p in tracked}
                current_registration = registration_snapshot(registration())
                current_fixtures = {path:file_sha(ROOT/path) for path in fixture_hashes}
                report['after_checks'] = dict(source_sha256=current_hashes, compiler_sha256=file_sha(compiler),
                    selected_registration_sha256=canonical_hash(current_registration), fixture_sha256=current_fixtures)
                assert current_hashes == initial_hashes, 'Sources/helpers/test/contract changed during run'
                assert file_sha(compiler) == initial_compiler_hash, 'Compiler executable changed during run'
                assert current_registration == initial_registration, 'Selected registration changed during run'
                assert current_fixtures == fixture_hashes, 'Generated fixtures changed during run'
                report['provenance_unchanged'] = True
            except BaseException as error:
                report['provenance_unchanged'] = False
                report['provenance_failure'] = f'{type(error).__name__}: {error}'
                if failure is None:
                    failure = error
            report['passed'] = failure is None
            report['finished_at'] = datetime.now(timezone.utc).isoformat()
            (work / 'report.json').write_text(json.dumps(report, indent=2)+'\n')
            print('Report:', (work / 'report.json').relative_to(ROOT), flush=True)
        if failure is not None:
            raise failure


if __name__ == '__main__':
    main()
