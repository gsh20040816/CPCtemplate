#!/usr/bin/env python3
import hashlib,json,os,random,subprocess,sys
from pathlib import Path
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from usage_examples import records
from audit_copy_context import candidate,extract_components
san='--sanitize' in sys.argv
mode='sanitizer' if san else 'normal'
out=ROOT/'build/short-walks'/mode
out.mkdir(parents=True,exist_ok=True)
flags=['-std=c++20','-O1' if san else '-O2']
if san:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
rows=[r for r in records() if r['symbol'] in ['StrictSecondShortest','KShortestWalks']]
paths=['src/compact/shortest_walks.hpp','tests/shortest_walks.cpp','tests/shortest_walks.py','docs/catalog.json','docs/usage-examples.json']+[r['driver'] for r in rows]
sha=lambda b:hashlib.sha256(b).hexdigest()
hashes={p:sha((ROOT/p).read_bytes()) for p in paths}
components={r['symbol']:r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
def compile(src,exe,extra=[]):
 r=subprocess.run([CXX,*flags,*extra,str(src),'-o',str(exe)],capture_output=True,text=True)
 assert r.returncode==0,r.stderr

def run(exe,data=''):
 r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=180)
 assert r.returncode==0,r.stderr
 return r.stdout
core={}
for form in ['header','ndebug','copied']:
 src=ROOT/'tests/shortest_walks.cpp';exe=out/('core-'+form)
 if form=='copied':
  copied='\n'.join(candidate(r,r['requires'],components)['program'].split('int main()')[0] for r in rows)
  src=exe.with_suffix('.cpp');src.write_text((ROOT/'tests/shortest_walks.cpp').read_text().replace('#include "../src/compact/shortest_walks.hpp"',copied))
 compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
 core[form]=run(exe).strip();print(mode,form,core[form],flush=True)
rng=random.Random(28652901)
cases={r['id']:[] for r in rows}
for _ in range(120):
 n=rng.randrange(2,9);edges=[]
 for v in range(2,n+1):edges.append((rng.randrange(1,v),v,rng.randrange(1,6)))
 for i in range(rng.randrange(20)):edges.append((rng.randrange(1,n+1),rng.randrange(1,n+1),rng.randrange(1,6)))
 reach=[[False]*(n+1) for i in range(4*n*5+1)];reach[0][1]=True
 for d in range(len(reach)):
  for u,v,w in edges:
   if d+w<len(reach):
    reach[d+w][v]|=reach[d][u];reach[d+w][u]|=reach[d][v]
 want=[d for d in range(len(reach)) if reach[d][n]][1]
 data=f'{n} {len(edges)}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in edges)
 cases['example-358'].append((data,[want]))
for _ in range(120):
 n=rng.randrange(2,10);k=rng.randrange(1,15);edges=[];g=[[] for i in range(n+1)]
 for u in range(2,n+1):
  for v in range(1,u):
   for j in range(rng.randrange(3)):
    w=rng.randrange(1,8);edges.append((u,v,w));g[u].append((v,w))
 if not edges:edges=[(n,1,1)];g[n].append((1,1))
 lengths=[]
 def dfs(u,d):
  if u==1:lengths.append(d)
  for v,w in g[u]:dfs(v,d+w)
 dfs(n,0);lengths.sort();want=lengths[:k]+[-1]*max(0,k-len(lengths))
 data=f'{n} {len(edges)} {k}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in edges)
 cases['example-359'].append((data,want))
# Maximum-size applications, with closed-form answers.
n=5000;m=100000
edges=[(v,v+1,5000) for v in range(1,n)]
edges += [(1,2,5000)]*(m-len(edges))
cases['example-358'].append((f'{n} {m}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in edges),[(n+1)*5000]))
n=1000;m=10000;k=100
edges=[(v,v-1,1000000) for v in range(2,n+1)]
edges += [(n,n-1,1000000)]*(m-len(edges))
cases['example-359'].append((f'{n} {m} {k}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in edges),[(n-1)*1000000]*k))
usage={}
for row in rows:
 forms={}
 for form in ['header','ndebug','expanded','copied']:
  src=ROOT/row['driver'];exe=out/(row['id']+'-'+form)
  if form in ['expanded','copied']:
   src=exe.with_suffix('.cpp');src.write_text(row['program'] if form=='expanded' else candidate(row,row['requires'],components)['program'])
  compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
  for data,want in cases[row['id']]:
   got=list(map(int,run(exe,data).split()));assert got==want,(row['id'],form,got[:10],want[:10])
  forms[form]=len(cases[row['id']]);print(mode,row['id'],form,'PASS',forms[form],flush=True)
 usage[row['id']]={'program_sha256':row['program_sha256'],'forms':forms}
assert hashes=={p:sha((ROOT/p).read_bytes()) for p in paths}
report=dict(status='pass',mode=mode,source_sha256=hashes,core=core,usage=usage,scope='Length-layer reachability/counting truth on cyclic multigraphs; independent recursive enumeration on DAG uses; maximum-scale applications. Online acceptance separately recorded.')
(ROOT/f'verification/short-walks-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
