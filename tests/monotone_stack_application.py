"""Great City Saint Petersburg: full driver versus prefix/suffix envelopes."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess
root = Path(__file__).resolve().parents[1]
source = root / 'build/P12438.cpp'
exe = root / 'build/P12438'
subprocess.run(['python3', 'tools/bundle.py', 'verify/luogu/P12438.compact.cpp', str(source)], cwd=root, check=True)
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)

def water(a):
    left, right = [], [0]*len(a)
    h = a[0]
    for x in a:
        h = max(h, x)
        left.append(h)
    h = a[-1]
    for i in range(len(a)-1, -1, -1):
        h = max(h, a[i])
        right[i] = h
    return sum(min(left[i], right[i])-x for i, x in enumerate(a))

def check(a, ops, expected=None):
    data = f'{len(a)} {len(ops)}\n'+' '.join(map(str,a))+'\n'
    data += ''.join(f'{l+1} {r}\n' for l,r in ops)
    if expected is None:
        a = a[:]
        expected = [water(a)]
        for l,r in ops:
            for i in range(l,r):
                a[i] += 1
            expected.append(water(a))
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=120)
    assert not p.stderr, p.stderr
    assert list(map(int,p.stdout.split())) == expected

check([3,2,1,2,3], [(0,5),(1,4),(0,2),(4,5)], [4,4,1,1,3])
check([1,10**9,1,1,1,10**9,1], [(0,3),(3,5),(4,7)], [2999999997,2999999996,2999999994,2999999996])
rng = random.Random(12438)
for case in range(150):
    n = rng.randrange(1,80)
    a = [rng.randrange(1,10**9+1) for _ in range(n)]
    ops = []
    for _ in range(200):
        l,r = sorted((rng.randrange(n),rng.randrange(n)))
        ops.append((l,r+1))
    check(a,ops)
n = q = 200000
ops = [(0,n) if i % 2 else (1,n-1) for i in range(q)]
a = [10**9]+[1]*(n-2)+[10**9]
expected = [(10**9-1)*(n-2)]
for i in range(q):
    expected.append((10**9-1-(i+2)//2)*(n-2))
check(a,ops,expected)
print('P12438: two official samples, 150 random programs, n=q=200000 closed-form case PASS')
