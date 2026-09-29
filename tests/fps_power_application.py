"""Complete power drivers, independent truncated multiplication and binomials."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess
root = Path(__file__).resolve().parents[1]
p = 998244353
rng = random.Random(52455273)
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']

def multiply(a, b, n):
    c = [0]*n
    for i, x in enumerate(a):
        for j in range(min(len(b), n-i)):
            c[i+j] = (c[i+j]+x*b[j]) % p
    return c

def slow(a, k):
    n = len(a)
    b = [1]+[0]*(n-1)
    while k:
        if k & 1:
            b = multiply(b, a, n)
        a = multiply(a, a, n)
        k >>= 1
    return b

for name, path in [('P5245','luogu/P5245'), ('P5273','luogu/P5273'), ('LC power','library_checker/pow_of_formal_power_series')]:
    source = root / f'build/power-{Path(path).name}.cpp'
    exe = source.with_suffix('')
    subprocess.run(['python3','tools/bundle.py',f'verify/{path}.compact.cpp',str(source)],cwd=root,check=True)
    subprocess.run([CXX,*flags,str(source),'-o',str(exe)],check=True)
    def check(a, k, want):
        data = f'{len(a)} {k}\n'+' '.join(map(str,a))+'\n'
        run = subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=120)
        assert not run.stderr, run.stderr
        assert list(map(int,run.stdout.split())) == want, (name,len(a),str(k)[:30])
    for trial in range(100):
        n = rng.randrange(2,45)
        a = [rng.randrange(p) for _ in range(n)]
        if name == 'P5245':
            a[0] = 1
        elif trial % 3 == 0:
            prefix = rng.randrange(n+1)
            a[:prefix] = [0]*prefix
        k = rng.randrange(1 if name == 'P5245' else 0, 10)
        if trial % 10 == 0:
            k = [p-1,p,p+1,10**18][trial//10 % 4]
        check(a, str(k), slow(a,k))
    n = 500000 if name == 'LC power' else 100000
    if name == 'LC power':
        exponent = str(10**18)
        km = 10**18 % p
        phi = 10**18 % (p-1)
    else:
        exponent = '1'+'0'*100000
        km = pow(10,100000,p)
        phi = pow(10,100000,p-1)
    leading = 1 if name == 'P5245' else 3
    a = [leading,leading]+[0]*(n-2)
    inv = [0]*n
    inv[1] = 1
    for i in range(2,n):
        inv[i] = (p-p//i)*inv[p%i] % p
    want = [pow(leading,phi,p)]
    for i in range(1,n):
        want.append(want[-1]*(km-i+1)*inv[i] % p)
    check(a,exponent,want)
    print(f'{name}: 100 binary-convolution oracle programs and n={n} binomial with {len(exponent)}-digit exponent PASS')
