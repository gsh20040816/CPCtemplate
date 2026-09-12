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
for style in ['compact']:
    name = f'P3379.euler.{style}'
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
    print(f'P3379 euler {style}: {len(cases)} cases including n=q=500000 passed; recursive driver executed on 256MB pthread stack')

# POJ1330: directed parent-child edges, inferred root, one query per dataset.
small = cases[:-1] + [(10000, 10000, [(u + 1, u) for u in range(1, 10000)], [(1, 5000)], [5000])]
data = str(len(small)) + '\n'
expected = []
for n, r, edges, queries, answers in small:
    g = [[] for _ in range(n + 1)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    parent = [0] * (n + 1)
    queue = [r]
    directed = []
    for u in queue:
        for v in g[u]:
            if v != parent[u]:
                parent[v] = u
                directed.append((u, v))
                queue.append(v)
    rng.shuffle(directed)
    data += str(n) + '\n' + ''.join(f'{u} {v}\n' for u, v in directed)
    u, v = queries[0]
    data += f'{u} {v}\n'
    expected.append(answers[0])
for style in ['compact']:
    bundle = root / f'build/poj1330.{style}.cpp'
    exe = root / f'build/poj1330.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/poj/1330.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=10)
    assert list(map(int, result.stdout.split())) == expected
    print(f'POJ1330 {style}: directed edges, inferred roots, shuffled input, 71 datasets and n=10000 passed')
