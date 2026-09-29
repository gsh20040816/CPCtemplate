"""Complete tree drivers vs path enumeration, ancestor histograms and cut subsets."""
from compiler_config import CXX
from pathlib import Path
from collections import Counter
import os
import random
import subprocess

root=Path(__file__).resolve().parents[1]
mode='san' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
flags=['-std=c++20','-O2'] if mode=='normal' else ['-std=c++20','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
if os.uname().sysname=='Darwin': flags+=['-Wl,-stack_size,0x20000000']
exe={}
for name in ['P3806','CF600E','P2495']:
 dest=root/f'build/tree-usage-{name}-{mode}.cpp'
 binary=dest.with_suffix('')
 subprocess.run(['python3',str(root/'tools/bundle.py'),str(root/f'verify/luogu/{name}.compact.cpp'),str(dest)],check=True)
 subprocess.run([CXX,*flags,str(dest),'-o',str(binary)],check=True)
 exe[name]=binary
rng=random.Random(2026092901)


def run(name,data):
 p=subprocess.run([str(exe[name])],input=data,text=True,capture_output=True,check=True,timeout=90)
 assert not p.stderr,p.stderr
 return p.stdout.split()


def weighted(edges):return ''.join(f'{u} {v} {w}\n' for u,v,w in edges)
def unweighted(edges):return ''.join(f'{u} {v}\n' for u,v,w in edges)


for _ in range(220):
 n=rng.randrange(1,45)
 edges=[(rng.randrange(1,v),v,rng.randrange(1,10001)) for v in range(2,n+1)]
 g=[[] for _ in range(n+1)]
 for u,v,w in edges:g[u].append((v,w));g[v].append((u,w))
 distances=set()
 # Breadth-first paths in a tree: reference does not use centroid decomposition.
 for u in range(1,n+1):
  queue=[(u,0,0)]
  for v,parent,d in queue:
   if v>u: distances.add(d)
   for x,w in g[v]:
    if x!=parent:queue.append((x,v,d+w))
 qs=[rng.randrange(1,10**7+1) for _ in range(40)]+rng.sample(sorted(distances),min(60,len(distances)))
 assert run('P3806',f'{n} {len(qs)}\n'+weighted(edges)+'\n'.join(map(str,qs))+'\n')==['AYE' if q in distances else 'NAY' for q in qs]
n=10000
qs=[1,10000,99990000,10000000,9999999]*20
edges=[(v-1,v,10000) for v in range(2,n+1)]
# k is bounded by 1e7 in official input; largest path tested separately in core.
qs=[min(k,10000000) for k in qs]
assert run('P3806',f'{n} 100\n'+weighted(edges)+'\n'.join(map(str,qs))+'\n')==['AYE' if k%10000==0 and k//10000<n else 'NAY' for k in qs]
assert run('P3806','1 3\n1\n10000\n10000000\n')==['NAY']*3
print('P3806 full driver: 220 independent all-path inputs, 10000-node chain/100 queries and singleton PASS',flush=True)

for _ in range(260):
 n=rng.randrange(1,90)
 parent=[0,0]+[rng.randrange(1,v) for v in range(2,n+1)]
 edges=[(parent[v],v,1) for v in range(2,n+1)]
 colors=[0]+[rng.randrange(1,n+1) for _ in range(n)]
 counts=[Counter() for _ in range(n+1)]
 for v in range(1,n+1):
  u=v
  while u:
   counts[u][colors[v]]+=1
   u=parent[u]
 expected=[]
 for h in counts[1:]:
  best=max(h.values());expected.append(str(sum(c for c,f in h.items() if f==best)))
 assert run('CF600E',str(n)+'\n'+' '.join(map(str,colors[1:]))+'\n'+unweighted(edges))==expected
n=100000
chain=[(v-1,v,1) for v in range(2,n+1)]
assert run('CF600E',str(n)+'\n'+' '.join(['7']*n)+'\n'+unweighted(chain))==['7']*n
colors=list(range(1,n+1))
expected=[str((u+n)*(n-u+1)//2) for u in range(1,n+1)]
assert run('CF600E',str(n)+'\n'+' '.join(map(str,colors))+'\n'+unweighted(chain))==expected
star=[(1,v,1) for v in range(2,n+1)]
assert run('CF600E',str(n)+'\n'+' '.join(map(str,colors))+'\n'+unweighted(star))==[str(n*(n+1)//2)]+list(map(str,range(2,n+1)))
print('CF600E full driver: 260 independent ancestor histograms, 100000-node same/distinct-color chains and distinct-color star with 64-bit sum PASS',flush=True)


def cut_oracle(n,edges,keys):
 best=sum(w for u,v,w in edges)
 for mask in range(1<<len(edges)):
  g=[[] for _ in range(n+1)];cost=0
  for i,(u,v,w) in enumerate(edges):
   if mask>>i&1:cost+=w
   else:g[u].append(v);g[v].append(u)
  if cost>=best:continue
  seen={1};queue=[1]
  for u in queue:
   for v in g[u]:
    if v not in seen:seen.add(v);queue.append(v)
  if not seen.intersection(keys):best=cost
 return best


def virtual(n,edges,qs,expected):
 inp=str(n)+'\n'+weighted(edges)+str(len(qs))+'\n'+''.join(str(len(q))+' '+' '.join(map(str,q))+'\n' for q in qs)
 assert sum(map(len,qs))<=500000
 assert run('P2495',inp)==list(map(str,expected))


for _ in range(160):
 n=rng.randrange(2,10)
 edges=[(rng.randrange(1,v),v,rng.randrange(1,101)) for v in range(2,n+1)]
 qs=[rng.sample(range(2,n+1),rng.randrange(1,n)) for _ in range(14)]
 virtual(n,edges,qs,[cut_oracle(n,edges,q) for q in qs])
n=250000
edges=[(v-1,v,(v*97)%100000+1) for v in range(2,n+1)]
prefix=[100001]*(n+1)
for u,v,w in edges:prefix[v]=min(prefix[u],w)
qs=[[n],list(range(2,n+1)),[2,n],list(range(n//2,n+1))]
virtual(n,edges,qs,[prefix[min(q)] for q in qs])
# Maximum query count; persistent marked/dp buffers must be cleared each time.
virtual(n,edges,[[2] if t%2 else [n] for t in range(500000)],[prefix[2] if t%2 else prefix[n] for t in range(500000)])
star=[(1,v,100000) for v in range(2,n+1)]
virtual(n,star,[list(range(2,n+1)),[2],[n]],[24999900000,100000,100000])
print('P2495 full driver: 160 trees/2240 exhaustive cut-subset queries, 250000-node weighted chain/star, 500000-query reset, nested keys and 24999900000 answer PASS',flush=True)
