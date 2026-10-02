#!/usr/bin/env python3
"""CSES 1724 registered application checks; no online AC or judge-timing claim."""
import argparse
import collections
import datetime
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'src/compact/optimization.hpp').is_file())
SEED = 1724
LIMIT = 10**9


def sha(data):
    return hashlib.sha256(data).hexdigest()


def walk(n, edges, k):
    """Literal edge-by-edge enumeration; parallel edges remain distinct."""
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    answer = None
    def visit(u, left, cost):
        nonlocal answer
        if not left:
            if u == n - 1:
                answer = cost if answer is None else min(answer, cost)
        else:
            for v, w in adj[u]:
                visit(v, left - 1, cost + w)
    visit(0, k, 0)
    return -1 if answer is None else answer


def matrix(n, edges, k):
    """Independent Python arbitrary-precision min-plus with None, not a finite sentinel."""
    a = [[None] * n for _ in range(n)]
    for u, v, w in edges:
        a[u][v] = w if a[u][v] is None else min(a[u][v], w)
    r = [[0 if i == j else None for j in range(n)] for i in range(n)]
    def mul(a, b):
        c = [[None] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                values = [a[i][z] + b[z][j] for z in range(n)
                          if a[i][z] is not None and b[z][j] is not None]
                if values:
                    c[i][j] = min(values)
        return c
    while k:
        if k & 1:
            r = mul(r, a)
        k //= 2
        if k:
            a = mul(a, a)
    return -1 if r[0][-1] is None else r[0][-1]


def violations(n, edges, k):
    bad = []
    if not 1 <= n <= 100: bad.append('n')
    if not 1 <= len(edges) <= n * (n - 1): bad.append('m')
    if not 1 <= k <= LIMIT: bad.append('k')
    if any(not (0 <= u < n and 0 <= v < n and 1 <= w <= LIMIT) for u, v, w in edges): bad.append('edges')
    return bad


def case(label, n, edges, k, answer=None, oracle='python-int-min-plus'):
    assert n >= 1 and k >= 0
    assert all(0 <= u < n and 0 <= v < n and 1 <= w <= LIMIT for u, v, w in edges)
    if answer is None:
        answer = matrix(n, edges, k)
    data = (f'{n} {len(edges)} {k}\n' + ''.join(f'{u+1} {v+1} {w}\n' for u, v, w in edges)).encode()
    return dict(label=label, n=n, m=len(edges), k=k, data=data, expected=f'{answer}\n'.encode(),
                oracle=oracle, violations=violations(n, edges, k))


def cases():
    # Keep historical 603 cases reproducible, but classify each from actual bounds.
    yield case('official-sample', 3, [(0,1,5),(1,2,4),(2,0,1),(2,1,2)], 8, 27, 'official sample')
    for index, weights in enumerate(itertools.product((None, 1, 3), repeat=4)):
        edges = [(u,v,weights[2*u+v]) for u in range(2) for v in range(2) if weights[2*u+v] is not None]
        for k in range(6):
            answer = walk(2, edges, k)
            assert matrix(2, edges, k) == answer
            yield case(f'tiny-{index}-{k}', 2, edges, k, answer, 'literal walks cross-check Python matrix')
    rng = random.Random(SEED)
    for index in range(80):
        n = rng.randrange(2,5)
        edges = [(rng.randrange(n),rng.randrange(n),rng.choice((1,2,7,LIMIT))) for _ in range(rng.randrange(1,7))]
        k = rng.randrange(6)
        answer = walk(n, edges, k)
        assert matrix(n, edges, k) == answer
        yield case(f'random-{index}', n, edges, k, answer, 'literal walks cross-check Python matrix')
    for k in (0,1,2,2**29-1,2**29,2**29+1,LIMIT-1,LIMIT):
        for index, edges in enumerate([[(0,1,LIMIT),(1,0,LIMIT)],[(0,0,LIMIT),(0,1,LIMIT)],[(0,1,9),(0,1,1)],[(0,1,1),(1,2,2),(2,0,3),(2,2,LIMIT)]]):
            n = 1 + max(max(u,v) for u,v,_ in edges)
            yield case(f'exponent-{index}-{k}', n, edges, k)
    yield case('maximum-finite', 2, [(0,0,LIMIT),(0,1,LIMIT)], LIMIT, LIMIT**2, 'all edges same cost; source loop then target')
    yield case('API-single-zero', 1, [], 0, 0, 'empty walk identity')
    yield case('API-single-loop', 1, [(0,0,7)], 5, 35, 'five loops')
    yield case('maximum-dense', 100, [(u,v,LIMIT) for u in range(100) for v in range(100) if u != v], LIMIT, LIMIT**2, 'complete graph on >=3 vertices has exact k>=2 walk; uniform cost')
    # Additional official-domain adversarial and maximum-size coverage.
    yield case('asymmetric-direction', 3, [(1,0,1),(1,2,1)], 2, -1, 'source has no outgoing edge')
    yield case('no-artificial-identity', 2, [(0,1,7)], 2, -1, 'only a one-edge walk exists')
    yield case('parallel-order', 3, [(0,1,9),(0,1,1),(0,1,8),(1,2,3)], 2, 4, 'minimum parallel edge then final edge')
    yield case('real-loop', 3, [(0,0,2),(0,1,3),(1,2,5)], 4, 12, 'two actual loops followed by unique route')
    yield case('maximum-disconnected', 100, [(u,v,1) for u in range(99) for v in range(99) if u != v], LIMIT, -1, 'target isolated')
    yield case('maximum-asymmetric', 100, [(u,v,1+v-u) for u in range(100) for v in range(u+1,100)], 99, 198, 'DAG unique 99-edge consecutive walk; telescoping cost')
    yield case('maximum-asymmetric-too-long', 100, [(u,v,1+v-u) for u in range(100) for v in range(u+1,100)], 100, -1, 'DAG walk has at most 99 edges')
    yield case('maximum-parallel', 100, [(0,99,LIMIT-i) for i in range(9900)], 1, LIMIT-9899, 'minimum of 9900 parallel costs')
    yield case('maximum-dense-nonuniform', 100, [(u,v,1+v) for u in range(100) for v in range(100) if u != v], LIMIT, (LIMIT-2)//2*3+2+100, 'destination costs; cheapest alternation vertices 0,1 then target; even k')


def main():
    if not __debug__:
        raise SystemExit('Assertions are required: do not use python -O or PYTHONOPTIMIZE')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sanitize', action='store_true')
    ap.add_argument('--report', type=Path)
    ap.add_argument('--driver', type=Path, default=ROOT / 'verify/cses/1724.compact.cpp')
    ap.add_argument('--fixtures', type=Path, default=ROOT / 'tests/fixtures/maxplus')
    ap.add_argument('--usage', default='example-223', choices=['example-223'], help='Required registered application with exact printed body')
    args = ap.parse_args()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / 'tests'))
    sys.path.insert(0, str(ROOT / 'tools'))
    from compiler_config import CXX
    from usage_examples import records
    san = args.sanitize or os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1'
    mode = 'sanitizer' if san else 'normal'
    build = ROOT / 'build/maxplus-next'
    build.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix=mode + '-minimal-', dir=build))
    path = args.report or out / 'report.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    driver = args.driver.resolve()
    core = ROOT / 'src/compact/optimization.hpp'
    source = driver.read_text()
    snippet = source[source.index('int main()'):]
    programs = {'direct': driver}
    tracked = [Path(__file__).resolve(), driver, core, ROOT/'tools/usage_examples.py', ROOT/'tests/compiler_config.py', ROOT/'docs/catalog.json']
    row = next(r for r in records() if r['id'] == args.usage)
    assert row['driver'] == str(driver.relative_to(ROOT)) and row['symbol'] == 'MaxPlusMatrix'
    assert row['kind'] == 'application' and row['requires'] == ['MaxPlusMatrix']
    assert row['snippet'] == snippet
    printed = ROOT / row['snippet_file']
    assert printed.read_bytes() == snippet.encode(), 'Published body must match driver exactly'
    tracked += [ROOT/'docs/usage-examples.json', printed]
    # The registered expanded form intentionally includes the whole header.
    # Runtime-test the printed body separately with only its declared component.
    programs['expanded'] = row['program']
    assert sha(row['program'].encode()) == row['program_sha256']
    matches = list(re.finditer(r'^struct MaxPlusMatrix\n\{.*?^\};', core.read_text(), re.M | re.S))
    assert len(matches) == 1, 'Expected exactly one anchored outer MaxPlusMatrix definition'
    component = matches[0].group()
    assert re.findall(r'\b(?:struct|class)\s+(\w+)', component) == ['MaxPlusMatrix'], 'Extra component in minimal context'
    assert '#include' not in component and 'int main' not in component
    context = '#include <bits/stdc++.h>\nusing namespace std;\n\n' + component + '\n\n'
    programs['printed'] = context + printed.read_text()
    assert programs['printed'].removeprefix(context) == snippet
    minimal_context = dict(component='MaxPlusMatrix', component_sha256=sha(component.encode()),
                           context_sha256=sha(context.encode()), snippet_sha256=sha(printed.read_bytes()),
                           program_sha256=sha(programs['printed'].encode()),
                           other_component_definitions=[],
                           scope='Only the anchored MaxPlusMatrix struct, standard headers and exact published snippet')
    registration = {k:v for k,v in row.items() if k not in ('program','snippet')}
    fixtures = [args.fixtures.resolve() / n for n in ('official-sample.in','official-sample.out','contract.json')]
    tracked += fixtures
    before = {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in tracked}
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    compiler_hash = sha(compiler.read_bytes())
    frontend_name = subprocess.check_output([CXX, '-print-prog-name=cc1plus'], text=True).strip()
    frontend = Path(shutil.which(frontend_name) or frontend_name).resolve()
    assert frontend.is_file(), 'Cannot bind compiler frontend: ' + frontend_name
    frontend_hash = sha(frontend.read_bytes())
    flags = ['-std=c++20','-O2'] if not san else ['-std=c++20','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    env = os.environ.copy()
    if san:
        options = [x for x in env.get('ASAN_OPTIONS','').split(':') if x]
        assert not any('quarantine' in x for x in options), 'Default ASan quarantine required'
        options = [x for x in options if not x.startswith(('detect_leaks=','halt_on_error='))]
        env['ASAN_OPTIONS'] = ':'.join(options+['detect_leaks=0','halt_on_error=1'])
        env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
    all_cases = list(cases())
    assert all_cases[0]['data'] == fixtures[0].read_bytes() and all_cases[0]['expected'] == fixtures[1].read_bytes()
    contract = json.loads(fixtures[2].read_text())
    assert contract['classification'] == 'application' and contract['sample_answer'] == 27
    assert contract['n'] == [1,100] and contract['m'] == '1..n*(n-1)'
    assert contract['k'] == [1,LIMIT] and contract['cost'] == [1,LIMIT]
    official = sum(not c['violations'] for c in all_cases)
    assert len(all_cases) == 612 and official == 256
    assert dict(collections.Counter(','.join(c['violations']) for c in all_cases if c['violations'])) == {'m':257,'k':45,'m,k':54}
    for c in all_cases:
        c['domain'] = 'api-extension' if c['violations'] else 'official'
    report = dict(status='running', mode=mode, seed=SEED, sources=before,
                  build_directory=str(out.relative_to(ROOT)), minimal_context=minimal_context,
                  compiler=str(compiler), compiler_sha256=compiler_hash,
                  frontend=str(frontend), frontend_sha256=frontend_hash,
                  compiler_version=subprocess.check_output([CXX,'--version'],text=True), flags=flags,
                  environment={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')},
                  registration=registration, cases_per_form=len(all_cases), official_cases_per_form=official,
                  api_extension_cases_per_form=len(all_cases)-official,
                  api_violation_counts=dict(collections.Counter(','.join(c['violations']) for c in all_cases if c['violations'])),
                  scope='Local direct, registered expanded, and exact printed body in MaxPlusMatrix-only context runtime correctness. No online AC, official 1-second judge timing, full-toolchain, formal-template or leak-detection claim.',
                  started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), forms={})
    def save():
        path.write_text(json.dumps(report,indent=2)+'\n')
    save()
    try:
        for form, text in programs.items():
            cpp = text if isinstance(text,Path) else out/(form+'.cpp')
            if not isinstance(text,Path): cpp.write_text(text)
            exe = out/form
            command = [CXX,*flags,str(cpp),'-o',str(exe)]
            subprocess.run(command,check=True)
            info = dict(command=command, source_sha256=sha(cpp.read_bytes()), binary_sha256=sha(exe.read_bytes()),cases=[])
            report['forms'][form] = info
            for c in all_cases:
                report['active'] = [form,c['label']]
                save()
                started = time.monotonic()
                p = subprocess.run([str(exe)],input=c['data'],capture_output=True,env=env,timeout=60)
                item = {k:v for k,v in c.items() if k not in ('data','expected')}
                item.update(input_sha256=sha(c['data']),expected_sha256=sha(c['expected']),actual_sha256=sha(p.stdout),returncode=p.returncode,stderr=p.stderr.decode(errors='replace'),wall_seconds=time.monotonic()-started)
                info['cases'].append(item)
                assert p.returncode == 0 and not p.stderr and p.stdout == c['expected'], (form,c['label'],p.stdout,c['expected'],p.stderr)
        assert before == {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in tracked}, 'Bound sources changed during run'
        assert compiler_hash == sha(compiler.read_bytes()), 'Compiler changed during run'
        assert frontend_hash == sha(frontend.read_bytes()), 'Compiler frontend changed during run'
        current = next(r for r in records() if r['id'] == args.usage)
        assert {k:v for k,v in current.items() if k not in ('program','snippet')} == registration
        assert current['snippet'] == printed.read_text() == snippet
        report['sources_after'] = {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in tracked}
        report['compiler_after_sha256'] = sha(compiler.read_bytes())
        report['frontend_after_sha256'] = sha(frontend.read_bytes())
        report['status'] = 'passed'
        report.pop('active',None)
    except BaseException:
        report['status'] = 'failed'
        report['error'] = traceback.format_exc()
        raise
    finally:
        report['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save()
    print(f'MaxPlusMatrix {mode}: {official} official + {len(all_cases)-official} API extension cases per {list(programs)} PASS; {path}')


if __name__ == '__main__':
    main()
