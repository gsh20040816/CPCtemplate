"""P4897 has n+1 vertices numbered 0..n, not n vertices."""
from pathlib import Path
import os,random,subprocess
root=Path(__file__).resolve().parents[1]
rng=random.Random(4897)
cases=[]
for _ in range(100):
    size=rng.randrange(2,8)
    edges=[(v,rng.randrange(v),rng.randrange(30)) for v in range(1,size)]
    for _ in range(15):
        u,v=rng.sample(range(size),2)
        edges.append((u,v,rng.randrange(30)))
    queries=[(u,v) for u in range(size) for v in range(size) if u!=v]
    expected=[]
    cuts=[]
    for mask in range(1,(1<<size)-1):
        cost=sum(w for u,v,w in edges if ((mask>>u)&1)!=((mask>>v)&1))
        cuts.append((mask,cost))
    for u,v in queries:
        expected.append(min(cost for mask,cost in cuts if ((mask>>u)&1)!=((mask>>v)&1)))
    cases.append((size-1,edges,queries,expected))
cases.append((1,[(0,1,0)],[(0,1),(1,0)],[0,0]))
cases.append((1,[(0,1,10000)],[],[]))
# 501 vertices, 1500 edges, 100000 queries. Three parallel edges per path link.
edges=[(i,i+1,i%97+1) for i in range(500) for _ in range(3)]
values=[[0]*501 for _ in range(501)]
for u in range(501):
    best=10**18
    for v in range(u+1,501):
        best=min(best,3*((v-1)%97+1))
        values[u][v]=values[v][u]=best
queries=[]
for i in range(100000):
    queries.append((i%500,i%500+1) if i%5==0 else tuple(rng.sample(range(501),2)))
cases.append((500,edges,queries,[values[u][v] for u,v in queries]))
for style in ['compact','classic']:
    bundle=root/f'build/P4897.{style}.cpp'; exe=root/f'build/P4897.{style}'
    subprocess.run(['python3','tools/bundle.py',f'verify/luogu/P4897.{style}.cpp',str(bundle)],cwd=root,check=True)
    flags=['-O2'] if os.environ.get('SANITIZE')!='1' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    subprocess.run([os.environ.get('CXX','/opt/homebrew/bin/g++-16'),'-std=c++20',*flags,str(bundle),'-o',str(exe)],check=True)
    for n,edges,queries,expected in cases:
        data=f'{n} {len(edges)}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in edges)+f'{len(queries)}\n'+''.join(f'{u} {v}\n' for u,v in queries)
        result=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=30)
        assert result.stdout.splitlines()==list(map(str,expected))
        assert not result.stderr,result.stderr
    print(f'P4897 {style}: 103 graphs, exhaustive cut oracle, n+1 indexing, zero queries and 501 vertices/1500 edges/100000 queries PASS')
