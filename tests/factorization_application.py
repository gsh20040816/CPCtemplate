"""Factorization drivers: trial-certified factors, maximum-sized hard batch."""
from pathlib import Path
import math
import os
import subprocess
import time
root = Path(__file__).resolve().parents[1]

def prime(n):
    return n >= 2 and all(n % d for d in range(2,math.isqrt(n)+1))

fixtures = [(2,), (3,), (999999937,), (999999929,), (999999937,999999929),
            (999999937,999999937), (999999929,999999929),
            (151,751,28351), (2,)*59, (3,)*37]
assert all(prime(p) for fs in fixtures for p in set(fs))
for style in ['compact','classic']:
    for judge,pid,end,limit in [('luogu','P4718',max,10**18),('poj','1811',min,2**54-1)]:
        options = [fs for fs in fixtures if math.prod(fs) <= limit]
        if pid == '1811':
            small = (100000007,100000037)
            assert all(prime(p) for p in small)
            options.append(small)
        cases = [options[i % len(options)] for i in range(350)]
        if pid == 'P4718':
            cases = [fixtures[4 + i % 3] for i in range(300)] + cases[:50]
        expected = ['Prime' if len(fs)==1 else str(end(fs)) for fs in cases]
        data = '350\n' + ''.join(str(math.prod(fs))+'\n' for fs in cases)
        bundle = root / f'build/{pid}.{style}.cpp'
        exe = root / f'build/{pid}.{style}'
        subprocess.run(['python3','tools/bundle.py',f'verify/{judge}/{pid}.{style}.cpp',str(bundle)],cwd=root,check=True)
        flags = ['-O2']
        if os.environ.get('SANITIZE') == '1':
            flags = ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
        subprocess.run([os.environ.get('CXX','/opt/homebrew/bin/g++-16'),'-std=c++20',*flags,str(bundle),'-o',str(exe)],check=True)
        start = time.perf_counter()
        result = subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=120)
        elapsed = time.perf_counter()-start
        assert result.stdout.splitlines() == expected
        assert not result.stderr, result.stderr
        print(f'{pid} {style}: 350 trial-certified cases, prime labels and factor extrema PASS; local elapsed {elapsed:.3f}s',flush=True)
