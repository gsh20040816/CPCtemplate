"""P3807 dual programs checked against Python exact binomial coefficients."""
from pathlib import Path
import math
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(3807)
cases = [(rng.randrange(1, 1001), rng.randrange(1, 1001), rng.choice([2, 3, 5, 7, 97, 997])) for _ in range(70)]
cases += [(100000, 100000, p) for p in [2, 3, 5, 7, 97, 997, 99991]]
cases += [(1, 100000, 99991), (99990, 1, 99991), (99991, 99991, 99991)]
expected = [str(math.comb(n + m, n) % p) for n, m, p in cases]
for style in ['compact', 'classic']:
    bundle = root / f'build/P3807.{style}.cpp'
    exe = root / f'build/P3807.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/luogu/P3807.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    for begin in range(0, len(cases), 10):
        group = cases[begin:begin+10]
        data = str(len(group)) + '\n' + ''.join(f'{n} {m} {p}\n' for n, m, p in group)
        result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=10)
        assert result.stdout.splitlines() == expected[begin:begin+10]
    print(f'P3807 {style}: 80 exact Python binomial cases, changing moduli, n=m=100000 and base-p carries PASS')
