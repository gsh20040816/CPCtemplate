"""P4126 adapter checked against all source/sink partitions."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root=Path(__file__).resolve().parents[1]
flags=['-std=c++20','-O2']
if os.environ.get('SANITIZE')=='1': flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined']
if os.uname().sysname=='Darwin': flags+=['-Wl,-stack_size,0x20000000']
exe=root/'build/mincut-application'
subprocess.run([CXX,*flags,str(root/'verify/luogu/P4126.compact.cpp'),'-o',str(exe)],check=True)
def run(n,edges,expected):
    data=f'{n} {len(edges)} 1 {n}\n'+''.join(f'{u+1} {v+1} {c}\n' for u,v,c in edges)
    result=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=30)
    assert not result.stderr,result.stderr
    assert [tuple(map(int,line.split())) for line in result.stdout.splitlines()]==expected
rng=random.Random(4126)
for _ in range(200):
    n=rng.randrange(2,9)
    edges=[(rng.randrange(n),rng.randrange(n),rng.randrange(1,10)) for _ in range(rng.randrange(1,25))]
    cuts=[]
    best=None
    for mask in range(1<<n):
        if not(mask&1) or (mask>>(n-1)&1): continue
        chosen={i for i,(u,v,c) in enumerate(edges) if mask>>u&1 and not(mask>>v&1)}
        value=sum(edges[i][2] for i in chosen)
        if best is None or value<best: best=value;cuts=[]
        if value==best: cuts.append(chosen)
    run(n,edges,[(int(any(i in c for c in cuts)),int(all(i in c for c in cuts))) for i in range(len(edges))])
n=4000
edges=[(i,i+1,100000) for i in range(n-1)]
edges += [(0,0,100000)]*(60000-len(edges))
run(n,edges,[(1,0)]*(n-1)+[(0,0)]*(len(edges)-n+1))
run(4000,[(0,3999,100000)]*60000,[(1,1)]*60000)
print('P4126: 200 exhaustive partition output oracles; 4000 vertices / 60000 edges, loops, parallel roads and flow above int32 PASS')
