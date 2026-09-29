"""Full P3376/P3381 programs checked against cuts and enumerated feasible flows."""
from compiler_config import CXX
from pathlib import Path
import itertools
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(20260929)
sanitize = os.environ.get('CPC_SANITIZE') == '1'
mode = 'san' if sanitize else 'normal'
flags = ['-std=c++20', '-O2']
if sanitize:
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']


def build(problem):
    exe = root / f'build/flow-{problem}-{mode}'
    subprocess.run([CXX, *flags, str(root / f'verify/luogu/{problem}.compact.cpp'), '-o', str(exe)], check=True)
    return exe


def run(exe, n, edges, expected):
    data = f'{n} {len(edges)} 1 {n}\n' + ''.join(' '.join(map(str, e)) + '\n' for e in edges)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
    assert not result.stderr, result.stderr
    assert tuple(map(int, result.stdout.split())) == expected, (n, edges[:20], result.stdout, expected)


maxflow = build('P3376')
for _ in range(200):
    n = rng.randint(2, 8)
    e = [(rng.randint(1, n), rng.randint(1, n), rng.randrange(2**31)) for _ in range(20)]
    answer = min(sum(c for u, v, c in e if (mask >> (u - 1) & 1) and not (mask >> (v - 1) & 1))
                 for mask in range(1 << n) if mask & 1 and not (mask >> (n - 1) & 1))
    run(maxflow, n, e, (answer,))
e = [(1, 2, 2**31 - 1)] * 2500 + [(2, 200, 2**31 - 1)] * 2500
run(maxflow, 200, e, (2500 * (2**31 - 1),))
print('P3376: 200 arbitrary-integer cut oracles, 200 vertices / 5000 edges and int64 total PASS', flush=True)

costflows = [build(name) for name in ['P3381', 'P3381.slope', 'P3381.spfa']]
for _ in range(200):
    n = rng.randint(2, 5)
    edges = []
    for _ in range(7):
        u, v = rng.sample(range(1, n + 1), 2)
        edges.append((u, v, rng.randrange(3), rng.randrange(1001)))
    best = (0, 0)
    for flows in itertools.product(*(range(c + 1) for u, v, c, w in edges)):
        balance = [0] * (n + 1)
        cost = 0
        for f, (u, v, c, w) in zip(flows, edges):
            balance[u] -= f
            balance[v] += f
            cost += f * w
        if any(balance[2:n]) or balance[n] != -balance[1]:
            continue
        best = max(best, (-balance[1], -cost))
    for exe in costflows:
        run(exe, n, edges, (best[0], -best[1]))
edges = [(1, u, 1, u - 2) for u in range(2, 1002)]
edges += [(u, 5000, 1, 0) for u in range(2, 1002)]
edges += [(4998, 4999, 0, i % 1001) for i in range(48000)]
for exe in costflows:
    run(exe, 5000, edges, (1000, 999 * 1000 // 2))
# Deliberately require many successful shortest-path relaxations in reverse edge order.
chain = [(u, u + 1, 1, 0) for u in range(4999, 0, -1)]
chain += [(1, 5000, 0, 1000)] * (50000 - len(chain))
for exe in costflows:
    run(exe, 5000, chain, (1, 0))
active = [(1, 2, 1, 0)] + [(u, u + 1, 1000, 1) for u in range(2, 5000)]
while len(active) < 50000:
    u = rng.randint(2, 4999)
    v = rng.randint(u + 1, 5000)
    active.append((u, v, 1000, rng.randint(0, 1000)))
# Cut {1} bounds the total flow by one. A DAG shortest path gives its cost independently.
adj = [[] for _ in range(5001)]
for u, v, cap, cost in active:
    adj[u].append((v, cost))
distance = [10**30] * 5001
distance[1] = 0
for u in range(1, 5001):
    for v, cost in adj[u]:
        distance[v] = min(distance[v], distance[u] + cost)
for exe in costflows:
    run(exe, 5000, active, (1, distance[5000]))
print('P3381 flow/slope/SPFA: each 200 enumerated feasible-flow cases, 1000 augmentations '
      'at 5000 vertices / 50000 edges, reverse-ordered chain and 50000 positive-capacity '
      'DAG edges with a topological-DP oracle PASS', flush=True)
