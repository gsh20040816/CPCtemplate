from compiler_config import CXX
from pathlib import Path
import math
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE', os.environ.get('CPC_SANITIZE')) == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
exe = root / 'build/matrix-inverse-application'
subprocess.run([CXX, *flags, str(root / 'verify/luogu/P4783.compact.cpp'), '-o', str(exe)], check=True)
P = 1000000007

def run(a, expected):
    data = str(len(a)) + '\n' + '\n'.join(' '.join(map(str, row)) for row in a) + '\n'
    out = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=120)
    assert not out.stderr, out.stderr
    want = ['No', 'Solution'] if expected is None else [str(x) for row in expected for x in row]
    assert out.stdout.split() == want

rng = random.Random(4783)
for n in [1, 2, 7, 40, 400]:
    # Pascal matrix has inverse (-1)^(i-j) binom(i,j); independently known identity.
    a = [[math.comb(i, j) % P if j <= i else 0 for j in range(n)] for i in range(n)]
    inv = [[((-1)**(i-j) * math.comb(i, j)) % P if j <= i else 0 for j in range(n)] for i in range(n)]
    perm = list(range(n))
    rng.shuffle(perm)
    b = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            b[i][j] = inv[i][perm[j]]
    run([a[i] for i in perm], b)
    if n > 1:
        a[0] = a[-1][:]
        run(a, None)
run([[0]], None)
print('P4783: shuffled Pascal/inverse-binomial certificates through n=400, row swaps and singular variants PASS')
