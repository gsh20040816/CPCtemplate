"""Verify input ordering, terminator, minimum solutions, and no-solution output."""
from compiler_config import CXX
from pathlib import Path
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(4195)
cases = [(1, 1, 1), (2, 8, 8), (4, 8, 2), (1, 17, 2)]
for _ in range(1000):
    cases.append((rng.randrange(1, 1000), rng.randrange(1, 300), rng.randrange(1, 1000)))
expected = []
for a, p, b in cases:
    first = {}
    value = 1 % p
    while value not in first:
        first[value] = len(first)
        value = value * a % p
    expected.append(str(first[b % p]) if b % p in first else 'No Solution')
text = ''.join(f'{a} {p} {b}\n' for a, p, b in cases) + '0 0 0\n'
for style in ['compact']:
    source = root / f'build/P4195.{style}.cpp'
    exe = root / f'build/P4195.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P4195.{style}.cpp'), str(source)], check=True)
    subprocess.run([CXX, '-std=c++20', '-O2', str(source), '-o', str(exe)], check=True)
    got = subprocess.check_output([str(exe)], input=text.encode()).decode().splitlines()
    assert got == expected
    assert subprocess.check_output([str(exe)], input=b'0 0 0\n') == b''
    print(f'P4195 {style} bundled driver / minimum exponents and input protocol PASS')
