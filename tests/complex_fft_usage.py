#!/usr/bin/env python3
"""Check direct ComplexFFT P3803 usage against independent exact convolution.

Normal mode is default; SANITIZE=1 or CPC_SANITIZE=1 selects ASan/UBSan.
All generated programs, large fixtures and reports stay under build/.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import argparse
import hashlib
import itertools
import json
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from compiler_config import CXX
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records

DRIVER = 'verify/luogu/P3803.transform.compact.cpp'
CORE = 'src/compact/fft.hpp'
FIXTURES = 'tests/fixtures/complex-fft-transform'
EXAMPLE = 'example-222'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    return sha(Path(path).read_bytes())


def snapshot(compiler):
    files = [DRIVER, CORE, 'tests/complex_fft_usage.py', 'tests/compiler_config.py',
             'tools/usage_examples.py', 'docs/usage/' + EXAMPLE + '.cpp']
    files += [str(p.relative_to(ROOT)) for p in sorted((ROOT / FIXTURES).glob('*')) if p.is_file()]
    registration = [r for r in json.loads((ROOT / 'docs/usage-examples.json').read_text())
                    if r['id'] == EXAMPLE]
    catalog = [r for r in json.loads((ROOT / 'docs/catalog.json').read_text()) if r[1] == 'ComplexFFT']
    assert len(registration) == len(catalog) == 1
    frontend = Path(subprocess.check_output([str(compiler), '-print-prog-name=cc1plus'], text=True).strip()).resolve()
    return dict(source_sha256={p: file_sha(ROOT / p) for p in files},
                selected_registration=registration[0], selected_catalog=catalog[0],
                compiler_executable=str(compiler), compiler_sha256=file_sha(compiler),
                frontend_executable=str(frontend), frontend_sha256=file_sha(frontend))


def schoolbook(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i+j] += x*y
    return result


def cases():
    yield 'official_sample', [1, 2], [1, 2, 1], [1, 4, 5, 2]
    for a, b in [([0], [0]), ([9], [9]), ([0], [1, 9, 3]),
                 ([9], [1, 0, 2, 9]), ([0]*19, [9]*37),
                 ([0]*7+[9], [9]+[0]*15), ([1, 2, 3], [9]*67)]:
        yield 'fixed_zero_constant_impulse_asymmetric', a, b, schoolbook(a, b)
    values = [list(v) for n in range(1, 4) for v in itertools.product((0, 9), repeat=n)]
    for a in values:
        for b in values:
            yield 'exhaustive_short_binary', a, b, schoolbook(a, b)
    rng = random.Random(380322220261002)
    for k in range(1, 13):
        for shift in (-1, 0, 1):
            length = 2**k + shift
            a = [rng.randrange(10) for _ in range(min(7, length))]
            b = [rng.randrange(10) for _ in range(length-len(a)+1)]
            yield 'padding_boundaries', a, b, schoolbook(a, b)
    for _ in range(100):
        a = [rng.randrange(10) for _ in range(rng.randint(1, 80))]
        b = [rng.randrange(10) for _ in range(rng.randint(1, 90))]
        yield 'seeded_schoolbook', a, b, schoolbook(a, b)
    n = 1000001
    yield 'maximum_all_nine', [9]*n, [9]*n, [81*min(i+1, 2*n-1-i) for i in range(2*n-1)]
    # Only five nonzero terms in a. Exact integer shifts, independent of FFT.
    a, b = [0]*n, [i % 10 for i in range(n)]
    taps = [(0, 9), (1, 7), (131071, 3), (524288, 5), (1000000, 8)]
    expected = [0]*(2*n-1)
    for shift, value in taps:
        a[shift] = value
        for j, x in enumerate(b):
            expected[shift+j] += value*x
    yield 'maximum_sparse_periodic', a, b, expected


def main():
    if not __debug__:
        raise RuntimeError('Run without python -O; assertions are required')
    parser = argparse.ArgumentParser(description=__doc__)
    default = 'sanitizer' if any(os.getenv(k) == '1' for k in ('SANITIZE', 'CPC_SANITIZE')) else 'normal'
    parser.add_argument('--mode', choices=('normal', 'sanitizer', 'both'), default=default)
    parser.add_argument('--report-dir', type=Path, help='Explicit report directory; default is the fresh build directory')
    args = parser.parse_args()
    compiler = Path(shutil.which(CXX)).resolve()
    if args.report_dir:
        args.report_dir.mkdir(parents=True, exist_ok=True)
    before = snapshot(compiler)
    row = next(r for r in records() if r['id'] == EXAMPLE)
    assert row['driver'] == DRIVER and row.get('kind', 'template') == 'template'
    assert row['symbol'] == 'ComplexFFT' and row['requires'] == ['ComplexFFT']
    assert not row.get('also_covers')
    driver = (ROOT / DRIVER).read_text()
    snippet = (ROOT / ('docs/usage/' + EXAMPLE + '.cpp')).read_text()
    assert row['snippet'] == snippet == driver[driver.index('int main()'):]
    assert 'convolution_fft' not in driver
    assert driver.count('fft.transform(') == 3
    core = '\n'.join(line for line in (ROOT / CORE).read_text().splitlines()
                     if not line.startswith('#') and line != 'using namespace std;') + '\n'
    printed = '#include <bits/stdc++.h>\nusing namespace std;\n' + core + snippet
    programs = {'direct_driver': driver, 'expanded_registered': row['program'], 'printed_usage': printed}
    assert sha(row['program'].encode()) == row['program_sha256']
    (ROOT / 'build').mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='complex-fft-transform-', dir=ROOT / 'build'))
    checks = []
    for index, (group, a, b, expected) in enumerate(cases()):
        assert 1 <= len(a) <= 1000001 and 1 <= len(b) <= 1000001
        assert all(0 <= x <= 9 for x in a+b)
        data = (f'{len(a)-1} {len(b)-1}\n' + ' '.join(map(str, a)) + '\n' + ' '.join(map(str, b)) + '\n').encode()
        want = (' '.join(map(str, expected)) + ' \n').encode()
        inp, out = work / f'case-{index}.in', work / f'case-{index}.out'
        inp.write_bytes(data)
        out.write_bytes(want)
        checks.append(dict(group=group, input=str(inp.relative_to(ROOT)), expected=str(out.relative_to(ROOT)),
                           input_sha256=sha(data), expected_sha256=sha(want), coefficients=len(expected)))
    assert (ROOT / checks[0]['input']).read_bytes() == (ROOT / FIXTURES / 'sample.in').read_bytes()
    assert (ROOT / checks[0]['expected']).read_bytes().split() == (ROOT / FIXTURES / 'sample.out').read_bytes().split()
    fixture = work / 'cases.json'
    fixture.write_text(json.dumps(checks, indent=2)+'\n')
    with localcontext() as context:
        context.prec = 100
        u, levels, norm = Decimal(2)**-53, 21, Decimal(81000081)
        bound = norm*((1+u)**(3*levels)*(1+Decimal(5).sqrt()*u)**(3*levels+1)*(1+8*u)**(3*levels)-1)
        assert bound < Decimal('0.000006386') < Decimal('0.5')
    print('Artifacts:', work.relative_to(ROOT), flush=True)
    modes = ('normal', 'sanitizer') if args.mode == 'both' else (args.mode,)
    for mode in modes:
        flags = ['-std=c++20', '-O2'] if mode == 'normal' else ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        report = dict(passed=False, mode=mode, checked_at=datetime.now(timezone.utc).isoformat(),
                      id=EXAMPLE, component='ComplexFFT', driver=DRIVER, before=before,
                      program_sha256=row['program_sha256'], cases_file=str(fixture.relative_to(ROOT)),
                      cases_sha256=file_sha(fixture), cases_per_program=len(checks),
                      groups=dict(Counter(c['group'] for c in checks)), executions=[], flags=flags,
                      compiler_version=subprocess.check_output([str(compiler), '--version'], text=True),
                      platform=platform.platform(), conditional_absolute_error_bound=str(bound),
                      assumptions=json.loads((ROOT / FIXTURES / 'contract.json').read_text())['floating_point_assumptions'],
                      scope='Local exact-output tests of direct ComplexFFT usage only. No online AC, judge timing, universal floating-point guarantee, or LeakSanitizer claim.',
                      oracle='Integer schoolbook; maximum all-nine triangle; maximum sparse times periodic integer shifts. No FFT or wrapper oracle.',
                      sanitizer_options={k: env[k] for k in ('ASAN_OPTIONS', 'UBSAN_OPTIONS')},
                      pie='Compiler default, no override', quarantine='ASan default, no override')
        try:
            probe_source = work / (mode+'-precision.cpp')
            probe_source.write_text('#include <limits>\n#include <cfenv>\n#include <iostream>\n'
                '#ifdef __FAST_MATH__\n#error fast math is unsupported\n#endif\n'
                'int main(){ if(std::fegetround()!=FE_TONEAREST) return 1; '
                'std::cout << std::numeric_limits<long double>::radix << " " '
                '<< std::numeric_limits<long double>::digits << " nearest\\n"; }\n')
            probe_exe = work / (mode+'-precision')
            probe_command = [str(compiler), *flags, str(probe_source), '-o', str(probe_exe)]
            subprocess.run(probe_command, check=True, capture_output=True, timeout=120)
            probe = subprocess.run([str(probe_exe)], capture_output=True, text=True, env=env, timeout=20)
            assert probe.returncode == 0 and not probe.stderr
            radix, digits, rounding = probe.stdout.split()
            assert int(radix) == 2 and int(digits) >= 53 and rounding == 'nearest'
            report['precision_probe'] = dict(stdout=probe.stdout, program_sha256=file_sha(probe_source),
                binary_sha256=file_sha(probe_exe), compile_command=probe_command)
            for form, program in programs.items():
                source = ROOT / DRIVER if form == 'direct_driver' else work / (mode+'-'+form+'.cpp')
                if form != 'direct_driver': source.write_text(program)
                exe = work / (mode+'-'+form)
                command = [str(compiler), *flags, str(source), '-o', str(exe)]
                entry = dict(form=form, program_sha256=sha(program.encode()), compile_command=command, completed_cases=0)
                report['executions'].append(entry)
                compiled = subprocess.run(command, capture_output=True, text=True, timeout=120)
                entry['compile'] = dict(returncode=compiled.returncode, stdout=compiled.stdout, stderr=compiled.stderr)
                assert compiled.returncode == 0, compiled.stderr
                entry['binary_sha256'] = file_sha(exe)
                started = time.monotonic()
                outputs, large_times = hashlib.sha256(), {}
                for index, case in enumerate(checks):
                    data = (ROOT / case['input']).read_bytes()
                    want = (ROOT / case['expected']).read_bytes()
                    assert sha(data) == case['input_sha256'] and sha(want) == case['expected_sha256']
                    start = time.monotonic()
                    run = subprocess.run([str(exe)], input=data, capture_output=True, env=env, timeout=180)
                    elapsed = time.monotonic()-start
                    if run.returncode or run.stderr or run.stdout != want:
                        entry['failure'] = dict(case_index=index, group=case['group'], returncode=run.returncode,
                                                stderr=run.stderr.decode(errors='replace'), stdout_sha256=sha(run.stdout))
                        raise AssertionError(f'{mode} {form} case {index} failed')
                    outputs.update(run.stdout)
                    entry['completed_cases'] += 1
                    if case['group'].startswith('maximum_'):
                        large_times[case['group']] = round(elapsed, 3)
                assert file_sha(exe) == entry['binary_sha256'], 'Binary changed during run'
                entry.update(stdout_sha256=outputs.hexdigest(), seconds=round(time.monotonic()-started, 3), maximum_case_seconds=large_times)
                print(mode, form, len(checks), 'PASS', large_times, flush=True)
            assert len({e['stdout_sha256'] for e in report['executions']}) == 1
            assert file_sha(fixture) == report['cases_sha256'], 'Fixture manifest changed during run'
            report['after'] = snapshot(compiler)
            assert report['after'] == before, 'Sources/catalog/registration/compiler changed; rerun'
            report['passed'] = True
        except BaseException as error:
            report['error'] = repr(error)
            raise
        finally:
            report['after'] = snapshot(compiler)
            report['source_unchanged'] = report['after'] == before
            if not report['source_unchanged']: report['passed'] = False
            path = (args.report_dir / ('complex-fft-transform-'+mode+'.json')
                    if args.report_dir else work / (mode+'.json'))
            path.write_text(json.dumps(report, indent=2)+'\n')
            print('Report:', path, flush=True)


if __name__ == '__main__':
    main()
