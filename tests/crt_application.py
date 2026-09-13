"""P4777 full programs: independent Python exact arithmetic and planted systems."""
from compiler_config import CXX
from pathlib import Path
import math
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(4777)


def oracle(equations):
    r, period = 0, 1
    for modulus, residue in equations:
        g = math.gcd(period, modulus)
        assert (residue - r) % g == 0
        q = modulus // g
        step = ((residue - r) // g * pow(period // g, -1, q)) % q
        r += period * step
        period *= q
        r %= period
    return r


cases = [[(3, 2), (5, 3), (7, 2)], [(1, 10**12)],
         [(12, 11), (18, 17), (6, 5)],
         [(10**12, 10**12), (10**6, 0)]]
# Divisors of the same period guarantee the judge's LCM constraint.
for _ in range(180):
    divisors = [2**rng.randrange(13) * 3**rng.randrange(8) * 5**rng.randrange(7)
                for _ in range(rng.randrange(1, 60))]
    divisors = [m for m in divisors if m <= 10**12]
    x = rng.randrange(10**18)
    cases.append([(m, x % m) for m in divisors])
# Exact upper LCM bound: 10^12 and 10^6-1 are coprime, product just below 10^18.
cases.append([(10**12, 10**12-1), (999999, 999998)])
moduli = [2**a * 5**b for a in range(13) for b in range(13)
          if 2**a * 5**b <= 10**12]
x = 10**12 - 1
cases.append([(m, x % m) for m in (rng.choice(moduli) for _ in range(100000))])
for equations in cases:
    assert 1 <= len(equations) <= 100000
    assert all(1 <= m <= 10**12 and 0 <= b <= 10**12 for m, b in equations)
    assert math.lcm(*(m for m, _ in equations)) <= 10**18

for style in ['compact']:
    bundle = root / f'build/P4777.{style}.cpp'
    exe = root / f'build/P4777.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/luogu/P4777.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run([CXX, '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    for equations in cases:
        data = str(len(equations)) + '\n' + ''.join(f'{m} {b}\n' for m, b in equations)
        result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=10)
        assert result.stdout.strip() == str(oracle(equations))
    print(f'P4777 {style}: {len(cases)} consistent systems, Python exact oracle, noncoprime/repeated moduli, modulus one, near 1e18 LCM and n=100000 passed')
