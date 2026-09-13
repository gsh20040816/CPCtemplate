"""P5431: independent individual inverse oracle and full-size geometric sums."""
from compiler_config import CXX
from pathlib import Path
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(5431)
cases = []
for _ in range(80):
    p = rng.choice([3, 7, 101, 1000003, 998244353])
    k = rng.randrange(2, p)
    a = [rng.randrange(1, p) for _ in range(rng.randrange(1, 250))]
    want = sum(pow(k, i, p) * pow(x, -1, p) for i, x in enumerate(a, 1)) % p
    cases.append((f'{len(a)} {p} {k}\n' + ' '.join(map(str,a)) + '\n', want))
for style in ['compact']:
    bundle = root / f'build/P5431.{style}.cpp'
    exe = root / f'build/P5431.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/luogu/P5431.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run([CXX, '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    for data, want in cases:
        result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=5)
        assert result.stdout.strip() == str(want)
    n, p, k = 5000000, 998244353, 2
    for value in [1, p-1]:
        data = f'{n} {p} {k}\n' + (str(value)+' ') * n + '\n'
        want = (pow(k,n+1,p)-k) * pow(k-1,-1,p) * pow(value,-1,p) % p
        result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=20)
        assert result.stdout.strip() == str(want)
    print(f'P5431 {style}: 80 individual-inverse cases and two n=5000000 geometric-sum cases PASS')
