from compiler_config import CXX
from pathlib import Path
import os
import subprocess

root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE', os.environ.get('CPC_SANITIZE')) == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
exe = root / 'build/min25-application'
subprocess.run([CXX, *flags, str(root / 'verify/luogu/P5325.compact.cpp'), '-o', str(exe)], check=True)
P = 1000000007
N = 100000
least = [0]*(N+1)
for p in range(2, N+1):
    if least[p] == 0:
        for x in range(p, N+1, p):
            if least[x] == 0:
                least[x] = p
pref = [0]*(N+1)
pref[1] = 1
for x in range(2, N+1):
    v, value = x, 1
    while v > 1:
        p, pe = least[v], 1
        while v % p == 0:
            v //= p
            pe *= p
        value = value*pe*(pe-1) % P
    pref[x] = (pref[x-1]+value) % P
for n in list(range(1, 101)) + [999, 1000, 1023, 1024, 1025, 99991, N]:
    out = subprocess.run([str(exe)], input=str(n)+'\n', text=True, capture_output=True, check=True, timeout=120)
    assert not out.stderr, out.stderr
    assert int(out.stdout) == pref[n]
print('P5325: 107 complete driver cases against independent prime-factor prefix through 100000 PASS')
