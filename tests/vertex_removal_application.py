"""POJ2117 and UVA796 adapters against explicit vertex/edge deletion."""
from compiler_config import CXX
from pathlib import Path
import random
import subprocess
root=Path(__file__).resolve().parents[1]
rng=random.Random(2117)
def components(n,edges,removed=-1,skip=-1):
    g=[[] for _ in range(n)]
    for i,(u,v) in enumerate(edges):
        if i!=skip and u!=removed and v!=removed:
            g[u].append(v)
            g[v].append(u)
    seen={removed}
    count=0
    for u in range(n):
        if u not in seen:
            count+=1
            seen.add(u)
            q=[u]
            for x in q:
                for v in g[x]:
                    if v not in seen:
                        seen.add(v)
                        q.append(v)
    return count
poj_cases=[]
for _ in range(200):
    n=rng.randrange(1,13)
    edges=[(rng.randrange(n),rng.randrange(n)) for _ in range(rng.randrange(40))]
    poj_cases.append((n,edges,max(components(n,edges,u) for u in range(n))))
poj_cases.append((10000,[(i,i+1) for i in range(9999)],2))
poj_input=''.join(f'{n} {len(e)}\n'+''.join(f'{u} {v}\n' for u,v in e) for n,e,_ in poj_cases)+'0 0\n'
poj_expected=''.join(f'{answer}\n' for _,_,answer in poj_cases)
uva_input=''
uva_expected=''
for n in [0,1,8,0]+[rng.randrange(1,20) for _ in range(100)]:
    edges=[(u,v) for u in range(n) for v in range(u+1,n) if rng.randrange(5)==0]
    before=components(n,edges)
    bridges=[e for i,e in enumerate(edges) if components(n,edges,skip=i)>before]
    rows=list(range(n))
    rng.shuffle(rows)
    g=[[] for _ in range(n)]
    for u,v in edges:
        g[u].append(v)
        g[v].append(u)
    uva_input+=f'{n}\n'
    for u in rows:
        rng.shuffle(g[u])
        uva_input+=f'{u} ({len(g[u])}) '+' '.join(map(str,g[u]))+'\n'
    uva_expected+=f'{len(bridges)} critical links\n'+''.join(f'{u} - {v}\n' for u,v in sorted(bridges))+'\n'
for style in ['compact']:
    for folder,problem,text,want in [('poj','2117',poj_input,poj_expected),('uva','796',uva_input,uva_expected)]:
        name=f'{folder}{problem}.{style}'
        source=root/f'build/{name}.cpp'
        exe=root/f'build/{name}'
        subprocess.run(['python3',str(root/'tools/bundle.py'),str(root/f'verify/{folder}/{problem}.{style}.cpp'),str(source)],check=True)
        subprocess.run([CXX,'-std=c++20','-O2',str(source),'-o',str(exe)],check=True)
        got=subprocess.check_output([str(exe)],input=text.encode(),timeout=60).decode()
        assert got==want,(folder,style)
        print(f'{folder.upper()}{problem} {style} bundled driver / explicit deletion and exact output PASS')
