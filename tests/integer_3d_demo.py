#!/usr/bin/env python3
"""Independent custom integer-3D API checks: direct, expanded, printed, and core."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import itertools
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'tests/fixtures/integer-3d-demo'
DRIVER = ROOT / 'docs/usage-drivers/integer-3d-demo.cpp'
CORE_TEST = ROOT / 'tests/integer_3d_demo_core.cpp'
HEADER = ROOT / 'src/compact/geometry_extra.hpp'
EXAMPLE = 'example-225'
PRINTED = ROOT / f'docs/usage/{EXAMPLE}.cpp'

B = 10**9
PERMUTATIONS = [(p, (-1)**sum(p[i]>p[j] for i in range(4) for j in range(i+1,4)))
                for p in itertools.permutations(range(4))]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def oracle(points, primitive=False):
    a,b,c,d = points
    u = tuple(b[i]-a[i] for i in range(3))
    v = tuple(d[i]-c[i] for i in range(3))
    if primitive:
        cross = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        # Polarization identity is independent of the implementation's dot sum.
        dot = (sum((x+y)**2 for x,y in zip(u,v))-sum(x*x for x in u)-sum(y*y for y in v))//2
        return (*u,*v,*cross,dot)
    # Homogeneous 4x4 Leibniz determinant, not a cross-dot reproduction.
    matrix = [(1,*p) for p in points]
    orientation = 0
    for perm,sign in PERMUTATIONS:
        term=sign
        for i in range(4): term*=matrix[i][perm[i]]
        orientation+=term
    def collinear(x,y,z):
        v=[y[i]-x[i] for i in range(3)]
        w=[z[i]-x[i] for i in range(3)]
        return all(v[i]*w[j]==v[j]*w[i] for i in range(3) for j in range(i+1,3))
    segment = collinear(a,b,d) and all(min(a[i],b[i])<=d[i]<=max(a[i],b[i]) for i in range(3))
    return orientation,int(collinear(a,b,c)),int(segment)


def case(name, queries):
    assert 0<=len(queries)<=200000
    assert all(len(q)==4 and all(len(p)==3 and all(-B<=v<=B for v in p) for p in q) for q in queries)
    data=str(len(queries))+'\n'+''.join(' '.join(str(v) for p in q for v in p)+'\n' for q in queries)
    unique=set(queries)
    answers={q:' '.join(map(str,oracle(q)))+'\n' for q in unique}
    primitives={q:' '.join(map(str,oracle(q,True)))+'\n' for q in unique}
    return dict(name=name,input=data,expected=''.join(answers[q] for q in queries),
                primitive_expected=''.join(primitives[q] for q in queries),queries=len(queries))


def cases():
    values=list(map(int,(HERE/'sample.in').read_text().split()))
    q=values[0]; assert len(values)==1+12*q
    sample=[tuple(tuple(values[1+12*k+3*j:1+12*k+3*j+3]) for j in range(4)) for k in range(q)]
    c=case('custom-sample',sample)
    assert c['expected']==(HERE/'sample.out').read_text()
    yield c
    yield case('zero-queries',[])
    for coordinates,name in [((0,1),'unit'),((-B,B),'extreme')]:
        cube=list(itertools.product(coordinates,repeat=3))
        yield case('exhaustive-'+name+'-cube',list(itertools.product(cube,repeat=4)))
    special=[]
    for a,b in [((0,0,0),(0,0,0)),((-B,-B,-B),(B,B,B)),((0,0,0),(2,4,6))]:
        for d in [a,b,(0,0,0),(1,2,3),(3,6,9),(-1,-2,-3)]:
            for c in [a,b,d,(0,1,0)]: special.append((a,b,c,d))
    # Unimodular large rows: subtract first row from the other two to see det=1.
    near=((0,0,0),(B,B-1,B-2),(B-1,B-2,B-3),(B-1,B-2,B-2))
    assert oracle(near)[0]==-1
    special.extend(itertools.permutations(near))
    for scale,shift in [(2,(13,-17,19)),(-3,(-12,14,8))]:
        base=((0,0,0),(1,2,3),(3,1,2),(2,3,1))
        special.extend(itertools.permutations(tuple(tuple(scale*p[i]+shift[i] for i in range(3)) for p in base)))
    yield case('degenerate-endpoint-near-singular-permutations',special)
    rng=random.Random(20261002)
    randoms=[tuple(tuple(rng.randint(-B,B) for _ in range(3)) for _ in range(4)) for _ in range(6000)]
    for i in range(300):
        a,b,c,d=randoms[i]; randoms.extend([(a,a,c,d),(a,b,a,d),(a,b,c,a),(a,b,c,b)])
    yield case('seeded-random-and-duplicates',randoms)
    pool=sample+special
    yield case('maximum-q-repeated-exact-pool',[pool[i%len(pool)] for i in range(200000)])


def local_headers(path, seen=None):
    seen = set() if seen is None else seen
    path = path.resolve()
    assert path.is_relative_to(ROOT), path
    if path in seen:
        return seen
    seen.add(path)
    for inc in re.findall(r'^\s*#include "([^"\n]+)"\s*$', path.read_text(), re.M):
        local_headers(path.parent / inc, seen)
    return seen


def selected_metadata():
    registration = [r for r in json.loads((ROOT/'docs/usage-examples.json').read_text()) if r['id'] == EXAMPLE]
    catalog = [r for r in json.loads((ROOT/'docs/catalog.json').read_text()) if r[1] == 'IntegerGeometry3D']
    assert len(registration) == len(catalog) == 1
    return dict(registration=registration[0], catalog=catalog[0])


def snapshot(compiler):
    files = local_headers(DRIVER) | local_headers(CORE_TEST)
    files.update((Path(__file__).resolve(), PRINTED, ROOT/'tests/compiler_config.py', ROOT/'tools/usage_examples.py'))
    files.update(p for p in HERE.iterdir() if p.is_file())
    # GCC launches cc1plus separately; hash the frontend as well as the driver.
    frontend_name = subprocess.check_output([str(compiler),'-print-prog-name=cc1plus'],text=True).strip()
    frontend = Path(shutil.which(frontend_name) or frontend_name).resolve()
    assert frontend.is_file(), f'Cannot resolve compiler frontend: {frontend_name}'
    metadata = selected_metadata()
    return dict(source_sha256={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(files)},
                selected_metadata=metadata, selected_metadata_sha256=sha(json.dumps(metadata,sort_keys=True).encode()),
                compiler_executable=str(compiler),compiler_sha256=sha(compiler.read_bytes()),
                frontend_executable=str(frontend),frontend_sha256=sha(frontend.read_bytes()))


def programs():
    sys.path.insert(0,str(ROOT/'tools'))
    from usage_examples import records
    matches = [r for r in records() if r['id'] == EXAMPLE]
    assert len(matches) == 1
    row = matches[0]
    assert row['kind'] == 'api' and row['symbol'] == 'IntegerGeometry3D'
    assert row['driver'] == str(DRIVER.relative_to(ROOT)) and row['requires'] == ['IntegerGeometry3D']
    assert not row.get('also_covers')
    driver = DRIVER.read_text()
    start = re.search(r'(?m)^int main\(\)',driver)
    assert start and driver[start.start():] == row['snippet']
    printed = PRINTED.read_text()
    assert printed == row['snippet'], 'Generated printed snippet is stale'
    assert sha(row['program'].encode()) == row['program_sha256']
    # This standalone component is the declared context of the actual printed main.
    header = HEADER.read_text()
    match = re.search(r'^struct IntegerGeometry3D\n\{.*?^\};',header,re.M|re.S)
    assert match
    context = match[0]+'\n'
    pasted = '#include <bits/stdc++.h>\nusing namespace std;\n'+context+printed
    printer = re.search(r'    auto print = \[\]\(__int128_t x\)\n    \{.*?^    \};',driver,re.M|re.S)
    assert printer
    printer_program = '#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n'+printer[0]+r'''
    __int128_t hi = __int128_t((__uint128_t(1)<<127)-1);
    for (__int128_t x : {__int128_t(0), __int128_t(1), __int128_t(-1), hi, -hi-1,
                        __int128_t(8000000000000000000LL)*1000000000,
                        -__int128_t(8000000000000000000LL)*1000000000}) { print(x); cout << '\n'; }
}
'''
    return dict(printer_only=printer_program,complete_driver=driver,registered_program=row['program'],printed_copy=pasted,
                separate_core=CORE_TEST.read_text()), dict(
                    program_sha256=row['program_sha256'], printed_snippet_sha256=sha(printed.encode()),
                    printed_context=dict(symbol='IntegerGeometry3D',path=str(HEADER.relative_to(ROOT)),
                                         source_sha256=sha(header.encode()),context_sha256=sha(context.encode())))


def main():
    if not __debug__:
        raise SystemExit('Run without python -O: validation assertions must remain enabled')
    sys.path.insert(0,str(ROOT/'tests'))
    from compiler_config import CXX
    ap = argparse.ArgumentParser(description=__doc__)
    default = 'sanitizer' if any(os.getenv(k)=='1' for k in ('SANITIZE','CPC_SANITIZE')) else 'normal'
    ap.add_argument('--mode',choices=('normal','sanitizer','both'),default=default)
    ap.add_argument('--report',type=Path,help='JSON report path under build/ or verification/')
    args = ap.parse_args()
    report_path = args.report.resolve() if args.report else None
    if report_path and not any(report_path.is_relative_to(ROOT/p) for p in ('build','verification')):
        ap.error('--report must remain under repository build/ or verification/')
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    assert compiler.is_file(), 'No compiler found'
    build = ROOT/'build'
    build.mkdir(exist_ok=True)
    build = build/'integer-3d-next'
    build.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='run-',dir=build))
    if report_path is None: report_path = work/'report.json'
    report_path.parent.mkdir(parents=True,exist_ok=True)
    before = None
    report = dict(passed=False,mode=args.mode,id=EXAMPLE,kind='api',component='IntegerGeometry3D',
                  scope='Custom API protocol; finite local checks, no official problem, online AC or full-suite claim',
                  created=datetime.now(timezone.utc).isoformat(), modes=[], executions=[],
                  compiler_version=subprocess.check_output([str(compiler),'--version'],text=True),
                  pie='compiler default',quarantine='ASan default',
                  oracle='Python arbitrary-precision 4x4 permutation determinant, pairwise minors, coordinate-box segment; primitive polarization dot and minors; cached exact maximum-Q pool')
    def save():
        report_path.write_text(json.dumps(report,indent=2)+'\n')
    print('Artifacts:',work,flush=True)
    try:
        before = snapshot(compiler)
        report['before'] = before
        sources, provenance = programs()
        report.update(provenance)
        checks = list(cases())
        contract = json.loads((HERE/'contract.json').read_text())
        assert contract['kind']=='api' and contract['symbol']=='IntegerGeometry3D'
        assert contract['domain']==dict(q=[0,200000],coordinate=[-B,B],degeneracies='all permitted')
        assert contract['custom_sample']==dict(input=(HERE/'sample.in').read_text(),output=(HERE/'sample.out').read_text())
        fixtures = work/'cases.jsonl'
        fixtures.write_text(''.join(json.dumps(c,sort_keys=True)+'\n' for c in checks))
        report.update(cases_file=str(fixtures.relative_to(ROOT)),cases_sha256=sha(fixtures.read_bytes()),
                      case_count_per_form=len(checks),queries_per_form=sum(c['queries'] for c in checks),
                      maximum_q=max(c['queries'] for c in checks),domain=contract['domain'])
        modes = ('normal','sanitizer') if args.mode == 'both' else (args.mode,)
        for mode in modes:
            report['modes'].append(mode)
            flags = ['-std=c++20','-Wall','-Wextra'] + (['-O2'] if mode=='normal' else
                     ['-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer'])
            env = os.environ.copy()
            for key in ('ASAN_OPTIONS','LSAN_OPTIONS','UBSAN_OPTIONS'): env.pop(key,None)
            if mode=='sanitizer': env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
            for form, program in sources.items():
                source = DRIVER if form=='complete_driver' else CORE_TEST if form=='separate_core' else work/f'{mode}-{form}.cpp'
                if form not in ('complete_driver','separate_core'): source.write_text(program)
                exe = work/f'{mode}-{form}'
                command = [str(compiler),*flags,str(source),'-o',str(exe)]
                entry = dict(mode=mode,form=form,compile_command=command,completed_cases=0,cases=[],
                             source=str(source.relative_to(ROOT)),source_sha256=sha(source.read_bytes()),
                             sanitizer_options={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS','LSAN_OPTIONS')})
                report['executions'].append(entry); save()
                cp = subprocess.run(command,capture_output=True,text=True,timeout=120,env=env,cwd=ROOT)
                entry['compile'] = dict(returncode=cp.returncode,stdout=cp.stdout,stderr=cp.stderr)
                assert cp.returncode == 0, cp.stderr
                entry['binary_sha256'] = sha(exe.read_bytes())
                selected = checks if form!='separate_core' else [dict(c,expected=c['primitive_expected']) for c in checks]
                if form=='printer_only':
                    values=[0,1,-1,2**127-1,-2**127,8*10**27,-8*10**27]
                    selected=[dict(name='printer-only-int128-boundaries',input='',expected=''.join(str(v)+'\n' for v in values))]
                output_hash = hashlib.sha256()
                for i,c in enumerate(selected):
                    stem = work/f'{mode}-{form}-{i:03}'
                    try:
                        result = subprocess.run([str(exe)],input=c['input'],text=True,capture_output=True,timeout=180,env=env,cwd=ROOT)
                    except subprocess.TimeoutExpired as error:
                        for suffix, value in [('.stdout',error.stdout or b''),('.stderr',error.stderr or b'')]:
                            stem.with_suffix(suffix).write_bytes(value if isinstance(value,bytes) else value.encode())
                        stem.with_suffix('.in').write_text(c['input'])
                        stem.with_suffix('.expected').write_text(c['expected'])
                        entry['cases'].append(dict(name=c['name'],passed=False,timeout=True,artifact_prefix=str(stem.relative_to(ROOT))))
                        raise
                    stem.with_suffix('.stdout').write_text(result.stdout)
                    stem.with_suffix('.stderr').write_text(result.stderr)
                    ok = result.returncode==0 and result.stdout==c['expected'] and not result.stderr
                    entry['cases'].append(dict(name=c['name'],passed=ok,returncode=result.returncode,
                                               input_sha256=sha(c['input'].encode()),expected_sha256=sha(c['expected'].encode()),
                                               stdout_file=str(stem.with_suffix('.stdout').relative_to(ROOT)),stderr_file=str(stem.with_suffix('.stderr').relative_to(ROOT)),
                                               stdout_sha256=sha(result.stdout.encode()),stderr_sha256=sha(result.stderr.encode())))
                    if not ok:
                        stem.with_suffix('.in').write_text(c['input']); stem.with_suffix('.expected').write_text(c['expected'])
                        raise AssertionError(f'{mode} {form} {c["name"]}: {result.stderr[:1000]}')
                    output_hash.update((json.dumps(result.stdout)+'\n').encode())
                    entry['completed_cases'] += 1
                entry['stdout_sha256'] = output_hash.hexdigest()
                assert sha(exe.read_bytes()) == entry['binary_sha256']
                assert sha(source.read_bytes()) == entry['source_sha256']
                print(mode,form,entry['completed_cases'],'PASS',flush=True); save()
            assert len({e['stdout_sha256'] for e in report['executions'] if e['mode']==mode and e['form'] not in ('separate_core','printer_only')}) == 1
        assert sha(fixtures.read_bytes()) == report['cases_sha256']
        assert snapshot(compiler) == before, 'Inputs, selected metadata, or compiler changed during run'
        report['passed'] = True
    except BaseException as e:
        report['error'] = repr(e)
        raise
    finally:
        try:
            report['after'] = snapshot(compiler)
            report['source_unchanged'] = before is not None and report['after'] == before
        except BaseException as e:
            report.update(after_error=repr(e),source_unchanged=False)
        if not report['source_unchanged']: report['passed'] = False
        save()
        print('Report:',report_path,flush=True)


if __name__ == '__main__':
    main()
