from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE', os.environ.get('CPC_SANITIZE')) == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
exe = root / 'build/euler-power-application'
subprocess.run([CXX, *flags, str(root / 'verify/luogu/P5091.compact.cpp'), '-o', str(exe)], check=True)

def run(a, m, b, expected):
    data = f'{a} {m} {b}\n'
    out = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=120)
    assert not out.stderr, out.stderr
    assert int(out.stdout) == expected, (a, m, len(b), out.stdout, expected)

rng = random.Random(5091)
for t in range(200):
    a, m = rng.randrange(1, 10**9+1), rng.randrange(1, 10**8+1)
    b = str(rng.randrange(1, 10**100))
    run(a, m, b, pow(a, int(b), m))
for m in [1, 2, 4, 8, 12, 16, 36, 100, 99991]:
    for b in ['1', '2', '3', '4', '5', '000000000000000000001']:
        run(6, m, b, pow(6, int(b), m))
# Full statement limit: b=10^20000000 has 20000001 decimal digits.
run(2, 1 << 26, '1' + '0'*20000000, 0)
# Independent parity identity for a=-1 modulo m, not Euler reduction.
run(99999999, 100000000, '9'*20000000, 99999999)
# Many leading zeroes must not be mistaken for a large exponent.
run(2, 8, '0'*20000000 + '1', 2)
print('P5091: 200 Python pow oracles, noncoprime/leading-zero cases; 20000001-digit exponent, parity identity and long-small exponent PASS')
