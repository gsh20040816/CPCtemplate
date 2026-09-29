"""P4721 complete programs versus quadratic DP and closed-form kernels."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess
root = Path(__file__).resolve().parents[1]
source = root / 'build/P4721.cpp'
exe = root / 'build/P4721'
subprocess.run(['python3','tools/bundle.py','verify/luogu/P4721.compact.cpp',str(source)],cwd=root,check=True)
flags = ['-std=c++20','-O2']
if os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
subprocess.run([CXX,*flags,str(source),'-o',str(exe)],check=True)
p = 998244353
rng = random.Random(4721115)

def check(g, expected=None):
    n = len(g)
    if expected is None:
        expected = [1]+[0]*(n-1)
        for i in range(1,n):
            expected[i] = sum(expected[j]*g[i-j] for j in range(i)) % p
    data = f'{n}\n'+' '.join(map(str,g[1:]))+'\n'
    run = subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=120)
    assert not run.stderr, run.stderr
    assert list(map(int,run.stdout.split())) == expected

for _ in range(150):
    n = rng.randrange(2,100)
    check([0]+[rng.randrange(p) for _ in range(n-1)])
n = 100000
check([0]*n,[1]+[0]*(n-1))
check([0]+[1]*(n-1),[1]+[pow(2,i-1,p) for i in range(1,n)])
check([0]+[2*pow(3,i-1,p)%p for i in range(1,n)], [1]+[2*pow(5,i-1,p)%p for i in range(1,n)])
g = [0]*n
g[7] = 1
check(g,[int(i%7==0) for i in range(n)])
print('P4721: 150 quadratic-DP programs and four n=100000 zero/all-one/geometric/sparse closed forms PASS')
