"""P5192 adapter verified by independent enumeration of photo counts."""
from compiler_config import CXX
from pathlib import Path
from itertools import product
import random
import os
import subprocess

root=Path(__file__).resolve().parents[1]
flags=['-std=c++20','-O2']
if os.environ.get('SANITIZE')=='1': flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined']
exe=root/'build/bounded-maxflow-application'
subprocess.run([CXX,*flags,str(root/'verify/luogu/P5192.compact.cpp'),'-o',str(exe)],check=True)
def case(n,m,needs,days):
    lines=[f'{n} {m}',' '.join(map(str,needs))]
    for cap,edges in days:
        lines.append(f'{len(edges)} {cap}')
        lines.extend(f'{j} {lo} {hi}' for j,lo,hi in edges)
    return '\n'.join(lines)+'\n'
def run(data,expected):
    result=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=60)
    assert not result.stderr,result.stderr
    assert result.stdout==''.join(str(x)+'\n\n' for x in expected)
rng=random.Random(5192)
batch,answers=[],[]
for trial in range(200):
    n,m=rng.randrange(1,4),rng.randrange(1,4)
    needs=[rng.randrange(4) for _ in range(m)]
    days=[]
    flat=[]
    for day in range(n):
        cap=rng.randrange(7)
        edges=[]
        for _ in range(rng.randrange(1,3)):
            j,hi=rng.randrange(m),rng.randrange(3)
            lo=rng.randrange(hi+1)
            edges.append((j,lo,hi))
            flat.append((day,j,lo,hi))
        days.append((cap,edges))
    best=-1
    for values in product(*(range(lo,hi+1) for _,_,lo,hi in flat)):
        daily=[0]*n
        girls=[0]*m
        for value,(day,j,_,_) in zip(values,flat):
            daily[day]+=value
            girls[j]+=value
        if all(daily[i]<=days[i][0] for i in range(n)) and all(girls[j]>=needs[j] for j in range(m)):
            best=max(best,sum(values))
    batch.append(case(n,m,needs,days));answers.append(best)
    if len(batch)==10:
        run(''.join(batch),answers);batch=[];answers=[]
run(case(0,0,[],[])+case(0,1,[1],[]),[0,-1])
days=[(30000,[(j,0,100) for j in range(300)]) for _ in range(365)]
run(case(365,1000,[0]*1000,days),[365*30000])
run(case(365,1000,[100000]*1000,days),[-1])
print('P5192: 200 exhaustive photo-assignment oracles in EOF batches, duplicate targets, empty graph, required blank lines; 365 days / 1000 targets / 109500 edges scale PASS')
