"""P7173 full driver checked by exhaustive integral flows and closed-form scale cases."""
from compiler_config import CXX
from pathlib import Path
from itertools import product
import os
import random
import subprocess

root=Path(__file__).resolve().parents[1]
flags=['-std=c++20','-O2']
if os.environ.get('SANITIZE')=='1': flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined']
exe=root/'build/negative-cost-application'
subprocess.run([CXX,*flags,str(root/'verify/luogu/P7173.compact.cpp'),'-o',str(exe)],check=True)
def run(n,edges,expected):
    data=f'{n} {len(edges)} 1 {n}\n'+''.join(f'{u+1} {v+1} {cap} {w}\n' for u,v,cap,w in edges)
    result=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=60)
    assert not result.stderr,result.stderr
    assert tuple(map(int,result.stdout.split()))==expected
rng=random.Random(7173)
for _ in range(200):
    n=rng.randrange(2,6)
    edges=[(rng.randrange(n),rng.randrange(n),rng.randrange(3),rng.randrange(-4,5)) for _ in range(rng.randrange(1,8))]
    best=None
    for flow in product(*(range(c+1) for _,_,c,_ in edges)):
        net=[0]*n
        cost=0
        for f,(u,v,_,w) in zip(flow,edges):net[u]+=f;net[v]-=f;cost+=f*w
        if any(net[1:-1]):continue
        key=(-net[0],cost)
        if best is None or key<best:best=key
    run(n,edges,(-best[0],best[1]))
# Independent 1->n arcs: every arc saturates for maximum flow.
edges=[(0,199,100,i%201-100) for i in range(10000)]
run(200,edges,(1000000,100*sum(e[3] for e in edges)))
# A disconnected negative cycle contributes even when the max-flow value is zero.
edges=[(1,2,100,-100),(2,1,100,99)]*5000
run(200,edges,(0,-500000))
print('P7173: 200 exhaustive flow/cost output oracles; 200 vertices / 10000 arcs / capacity-cost 100 scale, disconnected negative cycles PASS')
