"""Check both biconnected output adapters on fixed multigraph certificates."""
from compiler_config import CXX
from pathlib import Path
import os
import subprocess

root = Path(__file__).resolve().parents[1]
flags = ['-O2'] if os.environ.get('SANITIZE') != '1' else ['-O1', '-g', '-fsanitize=address,undefined']
cases = [
    (1, [(1, 1)], [(1,)], [(1,)]),
    (8, [(1, 2), (2, 3), (3, 1), (3, 4), (4, 5), (4, 5), (6, 6)],
     [(1, 2, 3), (3, 4), (4, 5), (6,), (7,), (8,)],
     [(1, 2, 3), (4, 5), (6,), (7,), (8,)]),
    (6, [(i, i + 1) for i in range(1, 6)], [(i, i + 1) for i in range(1, 6)], [(i,) for i in range(1, 7)])
]
for index, problem in enumerate(['P8435', 'P8436']):
    bundle = root / f'build/{problem}-components.cpp'
    exe = root / f'build/{problem}-components'
    subprocess.run(['python3', str(root / 'tools/bundle.py'), str(root / f'verify/luogu/{problem}.compact.cpp'), str(bundle)], check=True)
    subprocess.run([CXX, '-std=c++20', *flags, str(bundle), '-o', str(exe)], check=True)
    for n, edges, point, edge in cases:
        data = f'{n} {len(edges)}\n' + ''.join(f'{u} {v}\n' for u, v in edges)
        result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
        assert not result.stderr, result.stderr
        lines = result.stdout.splitlines()
        assert int(lines[0]) == len(lines) - 1
        actual = []
        for line in lines[1:]:
            row = list(map(int, line.split()))
            assert row[0] == len(row) - 1 and len(set(row[1:])) == row[0]
            actual.append(tuple(sorted(row[1:])))
        assert sorted(actual) == sorted(point if index == 0 else edge), (problem, data, actual)
print('Biconnected drivers: point/edge block output certificates, parallel edges, loops, isolated vertices and bridge chain PASS')
