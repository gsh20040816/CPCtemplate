"""P4213 small exact oracle and maximum-input repeated-query consistency."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
exe = root / 'build/dujiao-application'
subprocess.run([CXX, *flags, str(root / 'verify/luogu/P4213.compact.cpp'), '-o', str(exe)], check=True)
n = 20000
mu, phi = [0], [0]
for x in range(1,n+1):
    v, m, f, p = x, 1, x, 2
    while p*p <= v:
        if v%p == 0:
            f = f//p*(p-1)
            count=0
            while v%p == 0:
                v//=p
                count+=1
            m = 0 if count>1 else -m
        p+=1
    if v>1:
        f=f//v*(v-1)
        m=-m
    mu.append(mu[-1]+m)
    phi.append(phi[-1]+f)
def run(a):
    result=subprocess.run([str(exe)], input=str(len(a))+'\n'+'\n'.join(map(str,a))+'\n', text=True, capture_output=True, check=True, timeout=60)
    assert not result.stderr, result.stderr
    values=[tuple(map(int,line.split())) for line in result.stdout.splitlines()]
    assert len(values)==len(a) and all(len(v)==2 for v in values)
    return values
rng=random.Random(4213)
for _ in range(30):
    a=[rng.randrange(1,n+1) for _ in range(10)]
    assert run(a)==[(phi[x],mu[x]) for x in a]
a=[2147483647]*10
out=run(a)
assert len(set(out))==1
p,m=out[0]
assert 1<=p<=a[0]*(a[0]+1)//2 and abs(m)<=a[0]
print('P4213: 30x10 trial-factor exact prefix queries PASS; ten maximum queries pass scale/bounds/repetition consistency (not independent large oracle)')
