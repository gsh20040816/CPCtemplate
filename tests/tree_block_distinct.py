"""Independent online oracle and copy/sanitizer checks for tree blocking."""
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
SAN = '--sanitize' in sys.argv
MODE = 'sanitizer' if SAN else 'normal'
WORK = ROOT / 'build/tree-block' / MODE
WORK.mkdir(parents=True, exist_ok=True)
HEADER = ROOT / 'src/compact/tree_block_distinct.hpp'
CORE = ROOT / 'tests/tree_block_distinct.cpp'
DRIVER = ROOT / 'verify/luogu/P6177.compact.cpp'
code = HEADER.read_text().replace('#pragma once\n', '')
program = DRIVER.read_text().replace('#include "../../src/compact/tree_block_distinct.hpp"', code)
(ROOT / 'build/tree-block/P6177.cpp').write_text(program)
flags = ['-std=c++20', '-O1' if SAN else '-O2']
if SAN:
    flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
commands = []
def compile(src, out, extra=()):
    cmd = [CXX, *flags, *extra, str(src), '-o', str(out)]
    commands.append(cmd)
    subprocess.run(cmd, check=True, capture_output=True, text=True)
def run(exe, data=''):
    p = subprocess.run([str(exe)], input=data, capture_output=True, text=True, env=env, timeout=180)
    assert p.returncode == 0, p.stderr
    return p.stdout
core_source = CORE.read_text().replace('#include "../src/compact/tree_block_distinct.hpp"', code)
core = {}
for form in ['header', 'ndebug', 'copied']:
    src = CORE
    exe = WORK / ('core-' + form)
    if form == 'copied':
        src = exe.with_suffix('.cpp')
        src.write_text(core_source)
    compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
    core[form] = run(exe).strip()
    print(MODE, form, core[form], flush=True)

cases = [('8 2\n105 2 9 3 8 5 7 7\n1 2\n1 3\n1 4\n3 5\n3 6\n3 7\n4 8\n2 5\n3 8\n', [4, 4])]
rng = random.Random(6177)
for trial in range(100):
    n = rng.randrange(1, 100)
    colors = [rng.randrange(1, 30) for _ in range(n)]
    edges = [(v, rng.randrange(v)) for v in range(1, n)]
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    queries = [(rng.randrange(n), rng.randrange(n)) for _ in range(100)]
    want = []
    encoded = []
    last = 0
    for u, v in queries:
        # Breadth-first parents are independent of the implementation's LCA and blocks.
        parent = [-1] * n
        parent[u] = u
        queue = [u]
        for x in queue:
            for y in graph[x]:
                if parent[y] < 0:
                    parent[y] = x
                    queue.append(y)
        seen = {colors[u]}
        x = v
        while x != u:
            seen.add(colors[x])
            x = parent[x]
        encoded.append((u + 1 ^ last, v + 1))
        last = len(seen)
        want.append(last)
    data = f'{n} {len(queries)}\n' + ' '.join(map(str, colors)) + '\n'
    data += ''.join(f'{u+1} {v+1}\n' for u, v in edges)
    data += ''.join(f'{u} {v}\n' for u, v in encoded)
    cases.append((data, want))
forms = {}
for form in ['header', 'ndebug', 'copied']:
    exe = WORK / ('driver-' + form)
    src = DRIVER if form != 'copied' else ROOT / 'build/tree-block/P6177.cpp'
    compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
    for data, want in cases:
        assert list(map(int, run(exe, data).split())) == want
    forms[form] = len(cases)
    print(MODE, form, 'online cases PASS', flush=True)
mutants = {}
if not SAN:
    changes = [('above-lca', 'int b = near[x];', 'int b = near[ancestor];'),
               ('duplicate-clear', 'if (--count[x] == 0)', 'if (--count[x] >= 0)'),
               ('missing-lca', 'ans[c[p] >> 6] |= 1ULL << (c[p] & 63);', '')]
    for name, old, new in changes:
        assert old in core_source
        src = WORK / ('mutant-' + name + '.cpp')
        exe = src.with_suffix('')
        src.write_text(core_source.replace(old, new))
        compile(src, exe, ['-D_GLIBCXX_ASSERTIONS'])
        try:
            p = subprocess.run([str(exe)], capture_output=True, timeout=15)
            assert p.returncode != 0, name
            mutants[name] = 'detected'
        except subprocess.TimeoutExpired:
            mutants[name] = 'detected by timeout'
files = [HEADER, CORE, DRIVER, Path(__file__)]
report = dict(status='pass', mode=MODE, core=core, online_cases=forms, mutants=mutants, commands=commands,
              source_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
              scope='1442 labelled trees, 1500 random trees, repeated build/root/block/copy/bit boundaries; official sample and 100 independently encoded online cases. Large scale and actual OJ separate.')
(ROOT / f'verification/tree-block-{MODE}.json').write_text(json.dumps(report, indent=2) + '\n')
