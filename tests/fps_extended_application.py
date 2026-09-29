"""Luogu division/sqrt complete programs versus independent coefficient oracles."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess
root = Path(__file__).resolve().parents[1]
p = 998244353
rng = random.Random(45125205)
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
for problem in ['P4512', 'P5205']:
    source = root / f'build/{problem}.cpp'
    exe = root / f'build/{problem}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/luogu/{problem}.compact.cpp', str(source)], cwd=root, check=True)
    subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)
    def check(data, want):
        run = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=120)
        assert not run.stderr, run.stderr
        assert list(map(int, run.stdout.split())) == want, problem
    if problem == 'P4512':
        for _ in range(150):
            n = rng.randrange(1, 80)
            m = rng.randrange(1, n + 1)
            a = [rng.randrange(p) for _ in range(n)] + [rng.randrange(1, p)]
            b = [rng.randrange(p) for _ in range(m)] + [rng.randrange(1, p)]
            rem = a[:]
            q = [0] * (n - m + 1)
            iv = pow(b[-1], p - 2, p)
            for i in range(n - m, -1, -1):
                q[i] = rem[i+m] * iv % p
                for j, x in enumerate(b):
                    rem[i+j] = (rem[i+j] - q[i]*x) % p
            data = f'{n} {m}\n' + ' '.join(map(str, a)) + '\n' + ' '.join(map(str, b)) + '\n'
            check(data, q + rem[:m])
        n, m = 100000, 50000
        q = [(i*i+17) % p for i in range(n-m+1)]
        rem = [(7*i+9) % p for i in range(m)]
        a = rem + [0] * (n+1-m)
        for i, x in enumerate(q):
            a[i] = (a[i]+x) % p
            a[i+m] = (a[i+m]+x) % p
        b = [1] + [0]*(m-1) + [1]
        check(f'{n} {m}\n'+' '.join(map(str,a))+'\n'+' '.join(map(str,b))+'\n', q+rem)
    else:
        for trial in range(150):
            n = 1 if trial == 0 else rng.randrange(2, 100)
            a = [1] + [rng.randrange(p) for _ in range(n-1)]
            b = [1] + [0]*(n-1)
            for i in range(1, n):
                b[i] = (a[i]-sum(b[j]*b[i-j] for j in range(1,i))) * ((p+1)//2) % p
            check(f'{n}\n'+' '.join(map(str,a))+'\n', b)
        n = 100000
        check(f'{n}\n'+' '.join(str(i+1) for i in range(n))+'\n', [1]*n)
    print(f'{problem}: 150 independent quadratic-oracle programs and a 100000-scale closed form PASS')
