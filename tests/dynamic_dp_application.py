#!/usr/bin/env python3
"""P4719 full driver versus an independent per-query tree DP; maximum-size chain and star timing."""
import os
import random
import subprocess
import time
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
exe = root / 'build/P4719'
flags = ['-std=c++20', '-O2']
if os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
if os.uname().sysname == 'Darwin':
    flags.append('-Wl,-stack_size,0x20000000')
subprocess.run([CXX, *flags, str(root / 'verify/luogu/P4719.compact.cpp'), '-o', str(exe)], check=True)


def brute(n, w, edges):
    g = [[] for _ in range(n + 1)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    order, fa = [1], [0] * (n + 1)
    for u in order:
        for v in g[u]:
            if v != fa[u]:
                fa[v] = u
                order.append(v)
    f0, f1 = [0] * (n + 1), [0] * (n + 1)
    for u in reversed(order):
        f1[u] += w[u]
        if fa[u]:
            f0[fa[u]] += max(f0[u], f1[u])
            f1[fa[u]] += f0[u]
    return max(f0[1], f1[1])


rng = random.Random(4719)
for case in range(300):
    n = rng.randint(1, 25)
    m = rng.randint(1, 25)
    w = [0] + [rng.randint(-100, 100) for _ in range(n)]
    edges = [(rng.randint(1, v - 1), v) for v in range(2, n + 1)]
    ops = [(rng.randint(1, n), rng.randint(-100, 100)) for _ in range(m)]
    text = f'{n} {m}\n' + ' '.join(map(str, w[1:])) + '\n' + ''.join(f'{u} {v}\n' for u, v in edges)
    text += ''.join(f'{x} {y}\n' for x, y in ops)
    out = subprocess.run([str(exe)], input=text, capture_output=True, text=True, check=True).stdout.split()
    want = []
    for x, y in ops:
        w[x] = y
        want.append(str(brute(n, w, edges)))
    assert out == want, case

n = m = 100000
for name, edges in [('chain', [(i, i + 1) for i in range(1, n)]), ('star', [(1, i) for i in range(2, n + 1)])]:
    w = [rng.randint(-100, 100) for _ in range(n)]
    ops = [(rng.randint(1, n), rng.randint(-100, 100)) for _ in range(m)]
    text = f'{n} {m}\n' + ' '.join(map(str, w)) + '\n' + ''.join(f'{u} {v}\n' for u, v in edges)
    text += ''.join(f'{x} {y}\n' for x, y in ops)
    start = time.monotonic()
    out = subprocess.run([str(exe)], input=text, capture_output=True, text=True, check=True).stdout.split()
    assert len(out) == m and time.monotonic() - start < 2, name
print('P4719 driver: 300 random trees vs per-query tree DP, 1e5 chain and star within 2s PASS', flush=True)
