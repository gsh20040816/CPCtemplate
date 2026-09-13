"""POJ1637 circuit-only adapter, checked by enumerating edge orientations."""
from compiler_config import CXX
from pathlib import Path
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(1637)

def oracle(n, edges):
    g = [[] for _ in range(n + 1)]
    for u, v, kind in edges:
        g[u].append(v)
        g[v].append(u)
    if edges:
        seen = {edges[0][0]}
        queue = list(seen)
        for u in queue:
            for v in g[u]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        if any(g[u] and u not in seen for u in range(1, n + 1)):
            return False
    count = sum(kind == 0 for u, v, kind in edges)
    for mask in range(1 << count):
        delta = [0] * (n + 1)
        k = 0
        for u, v, kind in edges:
            if kind == 0:
                if mask >> k & 1:
                    u, v = v, u
                k += 1
            delta[u] += 1
            delta[v] -= 1
        if not any(delta):
            return True
    return False

cases = []
for _ in range(180):
    n = rng.randrange(1, 7)
    edges = [(rng.randrange(1, n + 1), rng.randrange(1, n + 1), rng.randrange(2)) for _ in range(rng.randrange(9))]
    cases.append((n, edges, oracle(n, edges)))
# Full-scale dense reversals and a fixed one-way obstruction.
cases += [(200, [(u, u + 1, 0) for u in range(1, 200)] * 10, True),
          (200, [(u, u + 1, 1) for u in range(1, 200)] * 10, False),
          (200, [(u, u % 200 + 1, 1) for u in range(1, 201)] * 50, True)]
data = str(len(cases)) + '\n'
expected = []
for n, edges, answer in cases:
    data += f'{n} {len(edges)}\n' + ''.join(f'{u} {v} {kind}\n' for u, v, kind in edges)
    expected.append('possible' if answer else 'impossible')
for style in ['compact']:
    bundle = root / f'build/poj1637.{style}.cpp'
    exe = root / f'build/poj1637.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/poj/1637.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run([CXX, '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=15)
    assert result.stdout.splitlines() == expected
    print(f'POJ1637 {style}: 183 cases, orientation enumeration, parsing/reset and dense 200-node cases passed; circuit verdict only')
