"""Attachment input adapter, checked by explicit paths after every update."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(108)
mod = 998244353
source = root / 'build/tree-path-products-driver.cpp'
exe = root / 'build/tree-path-products-driver'
subprocess.run(['python3', 'tools/bundle.py',
                'verify/examples/tree_path_products.compact.cpp', str(source)],
               cwd=root, check=True)
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)
for case in range(150):
    n = rng.randrange(1, 30)
    g = [[] for _ in range(n)]
    edges = []
    for u in range(1, n):
        v = rng.randrange(u)
        g[u].append(v)
        g[v].append(u)
        edges.append((u, v))
    x = [rng.choice([0, 1, 2, mod-1, rng.randrange(mod)]) for _ in range(n)]
    lines = [f'{n} 100', ' '.join(map(str, x))]
    lines += [f'{u+1} {v+1}' for u, v in edges]
    expected = []
    def dfs(u, parent, product):
        product = product * (1-x[u]) % mod
        return (product + sum(dfs(v, u, product) for v in g[u] if v != parent)) % mod
    for step in range(100):
        u = rng.randrange(n)
        if step % 3 == 0:
            x[u] = rng.randrange(mod)
            lines.append(f'1 {u+1} {x[u]}')
        else:
            lines.append(f'2 {u+1}')
            expected.append(dfs(u, -1, 1))
    run = subprocess.run([str(exe)], input='\n'.join(lines)+'\n', text=True,
                         capture_output=True, check=True, timeout=30)
    assert not run.stderr, run.stderr
    assert list(map(int, run.stdout.split())) == expected
print('TreePathProducts attachment driver: 150 trees, 15000 operations, 1-based vertices and 1-x conversion PASS')
