#!/usr/bin/env python3
import os
from pathlib import Path
import random
import shutil
import subprocess
root=Path(__file__).resolve().parents[1]
flags=['-std=c++20','-O2']
if os.environ.get('SANITIZE')=='1': flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined']
exe=root/'build/dynamic-batch-driver'
subprocess.run([os.environ.get('CXX') or shutil.which('g++-16') or 'g++',*flags,str(root/'verify/luogu/P5431.mint.compact.cpp'),'-o',str(exe)],check=True)
def check(text, expected):
 result=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True)
 assert result.stdout.strip()==str(expected)
 assert not result.stderr
rng=random.Random(36712)
for p in [3,17,257,998244353]:
 for n in [1,2,100,10000]:
  k=rng.randrange(2,p);a=[rng.randrange(1,p) for _ in range(n)]
  expected=sum(pow(k,i+1,p)*pow(x,-1,p) for i,x in enumerate(a))%p
  check(f'{n} {p} {k}\n'+' '.join(map(str,a))+'\n',expected)
n=5000000;p=998244353
# All denominators 3: closed-form geometric sum, independent of prefix products.
expected=(pow(2,n+1,p)-2)*pow(3,-1,p)%p
check(f'{n} {p} 2\n'+'3 '*n+'\n',expected)
print('Dynamic mint P5431 driver: Python inverse/power oracle and five-million geometric-sum case PASS')
