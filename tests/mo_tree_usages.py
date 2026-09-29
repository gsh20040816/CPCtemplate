"""Complete contest drivers against set/path/BFS oracles; local evidence only."""
from compiler_config import CXX
from pathlib import Path
from collections import Counter, deque
import hashlib
import itertools
import json
import os
import random
import subprocess
import time

root = Path(__file__).resolve().parents[1]
os.chdir(root)
mode = 'sanitizer' if os.getenv('CPC_SANITIZE') == '1' else 'normal'
work = root / 'build' / ('mo-tree-' + mode)
work.mkdir(parents=True, exist_ok=True)
flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2']
if os.uname().sysname == 'Darwin':
    flags += ['-Wl,-stack_size,0x20000000']
drivers = {'mo': 'verify/luogu/P1903.compact.cpp',
           'intersection': 'verify/luogu/P3398.compact.cpp',
           'diameter': 'verify/luogu/CF379F.compact.cpp'}
for name, driver in drivers.items():
    subprocess.run(['python3', 'tools/bundle.py', driver, str(work / (name + '.cpp'))], check=True)
    subprocess.run([CXX, '-std=c++20', *flags, str(work / (name + '.cpp')), '-o', str(work / name)], check=True)
counts = Counter()
seconds = Counter()
def run(name, data, expected):
    start = time.monotonic()
    p = subprocess.run([str(work / name)], input=data, text=True, capture_output=True, timeout=180, check=True)
    seconds[name] += time.monotonic() - start
    assert not p.stderr, p.stderr
    assert p.stdout.split() == list(map(str, expected)), (name, data[:1000], p.stdout[:1000], str(expected)[:1000])
    counts[name] += 1

rng = random.Random(19033398379)
for trial in range(300):
    n = rng.randint(1, 40)
    initial = [rng.choice([1, 2, 3, 1000000]) for _ in range(n)]
    a = initial[:]
    operations, expected = [], []
    for _ in range(rng.randint(1, 120)):
        if trial % 5 == 0 or (trial % 5 != 1 and rng.randrange(2)):
            l, r = sorted([rng.randrange(n), rng.randrange(n)])
            operations.append(f'Q {l+1} {r+1}')
            expected.append(len(set(a[l:r+1])))
        else:
            p, c = rng.randrange(n), rng.choice([1, 2, 3, 1000000])
            operations.append(f'R {p+1} {c}')
            a[p] = c
    run('mo', f'{n} {len(operations)}\n' + ' '.join(map(str, initial)) + '\n' + '\n'.join(operations) + '\n', expected)
# Largest statement size, unique colors and many intervals; no-update boundary.
n = 133333
queries = [(rng.randrange(n), rng.randrange(n)) for _ in range(n)]
queries = [tuple(sorted(x)) for x in queries]
run('mo', f'{n} {n}\n' + ' '.join(map(str, range(1, n+1))) + '\n' + ''.join(f'Q {l+1} {r+1}\n' for l, r in queries), [r-l+1 for l, r in queries])
# Maximum updates/queries combined, repeated edits inside a full active interval.
ops = []
expected = []
for i in range(n):
    if i % 2 == 0:
        ops.append(f'R 1 {2 if i % 4 == 0 else 1}')
    else:
        ops.append(f'Q 1 {n}')
        expected.append(2 if i % 4 == 1 else 1)
run('mo', f'{n} {n}\n' + '1 ' * n + '\n' + '\n'.join(ops) + '\n', expected)

def paths(n, edges):
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    result = {}
    for s in range(n):
        parent = [-1] * n
        parent[s] = s
        q = [s]
        for u in q:
            for v in g[u]:
                if parent[v] < 0:
                    parent[v] = u
                    q.append(v)
        for v in range(n):
            seen = {s}
            u = v
            while u != s:
                seen.add(u)
                u = parent[u]
            result[s, v] = seen
    return result

def check_paths(n, edges, queries):
    oracle = paths(n, edges)
    data = f'{n} {len(queries)}\n' + ''.join(f'{u+1} {v+1}\n' for u, v in edges)
    data += ''.join(' '.join(str(v+1) for v in query) + '\n' for query in queries)
    expected = ['Y' if oracle[a, b] & oracle[c, d] else 'N' for a, b, c, d in queries]
    run('intersection', data, expected)

trees = 0
for n in range(1, 6):
    for seq in itertools.product(range(n), repeat=max(0, n-2)):
        deg = [1] * n
        for u in seq:
            deg[u] += 1
        edges = []
        for u in seq:
            v = next(v for v in range(n) if deg[v] == 1)
            edges.append((u, v))
            deg[u] -= 1
            deg[v] -= 1
        last = [v for v in range(n) if deg[v] == 1]
        if n > 1:
            edges.append(tuple(last))
        check_paths(n, edges, list(itertools.product(range(n), repeat=4)))
        trees += 1
for _ in range(100):
    n = rng.randint(2, 40)
    labels = list(range(n))
    rng.shuffle(labels)
    edges = [(labels[v], labels[rng.randrange(v)]) for v in range(1, n)]
    check_paths(n, edges, [tuple(rng.randrange(n) for _ in range(4)) for _ in range(100)])
n = 100000
queries = [tuple(rng.randint(1, n) for _ in range(4)) for _ in range(n)]
expected = []
for a, b, c, d in queries:
    a, b = sorted((a, b))
    c, d = sorted((c, d))
    expected.append('Y' if max(a, c) <= min(b, d) else 'N')
run('intersection', f'{n} {n}\n' + ''.join(f'{v} {v+1}\n' for v in range(1, n)) + ''.join(' '.join(map(str, x)) + '\n' for x in queries), expected)

# Rebuild each small current tree and find its diameter via two independent BFS.
def diameter(g):
    def bfs(s):
        d = [-1] * len(g)
        d[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in g[u]:
                if d[v] == -1:
                    d[v] = d[u] + 1
                    q.append(v)
        u = max(range(len(g)), key=d.__getitem__)
        return u, d[u]
    return bfs(bfs(0)[0])[1]
for _ in range(250):
    q = rng.randint(1, 100)
    g = [[1, 2, 3], [0], [0], [0]]
    leaves = [1, 2, 3]
    ops, expected = [], []
    for _ in range(q):
        idx = rng.randrange(len(leaves))
        v = leaves.pop(idx)
        ops.append(v+1)
        for _ in range(2):
            w = len(g)
            g.append([v])
            g[v].append(w)
            leaves.append(w)
        expected.append(diameter(g))
    run('diameter', str(q) + '\n' + '\n'.join(map(str, ops)) + '\n', expected)
# q=500000 gives 1000004 vertices and recursive depth500001, no explicit DFS stack.
q = 500000
ops = [2] + [5 + 2*i for i in range(q-1)]
run('diameter', str(q) + '\n' + '\n'.join(map(str, ops)) + '\n', range(3, q+3))
report = {'mode': mode, 'counts': dict(counts), 'seconds': dict(seconds), 'all_labelled_trees_up_to_5': trees,
          'scope': 'Local complete drivers. Color-set oracle; explicit path-set intersection; two-BFS rebuilt diameter. Maximum constraints including recursive chains. No online AC or speed-rank claim.',
          'programs': {name: {'driver': driver, 'bundle_sha256': hashlib.sha256((work/(name+'.cpp')).read_bytes()).hexdigest()} for name, driver in drivers.items()}}
(root / 'verification' / ('mo-tree-usages-' + mode + '.json')).write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
