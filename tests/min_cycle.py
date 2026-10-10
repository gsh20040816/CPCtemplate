import hashlib
import json
import os
import random
import subprocess
import sys
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import records
from audit_copy_context import candidate, extract_components

san = '--sanitize' in sys.argv
mode = 'sanitizer' if san else 'normal'
work = root / 'build/min-cycle' / mode
work.mkdir(parents=True, exist_ok=True)
flags = ['-std=c++20', '-O1' if san else '-O2']
if san:
    flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
rows = [r for r in records() if r['id'] in ['example-374', 'example-375']]
components = {r['symbol']: r for r in extract_components(json.loads((root / 'docs/catalog.json').read_text()))}
commands = []

def compile(src, exe, extra=()):
    cmd = [CXX, *flags, *extra, str(src), '-o', str(exe)]
    commands.append(cmd)
    subprocess.run(cmd, check=True, capture_output=True, text=True)

def run(exe, data=''):
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env=env, timeout=90)
    assert p.returncode == 0, p.stderr
    return p.stdout

prefix = candidate(rows[0], ['MinCycle'], components)['program'].split('int main()')[0]
core_source = (root / 'tests/min_cycle.cpp').read_text().replace('#include "../src/compact/min_cycle.hpp"', prefix)
core = {}
for form in ['header', 'ndebug', 'copied']:
    src = root / 'tests/min_cycle.cpp'
    exe = work / ('core-' + form)
    if form == 'copied':
        src = exe.with_suffix('.cpp')
        src.write_text(core_source)
    compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
    core[form] = run(exe).strip()
    print(mode, form, core[form], flush=True)

def brute(n, edges):
    w = [[None] * n for _ in range(n)]
    for u, v, c in edges:
        if u != v and (w[u][v] is None or c < w[u][v]):
            w[u][v] = w[v][u] = c
    best = None
    def dfs(s, u, mask, length, cost):
        nonlocal best
        if length >= 3 and w[u][s] is not None:
            value = cost + w[u][s]
            best = value if best is None else min(best, value)
        for v in range(s + 1, n):
            if not mask >> v & 1 and w[u][v] is not None:
                dfs(s, v, mask | (1 << v), length + 1, cost + w[u][v])
    for s in range(n):
        dfs(s, s, 1 << s, 1, 0)
    return best

rng = random.Random(6175)
graphs = []
for trial in range(150):
    n = rng.randrange(1, 9)
    edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(1, 100)) for _ in range(rng.randrange(1, 30))]
    graphs.append((n, edges, brute(n, edges)))
n = 100
ring = [(i, (i + 1) % n, 100000) for i in range(n)] + [(0, 1, 100000)] * 4900
dense = [(u, v, 100000) for u in range(n) for v in range(u + 1, n)] + [(0, 0, 1)] * 50
graphs += [(n, ring, 10000000), (n, dense, 300000), (2, [(0, 0, 1), (0, 1, 2), (0, 1, 3)], None)]
cases = {'example-374': [], 'example-375': []}
for n, edges, want in graphs:
    data = [f'{n} {len(edges)}', *[f'{u+1} {v+1} {w}' for u, v, w in edges]]
    cases['example-374'].append(('\n'.join(data) + '\n', n, edges, want))
api_graphs = [(0, [], None)]
for trial in range(100):
    n = rng.randrange(1, 9)
    edges = [(rng.randrange(n), rng.randrange(n), rng.choice([0, 1, 17, 2**63-1])) for _ in range(rng.randrange(30))]
    api_graphs.append((n, edges, brute(n, edges)))
api_graphs += [(100, [(i, (i+1)%100, 2**63-1) for i in range(100)], 100*(2**63-1))]
for n, edges, want in api_graphs:
    data = [f'{n} {len(edges)}', *[f'{u} {v} {w}' for u, v, w in edges]]
    cases['example-375'].append(('\n'.join(data) + '\n', n, edges, want))

def validate(row, output, n, edges, want):
    if row['id'] == 'example-374':
        assert output.strip() == ('No solution.' if want is None else str(want)), (output, want)
        return
    if want is None:
        assert output.strip() == 'NONE'
        return
    a = list(map(int, output.split()))
    assert len(a) >= 2 and a[0] == want
    k = a[1]
    assert 3 <= k <= n and len(a) == 2 + 2*k
    vs, ids = a[2:2+k], a[2+k:]
    assert len(set(vs)) == k and all(0 <= u < n for u in vs)
    total = 0
    for i, eid in enumerate(ids):
        assert 0 <= eid < len(edges)
        u, v, w = edges[eid]
        assert {u, v} == {vs[i], vs[(i+1)%k]}
        total += w
    assert total == want

usage = {}
for row in rows:
    forms = {}
    for form in ['header', 'ndebug', 'expanded', 'copied']:
        src = root / row['driver']
        exe = work / (row['id'] + '-' + form)
        if form in ['expanded', 'copied']:
            src = exe.with_suffix('.cpp')
            src.write_text(row['program'] if form == 'expanded' else candidate(row, ['MinCycle'], components)['program'])
        compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
        for data, n, edges, want in cases[row['id']]:
            validate(row, run(exe, data), n, edges, want)
        forms[form] = len(cases[row['id']])
        print(mode, row['id'], form, 'PASS', flush=True)
    usage[row['id']] = dict(program_sha256=row['program_sha256'], forms=forms)
mutants = {}
if not san:
    for name, old, new in [('two-vertex-cycle', 'int j = i + 1; j < k', 'int j = i; j < k'), ('parallel-max', 'w < e[id[u][v]].w', 'w > e[id[u][v]].w'), ('weight-truncation', 'I w = d[i][j] + e[id[i][k]].w + e[id[j][k]].w;', 'I w = (long long)(d[i][j] + e[id[i][k]].w + e[id[j][k]].w);')]:
        assert old in core_source
        src = work / ('mutant-' + name + '.cpp')
        exe = src.with_suffix('')
        src.write_text(core_source.replace(old, new))
        compile(src, exe)
        p = subprocess.run([str(exe)], capture_output=True, timeout=90)
        assert p.returncode != 0, name
        mutants[name] = 'detected'
files = ['src/compact/min_cycle.hpp', 'tests/min_cycle.cpp', 'tests/min_cycle.py'] + [r['driver'] for r in rows]
report = dict(status='pass', mode=mode, compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0], commands=commands, core=core, usage=usage, mutants=mutants, source_sha256={p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in files}, scope='Definition-only simple cycle enumeration, original edge and vertex witness checks, full64 weights, largest P6175 graph sizes; online and ranking tracked separately.')
(root / f'verification/min-cycle-{mode}.json').write_text(json.dumps(report, indent=2) + '\n')
