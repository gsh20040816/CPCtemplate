#!/usr/bin/env python3
"""Independent P1082 driver, registered-program, and minimal-copy checks.

Defaults to one mode; SANITIZE=1 or CPC_SANITIZE=1 selects sanitizer.
Use --mode both explicitly. Every invocation creates a fresh build directory.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import argparse, hashlib, json, math, os, platform, random, re, shutil
import subprocess, sys, tempfile, time

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'tools/usage_examples.py').is_file()
            and (p / 'src/compact/mod_inverse.hpp').is_file())
sys.path.insert(0, str(ROOT / 'tests'))
from compiler_config import CXX
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records

DRIVER = 'verify/luogu/P1082.compact.cpp'
CONTRACT = 'tests/fixtures/mod-inverse/contract.json'
EXAMPLE = 'example-219'
HEADERS = ['src/compact/extended_gcd.hpp', 'src/compact/mod_inverse.hpp']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def file_sha(path):
    return sha(Path(path).read_bytes())

def selected_registration():
    rows = json.loads((ROOT / 'docs/usage-examples.json').read_text())
    selected = [r for r in rows if r['id'] == EXAMPLE]
    assert len(selected) == 1
    return selected[0]

def transitive_files(path, seen=None):
    seen = set() if seen is None else seen
    path = path.resolve()
    assert path.is_relative_to(ROOT)
    if path in seen:
        return seen
    seen.add(path)
    for inc in re.findall(r'^\s*#include "([^"\n]+)"\s*$', path.read_text(), re.M):
        transitive_files(path.parent / inc, seen)
    return seen

def snapshot(compiler):
    files = transitive_files(ROOT / DRIVER)
    files.update((Path(__file__).resolve(), ROOT / CONTRACT,
                  ROOT / 'tests/compiler_config.py', ROOT / 'tools/usage_examples.py'))
    registration = selected_registration()
    return dict(source_sha256={str(p.relative_to(ROOT)): file_sha(p) for p in sorted(files)},
                selected_registration=registration,
                selected_registration_sha256=sha(json.dumps(registration,sort_keys=True).encode()),
                compiler_executable=str(compiler), compiler_sha256=file_sha(compiler))

def cases():
    result = []
    def add(a, b, group, expected=None):
        assert 2 <= a <= 2000000000 and 2 <= b <= 2000000000
        assert math.gcd(a, b) == 1
        expected = pow(a, -1, b) if expected is None else expected
        assert 1 <= expected < b and a * expected % b == 1
        result.append(dict(input=f'{a} {b}\n', expected=f'{expected}\n', group=group))
    official = json.loads((ROOT / CONTRACT).read_text())
    assert official['samples'] == [['3 10', '7']]
    assert official['source'] == 'https://www.luogu.com.cn/problem/P1082'
    assert official['domain'] == dict(minimum_a=2,maximum_a=2000000000,minimum_b=2,maximum_b=2000000000,solution_guaranteed=True,answer='smallest positive x satisfying a*x == 1 modulo b')
    for data, answer in official['samples']:
        add(*map(int, data.split()), 'official_sample', int(answer))
    # Independent exhaustive search of candidate answers; no Euclidean algorithm.
    for a in range(2, 41):
        for b in range(2, 41):
            if math.gcd(a, b) == 1:
                x = next(x for x in range(1, b) if a*x % b == 1)
                add(a, b, 'exhaustive_coprime_2_to_40', x)
    # Composite moduli invalidate Fermat's a^(b-2) shortcut in general.
    for b in (4, 6, 8, 9, 10, 12, 25, 100, 65536, 1000000000, 1073741824, 2000000000):
        for a in (3, 7, b-1, b+1, 1999999999, 2000000000):
            if 2 <= a <= 2000000000 and math.gcd(a,b) == 1:
                add(a, b, 'composite_moduli_and_a_greater_than_b')
    for b in (2, 3, 40, 99991, 999999937, 1999999999):
        add(b+1, b, 'a_mod_b_is_one', 1)
    for a in range(1999999985, 2000000001):
        for b in range(1999999985, 2000000001):
            if math.gcd(a,b) == 1:
                add(a, b, 'near_statement_maxima')
    rng = random.Random(1082)
    for _ in range(200):
        while True:
            a, b = rng.randint(2,2000000000), rng.randint(2,2000000000)
            if math.gcd(a,b) == 1: break
        add(a, b, 'seeded_full_range')
    # Consecutive Fibonacci values stress Euclidean recursion within the domain.
    a, b = 2, 3
    while b <= 2000000000:
        add(a, b, 'consecutive_fibonacci')
        add(b, a, 'consecutive_fibonacci')
        a, b = b, a+b
    return result

def main():
    assert __debug__, 'Run without python -O'
    parser = argparse.ArgumentParser(description=__doc__)
    default = 'sanitizer' if any(os.getenv(k) == '1' for k in ('SANITIZE','CPC_SANITIZE')) else 'normal'
    parser.add_argument('--mode', choices=('normal','sanitizer','both'), default=default)
    args = parser.parse_args()
    compiler = Path(shutil.which(CXX)).resolve()
    before = snapshot(compiler)
    row = next(r for r in records() if r['id'] == EXAMPLE)
    assert row['driver'] == DRIVER and row['kind'] == 'application'
    assert row['symbol'] == 'mod_inverse'
    assert row['requires'] == ['extended_gcd','mod_inverse']
    assert not row.get('also_covers'), 'extended_gcd is dependency-only'
    driver = (ROOT / DRIVER).read_text()
    assert row['snippet'] == driver[driver.index('int main()'):]
    minimal = '#include <bits/stdc++.h>\nusing namespace std;\n'
    regions = []
    for symbol, header in zip(row['requires'], HEADERS):
        text = (ROOT / header).read_text()
        begin, end = '// BEGIN '+symbol+'\n', '// END '+symbol
        assert text.count(begin) == text.count(end) == 1
        region = text.split(begin,1)[1].split(end,1)[0]
        minimal += region+'\n'
        regions.append(dict(symbol=symbol,path=header,region_sha256=sha(region.encode())))
    minimal += row['snippet']
    assert sha(row['program'].encode()) == row['program_sha256']
    programs = {'complete_driver': driver, 'registered_program': row['program'], 'minimal_copy': minimal}
    checks = cases()
    fixture_text = ''.join(json.dumps(c,sort_keys=True)+'\n' for c in checks)
    modes = ('normal','sanitizer') if args.mode == 'both' else (args.mode,)
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='mod-inverse-application-', dir=build))
    fixture = work / 'cases.jsonl'
    fixture.write_text(fixture_text)
    print('Artifacts:', work.relative_to(ROOT), flush=True)
    for mode in modes:
        flags = ['-O2'] if mode == 'normal' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                   UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        report_path = work / (mode+'.json')
        report = dict(passed=False,mode=mode,checked_at=datetime.now(timezone.utc).isoformat(),
            kind='application',id=EXAMPLE,component='mod_inverse',dependency_only=['extended_gcd'],
            statement_source='https://www.luogu.com.cn/problem/P1082',
            before=before, compiler_version=subprocess.check_output([str(compiler),'--version'],text=True),
            platform=platform.platform(), program_sha256=row['program_sha256'],
            cases_file=str(fixture.relative_to(ROOT)), cases_sha256=sha(fixture_text.encode()),
            cases_per_program=len(checks),groups=dict(Counter(c['group'] for c in checks)),
            copied_regions=regions,executions=[],
            oracle='Exhaustive inverse candidate enumeration for 2<=a,b<=40; Python pow(a,-1,b) for larger cases; official sample exactly.',
            scope='Only valid P1082 inputs: 2<=a,b<=2e9, gcd(a,b)=1. No nonunits, negative a, modulus 1, online AC, full-suite, performance or LeakSanitizer claim.',
            sanitizer_options={k:env[k] for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')},
            pie='Compiler default, no override',quarantine='ASan default, no override')
        try:
            for form, program in programs.items():
                source = ROOT / DRIVER if form == 'complete_driver' else work / (mode+'-'+form+'.cpp')
                if form != 'complete_driver': source.write_text(program)
                exe = work / (mode+'-'+form)
                command = [str(compiler),'-std=c++20',*flags,str(source),'-o',str(exe)]
                execution = dict(form=form,program_sha256=sha(program.encode()),compile_command=command,
                                 source=str(source.relative_to(ROOT)),completed_cases=0)
                report['executions'].append(execution)
                compiled = subprocess.run(command,capture_output=True,text=True,cwd=ROOT,timeout=120)
                execution['compile'] = dict(returncode=compiled.returncode,stdout=compiled.stdout,stderr=compiled.stderr)
                assert compiled.returncode == 0, (form,compiled.stderr)
                execution['executable_sha256'] = file_sha(exe)
                start = time.monotonic()
                outputs = hashlib.sha256()
                for index, case in enumerate(checks):
                    execution['current_case'] = dict(index=index,group=case['group'],input=case['input'])
                    run = subprocess.run([str(exe)],input=case['input'],text=True,capture_output=True,env=env,timeout=10)
                    if run.returncode != 0 or run.stderr or run.stdout != case['expected']:
                        execution['failure'] = dict(index=index,case=case,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr)
                        raise AssertionError(f'{mode} {form} case {index} failed')
                    outputs.update((json.dumps(run.stdout)+'\n').encode())
                    execution['completed_cases'] += 1
                execution.pop('current_case')
                execution.update(stdout_sha256=outputs.hexdigest(),seconds=round(time.monotonic()-start,3))
                print(mode,form,len(checks),'PASS',flush=True)
            assert len({e['stdout_sha256'] for e in report['executions']}) == 1
            assert file_sha(fixture) == report['cases_sha256']
            report['after'] = snapshot(compiler)
            assert report['after'] == before, 'Sources/registration/compiler changed during run'
            report['passed'] = True
        except BaseException as error:
            report['error'] = repr(error)
            raise
        finally:
            report['after'] = snapshot(compiler)
            report['source_unchanged'] = report['after'] == before
            if not report['source_unchanged']:
                report['passed'] = False
            report_path.write_text(json.dumps(report,indent=2)+'\n')
            print('Report:',report_path.relative_to(ROOT),flush=True)

if __name__ == '__main__': main()
