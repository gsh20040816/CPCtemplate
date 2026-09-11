"""P3398 complete-program tests; boolean intersection is the judge's only output."""
from pathlib import Path
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(3398)
cases = []
for _ in range(70):
    n = rng.randrange(1, 70)
    labels = list(range(1, n + 1))
    rng.shuffle(labels)
    edges = [(labels[u], labels[rng.randrange(u)]) for u in range(1, n)]
    g = [[] for _ in range(n + 1)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    masks = [[0] * (n + 1) for _ in range(n + 1)]
    for s in range(1, n + 1):
        p = [0] * (n + 1)
        queue = [s]
        for u in queue:
            masks[s][u] = masks[s][p[u]] | (1 << u)
            for v in g[u]:
                if v != p[u]:
                    p[v] = u
                    queue.append(v)
    queries = [tuple(rng.randrange(1, n + 1) for _ in range(4)) for _ in range(300)]
    expected = ['Y' if masks[a][b] & masks[c][d] else 'N' for a, b, c, d in queries]
    cases.append((n, edges, queries, expected))
n = 100000
queries = [tuple(rng.randrange(1, n + 1) for _ in range(4)) for _ in range(n)]
expected = ['Y' if max(min(a, b), min(c, d)) <= min(max(a, b), max(c, d)) else 'N' for a, b, c, d in queries]
cases.append((n, [(u - 1, u) for u in range(2, n + 1)], queries, expected))
for style in ['compact', 'classic']:
    name = f'P3398.{style}'
    bundle = root / f'build/{name}.cpp'
    obj = root / f'build/{name}.o'
    exe = root / f'build/{name}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/luogu/{name}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', '-Dmain=cpc_entry', '-c', str(bundle), '-o', str(obj)], check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', '-pthread', str(obj), 'tests/driver_stack.cpp', '-o', str(exe)], cwd=root, check=True)
    for n, edges, queries, expected in cases:
        data = f'{n} {len(queries)}\n' + ''.join(f'{u} {v}\n' for u, v in edges)
        data += ''.join(' '.join(map(str, q)) + '\n' for q in queries)
        result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=10)
        assert result.stdout.splitlines() == expected
    print(f'P3398 {style}: 71 complete-program cases, independent path sets and n=q=100000 chain passed; 256MB local test stack')
