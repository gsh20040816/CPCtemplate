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
work = root / 'build/four-cycles' / mode
work.mkdir(parents=True, exist_ok=True)
flags = ['-std=c++20', '-O1' if san else '-O2']
if san:
    flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
rows = [r for r in records() if r['id'] in ['example-378', 'example-379']]
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

prefix = candidate(rows[0], ['count_four_cycles'], components)['program'].split('int main()')[0]
core_source = (root / 'tests/four_cycles.cpp').read_text().replace('#include "../src/compact/four_cycles.hpp"', prefix)
core = {}
for form in ['header', 'ndebug', 'copied']:
    src = root / 'tests/four_cycles.cpp'
    exe = work / ('core-' + form)
    if form == 'copied':
        src = exe.with_suffix('.cpp')
        src.write_text(core_source)
    compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
    core[form] = run(exe).strip()
    print(mode, form, core[form], flush=True)

def brute(n, edges):
    from itertools import combinations
    g = [[False] * n for _ in range(n)]
    for u, v in edges:
        g[u][v] = g[v][u] = True
    ans = 0
    for a, b, c, d in combinations(range(n), 4):
        ans += g[a][b] and g[b][c] and g[c][d] and g[d][a]
        ans += g[a][b] and g[b][d] and g[d][c] and g[c][a]
        ans += g[a][c] and g[c][b] and g[b][d] and g[d][a]
    return ans

rng = random.Random(367189)
graphs = []
for trial in range(151):
    n = rng.randrange(1, 30)
    edges = [(u, v) for u in range(n) for v in range(u + 1, n) if rng.randrange(4) == 0]
    rng.shuffle(edges)
    graphs.append((n, edges, brute(n, edges)))
graphs += [(4, [(u, v) for u in range(4) for v in range(u + 1, 4)], 3), (100000, [(u, v) for u in range(2) for v in range(2, 100000)], 99998 * 99997 // 2), (100000, [(0, v) for v in range(1, 100000)], 0)]
cases = {'example-378': [], 'example-379': []}
for name, offset in [('example-378', 1), ('example-379', 0)]:
    for n, edges, want in graphs:
        data = f'{n} {len(edges)}\n' + ''.join(f'{u + offset} {v + offset}\n' for u, v in edges)
        cases[name].append((data, [want]))
cases['example-379'].append(('0 0\n', [0]))
usage = {}
for row in rows:
    forms = {}
    for form in ['header', 'ndebug', 'expanded', 'copied']:
        src = root / row['driver']
        exe = work / (row['id'] + '-' + form)
        if form in ['expanded', 'copied']:
            src = exe.with_suffix('.cpp')
            src.write_text(row['program'] if form == 'expanded' else candidate(row, ['count_four_cycles'], components)['program'])
        compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
        for data, want in cases[row['id']]:
            got = list(map(int, run(exe, data).split()))
            assert got == want, (row['id'], form, data[:100], got[:50], want[:50])
        forms[form] = len(cases[row['id']])
        print(mode, row['id'], form, 'PASS', flush=True)
    usage[row['id']] = dict(program_sha256=row['program_sha256'], forms=forms)
mutants = {}
if not san:
    for name, old, new in [('tie-break', 'pair{g[u].size(), u} < pair{g[v].size(), v}', 'g[u].size() < g[v].size()'), ('reset', 'for (int w : touched) cnt[w] = 0;', '// missing reset'), ('width', 'long long ans = 0;', 'int ans = 0;')]:
        assert old in core_source
        src = work / ('mutant-' + name + '.cpp')
        exe = src.with_suffix('')
        src.write_text(core_source.replace(old, new))
        # Bounds checks make wrong-index mutants fail deterministically.
        compile(src, exe, ['-D_GLIBCXX_ASSERTIONS'])
        p = subprocess.run([str(exe)], capture_output=True, timeout=90)
        assert p.returncode != 0, name
        mutants[name] = 'detected'
files = ['src/compact/four_cycles.hpp', 'tests/four_cycles.cpp', 'tests/four_cycles.py'] + [r['driver'] for r in rows]
report = dict(status='pass', mode=mode, compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0], commands=commands, core=core, usage=usage, mutants=mutants, source_sha256={p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in files}, scope='Every simple graph through n=6 by explicit four-vertex cycle enumeration, random graph relabelling, dense/sparse closed-form stress and 64-bit answers; O2 and sanitizer separate. No online AC claimed by local tests.')
(root / f'verification/four-cycles-{mode}.json').write_text(json.dumps(report, indent=2) + '\n')
