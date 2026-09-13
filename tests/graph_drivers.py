from compiler_config import CXX
from pathlib import Path
import subprocess, random,itertools
r=random.Random(4782)
for style in ['compact']:
 for problem in ['P4779','P4782']:
  source=f'build/{problem}.{style}.cpp'
  exe=f'build/{problem}.{style}'
  subprocess.run(['python3','tools/bundle.py',f'verify/luogu/{problem}.{style}.cpp',source],check=True)
  subprocess.run([CXX,'-std=c++20','-O2',source,'-o',exe],check=True)
  for trial in range(100):
   n=r.randrange(1,9)
   if problem=='P4779':
    edges=[(i,i+1,r.randrange(10)) for i in range(1,n)]
    edges += [(r.randrange(1,n+1),r.randrange(1,n+1),r.randrange(20)) for _ in range(30)]
    d=[10**30]*(n+1);d[1]=0
    for _ in range(n):
     for u,v,w in edges:d[v]=min(d[v],d[u]+w)
    data=f'{n} {len(edges)} 1\n'+''.join(f'{u} {v} {w}\n' for u,v,w in edges)
    out=subprocess.check_output([exe],input=data.encode()).decode().split()
    assert list(map(int,out))==d[1:]
   else:
    clauses=[(r.randrange(1,n+1),r.randrange(2),r.randrange(1,n+1),r.randrange(2)) for _ in range(r.randrange(1,30))]
    def valid(a):return all(a[x-1]==b or a[y-1]==c for x,b,y,c in clauses)
    exists=any(valid(a) for a in itertools.product(range(2),repeat=n))
    data=f'{n} {len(clauses)}\n'+''.join(' '.join(map(str,c))+'\n' for c in clauses)
    out=subprocess.check_output([exe],input=data.encode()).decode().split()
    assert (out[0]=='POSSIBLE')==exists
    if exists:
     a=list(map(int,out[1:]));assert len(a)==n and all(x in (0,1) for x in a) and valid(a)
  print(problem,style,'bundled driver 100 random oracle cases PASS')
