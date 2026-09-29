"""Independent full SAM occurrence and integer-SA common-substring programs."""
from compiler_config import CXX
from pathlib import Path
from collections import Counter
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(83215)
mode = 'san' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-std=c++20', '-O2'] if mode == 'normal' else ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
exes = {}
for name, driver in [('sam','verify/luogu/P3804.compact.cpp'), ('lcs','verify/library_checker/longest_common_substring.compact.cpp')]:
    exe = root / f'build/suffix-attachment-{name}-{mode}'
    subprocess.run([CXX,*flags,str(root/driver),'-o',str(exe)],check=True)
    exes[name] = exe


def run(name, text):
    p = subprocess.run([str(exes[name])],input=text,text=True,capture_output=True,check=True,timeout=90)
    assert not p.stderr,p.stderr
    return list(map(int,p.stdout.split()))


for _ in range(200):
    s = ''.join(rng.choice('abcdez') for _ in range(rng.randint(1,65)))
    counts = Counter(s[l:r] for l in range(len(s)) for r in range(l+1,len(s)+1))
    expected = max([0] + [len(x)*c for x,c in counts.items() if c>1])
    assert run('sam',s+'\n') == [expected]
    t = ''.join(rng.choice('abcdef') for _ in range(rng.randint(1,65)))
    common = set(counts) & {t[l:r] for l in range(len(t)) for r in range(l+1,len(t)+1)}
    expected = max(map(len,common),default=0)
    a,b,c,d = run('lcs',s+'\n'+t+'\n')
    assert 0<=a<=b<=len(s) and 0<=c<=d<=len(t)
    assert s[a:b] == t[c:d] and b-a == expected
print('P3804 / integer-SA LCS: each 200 independent substring frequency/set oracles and output interval certificates PASS',flush=True)
n = 1000000
assert run('sam','a'*n+'\n') == [((n+1)*(n+1))//4]
# Alternating strings: count a length-L word from each valid starting parity independently.
expected = max(L*((n-L)//2+1) for L in range(1,n+1) if (n-L)//2+1>1)
assert run('sam','ab'*(n//2)+'\n') == [expected]
assert run('sam','abcdefghijklmnopqrstuvwxyz\n') == [0]
print('P3804: million-letter equal/alternating closed forms, 64-bit answer and no-repeat zero PASS',flush=True)
n = 500000
for s,t,expected in [('a'*n,'a'*n,n),('a'*n,'b'*n,0),('ab'*(n//2),'ba'*(n//2),n-1)]:
    a,b,c,d = run('lcs',s+'\n'+t+'\n')
    assert 0<=a<=b<=n and 0<=c<=d<=n and b-a==expected and s[a:b]==t[c:d]
print('Integer-SA LCS: two 500000-letter strings, equal/disjoint/shifted alternation interval certificates PASS',flush=True)
