#!/usr/bin/env python3
import bisect
import os
from pathlib import Path
import random
import shutil
import subprocess
root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20','-O2']
if os.environ.get('SANITIZE') == '1': flags = ['-std=c++20','-O1','-g','-fsanitize=address,undefined']
exe = root/'build/segtree-predecessor'
subprocess.run([os.environ.get('CXX') or shutil.which('g++-16') or 'g++',*flags,str(root/'verify/library_checker/predecessor_problem.compact.cpp'),'-o',str(exe)],check=True)
def run(lines, expected):
 p=subprocess.run([str(exe)],input='\n'.join(lines)+'\n',text=True,capture_output=True,check=True)
 assert p.stdout.split()==list(map(str,expected))
 assert not p.stderr
rng=random.Random(57325)
for n in [1,2,3,17,64,129]:
 for initial in ['0'*n,'1'*n,''.join(str(rng.randrange(2)) for _ in range(n))]:
  a=[i for i in range(n) if initial[i]=='1']
  lines=[f'{n} 5000',initial];expected=[]
  for _ in range(5000):
   c=rng.randrange(5);k=rng.randrange(n)
   lines.append(f'{c} {k}')
   p=bisect.bisect_left(a,k);has=p<len(a) and a[p]==k
   if c==0 and not has:a.insert(p,k)
   if c==1 and has:a.pop(p)
   if c==2:expected.append(int(has))
   if c==3:expected.append(a[p] if p<len(a) else -1)
   if c==4:
    p=bisect.bisect_right(a,k)-1
    expected.append(a[p] if p>=0 else -1)
  run(lines,expected)
# Official maximum N and Q: alternate a single endpoint between present/absent.
n=10000000;q=1000000
lines=[f'{n} {q}','0'*n];expected=[]
for i in range(q//5):
 k=0 if i%2==0 else n-1
 lines += [f'0 {k}',f'3 0',f'4 {n-1}',f'1 {k}',f'3 0']
 expected += [k,k,-1]
run(lines,expected)
print('Segtree predecessor driver: sorted-key oracle, empty/full sets, inclusive boundaries and N=10000000 Q=1000000 PASS')
