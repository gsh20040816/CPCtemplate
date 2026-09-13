"""Check the complete PBDS shortest-path driver against Floyd-Warshall."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
exe = root / 'build/lc-pheap-shortest-path'
subprocess.run([CXX, *flags, str(root / 'verify/library_checker/shortest_path.compact.cpp'), '-o', str(exe)], check=True)
rng = random.Random(915377)
for case in range(160):
    n = rng.randrange(2, 22)
    s, t = rng.sample(range(n), 2)
    edges = {}
    density = [0, .1, .4, 1][case % 4]
    for u in range(n):
        for v in range(n):
            if u != v and rng.random() < density:
                edges[u, v] = rng.choice([0, 1, 10**9, rng.randrange(100)])
    if not edges:
        edges[t, s] = 0
    inf = 10**30
    d = [[inf] * n for _ in range(n)]
    for u in range(n):
        d[u][u] = 0
    for (u, v), w in edges.items():
        d[u][v] = w
    for k in range(n):
        for u in range(n):
            for v in range(n):
                d[u][v] = min(d[u][v], d[u][k] + d[k][v])
    lines = [f'{n} {len(edges)} {s} {t}']
    lines += [f'{u} {v} {w}' for (u, v), w in edges.items()]
    result = subprocess.run([str(exe)], input='\n'.join(lines) + '\n', text=True, capture_output=True, check=True, timeout=30)
    assert not result.stderr, result.stderr
    tokens = list(map(int, result.stdout.split()))
    if d[s][t] == inf:
        assert tokens == [-1]
        continue
    cost, length = tokens[:2]
    assert cost == d[s][t] and len(tokens) == 2 + 2 * length
    current, total = s, 0
    seen = {s}
    for i in range(length):
        u, v = tokens[2 + 2*i:4 + 2*i]
        assert u == current and (u, v) in edges and v not in seen
        total += edges[u, v]
        current = v
        seen.add(v)
    assert current == t and total == cost
print('PBDS shortest-path driver: 160 Floyd-Warshall graph oracles, zero weights, unreachable targets and simple-path certificates PASS')
