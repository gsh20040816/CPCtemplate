"""P6091 full output checked independently with modular exponent tests."""
from pathlib import Path
import math
import subprocess
root = Path(__file__).resolve().parents[1]

def oracle(n):
    phi = sum(math.gcd(a, n) == 1 for a in range(1, n))
    factors = []
    x = phi
    d = 2
    while d * d <= x:
        if x % d == 0:
            factors.append(d)
            while x % d == 0:
                x //= d
        d += 1
    if x > 1:
        factors.append(x)
    return [g for g in range(1, n) if math.gcd(g, n) == 1
            and all(pow(g, phi // q, n) != 1 for q in factors)]

cases = [(n, 1 + n % 20) for n in range(2, 122)]
cases += [(999983, 200), (1000000, 200), (531441, 200), (524288, 200)]
expected = []
for n, d in cases:
    roots = oracle(n)
    expected.append([str(len(roots)), ' '.join(map(str, roots[d-1::d]))])
for style in ['compact']:
    bundle = root / f'build/P6091.{style}.cpp'
    exe = root / f'build/P6091.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/luogu/P6091.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    for begin in range(0, len(cases), 10):
        group = cases[begin:begin+10]
        data = str(len(group)) + '\n' + ''.join(f'{n} {d}\n' for n, d in group)
        result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=20)
        want = [line for pair in expected[begin:begin+10] for line in pair]
        assert result.stdout.splitlines() == want
    print(f'P6091 {style}: 124 cases, independent candidate scan, sorted sampling, empty lines, prime powers and n=1000000 PASS')
