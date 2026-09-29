"""P4887 full driver; direct pair enumeration and closed-form large cases."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess
root = Path(__file__).resolve().parents[1]
source = root / 'build/P4887.cpp'
exe = root / 'build/P4887'
subprocess.run(['python3', 'tools/bundle.py', 'verify/luogu/P4887.compact.cpp', str(source)], cwd=root, check=True)
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)
rng = random.Random(4887111)

def check(a, queries, k, expected=None):
    data = f'{len(a)} {len(queries)} {k}\n' + ' '.join(map(str, a))+'\n'
    data += ''.join(f'{l+1} {r}\n' for l, r in queries)
    if expected is None:
        expected = [sum(bin(a[i]^a[j]).count('1') == k for i in range(l, r) for j in range(i+1, r)) for l, r in queries]
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=120)
    assert not p.stderr, p.stderr
    assert list(map(int, p.stdout.split())) == expected

for t in range(150):
    n = rng.randrange(1, 50)
    a = [rng.randrange(1<<14) for _ in range(n)]
    if t % 3 == 0:
        a = [x % 8 for x in a]
    queries = []
    for _ in range(70):
        l, r = sorted((rng.randrange(n), rng.randrange(n)))
        queries.append((l, r+1))
    check(a, queries, [0, 1, 7, 14, 15, 16383][t % 6])
n = 100000
queries = [(0, n)] + [(i, n) for i in range(1, n)]
check([16383]*n, queries, 0, [(r-l)*(r-l-1)//2 for l, r in queries])
a = [127 if i % 2 else 0 for i in range(n)]
check(a, queries, 7, [(r//2-l//2)*(r-l-(r//2-l//2)) for l, r in queries])
check(a, queries, 16383, [0]*n)
print('P4887: 153 programs; direct pair oracle, k=0/7/14/out-of-range, n=m=100000 PASS')
