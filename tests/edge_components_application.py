"""CF118E bundles: validate every edge and strong connectivity, not one orientation order."""
from pathlib import Path
import random
import subprocess
root=Path(__file__).resolve().parents[1]
rng=random.Random(118)
def reaches(n,edges,reverse=False,skip=-1,undirected=False):
    g=[[] for _ in range(n)]
    for i,(u,v) in enumerate(edges):
        if i==skip:
            continue
        if reverse:
            u,v=v,u
        g[u].append(v)
        if undirected:
            g[v].append(u)
    seen={0}
    q=[0]
    for u in q:
        for v in g[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen)==n
cases=[]
for _ in range(140):
    n=rng.randrange(2,11)
    edges={(rng.randrange(i),i) for i in range(1,n)}
    edges|={(u,v) for u in range(n) for v in range(u+1,n) if rng.randrange(5)==0}
    edges=list(edges)
    rng.shuffle(edges)
    possible=all(reaches(n,edges,skip=i,undirected=True) for i in range(len(edges)))
    cases.append((n,edges,possible))
n=100000
edges=[(i,(i+k)%n) for k in [1,2,3] for i in range(n)]
cases.append((n,edges,True))
for style in ['compact']:
    source=root/f'build/CF118E.{style}.cpp'
    exe=root/f'build/CF118E.{style}'
    subprocess.run(['python3',str(root/'tools/bundle.py'),str(root/f'verify/luogu/CF118E.{style}.cpp'),str(source)],check=True)
    obj=root/f'build/CF118E.{style}.o'
    subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2','-Dmain=cpc_entry','-c',str(source),'-o',str(obj)],check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2','-pthread',str(obj),str(root/'tests/driver_stack.cpp'),'-o',str(exe)],check=True)
    for n,edges,possible in cases:
        text=f'{n} {len(edges)}\n'+''.join(f'{u+1} {v+1}\n' for u,v in edges)
        result=subprocess.check_output([str(exe)],input=text.encode(),timeout=60).decode().split()
        if not possible:
            assert result==['0']
            continue
        assert len(result)==2*len(edges)
        direction=[(int(result[i])-1,int(result[i+1])-1) for i in range(0,len(result),2)]
        assert {tuple(sorted(e)) for e in direction}=={tuple(sorted(e)) for e in edges}
        assert reaches(n,direction) and reaches(n,direction,reverse=True)
    print(f'CF118E {style} bundled driver / edge and strong-connectivity certificate, N=100000 M=300000 PASS')
