#!/usr/bin/env python3
"""Custom SupportHull API protocol checks; no official-task or online-AC claim."""
import argparse
import datetime
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'src/compact/support_hull.hpp').is_file())
BOUND = 10**18
SEED = 226


def sha(data):
    return hashlib.sha256(data).hexdigest()


def chain(points):
    # Lowest y per x is selected BEFORE the monotone scan, independently of core.
    lowest = {}
    for x, y in points:
        lowest[x] = min(lowest.get(x, y), y)
    result = []
    for p in sorted(lowest.items()):
        while len(result) > 1:
            a, b = result[-2:]
            turn = (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
            if turn > 0:
                break
            result.pop()
        result.append(p)
    return result


def case(label, points, queries):
    assert 0 <= len(points) <= 2000 and 0 <= len(queries) <= 200000
    assert all(abs(x) <= BOUND and abs(y) <= BOUND for x, y in points)
    assert all(abs(a) <= BOUND and -BOUND <= b <= 0 for a, b in queries)
    hull = chain(points)
    lines = [str(len(hull))] + [f'{x} {y}' for x, y in hull]
    cache = {}
    for a, b in queries:
        if not points:
            lines.append('EMPTY')
            continue
        if (a, b) not in cache:
            # Full ORIGINAL point set; Python integers, value and coordinate tie.
            value = max(a*x+b*y for x, y in points)
            x, y = min((x,y) for x,y in points if a*x+b*y == value)
            cache[a,b] = f'{value} {x} {y}'
        lines.append(cache[a,b])
    data = f'{len(points)} {len(queries)}\n'+''.join(f'{x} {y}\n' for x,y in points+queries)
    return dict(label=label,n=len(points),q=len(queries),data=data.encode(),expected=('\n'.join(lines)+'\n').encode(),unique_brute_queries=len(cache))


def cases():
    qs = list(itertools.product(range(-3,4),range(-3,1)))
    yield case('custom-sample',[(0,0),(1,-2),(2,-2),(3,0),(1,4),(1,-2)],[(0,-1),(1,-1),(-1,-1),(1,0),(0,0)])
    yield case('empty',[],[(0,0),(1,-1),(-1,0)])
    yield case('no-points-no-queries',[],[])
    yield case('singleton',[(4,-5)],qs)
    yield case('same-x',[(7,9),(7,-9),(7,0),(7,-9)],qs)
    yield case('collinear',[(x,2*x-5) for x in range(-8,9)],qs+[(2,-1)])
    yield case('edge-plateau',[(0,0),(1,-2),(2,-2),(3,-2),(4,0),(0,7),(4,8)],qs)
    yield case('extremes',[(-BOUND,-BOUND),(-BOUND,BOUND),(BOUND,-BOUND),(BOUND,BOUND),(0,-BOUND),(0,0)],[(a,b) for a in (-BOUND,0,BOUND) for b in (-BOUND,0)])
    yield case('negative-extreme-value',[(BOUND,BOUND)],[(BOUND,-BOUND),(-BOUND,-BOUND),(0,-BOUND)])
    grid = list(itertools.product(range(-1,2),repeat=2))
    for mask in range(512):
        yield case(f'exhaustive-{mask}',[p for i,p in enumerate(grid) if mask>>i&1],qs)
    rng = random.Random(SEED)
    for i in range(180):
        points = [(rng.randrange(-20,21),rng.randrange(-20,21)) for _ in range(rng.randrange(101))]
        queries = [(rng.randrange(-BOUND,BOUND+1),rng.randrange(-BOUND,1)) for _ in range(20)]+qs
        yield case(f'random-{i}',points,queries)
    p = [(x,x*x) for x in range(-1000,1000)]
    directions = [(a,-1) for a in range(-2000,2001,40)]+[(0,0),(BOUND,0),(-BOUND,0),(BOUND,-BOUND)]
    yield case('maximum-n-q',p,[directions[i%len(directions)] for i in range(200000)])


def main():
    if not __debug__ or os.environ.get('PYTHONOPTIMIZE') not in (None,'','0'):
        raise SystemExit('Assertions required; do not use -O or PYTHONOPTIMIZE')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sanitize', action='store_true')
    ap.add_argument('--report',type=Path,help='Default: report.json inside the fresh build directory')
    ap.add_argument('--driver',type=Path,default=ROOT/'docs/usage-drivers/lower-support-demo.cpp')
    ap.add_argument('--fixtures',type=Path,default=HERE/'fixtures/support-hull-demo')
    ap.add_argument('--core-harness',type=Path,default=HERE/'support_hull_demo_core.cpp')
    ap.add_argument('--usage',default='example-226',choices=['example-226'],help='Required actual registered API example and exact generated snippet')
    args = ap.parse_args()
    args.driver = args.driver.resolve()
    args.fixtures = args.fixtures.resolve()
    args.core_harness = args.core_harness.resolve()
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(ROOT/'tools'),str(ROOT/'tests')]
    from compiler_config import CXX
    from usage_examples import records
    san = args.sanitize or os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1'
    mode = 'sanitizer' if san else 'normal'
    build_root = ROOT/'build/support-hull-next'
    build_root.mkdir(parents=True,exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix=mode+'-',dir=build_root))
    args.report = args.report or out/'report.json'
    args.report.parent.mkdir(parents=True,exist_ok=True)
    source = args.driver.resolve().read_text()
    snippet = source[source.index('int main()'):]
    programs = {'direct':args.driver.resolve()}
    tracked = [Path(__file__).resolve(),args.driver.resolve(),args.core_harness.resolve(),ROOT/'src/compact/support_hull.hpp',ROOT/'tools/usage_examples.py',ROOT/'tests/compiler_config.py']
    row = next(r for r in records() if r['id'] == args.usage)
    assert row['driver'] == str(args.driver.resolve().relative_to(ROOT))
    assert row['symbol'] == 'SupportHull' and row['requires'] == ['SupportHull'] and row['kind'] == 'api'
    assert row['snippet'] == snippet
    printed = ROOT/row['snippet_file']
    assert printed.read_text() == snippet
    programs['registered-expanded'] = row['program']
    # Copy only the exact component definition, not the rest of its header.
    core_text = (ROOT/'src/compact/support_hull.hpp').read_text()
    begin = core_text.index('struct SupportHull\n')
    opening = core_text.index('{',begin)
    depth = 1
    end = opening + 1
    while depth:
        depth += (core_text[end] == '{') - (core_text[end] == '}')
        end += 1
    assert core_text[end] == ';'
    component = core_text[begin:end+1]
    programs['actual-minimal-copied-context'] = '#include <bits/stdc++.h>\nusing namespace std;\n'+component+'\n'+printed.read_text()
    tracked += [ROOT/'docs/usage-examples.json',ROOT/'docs/catalog.json',printed]
    registration = {k:v for k,v in row.items() if k not in ('program','snippet')}
    fixtures = [args.fixtures/name for name in ('custom-sample.in','custom-sample.out','empty.in','empty.out','contract.json')]
    tracked += sorted(p for p in args.fixtures.rglob('*') if p.is_file())
    bound = {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in tracked}
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    frontend = Path(subprocess.check_output([str(compiler),'-print-prog-name=cc1plus'],text=True).strip()).resolve()
    binaries = {str(p):sha(p.read_bytes()) for p in (compiler,frontend)}
    flags = ['-std=c++20','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if san else ['-std=c++20','-O2']
    env = os.environ.copy()
    if san:
        options = [x for x in env.get('ASAN_OPTIONS','').split(':') if x]
        assert not any('quarantine' in x for x in options), 'Default ASan quarantine is required'
        options = [x for x in options if not x.startswith(('detect_leaks=','halt_on_error='))]
        env['ASAN_OPTIONS'] = ':'.join(options+['detect_leaks=0','halt_on_error=1'])
        env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
    all_cases = list(cases())
    for i in range(2):
        assert all_cases[i]['data'] == fixtures[2*i].read_bytes()
        assert all_cases[i]['expected'] == fixtures[2*i+1].read_bytes()
    assert json.loads(fixtures[-1].read_text())['classification'] == 'custom-api-demonstration'
    report = dict(status='running',mode=mode,seed=SEED,sources=bound,compiler_binaries=binaries,
        compiler_version=subprocess.check_output([str(compiler),'--version'],text=True),flags=flags,
        environment={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS','CXX','CPATH','CPLUS_INCLUDE_PATH','LIBRARY_PATH','LD_LIBRARY_PATH')},
        output_directory=str(out.relative_to(ROOT)),registration=registration,
        minimal_component_sha256=sha(component.encode()),actual_printed_snippet_sha256=sha(printed.read_bytes()),custom_cases_per_form=len(all_cases),
        official_cases=0,queries_per_form=sum(c['q'] for c in all_cases),
        scope='Local custom API protocol and separate core tie-policy tests only; no online AC, official domain, timing, full baseline, or leak-detection claim. Default compiler PIE and ASan quarantine unchanged.',
        started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),forms={})
    def save(): args.report.write_text(json.dumps(report,indent=2)+'\n')
    save()
    try:
        for form,text in {**programs,'separate-core-tie-policies':args.core_harness.resolve()}.items():
            cpp = text if isinstance(text,Path) else out/(form+'.cpp')
            if not isinstance(text,Path): cpp.write_text(text)
            exe = out/form
            command = [str(compiler),*flags,str(cpp),'-o',str(exe)]
            subprocess.run(command,check=True)
            info = dict(command=command,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),cases=[])
            report['forms'][form] = info
            if form == 'separate-core-tie-policies':
                result = subprocess.run([str(exe)],capture_output=True,env=env,timeout=180)
                info.update(returncode=result.returncode,stdout=result.stdout.decode(),stderr=result.stderr.decode())
                assert result.returncode == 0 and not result.stderr and b'PASS separate custom core tie-policy harness:' in result.stdout
                continue
            for c in all_cases:
                report['active'] = [form,c['label']]
                start = time.monotonic()
                p = subprocess.run([str(exe)],input=c['data'],capture_output=True,env=env,timeout=90)
                item = {k:v for k,v in c.items() if k not in ('data','expected')}
                item.update(input_sha256=sha(c['data']),expected_sha256=sha(c['expected']),actual_sha256=sha(p.stdout),returncode=p.returncode,stderr=p.stderr.decode(errors='replace'),wall_seconds=time.monotonic()-start)
                info['cases'].append(item)
                assert p.returncode == 0 and not p.stderr and p.stdout == c['expected'], (form,c['label'],p.stdout[:1000],c['expected'][:1000],p.stderr)
            save()
        report['sources_after'] = {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in tracked}
        report['compiler_binaries_after'] = {str(p):sha(p.read_bytes()) for p in (compiler,frontend)}
        assert bound == report['sources_after'], 'Bound inputs changed'
        assert binaries == report['compiler_binaries_after'], 'Compiler driver/frontend changed'
        report['status'] = 'passed'
        report.pop('active',None)
    except BaseException:
        report['status'] = 'failed'
        report['error'] = traceback.format_exc()
        raise
    finally:
        report['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save()
    print(f'SupportHull {mode}: {len(all_cases)} custom cases per {list(programs)} and separate core harness PASS; {args.report}')


if __name__ == '__main__':
    main()
