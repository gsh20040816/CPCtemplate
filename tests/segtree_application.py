#!/usr/bin/env python3
import os
from pathlib import Path
import random
import shutil
import subprocess
root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20','-O2']
if os.environ.get('SANITIZE') == '1': flags = ['-std=c++20','-O1','-g','-fsanitize=address,undefined']
exe = root/'build/segtree-composite'
subprocess.run([os.environ.get('CXX') or shutil.which('g++-16') or 'g++',*flags,str(root/'verify/library_checker/point_set_range_composite.compact.cpp'),'-o',str(exe)],check=True)
rng = random.Random(76521)
p = 998244353
for n in [1,2,17,100]:
 a = [(rng.randrange(1,p),rng.randrange(p)) for _ in range(n)]
 lines = [f'{n} 3000', *[f'{c} {d}' for c,d in a]]
 expected = []
 for _ in range(3000):
  if rng.randrange(2):
   at=rng.randrange(n);c=rng.randrange(1,p);d=rng.randrange(p)
   a[at]=(c,d);lines.append(f'0 {at} {c} {d}')
  else:
   l=rng.randrange(n);r=rng.randrange(l+1,n+1);x=rng.randrange(p)
   lines.append(f'1 {l} {r} {x}')
   for c,d in a[l:r]:x=(c*x+d)%p
   expected.append(str(x))
 result=subprocess.run([str(exe)],input='\n'.join(lines)+'\n',text=True,capture_output=True,check=True)
 assert result.stdout.split()==expected
 assert not result.stderr
# Maximum-size alternating translations: independent closed-form prefix sums.
n=q=500000
lines=[f'{n} {q}', *['1 1']*n]
expected=[]
# All functions remain translations; one changed position has a known delta.
for i in range(q//2):
 pos=i%n
 lines.append(f'0 {pos} 1 2')
 lines.append(f'1 0 {n} {i}')
 expected.append(str((i+n+i+1)%p))
result=subprocess.run([str(exe)],input='\n'.join(lines)+'\n',text=True,capture_output=True,check=True)
assert result.stdout.split()==expected
assert not result.stderr
print('Point-set range-composite driver: direct sequential function evaluation oracle PASS')
