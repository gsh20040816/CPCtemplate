"""P5656: independent small enumeration and modular-inverse large oracle."""
from compiler_config import CXX
from pathlib import Path
import math
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]

def brute(a, b, c):
    if c % math.gcd(a, b):
        return '-1'
    ps = [(x, (c - a * x) // b) for x in range(1, c // a + 1)
          if c - a * x > 0 and (c - a * x) % b == 0]
    if ps:
        return f'{len(ps)} {min(x for x,y in ps)} {min(y for x,y in ps)} {max(x for x,y in ps)} {max(y for x,y in ps)}'
    x = next(x for x in range(1, b + 1) if (c - a * x) % b == 0)
    y = next(y for y in range(1, a + 1) if (c - b * y) % a == 0)
    return f'{x} {y}'

def large(a, b, c):
    g = math.gcd(a, b)
    if c % g:
        return '-1'
    aa, bb, cc = a // g, b // g, c // g
    x0 = pow(aa, -1, bb) * cc % bb if bb > 1 else 0
    y0 = (c - a * x0) // b
    lo = (1 - x0 + bb - 1) // bb
    hi = (y0 - 1) // aa
    xmin = x0 + lo * bb
    ymin = y0 - hi * aa
    if lo > hi:
        return f'{xmin} {ymin}'
    return f'{hi-lo+1} {xmin} {ymin} {x0+hi*bb} {y0-lo*aa}'

cases = [(a,b,c) for a in range(1,21) for b in range(1,21) for c in range(1,51)]
expected = [brute(*case) for case in cases]
assert expected == [large(*case) for case in cases]
rng = random.Random(5656)
for _ in range(1000):
    case = tuple(rng.randint(1,10**9) for _ in range(3))
    cases.append(case)
    expected.append(large(*case))
fixtures = [(1,1,10**9), (10**9,10**9,1), (10**9,1,1),
            (999999937,999999929,10**9), (2,4,6), (2,4,1)]
while len(cases) < 200000:
    case = fixtures[len(cases) % len(fixtures)]
    cases.append(case)
    expected.append(large(*case))
data = str(len(cases)) + '\n' + ''.join(f'{a} {b} {c}\n' for a,b,c in cases)
for style in ['compact']:
    bundle = root / f'build/P5656.{style}.cpp'
    exe = root / f'build/P5656.{style}'
    subprocess.run(['python3','tools/bundle.py',f'verify/luogu/P5656.{style}.cpp',str(bundle)],cwd=root,check=True)
    flags = ['-O2']
    if os.environ.get('SANITIZE') == '1':
        flags = ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    subprocess.run([os.environ.get('CXX',CXX),'-std=c++20',*flags,str(bundle),'-o',str(exe)],check=True)
    result = subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=30)
    assert result.stdout.splitlines() == expected
    assert not result.stderr, result.stderr
    print(f'P5656 {style}: 200000 cases, exhaustive positive-solution counts/extrema and independent minimum-positive coordinates PASS')
