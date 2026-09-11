"""Complete P3379 drivers, checked against parent climbing and chain formulas."""
from pathlib import Path
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(3379)
cases = []
for _ in range(70):
    n = rng.randrange(1, 70)
    edges = [(u, rng.randrange(1, u)) for u in range(2, n + 1)]
    rng.shuffle(edges)
    g = [[] for _ in range(n + 1)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    r = rng.randrange(1, n + 1)
    parent = [0] * (n + 1)
    depth = [0] * (n + 1)
    queue = [r]
    for u in queue:
        for v in g[u]:
            if v != parent[u]:
                parent[v] = u
                depth[v] = depth[u] + 1
                queue.append(v)
    queries = [(rng.randrange(1, n + 1), rng.randrange(1, n + 1)) for _ in range(120)]
    expected = []
    for u, v in queries:
        while u != v:
            if depth[u] >= depth[v]:
                u = parent[u]
            else:
                v = parent[v]
        expected.append(u)
    cases.append((n, r, edges, queries, expected))
n = 500000
r = n // 2
edges = [(u - 1, u) for u in range(2, n + 1)]
queries = [(u, n + 1 - u) for u in range(1, n + 1)]
expected = [max(min(u, v), min(r, max(u, v))) for u, v in queries]
cases.append((n, r, edges, queries, expected))
for style in ['compact', 'classic']:
    name = f'P3379.offline.{style}'
    bundle = root / f'build/{name}.cpp'
    obj = root / f'build/{name}.o'
    exe = root / f'build/{name}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/luogu/{name}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', '-Dmain=cpc_entry', '-c', str(bundle), '-o', str(obj)], check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', '-pthread', str(obj), 'tests/driver_stack.cpp', '-o', str(exe)], cwd=root, check=True)
    for n, r, edges, queries, expected in cases:
        data = f'{n} {len(queries)} {r}\n' + ''.join(f'{u} {v}\n' for u, v in edges + queries)
        result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
        assert list(map(int, result.stdout.split())) == expected
    print(f'P3379 offline {style}: {len(cases)} cases including n=q=500000 passed; recursive driver executed on 256MB pthread stack')
# kuangbin's POJ1470 application: directed child lists and LCA histograms.
text = ''
expected = []
for n, r, edges, queries, answers in cases[:-1]:
    g = [[] for _ in range(n + 1)]
    children = [[] for _ in range(n + 1)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    parent = [0] * (n + 1)
    queue = [r]
    for u in queue:
        for v in g[u]:
            if v != parent[u]:
                children[u].append(v)
                parent[v] = u
                queue.append(v)
    rng.shuffle(queue)
    text += str(n) + '\n'
    for u in queue:
        text += f'{u}:({len(children[u])}) ' + ' '.join(map(str, children[u])) + '\n'
    text += str(len(queries)) + '\n'
    text += ''.join(f'({u} {v})\n' for u, v in queries)
    count = [0] * (n + 1)
    for u in answers:
        count[u] += 1
    expected += [f'{u}:{count[u]}' for u in range(1, n + 1) if count[u]]
text += '1\n1:(0)\n0\n'
for style in ['compact', 'classic']:
    bundle = root / f'build/poj1470.{style}.cpp'
    exe = root / f'build/poj1470.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/poj/1470.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    result = subprocess.run([str(exe)], input=text, text=True, capture_output=True, check=True, timeout=10)
    assert result.stdout.splitlines() == expected
    print(f'POJ1470 {style}: directed child rows, inferred roots, query histogram, shuffled rows, 71 datasets and empty query set passed')
