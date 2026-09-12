"""Verify actual P6577 bundles, including the right-to-left output convention."""
import itertools
import random
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rng = random.Random(6577)
for style in ['compact']:
    source = root / f'build/P6577.{style}.cpp'
    exe = root / f'build/P6577.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P6577.{style}.cpp'), str(source)], check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(source), '-o', str(exe)], check=True)
    for trial in range(100):
        n = rng.randrange(1, 8)
        a = [[None] * n for _ in range(n)]
        edges = []
        for i in range(n):
            for j in range(n):
                if i == j or rng.randrange(2):
                    a[i][j] = rng.randrange(-19980731, 19980732)
                    edges.append((i + 1, j + 1, a[i][j]))
        best = None
        for p in itertools.permutations(range(n)):
            if all(a[p[j]][j] is not None for j in range(n)):
                weight = sum(a[p[j]][j] for j in range(n))
                best = weight if best is None else max(best, weight)
        data = f'{n} {len(edges)}\n'
        data += ''.join(f'{i} {j} {w}\n' for i, j, w in edges)
        result = subprocess.check_output([str(exe)], input=data.encode()).decode().split()
        assert len(result) == n + 1
        value = int(result[0])
        p = [int(x) - 1 for x in result[1:]]
        assert sorted(p) == list(range(n))
        assert all(a[p[j]][j] is not None for j in range(n))
        assert sum(a[p[j]][j] for j in range(n)) == value == best
    print(f'P6577 {style} bundled driver / permutation optimum and right-side output PASS')
