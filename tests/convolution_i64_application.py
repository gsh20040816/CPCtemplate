#!/usr/bin/env python3
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess
root=Path(__file__).resolve().parents[1]
flags=['-std=c++20','-O2']
if os.environ.get('SANITIZE')=='1':flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined']
exe=root/'build/convolution-i64-driver'
subprocess.run([CXX,*flags,str(root/'verify/luogu/P3803.i64.compact.cpp'),'-o',str(exe)],check=True)
def run(a,b,want):
 text=f'{len(a)-1} {len(b)-1}\n'+' '.join(map(str,a))+'\n'+' '.join(map(str,b))+'\n'
 result=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True)
 assert list(map(int,result.stdout.split()))==want
 assert not result.stderr
rng=random.Random(68321)
for _ in range(30):
 a=[rng.randrange(10) for _ in range(rng.randrange(1,50))];b=[rng.randrange(10) for _ in range(rng.randrange(1,50))]
 want=[0]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):want[i+j]+=x*y
 run(a,b,want)
n=1000001
run([9]*n,[9]*n,[81*min(i+1,2*n-1-i) for i in range(2*n-1)])
print('P3803 signed-convolution driver: integer schoolbook oracle and maximum-degree coefficient-nine triangle PASS')
