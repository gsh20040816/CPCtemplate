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
work = root / 'build/long-chain' / mode
work.mkdir(parents=True, exist_ok=True)
flags = ['-std=c++20', '-O1' if san else '-O2']
if san:
    flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
rows = [r for r in records() if r['id'] in ['example-376', 'example-377']]
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

prefix = candidate(rows[0], ['LongChain'], components)['program'].split('int main()')[0]
core_source = (root / 'tests/long_chain.cpp').read_text().replace('#include "../src/compact/long_chain.hpp"', prefix)
core = {}
for form in ['header', 'ndebug', 'copied']:
    src = root / 'tests/long_chain.cpp'
    exe = work / ('core-' + form)
    if form == 'copied':
        src = exe.with_suffix('.cpp')
        src.write_text(core_source)
    compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
    core[form] = run(exe).strip()
    print(mode, form, core[form], flush=True)

def reference(n, edges, root):
    g = [[] for _ in range(n + 1)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    parent = [-1] * (n + 1)
    dep = [0] * (n + 1)
    parent[root], dep[root] = 0, 1
    order = [root]
    for u in order:
        for v in g[u]:
            if parent[v] == -1:
                parent[v], dep[v] = u, dep[u] + 1
                order.append(v)
    return parent, dep

def jump(parent, u, k):
    for _ in range(k):
        if not u:
            break
        u = parent[u]
    return u

def generated(n, q, s, parent, dep):
    def get():
        nonlocal s
        s ^= (s << 13) & 0xffffffff
        s ^= s >> 17
        s ^= (s << 5) & 0xffffffff
        return s
    last, ans = 0, 0
    for i in range(1, q + 1):
        u = (get() ^ last) % n + 1
        k = (get() ^ last) % dep[u]
        last = jump(parent, u, k)
        ans ^= i * last
    return ans

rng = random.Random(5903)
cases = {'example-376': [('6 3 7\n5 5 2 2 0 3\n', [1])], 'example-377': []}
for trial in range(150):
    n = rng.randrange(1, 151)
    labels = list(range(1, n + 1))
    rng.shuffle(labels)
    edges = [(labels[i], labels[rng.randrange(i)]) for i in range(1, n)]
    root_node = rng.choice(labels)
    parent, dep = reference(n, edges, root_node)
    q, seed = 200, rng.randrange(1, 2**32)
    data = f'{n} {q} {seed}\n' + ' '.join(map(str, parent[1:])) + '\n'
    cases['example-376'].append((data, [generated(n, q, seed, parent, dep)]))
    queries = [(u, k) for u in labels for k in [0, dep[u] - 1, dep[u], 2147483647, rng.randrange(n + 1)]]
    data = f'{n} {root_node} {len(queries)}\n'
    data += ''.join(f'{u} {v}\n' for u, v in edges)
    data += ''.join(f'{u} {k}\n' for u, k in queries)
    cases['example-377'].append((data, [jump(parent, u, k) for u, k in queries]))
usage = {}
for row in rows:
    forms = {}
    for form in ['header', 'ndebug', 'expanded', 'copied']:
        src = root / row['driver']
        exe = work / (row['id'] + '-' + form)
        if form in ['expanded', 'copied']:
            src = exe.with_suffix('.cpp')
            src.write_text(row['program'] if form == 'expanded' else candidate(row, ['LongChain'], components)['program'])
        compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
        for data, want in cases[row['id']]:
            got = list(map(int, run(exe, data).split()))
            assert got == want, (row['id'], form, data[:100], got[:50], want[:50])
        forms[form] = len(cases[row['id']])
        print(mode, row['id'], form, 'PASS', flush=True)
    usage[row['id']] = dict(program_sha256=row['program_sha256'], forms=forms)
mutants = {}
if not san:
    for name, old, new in [('zero', 'if (k == 0) return u;', 'if (k == 0) return 0;'), ('up-index', 'up[t][k - d]', 'up[t][k - d - 1]'), ('down-index', 'down[t][d - k]', 'down[t][d - k + 1]')]:
        assert old in core_source
        src = work / ('mutant-' + name + '.cpp')
        exe = src.with_suffix('')
        src.write_text(core_source.replace(old, new))
        # Bounds checks make wrong-index mutants fail deterministically.
        compile(src, exe, ['-D_GLIBCXX_ASSERTIONS'])
        p = subprocess.run([str(exe)], capture_output=True, timeout=90)
        assert p.returncode != 0, name
        mutants[name] = 'detected'
files = ['src/compact/long_chain.hpp', 'tests/long_chain.cpp', 'tests/long_chain.py'] + [r['driver'] for r in rows]
report = dict(status='pass', mode=mode, compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0], commands=commands, core=core, usage=usage, mutants=mutants, source_sha256={p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in files}, scope='All labelled trees through n=6/all roots and random trees compared with BFS parents and direct climbing; full API boundaries/copy/reroot. Large Linux recursion and online evidence recorded separately.')
(root / f'verification/long-chain-{mode}.json').write_text(json.dumps(report, indent=2) + '\n')
