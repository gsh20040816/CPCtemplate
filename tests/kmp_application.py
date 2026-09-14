"""P3375 adapter: independent direct matching and border enumeration."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root=Path(__file__).resolve().parents[1]
flags=['-std=c++20','-O2']
if os.environ.get('SANITIZE')=='1': flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined']
exe=root/'build/kmp-application'
subprocess.run([CXX,*flags,str(root/'verify/luogu/P3375.compact.cpp'),'-o',str(exe)],check=True)
def run(s,t,locations,borders):
    result=subprocess.run([str(exe)],input=s+'\n'+t+'\n',text=True,capture_output=True,check=True,timeout=30)
    assert not result.stderr,result.stderr
    lines=result.stdout.splitlines()
    assert len(lines)==len(locations)+1
    assert [int(x) for x in lines[:-1]]==locations
    assert list(map(int,lines[-1].split()))==borders
rng=random.Random(3375)
for _ in range(200):
    s=''.join(rng.choice('ABC') for _ in range(rng.randrange(1,60)))
    t=''.join(rng.choice('ABC') for _ in range(rng.randrange(1,25)))
    locations=[i+1 for i in range(len(s)-len(t)+1) if s[i:i+len(t)]==t]
    borders=[]
    for i in range(1,len(t)+1):
        borders.append(max(k for k in range(i) if t[:k]==t[i-k:i]))
    run(s,t,locations,borders)
n=1000000
run('A'*n,'A'*n,[1],list(range(n)))
run('A'*n,'B'*n,[],list(range(n)))
print('P3375: 200 direct-match/border oracles; both strings of length 1000000, match/no-match and output-line shape PASS')
