"""Check P4174 closure modeling against exhaustive station subsets."""
from compiler_config import CXX
from pathlib import Path
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(4174)
cases = []
for _ in range(40):
    n, m = rng.randrange(1, 9), rng.randrange(1, 20)
    cost = [rng.randrange(101) for _ in range(n)]
    users = [(rng.randrange(n), rng.randrange(n), rng.randrange(101)) for _ in range(m)]
    best = 0
    for mask in range(1 << n):
        profit = -sum(cost[i] for i in range(n) if mask >> i & 1)
        profit += sum(w for u, v, w in users if mask >> u & 1 and mask >> v & 1)
        best = max(best, profit)
    text = f'{n} {m}\n' + ' '.join(map(str, cost)) + '\n'
    text += ''.join(f'{u + 1} {v + 1} {w}\n' for u, v, w in users)
    cases.append((text, best))
for style in ['compact']:
    source = root / f'build/P4174.{style}.cpp'
    exe = root / f'build/P4174.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P4174.{style}.cpp'), str(source)], check=True)
    subprocess.run([CXX, '-std=c++20', '-O2', str(source), '-o', str(exe)], check=True)
    for text, expected in cases:
        got = int(subprocess.check_output([str(exe)], input=text.encode()))
        assert got == expected
    print(f'P4174 {style} bundled driver / exhaustive station-subset oracle PASS')
