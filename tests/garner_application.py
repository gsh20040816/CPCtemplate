"""P1495 full-program tests, direct exact CRT formula as oracle."""
from pathlib import Path
import math
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(1495)
cases = [[(3, 1), (5, 1), (7, 2)], [(1, 0)]]
for _ in range(150):
    m = []
    for _ in range(10):
        x = rng.randrange(1, 100001)
        if math.gcd(x, math.prod(m)) == 1 and math.prod(m) * x <= 10**18:
            m.append(x)
    cases.append([(x, rng.randrange(x)) for x in m])
for style in ['compact']:
    bundle = root / f'build/P1495.{style}.cpp'
    exe = root / f'build/P1495.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/luogu/P1495.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    for equations in cases:
        period = math.prod(m for m, _ in equations)
        expected = sum(b * (period // m) * pow(period // m, -1, m) for m, b in equations) % period
        data = str(len(equations)) + '\n' + ''.join(f'{m} {b}\n' for m, b in equations)
        result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=5)
        assert result.stdout.strip() == str(expected)
    print(f'P1495 {style}: {len(cases)} direct big-integer CRT cases, sample, modulus one and full judge constraints PASS')
