"""P4097 encrypted input against exact Fraction segment scan."""
from compiler_config import CXX
from pathlib import Path
from fractions import Fraction
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
exe = root / 'build/segment-li-chao-application'
subprocess.run([CXX, *flags, str(root / 'verify/luogu/P4097.compact.cpp'), '-o', str(exe)], check=True)
def run(ops, expected):
    result = subprocess.run([str(exe)], input=str(len(ops))+'\n'+'\n'.join(ops)+'\n', text=True, capture_output=True, check=True, timeout=30)
    assert not result.stderr, result.stderr
    assert list(map(int, result.stdout.split())) == expected
rng = random.Random(4097)
for trial in range(100):
    lines, ops, expected, last = [], [], [], 0
    def encode(value, mod):
        return (value - last - 1) % mod + 1
    for i in range(300):
        if rng.randrange(3) == 0:
            x = rng.randrange(1, 31)
            ops.append(f'0 {encode(x, 39989)}')
            best, answer = None, 0
            for j, (a,b,c,d) in enumerate(lines, 1):
                if a <= x <= c:
                    y = Fraction(max(b,d)) if a == c else Fraction(b*(c-x)+d*(x-a), c-a)
                    if best is None or y > best:
                        best, answer = y, j
            expected.append(answer)
            last = answer
        else:
            a,c = rng.randrange(1,31),rng.randrange(1,31)
            b,d = rng.randrange(1,50),rng.randrange(1,50)
            if lines and rng.randrange(5) == 0:
                a,b,c,d = rng.choice(lines)
            ops.append(f'1 {encode(a,39989)} {encode(b,10**9)} {encode(c,39989)} {encode(d,10**9)}')
            if a > c: a,b,c,d = c,d,a,b
            lines.append((a,b,c,d))
    run(ops, expected)
ops, expected, last = [], [], 0
for i in range(1,50001):
    enc = lambda x,m: (x-last-1)%m+1
    ops.append(f'1 {enc(1,39989)} {enc(i,10**9)} {enc(39989,39989)} {enc(i,10**9)}')
    ops.append(f'0 {enc(20000,39989)}')
    expected.append(i)
    last=i
run(ops,expected)
print('P4097: 100x300 encrypted Fraction-oracle operations, ties/vertical/reversed/no-hit, 100000-operation scale PASS')
