#!/usr/bin/env python3
"""P3372 complete-driver, registered-program and minimal-copy independent checks.

Default: one mode, selected by SANITIZE/CPC_SANITIZE; --mode can override it.
Each invocation preserves a fresh artifact directory, including failed attempts.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
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

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'tools/usage_examples.py').is_file()
            and (p / 'src/compact/data_structure.hpp').is_file())
sys.path.insert(0, str(ROOT / 'tests'))
from compiler_config import CXX
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records

DRIVER = 'verify/luogu/P3372.compact.cpp'
HEADER = 'src/compact/data_structure.hpp'
CONTRACT = 'tests/fixtures/lazy-segment/contract.json'
EXAMPLE = 'example-220'
CAP = 2 * 10**18
DOMAIN = dict(minimum_n=1, maximum_n=100000, minimum_m=1, maximum_m=100000,
              initial_values='positive integers', increments='positive integers',
              maximum_total_sum=CAP)
SOURCE = 'https://www.luogu.com.cn/problem/P3372'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def file_sha(path):
    return sha(Path(path).read_bytes())

def selected_registration():
    rows = json.loads((ROOT / 'docs/usage-examples.json').read_text())
    chosen = [r for r in rows if r['id'] == EXAMPLE]
    assert len(chosen) == 1, f'Expected exactly one {EXAMPLE} registration'
    return chosen[0]

def transitive_files(path, seen=None):
    seen = set() if seen is None else seen
    path = path.resolve()
    assert path.is_relative_to(ROOT), path
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
                compiler_executable=str(compiler), compiler_sha256=file_sha(compiler),
                compiler_version=subprocess.check_output([str(compiler),'--version'],text=True))

def literal(name, values, operations):
    a = values.copy()
    out = []
    assert 1 <= len(a) <= 100000 and 1 <= len(operations) <= 100000
    assert all(x > 0 for x in a) and sum(a) <= CAP
    for op in operations:
        kind, l, r, *rest = op
        assert 1 <= l <= r <= len(a)
        if kind == 1:
            k, = rest
            assert k > 0
            for i in range(l - 1, r):
                a[i] += k
            assert sum(a) <= CAP
        else:
            assert kind == 2 and not rest
            out.append(sum(a[l - 1:r]))
    return serialize(name, values, operations, out)

def serialize(name, values, operations, out):
    data = f'{len(values)} {len(operations)}\n' + ' '.join(map(str, values)) + '\n'
    data += ''.join(' '.join(map(str, op)) + '\n' for op in operations)
    return name, data, ''.join(str(x) + '\n' for x in out)

def cases():
    official = json.loads((ROOT / CONTRACT).read_text())
    assert official['source'] == SOURCE
    assert official['domain'] == DOMAIN
    assert official['samples'] == [['5 5\n1 5 4 2 3\n2 2 4\n1 2 3 2\n2 3 4\n1 1 5 1\n2 1 4', '11\n8\n20']]
    for i, (data, output) in enumerate(official['samples']):
        yield f'official-sample-{i+1}', data.rstrip()+'\n', output.rstrip()+'\n'
    yield literal('minimum-query', [1], [(2, 1, 1)])
    yield literal('minimum-update-no-output', [1], [(1, 1, 1, 1)])
    yield literal('singleton-cap', [1], [(1, 1, 1, CAP-1), (2, 1, 1)])
    yield literal('large-initial', [CAP], [(2, 1, 1)])
    yield literal('nonpower-cap-push', [1]*7,
                  [(1,1,7,(CAP-7)//7),(2,2,6),(1,4,4,2),(2,1,7),(2,4,4)])
    rng = random.Random(33722026)
    for n in [1,2,3,7,8,15,16,17,31]:
        values = [rng.randint(1,10**9) for _ in range(n)]
        ops = []
        def all_ranges():
            ops.extend((2,l,r) for l in range(1,n+1) for r in range(l,n+1))
        all_ranges()
        # Nested/full/singleton/boundary updates with interleaved all-range reads.
        for l,r in [(1,n),(1,n),(max(1,n//3),max(1,2*n//3)),(1,1),(n,n)]:
            ops.append((1,l,r,rng.randint(1,10**10)))
            all_ranges()
        # Consecutive updates intentionally accumulate tags before any query.
        for step in range(35):
            for _ in range(1+step%4):
                l=rng.randint(1,n); r=rng.randint(l,n)
                ops.append((1,l,r,rng.randint(1,10**10)))
            all_ranges()
        yield literal(f'literal-allranges-n{n}',values,ops)
    n=100000
    # Exact maximum n,m; Python scalar oracle, no segment tree/Fenwick dependency.
    values=[10**9]*n; ops=[]; out=[]; value=10**9
    for j in range(50000):
        k=12345+j; ops.append((1,1,n,k)); value+=k
        l=1+(j*7919)%n; r=l+(j*1543)%(n-l+1)
        ops.append((2,l,r)); out.append((r-l+1)*value)
    assert len(ops)==100000 and n*value<=CAP
    yield serialize('maximum-global-add-partial-query',values,ops,out)
    # Point updates at maximum size; independently maintained literal array and scalar total.
    values=[1]*n; a=values.copy(); total=n; ops=[]; out=[]
    for j in range(50000):
        p=1+(j*7919)%n; k=10**12+j
        ops.append((1,p,p,k)); a[p-1]+=k; total+=k
        if j%2: ops.append((2,p,p)); out.append(a[p-1])
        else: ops.append((2,1,n)); out.append(total)
    assert len(ops)==100000 and total<=CAP
    yield serialize('maximum-point-add',values,ops,out)
    # Reach the exact official sum ceiling, then force lazy propagation with partial queries.
    ops=[(1,1,n,CAP//n-1),(2,1,n),(2,2,n-1),(2,1,1),(2,n,n)]
    yield serialize('maximum-n-exact-sum-cap',[1]*n,ops,[CAP,(n-2)*(CAP//n),CAP//n,CAP//n])

def main():
    assert __debug__, 'Run without python -O'
    parser = argparse.ArgumentParser(description=__doc__)
    default = 'sanitizer' if any(os.getenv(k) == '1' for k in ('SANITIZE','CPC_SANITIZE')) else 'normal'
    parser.add_argument('--mode', choices=('normal','sanitizer','both'), default=default)
    args = parser.parse_args()
    resolved = shutil.which(CXX)
    assert resolved, f'Compiler not found: {CXX}'
    compiler = Path(resolved).resolve()
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='lazy-segment-usage-', dir=build))
    print('Artifacts:', work.relative_to(ROOT), flush=True)
    modes = ('normal','sanitizer') if args.mode == 'both' else (args.mode,)
    for mode in modes:
        report_path = work / (mode+'.json')
        report = dict(passed=False, mode=mode, id=EXAMPLE, kind='template', component='LazySeg',
                      checked_at=datetime.now(timezone.utc).isoformat(), platform=platform.platform(),
                      statement_source=SOURCE, domain=DOMAIN, executions=[],
                      pie='Compiler default, no override', quarantine='ASan default, no override',
                      scope='Official positive-only P3372 inputs, n,m<=100000 and total<=2e18. No negative API extension, O(n) build, online AC or full-suite claim.',
                      oracle='Python literal-array sums for every interval of small arrays; uniform-value and point-array/scalar-total identities for maximum cases.')
        before = None
        try:
            before = snapshot(compiler)
            report['before'] = before
            row = next(r for r in records() if r['id'] == EXAMPLE)
            assert row['driver'] == DRIVER and row.get('kind','template') == 'template'
            assert row['symbol'] == 'LazySeg' and row['requires'] == ['LazySeg']
            assert not row.get('also_covers')
            driver = (ROOT / DRIVER).read_text()
            start = re.search(r'(?m)^int main\(\)', driver)
            assert start and row['snippet'] == driver[start.start():]
            header = (ROOT / HEADER).read_text()
            # Copy the entire unchanged existing LazySeg, stopping at its next top-level struct.
            assert header.count('struct LazySeg\n') == header.count('struct XorBasis\n') == 1
            core = header[header.index('struct LazySeg\n'):header.index('struct XorBasis\n')]
            assert re.findall(r'(?m)^struct (\w+)', core) == ['LazySeg']
            minimal = '#include <bits/stdc++.h>\nusing namespace std;\n' + core + row['snippet']
            assert sha(row['program'].encode()) == row['program_sha256']
            programs = {'complete_driver': driver, 'registered_program': row['program'], 'minimal_copy': minimal}
            report.update(program_sha256=row['program_sha256'], copied_region=dict(path=HEADER,symbol='LazySeg',region_sha256=sha(core.encode())))
            checks = list(cases())
            fixture_text = ''.join(json.dumps(dict(group=name,input=data,expected=want),sort_keys=True)+'\n' for name,data,want in checks)
            fixture = work / (mode+'-cases.jsonl')
            fixture.write_text(fixture_text)
            fixture_hash = file_sha(fixture)
            report.update(cases_file=str(fixture.relative_to(ROOT)), cases_sha256=fixture_hash,
                          cases_per_program=len(checks), groups=[name for name,_,_ in checks])
            flags = ['-std=c++20','-Wall','-Wextra']
            flags += ['-O2'] if mode == 'normal' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
            env = os.environ.copy()
            for key in ('ASAN_OPTIONS','LSAN_OPTIONS','UBSAN_OPTIONS'):
                env.pop(key,None)
            if mode == 'sanitizer':
                env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                           UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
            report['sanitizer_options'] = {key:env.get(key) for key in ('ASAN_OPTIONS','UBSAN_OPTIONS','LSAN_OPTIONS')}
            report['flags'] = flags
            report_path.write_text(json.dumps(report,indent=2)+'\n')
            for form, program in programs.items():
                source = ROOT / DRIVER if form == 'complete_driver' else work / (mode+'-'+form+'.cpp')
                if form != 'complete_driver': source.write_text(program)
                binary = work / (mode+'-'+form)
                command = [str(compiler),*flags,str(source),'-o',str(binary)]
                execution = dict(form=form,program_sha256=sha(program.encode()),
                                 source=str(source.relative_to(ROOT)),source_sha256=file_sha(source),
                                 compile_command=command,completed_cases=0,cases=[])
                report['executions'].append(execution)
                compiled = subprocess.run(command,capture_output=True,text=True,cwd=ROOT,timeout=120,env=env)
                execution['compile'] = dict(returncode=compiled.returncode,stdout=compiled.stdout,stderr=compiled.stderr)
                assert compiled.returncode == 0, f'{form} compile failed: {compiled.stderr}'
                execution['executable_sha256'] = file_sha(binary)
                stdout_hash = hashlib.sha256()
                for index,(name,data,want) in enumerate(checks):
                    stem = work / f'{mode}-{form}-{index:02d}'
                    case = dict(index=index,group=name,input_sha256=sha(data.encode()),expected_sha256=sha(want.encode()))
                    execution['cases'].append(case)
                    started = time.monotonic()
                    try:
                        result = subprocess.run([str(binary)],input=data,text=True,capture_output=True,env=env,timeout=90,cwd=ROOT)
                    except subprocess.TimeoutExpired as error:
                        stdout = error.stdout or b''; stderr = error.stderr or b''
                        stem.with_suffix('.stdout').write_bytes(stdout if isinstance(stdout,bytes) else stdout.encode())
                        stem.with_suffix('.stderr').write_bytes(stderr if isinstance(stderr,bytes) else stderr.encode())
                        stem.with_suffix('.in').write_text(data); stem.with_suffix('.expected').write_text(want)
                        case.update(passed=False,timeout=True,seconds=time.monotonic()-started,
                                    failure_artifact_prefix=str(stem.relative_to(ROOT)),
                                    stdout_sha256=file_sha(stem.with_suffix('.stdout')),stderr_sha256=file_sha(stem.with_suffix('.stderr')))
                        raise
                    stem.with_suffix('.stdout').write_text(result.stdout)
                    stem.with_suffix('.stderr').write_text(result.stderr)
                    ok = result.returncode == 0 and result.stdout == want and not result.stderr
                    case.update(returncode=result.returncode,passed=ok,seconds=time.monotonic()-started,
                                stdout_file=str(stem.with_suffix('.stdout').relative_to(ROOT)),
                                stderr_file=str(stem.with_suffix('.stderr').relative_to(ROOT)),
                                stdout_sha256=sha(result.stdout.encode()),stderr_sha256=sha(result.stderr.encode()))
                    if not ok:
                        stem.with_suffix('.in').write_text(data); stem.with_suffix('.expected').write_text(want)
                        case['failure_artifact_prefix'] = str(stem.relative_to(ROOT))
                        raise AssertionError(f'{mode} {form} case {name} failed')
                    stdout_hash.update((json.dumps(result.stdout)+'\n').encode())
                    execution['completed_cases'] += 1
                execution.update(stdout_sha256=stdout_hash.hexdigest(),
                                 executable_after_sha256=file_sha(binary),source_after_sha256=file_sha(source))
                assert execution['executable_after_sha256'] == execution['executable_sha256']
                assert execution['source_after_sha256'] == execution['source_sha256']
                print(mode,form,len(checks),'PASS',flush=True)
                report_path.write_text(json.dumps(report,indent=2)+'\n')
            assert len({e['stdout_sha256'] for e in report['executions']}) == 1
            assert file_sha(fixture) == fixture_hash
            report['cases_after_sha256'] = file_sha(fixture)
            report['after'] = snapshot(compiler)
            assert report['after'] == before, 'Sources, selected registration or compiler changed during run'
            report['passed'] = True
        except BaseException as error:
            report['error'] = repr(error)
            raise
        finally:
            try:
                report['after'] = snapshot(compiler)
                report['source_unchanged'] = before is not None and report['after'] == before
                if not report['source_unchanged']: report['passed'] = False
            except BaseException as error:
                report.update(after_error=repr(error),source_unchanged=False,passed=False)
            report_path.write_text(json.dumps(report,indent=2)+'\n')
            print('Report:', report_path.relative_to(ROOT), flush=True)

if __name__ == '__main__':
    main()
