#!/usr/bin/env python3
from compiler_config import CXX
from pathlib import Path
import itertools
import os
import random
import subprocess
root=Path(__file__).resolve().parents[1]
flags=['-std=c++20','-O2']
if os.environ.get('SANITIZE')=='1':flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined']
exe=root/'build/flow-slope-driver'
subprocess.run([CXX,*flags,str(root/'verify/luogu/P3381.slope.compact.cpp'),'-o',str(exe)],check=True)
rng=random.Random(81861)
for trial in range(150):
 n=5
 edges=[]
 for _ in range(7):
  u=rng.randrange(1,n);v=rng.randrange(u+1,n+1)
  edges.append((u,v,rng.randrange(3),rng.randrange(10)))
 best=(0,0)
 for fs in itertools.product(*(range(c+1) for u,v,c,w in edges)):
  b=[0]*(n+1);cost=0
  for f,(u,v,c,w) in zip(fs,edges):b[u]-=f;b[v]+=f;cost+=f*w
  if any(b[2:n]) or b[n]!=-b[1]:continue
  candidate=(-b[1],-cost)
  best=max(best,candidate)
 text=f'{n} {len(edges)} 1 {n}\n'+'\n'.join(' '.join(map(str,e)) for e in edges)+'\n'
 result=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True)
 assert list(map(int,result.stdout.split()))==[best[0],-best[1]]
 assert not result.stderr
print('P3381 slope endpoint driver: exhaustive feasible edge-flow assignment oracle PASS')
