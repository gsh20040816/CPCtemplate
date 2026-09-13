#!/usr/bin/env python3
import os
from pathlib import Path
import random
import shutil
import subprocess
root=Path(__file__).resolve().parents[1]
flags=['-std=c++20','-O2']
if os.environ.get('SANITIZE')=='1':flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined']
exe=root/'build/lazy-affine'
subprocess.run([os.environ.get('CXX') or shutil.which('g++-16') or 'g++',*flags,str(root/'verify/library_checker/range_affine_range_sum.compact.cpp'),'-o',str(exe)],check=True)
rng=random.Random(65731);mod=998244353
for n in [1,2,31,100]:
 a=[rng.randrange(mod) for _ in range(n)]
 lines=[f'{n} 3000',' '.join(map(str,a))];expected=[]
 for i in range(3000):
  l=rng.randrange(n);r=rng.randrange(l+1,n+1)
  if rng.randrange(2):
   b=rng.randrange(1,mod);c=rng.randrange(mod)
   lines.append(f'0 {l} {r} {b} {c}')
   for j in range(l,r):a[j]=(b*a[j]+c)%mod
  else:
   lines.append(f'1 {l} {r}');expected.append(str(sum(a[l:r])%mod))
 p=subprocess.run([str(exe)],input='\n'.join(lines)+'\n',text=True,capture_output=True,check=True)
 assert p.stdout.split()==expected
 assert not p.stderr
print('Generic lazy affine driver: independent modular vector updates and sums PASS')
