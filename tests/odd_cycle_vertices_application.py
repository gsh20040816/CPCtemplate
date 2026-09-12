"""POJ2942 complement-graph driver versus enumeration of simple odd cycles."""
from pathlib import Path
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(2942)

def oracle(n, hate):
    bad = {tuple(sorted(e)) for e in hate}
    g = [[False] * n for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            g[u][v] = g[v][u] = (u + 1, v + 1) not in bad
    marked = set()
    def visit(start, u, path, used):
        if len(path) >= 3 and len(path) % 2 and g[u][start]:
            marked.update(path)
        for v in range(start + 1, n):
            if g[u][v] and v not in used:
                visit(start, v, path + [v], used | {v})
    for s in range(n):
        visit(s, s, [s], {s})
    return n - len(marked)

cases = []
for _ in range(100):
    n = rng.randrange(1, 8)
    hate = [(u, v) for u in range(1, n + 1) for v in range(u + 1, n + 1) if rng.randrange(2)]
    cases.append((n, hate, oracle(n, hate)))
n = 1000
cases += [(n, [], 0),
          (n, [(u, v) for u in range(1, n + 1) for v in range(u + 1, n + 1)], n),
          (n, [(u, v) for u in range(1, n + 1) for v in range(u + 1, n + 1) if (u <= 500) == (v <= 500)], n)]
allowed = {(1, 2), (1, 3), (2, 3)} | {(u - 1, u) for u in range(4, n + 1)}
cases.append((n, [(u, v) for u in range(1, n + 1) for v in range(u + 1, n + 1) if (u, v) not in allowed], n - 3))
data = ''
expected = []
for n, hate, answer in cases:
    data += f'{n} {len(hate)}\n' + ''.join(f'{u} {v}\n' for u, v in hate)
    expected.append(answer)
data += '0 0\n'
for style in ['compact']:
    bundle = root / f'build/poj2942.{style}.cpp'
    exe = root / f'build/poj2942.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/poj/2942.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=20)
    assert list(map(int, result.stdout.split())) == expected
    print(f'POJ2942 {style}: {len(cases)} datasets, complement construction/simple-cycle oracle, n=1000 complete/bipartite/sparse graphs passed')
