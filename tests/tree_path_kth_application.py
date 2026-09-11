"""Test P2633 actual bundles, including online xor-last decoding."""
from pathlib import Path
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(2633)
cases = []
for trial in range(25):
    n = rng.randrange(1, 70)
    a = [rng.randrange(1, 1 << 31) for _ in range(n)]
    g = [[] for _ in range(n)]
    edges = []
    for v in range(1, n):
        u = rng.randrange(v)
        g[u].append(v)
        g[v].append(u)
        edges.append((u + 1, v + 1))
    last = 0
    lines = [f'{n} 100', ' '.join(map(str, a))]
    lines += [f'{u} {v}' for u, v in edges]
    expected = []
    for _ in range(100):
        u, v = rng.randrange(n), rng.randrange(n)
        parent = [-1] * n
        parent[u] = u
        queue = [u]
        for x in queue:
            for y in g[x]:
                if parent[y] == -1:
                    parent[y] = x
                    queue.append(y)
        values = [a[u]]
        x = v
        while x != u:
            values.append(a[x])
            x = parent[x]
        values.sort()
        k = rng.randrange(1, len(values) + 1)
        lines.append(f'{(u + 1) ^ last} {v + 1} {k}')
        last = values[k - 1]
        expected.append(last)
    cases.append(('\n'.join(lines) + '\n', expected))
for style in ['compact', 'classic']:
    source = root / f'build/P2633.{style}.cpp'
    exe = root / f'build/P2633.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P2633.{style}.cpp'), str(source)], check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(source), '-o', str(exe)], check=True)
    for text, expected in cases:
        got = list(map(int, subprocess.check_output([str(exe)], input=text.encode()).split()))
        assert got == expected
    print(f'P2633 {style} bundled driver / BFS sorted paths and xor-last protocol PASS')
