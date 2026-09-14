"""Shortest AC suffix matching against direct pattern suffix checks."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root=Path(__file__).resolve().parents[1]
flags=['-std=c++20','-O2']
if os.environ.get('SANITIZE')=='1': flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined']
exe=root/'build/ac-shortest-application'
subprocess.run([CXX,*flags,str(root/'verify/examples/ac_shortest.compact.cpp'),'-o',str(exe)],check=True)
def run(patterns,text,expected):
    data=str(len(patterns))+'\n'+'\n'.join(patterns)+'\n'+text+'\n'
    result=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=30)
    assert not result.stderr,result.stderr
    assert list(map(int,result.stdout.split()))==expected
rng=random.Random(811)
for _ in range(150):
    patterns=[''.join(rng.choice('abc') for _ in range(rng.randrange(1,9))) for _ in range(rng.randrange(30))]
    text=''.join(rng.choice('abcd') for _ in range(150))
    expected=[min((len(p) for p in patterns if i>=len(p) and text[i-len(p):i]==p),default=0) for i in range(1,len(text)+1)]
    run(patterns,text,expected)
run(['a'*200000,'a'*100000],'a'*2000000,[0]*99999+[100000]*1900001)
run(['a']*200000,'a'*2000000,[1]*2000000)
print('AC shortest suffix: 150 direct-suffix oracles, empty set, nested/duplicate patterns, 200000 pattern length/count and 2000000 text length PASS')
