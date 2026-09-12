"""P2860 bundled-program output versus independent edge-deletion oracle."""
from pathlib import Path
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(2860)

def oracle(n, edges):
    def groups(skip):
        p = list(range(n))
        def find(u):
            if p[u] != u:
                p[u] = find(p[u])
            return p[u]
        for i, (u, v) in enumerate(edges):
            if i != skip:
                p[find(u)] = find(v)
        return [find(u) for u in range(n)]
    bridges = [i for i in range(len(edges)) if len(set(groups(i))) > 1]
    remaining = [e for i, e in enumerate(edges) if i not in bridges]
    p = list(range(n))
    def find(u):
        if p[u] != u:
            p[u] = find(p[u])
        return p[u]
    for u, v in remaining:
        p[find(u)] = find(v)
    degree = [0] * n
    for i in bridges:
        u, v = edges[i]
        degree[find(u)] += 1
        degree[find(v)] += 1
    return (degree.count(1) + 1) // 2

cases = [(1, [], 0), (2, [(0, 1)], 1)]
for _ in range(120):
    n = rng.randrange(2, 11)
    edges = [(u, rng.randrange(u)) for u in range(1, n)]
    for _ in range(rng.randrange(n)):
        u, v = rng.sample(range(n), 2)
        edges.append((u, v))
    cases.append((n, edges, oracle(n, edges)))
cases += [(5000, [(u - 1, u) for u in range(1, 5000)], 1),
          (5000, [(0, u) for u in range(1, 5000)], 2500),
          (5000, [(u, (u + 1) % 5000) for u in range(5000)] * 2, 0)]
for style in ['compact']:
    bundle = root / f'build/P2860.{style}.cpp'
    exe = root / f'build/P2860.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/luogu/P2860.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    for n, edges, expected in cases:
        data = f'{n} {len(edges)}\n' + ''.join(f'{u+1} {v+1}\n' for u, v in edges)
        actual = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=10).stdout
        assert actual.split() == [str(expected)], (style, n, actual, expected)
    print(f'P2860 {style}: {len(cases)} cases passed, including n=5000 and m=10000')
