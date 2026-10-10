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
from audit_copy_context import candidate, extract_components, topological_closure
san = '--sanitize' in sys.argv
mode = 'sanitizer' if san else 'normal'
work = root / 'build/kruskal-tree' / mode
work.mkdir(parents=True, exist_ok=True)
flags = ['-std=c++20', '-O1' if san else '-O2']
if san:
    flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
rows = [r for r in records() if r['id'] in ['example-370', 'example-371']]
components = {r['symbol']:r for r in extract_components(json.loads((root / 'docs/catalog.json').read_text()))}
commands = []
def compile(src, exe, extra=[]):
    cmd = [CXX, *flags, *extra, str(src), '-o', str(exe)]
    commands.append(cmd)
    p = subprocess.run(cmd, text=True, capture_output=True)
    assert p.returncode == 0, p.stderr

def run(exe, data=''):
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env=env, timeout=90)
    assert p.returncode == 0, p.stderr
    return p.stdout

deps = json.loads((root / 'docs/template-dependencies.json').read_text())
prefix = candidate(rows[1], topological_closure(['KruskalTree'], deps), components)['program'].split('int main()')[0]
core_source = (root / 'tests/kruskal_tree.cpp').read_text().replace('#include "../src/compact/kruskal_tree.hpp"', prefix)
core = {}
for form in ['header', 'ndebug', 'copied']:
    src = root / 'tests/kruskal_tree.cpp'
    exe = work / ('core-' + form)
    if form == 'copied':
        src = exe.with_suffix('.cpp')
        src.write_text(core_source)
    compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
    core[form] = run(exe).strip()
    print(mode, form, core[form], flush=True)

rng = random.Random(4768)
cases = {r['id']:[] for r in rows}
# Floyd shortest paths plus explicit flood-fill after decoding each online query.
for trial in range(100):
    n = rng.randrange(1, 11)
    edges = [(i, rng.randrange(i), rng.randrange(1, 20), rng.randrange(1, 8)) for i in range(1, n)]
    edges += [(rng.randrange(n), rng.randrange(n), rng.randrange(1, 20), rng.randrange(1, 8)) for _ in range(rng.randrange(15))]
    dis = [[10**9] * n for _ in range(n)]
    for i in range(n):
        dis[i][i] = 0
    for u, v, l, a in edges:
        dis[u][v] = min(dis[u][v], l)
        dis[v][u] = min(dis[v][u], l)
    for k in range(n):
        for u in range(n):
            for v in range(n):
                dis[u][v] = min(dis[u][v], dis[u][k] + dis[k][v])
    k = trial % 2
    asks = [(rng.randrange(1, n + 1), rng.randrange(9)) for _ in range(50)]
    last = 0
    want = []
    for v0, p0 in asks:
        u = (v0 + k * last - 1) % n
        p = (p0 + k * last) % 9
        seen = {u}
        for _ in range(n):
            for a, b, l, w in edges:
                if w > p and (a in seen or b in seen):
                    seen.update([a, b])
        last = min(dis[x][0] for x in seen)
        want.append(last)
    data = ['1', f'{n} {len(edges)}']
    data += [f'{u+1} {v+1} {l} {a}' for u,v,l,a in edges]
    data += [f'50 {k} 8', *[f'{v} {p}' for v,p in asks]]
    cases['example-370'].append(('\n'.join(data) + '\n', want))
# One input exercises fresh state over three cases, including Q=0.
cases['example-370'].append(('3\n1 0\n0 1 1\n' + cases['example-370'][0][0][2:] + cases['example-370'][1][0][2:], cases['example-370'][0][1] + cases['example-370'][1][1]))
n = 200000
m = 400000
q = 400000
data = ['1', f'{n} {m}']
data += [f'{i} {i+1} 10000 {i}' for i in range(1, n)]
data += ['1 1 10000 1'] * (m - n + 1)
data += [f'{q} 1 1000000000']
last = 0
want = []
for i in range(q):
    v0 = i % n + 1
    p0 = i % n
    v = (v0 + last - 1) % n + 1
    p = (p0 + last) % 1000000001
    left = 1 if p == 0 else min(v, p + 1)
    last = (left - 1) * 10000
    data.append(f'{v0} {p0}')
    want.append(last)
cases['example-370'].append(('\n'.join(data) + '\n', want))
for trial in range(100):
    n = rng.randrange(1, 11)
    down = trial % 2
    weights = [-2**63, -5, -1, 0, 1, 5, 2**63-1]
    edges = [(rng.randrange(n), rng.randrange(n), rng.choice(weights)) for _ in range(rng.randrange(30))]
    def reachable(u, w=None, strict=False):
        seen = {u}
        for _ in range(n):
            for a,b,x in edges:
                ok = w is None or ((x >= w if down else x <= w) and (not strict or x != w))
                if ok and (a in seen or b in seen):
                    seen.update([a,b])
        return seen
    want = [len({tuple(sorted(reachable(u))) for u in range(n)})]
    asks = [(rng.randrange(n), rng.choice(weights), rng.randrange(2)) for _ in range(40)]
    for u,w,strict in asks:
        seen = reachable(u,w,strict)
        want += [len(seen),min(seen)]
    data = [f'{n} {len(edges)} 40 {down}', *[f'{u} {v} {w}' for u,v,w in edges], *[f'{u} {w} {s}' for u,w,s in asks]]
    cases['example-371'].append(('\n'.join(data)+'\n',want))
cases['example-371'].append(('0 0 0 0\n',[0]))
usage = {}
for row in rows:
    forms = {}
    for form in ['header', 'ndebug', 'expanded', 'copied']:
        src = root / row['driver']
        exe = work / (row['id'] + '-' + form)
        if form in ['expanded', 'copied']:
            src = exe.with_suffix('.cpp')
            src.write_text(row['program'] if form == 'expanded' else candidate(row,topological_closure(row['requires'],deps),components)['program'])
        compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
        for data,want in cases[row['id']]:
            got = list(map(int,run(exe,data).split()))
            assert got == want,(row['id'],form,data[:300],got[:30],want[:30])
        forms[form] = len(cases[row['id']])
        print(mode,row['id'],form,'PASS',flush=True)
    usage[row['id']] = dict(program_sha256=row['program_sha256'],forms=forms)
mutants = {}
if not san:
    for name,old,new in [('strict-equality','if (strict && val[v] == w) ok = false;',''),('direction','down ? val[v] >= w : val[v] <= w','down ? val[v] <= w : val[v] >= w'),('stale-top','top[u] = x;','top[v] = x;')]:
        assert old in core_source
        src=work/('mutant-'+name+'.cpp')
        exe=src.with_suffix('')
        src.write_text(core_source.replace(old,new))
        compile(src,exe)
        p=subprocess.run([str(exe)],capture_output=True,timeout=90)
        assert p.returncode != 0,name
        mutants[name]='detected'
files=['src/compact/kruskal_tree.hpp','tests/kruskal_tree.cpp','tests/kruskal_tree.py','src/compact/data_structure.hpp','src/compact/graph.hpp']+[r['driver'] for r in rows]
report=dict(status='pass',mode=mode,compiler=subprocess.check_output([CXX,'--version'],text=True).splitlines()[0],commands=commands,core=core,usage=usage,mutants=mutants,source_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files},scope='Exact threshold-component oracle and full P4768 decoding via Floyd/flood fill; largest n,m,q chain case; not online acceptance or runtime ranking.')
(root/f'verification/kruskal-tree-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
