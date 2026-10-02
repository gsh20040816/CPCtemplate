#!/usr/bin/env python3
"""Independent AOJ NTL_1_E minimum-norm Bezout usage checks.

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
            and (p / 'src/compact/extended_gcd.hpp').is_file())
sys.path.insert(0, str(ROOT / 'tests'))
from compiler_config import CXX
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records

DRIVER = 'verify/aoj/NTL_1_E.compact.cpp'
CONTRACT = 'tests/fixtures/bezout-minimum/contract.json'
EXAMPLE = 'example-221'
HEADERS = ['src/compact/extended_gcd.hpp']

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

def select_minimum(pairs):
    pairs = set(pairs)
    norm = min(abs(x)+abs(y) for x,y in pairs)
    winners = sorted((x,y) for x,y in pairs if abs(x)+abs(y) == norm)
    if len(winners) == 1:
        return winners[0]
    tied = [(x,y) for x,y in winners if x <= y]
    assert len(tied) == 1, winners
    return tied[0]

def enumerated_oracle(a, b):
    # Signed coefficient enumeration, independent of extended Euclid or inverses.
    # A Bezout solution has |x|<=b and |y|<=a; its norm <=a+b.
    # Thus any better or tied minimum lies in this finite signed box.
    bound = a+b
    g = math.gcd(a,b)
    return select_minimum((x,y) for x in range(-bound,bound+1)
                          for y in range(-bound,bound+1) if a*x+b*y == g)

def endpoint_oracle(a, b):
    g = math.gcd(a,b)
    A, B = a//g, b//g
    # Use Python's modular inverse, not a transcription of the C++ recurrence.
    x = pow(A,-1,B) if B > 1 else 0
    y = (1-A*x)//B
    # Every solution is (x+B*t,y-A*t). This convex piecewise-linear
    # objective can attain an integer minimum at floors/ceilings of its
    # two breakpoints -x/B and y/A. Include neighbors for explicit ties.
    near = {(-x)//B, y//A}
    ts = {q+d for q in near for d in (-1,0,1,2)}
    return select_minimum((x+B*t,y-A*t) for t in ts)

def cases():
    result = []
    def add(a,b,group,expected=None):
        assert 1 <= a <= 10**9 and 1 <= b <= 10**9
        oracle = endpoint_oracle(a,b)
        expected = oracle if expected is None else expected
        assert expected == oracle
        x,y = expected
        assert a*x+b*y == math.gcd(a,b)
        result.append(dict(input=f'{a} {b}\n',expected=f'{x} {y}\n',group=group))
    official = json.loads((ROOT / CONTRACT).read_text())
    assert official['samples'] == [['4 12','1 0'],['3 8','3 -1']]
    assert official['source'] == 'https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=NTL_1_E'
    assert official['domain'] == dict(minimum_a=1,maximum_a=10**9,minimum_b=1,maximum_b=10**9,
        identity='a*x+b*y=gcd(a,b)',primary='minimum abs(x)+abs(y)',secondary='x<=y among tied minima only')
    for data,answer in official['samples']:
        add(*map(int,data.split()),'official_sample',tuple(map(int,answer.split())))
    for a in range(1,26):
        for b in range(1,26):
            add(a,b,'signed_coefficient_enumeration_1_to_25',enumerated_oracle(a,b))
    for a in (1,2,3,25,65536,999999937,999999999,10**9):
        add(a,a,'equal_inputs_tie',(0,1))
        for k in (1,2,3,7,10000):
            if a*k <= 10**9:
                add(a,a*k,'divisible_inputs')
                add(a*k,a,'divisible_reversed')
    for a in range(10**9-15,10**9+1):
        for b in range(10**9-15,10**9+1):
            add(a,b,'near_statement_maxima')
    rng = random.Random(1001)
    for _ in range(200):
        a,b = rng.randint(1,10**9),rng.randint(1,10**9)
        add(a,b,'seeded_full_range')
        add(b,a,'seeded_reversed')
    a,b=1,2
    while b <= 10**9:
        add(a,b,'consecutive_fibonacci')
        add(b,a,'consecutive_fibonacci_reversed')
        a,b=b,a+b
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
    assert row['driver'] == DRIVER and row['kind'] == 'template'
    assert row['symbol'] == 'extended_gcd'
    assert row['requires'] == ['extended_gcd']
    assert not row.get('also_covers')
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
    build = ROOT / 'build/bezout-next'
    build.mkdir(parents=True,exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='bezout-minimum-usage-', dir=build))
    fixture = work / 'cases.jsonl'
    fixture.write_text(fixture_text)
    print('Artifacts:', work.relative_to(ROOT), flush=True)
    for mode in modes:
        flags = ['-O2'] if mode == 'normal' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                   UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        report_path = work / (mode+'.json')
        report = dict(passed=False,mode=mode,checked_at=datetime.now(timezone.utc).isoformat(),
            kind='template',id=EXAMPLE,component='extended_gcd',dependency_only=[],
            statement_source='https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=NTL_1_E',
            before=before, compiler_version=subprocess.check_output([str(compiler),'--version'],text=True),
            platform=platform.platform(), program_sha256=row['program_sha256'],
            cases_file=str(fixture.relative_to(ROOT)), cases_sha256=sha(fixture_text.encode()),
            cases_per_program=len(checks),groups=dict(Counter(c['group'] for c in checks)),
            copied_regions=regions,executions=[],
            oracle='Signed coefficient enumeration for 1<=a,b<=25; independent modular-inverse solution family with exact convex endpoint minimization and tie handling for large cases; both official samples exactly.',
            scope='Only valid AOJ NTL_1_E inputs: positive a,b<=1e9. No signed/zero-input, online AC, full-suite, performance or LeakSanitizer claim.',
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
