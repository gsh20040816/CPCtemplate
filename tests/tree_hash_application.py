#!/usr/bin/env python3
"""UOJ #763 full driver versus independent AHU canonical counting; million-vertex chain and star."""
import os
import random
import subprocess
import sys
import time
from pathlib import Path
from compiler_config import CXX

sys.setrecursionlimit(10000)
root = Path(__file__).resolve().parents[1]
exe = root / 'build/uoj763'
flags = ['-std=c++20', '-O2']
if os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
subprocess.run([CXX, *flags, str(root / 'verify/uoj/763.compact.cpp'), '-o', str(exe)], check=True)


def run(text):
    return subprocess.run([str(exe)], input=text, capture_output=True, text=True, check=True).stdout.split()


def oracle(n, edges):
    g = [[] for _ in range(n + 1)]
    for a, b in edges:
        g[a].append(b)
        g[b].append(a)
    forms = set()

    def canon(u, p):
        s = '(' + ''.join(sorted(canon(v, u) for v in g[u] if v != p)) + ')'
        forms.add(s)
        return s

    canon(1, 0)
    return len(forms)


def encode(n, edges):
    return f'{n}\n' + ''.join(f'{a} {b}\n' for a, b in edges)


assert run(encode(10, [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7), (3, 8), (8, 9), (8, 10)])) == ['4']
rng = random.Random(763)
for case in range(400):
    n = rng.randint(1, 60)
    perm = list(range(1, n + 1))
    rng.shuffle(perm)
    edges = []
    for v in range(2, n + 1):
        u = rng.randint(max(1, v - rng.choice([1, 3, v])), v - 1)
        edges.append((perm[u - 1], perm[v - 1]))
    rng.shuffle(edges)
    edges = [(b, a) if rng.random() < 0.5 else (a, b) for a, b in edges]
    # the problem roots the tree at vertex 1
    assert run(encode(n, edges)) == [str(oracle(n, edges))], (case, n)

n = 1000000
for name, edges, want in [('chain', [(i, i + 1) for i in range(1, n)], n),
                          ('star', [(1, i) for i in range(2, n + 1)], 2)]:
    start = time.monotonic()
    assert run(encode(n, edges)) == [str(want)], name
    elapsed = time.monotonic() - start
    assert elapsed < 5, (name, elapsed)
print('UOJ763 driver: official sample, 400 random relabelled trees vs AHU canonical forms, '
      'million-vertex chain and star within 5s PASS', flush=True)
