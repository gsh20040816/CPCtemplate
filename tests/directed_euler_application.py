"""P7771 complete programs compared with exhaustive lexicographic trail search."""
from pathlib import Path
import subprocess
import random

root = Path(__file__).resolve().parents[1]
rng = random.Random(7771)

def brute(n, edges):
    best = None
    def visit(u, mask, path):
        nonlocal best
        if mask == (1 << len(edges)) - 1:
            if best is None or path < best:
                best = path[:]
            return
        for i, (a, b) in enumerate(edges):
            if not (mask >> i & 1) and a == u:
                visit(b, mask | (1 << i), path + [b])
    for u in range(1, n + 1):
        visit(u, 0, [u])
    return best

cases = []
for _ in range(100):
    n = rng.randrange(1, 7)
    edges = [(rng.randrange(1, n + 1), rng.randrange(1, n + 1)) for _ in range(rng.randrange(8))]
    cases.append((n, edges, brute(n, edges)))
n = 100000
edges = [(u, u + 1) for u in range(1, n)] + [(u + 1, u) for u in range(1, n)]
rng.shuffle(edges)
cases.append((n, edges, list(range(1, n + 1)) + list(range(n - 1, 0, -1))))
cases.append((2, [(1, 2)] * 200000, None))
for style in ['compact']:
    name = f'P7771.{style}'
    bundle = root / f'build/{name}.cpp'
    obj = root / f'build/{name}.o'
    exe = root / f'build/{name}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/luogu/{name}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', '-Dmain=cpc_entry', '-c', str(bundle), '-o', str(obj)], check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', '-pthread', str(obj), 'tests/driver_stack.cpp', '-o', str(exe)], cwd=root, check=True)
    for n, edges, expected in cases:
        data = f'{n} {len(edges)}\n' + ''.join(f'{u} {v}\n' for u, v in edges)
        result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=15).stdout
        if expected is None:
            assert result.split() == ['No']
        else:
            assert list(map(int, result.split())) == expected
    print(f'P7771 {style}: 102 cases, exhaustive trail oracle, n=100000 and m=200000 passed; local 256MB recursive driver stack')
