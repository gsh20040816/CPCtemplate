"""Copied P6329 driver: BFS oracle and independent XOR encoder; max-size cases."""
from compiler_config import CXX
from collections import deque
from pathlib import Path
import os
import random
import resource
import subprocess

root = Path(__file__).resolve().parents[1]
mode = 'san' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-std=c++20', '-O2'] if mode == 'normal' else [
    '-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
source = root / f'build/centroid-sum-driver-{mode}.cpp'
source.parent.mkdir(exist_ok=True)
subprocess.run(['python3', str(root / 'tools/bundle.py'), str(root / 'verify/luogu/P6329.compact.cpp'), str(source)], check=True)
exe = source.with_suffix('')
subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)
# Preserve recursive DFS; provide sufficient native stack for the maximum chain.
soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
resource.setrlimit(resource.RLIMIT_STACK, (min(256 << 20, hard) if hard != -1 else 256 << 20, hard))


def run(values, edges, operations, answers):
    last, pos, encoded = 0, 0, []
    for op, u, x in operations:
        encoded.append((op, (u + 1) ^ last, x ^ last))
        if op == 0:
            last = answers[pos]
            pos += 1
    assert pos == len(answers)
    data = f'{len(values)} {len(operations)}\n' + ' '.join(map(str, values)) + '\n'
    data += ''.join(f'{u + 1} {v + 1}\n' for u, v in edges)
    data += ''.join(f'{op} {u} {x}\n' for op, u, x in encoded)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=90)
    assert not result.stderr, result.stderr
    assert result.stdout.split() == list(map(str, answers))


rng = random.Random(6329302026)
for case in range(140):
    n = rng.randrange(1, 65)
    edges = [(rng.randrange(v), v) for v in range(1, n)]
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    distances = []
    for s in range(n):
        d = [-1] * n
        d[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in g[u]:
                if d[v] < 0:
                    d[v] = d[u] + 1
                    queue.append(v)
        distances.append(d)
    values = [rng.randrange(1, 10001) for _ in range(n)]
    current, operations, answers = values[:], [], []
    for step in range(350):
        u = rng.randrange(n)
        if step % 3 == 0:
            x = current[u] if step % 9 == 0 else rng.randrange(1, 10001)
            operations.append((1, u, x))
            current[u] = x
        else:
            k = rng.randrange(n)
            operations.append((0, u, k))
            answers.append(sum(x for v, x in enumerate(current) if distances[u][v] <= k))
    run(values, edges, operations, answers)

n = 100000
for shape in range(4):
    edges = [(v - 1 if shape == 0 else 0 if shape == 1 else (v - 1) // 2 if shape == 2 else rng.randrange(v), v) for v in range(1, n)]
    current, operations, answers = [10000] * n, [], []
    total = 10000 * n
    for step in range(n):
        u = rng.randrange(n)
        if step % 3 == 0:
            x = rng.randrange(1, 10001)
            operations.append((1, u, x))
            total += x - current[u]
            current[u] = x
        else:
            k = 0 if step % 3 == 1 else n - 1
            operations.append((0, u, k))
            answers.append(current[u] if k == 0 else total)
    run([10000] * n, edges, operations, answers)
print('CentroidSum copied P6329 driver PASS: 140 BFS-oracle and four n=m=100000 online-XOR inputs')
