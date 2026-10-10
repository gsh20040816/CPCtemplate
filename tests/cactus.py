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
work = root / 'build/cactus' / mode
work.mkdir(parents=True, exist_ok=True)
flags = ['-std=c++20', '-O1' if san else '-O2']
if san:
    flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
row = next(r for r in records() if r['id'] == 'example-382')
components = {r['symbol']: r for r in extract_components(json.loads((root / 'docs/catalog.json').read_text()))}
copy = candidate(row, ['Cactus'], components)['program']
(root / 'build/cactus/P5236.cpp').write_text(copy)
commands = []
def compile(src, exe, extra=()):
    cmd = [CXX, *flags, *extra, str(src), '-o', str(exe)]
    commands.append(cmd)
    subprocess.run(cmd, check=True, capture_output=True, text=True)
def run(exe, data=''):
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env=env, timeout=120)
    assert p.returncode == 0, p.stderr
    return p.stdout
core_source = (root / 'tests/cactus.cpp').read_text().replace('#include "../src/compact/cactus.hpp"', copy.split('int main()')[0])
core = {}
for form in ['header', 'ndebug', 'copied']:
    src = root / 'tests/cactus.cpp'
    exe = work / ('core-' + form)
    if form == 'copied':
        src = exe.with_suffix('.cpp')
        src.write_text(core_source)
    compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
    core[form] = run(exe).strip()
    print(mode, form, core[form], flush=True)
cases = [('9 10 2\n1 2 1\n1 4 1\n3 4 1\n2 3 1\n3 7 1\n7 8 2\n7 9 2\n1 5 3\n1 6 4\n5 6 1\n1 9\n5 7\n', [5,6]), ('9 10 3\n1 2 1\n2 3 1\n2 4 4\n3 4 2\n4 5 1\n5 6 1\n6 7 2\n7 8 2\n8 9 4\n5 9 2\n1 9\n5 8\n3 4\n', [7,5,2])]
rng = random.Random(5236)
for trial in range(150):
    n = rng.randrange(1,35)
    edges = []
    now = 1
    while now < n:
        top = rng.randrange(1, now+1)
        size = min(n-now, rng.randrange(1,6))
        u = top
        for _ in range(size):
            now += 1
            edges.append((u, now, rng.randrange(100001)))
            u = now
        if size >= 2 and rng.randrange(2):
            edges.append((u, top, rng.randrange(100001)))
    if edges and trial % 3 == 0:
        edges.pop(rng.randrange(len(edges)))
    perm = list(range(1,n+1))
    rng.shuffle(perm)
    edges = [(perm[u-1],perm[v-1],w) for u,v,w in edges]
    rng.shuffle(edges)
    inf = 10**30
    d = [[inf] * n for _ in range(n)]
    for i in range(n): d[i][i] = 0
    for u,v,w in edges: d[u-1][v-1] = d[v-1][u-1] = w
    for k in range(n):
        for i in range(n):
            for j in range(n): d[i][j] = min(d[i][j], d[i][k]+d[k][j])
    data = f'{n} {len(edges)} {n*n}\n' + ''.join(f'{u} {v} {w}\n' for u,v,w in edges)
    data += ''.join(f'{i+1} {j+1}\n' for i in range(n) for j in range(n))
    cases.append((data, [x if x < inf else -1 for line in d for x in line]))
forms = {}
for form in ['header','ndebug','expanded','copied']:
    src = root / row['driver']
    exe = work / ('example-382-' + form)
    if form in ['expanded','copied']:
        src = exe.with_suffix('.cpp')
        src.write_text(row['program'] if form == 'expanded' else copy)
    compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
    for data,want in cases:
        assert list(map(int,run(exe,data).split())) == want
    forms[form] = len(cases)
    print(mode, form, 'driver PASS', flush=True)
mutants = {}
if not san:
    for name,old,new in [('ring-correction','min(arc, len[p] - arc)','arc'),('bridge','if (!bel[v])','if (true)'),('star-weight','min(pos[x], len[b] - pos[x])','pos[x]')]:
        assert old in core_source
        src = work / ('mutant-'+name+'.cpp')
        exe = src.with_suffix('')
        src.write_text(core_source.replace(old,new))
        compile(src,exe)
        p = subprocess.run([str(exe)], capture_output=True, timeout=120)
        assert p.returncode != 0, name
        mutants[name] = 'detected'
files = ['src/compact/cactus.hpp','tests/cactus.cpp','tests/cactus.py',row['driver']]
report = dict(status='pass',mode=mode,commands=commands,core=core,usage={'example-382':dict(program_sha256=row['program_sha256'],forms=forms)},mutants=mutants,source_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files},scope='Definition-only cycle enumeration for cactus input classification, Floyd distance oracle; official samples, copied forms and recursive DFS. Online evidence separate.')
(root/f'verification/cactus-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
