#!/usr/bin/env python3
import hashlib, json, os, random, subprocess, sys
from pathlib import Path
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from usage_examples import records
from audit_copy_context import candidate,extract_components
san='--sanitize' in sys.argv
mode='sanitizer' if san else 'normal'
out=ROOT/'build/mo'/mode
out.mkdir(parents=True,exist_ok=True)
flags=['-std=c++20','-O1' if san else '-O2']
if sys.platform == 'darwin': flags += ['-Wl,-stack_size,0x10000000']
if san: flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
rows=[r for r in records() if r['symbol'] in ['TreeMo','RollbackMo']]
paths=['src/compact/tree_mo.hpp','src/compact/rollback_mo.hpp','src/compact/tree.hpp','tests/mo.cpp','tests/mo.py','docs/catalog.json','docs/usage-examples.json']+[r['driver'] for r in rows]
sha=lambda b:hashlib.sha256(b).hexdigest()
hashes={p:sha((ROOT/p).read_bytes()) for p in paths}
components={r['symbol']:r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
def compile(src,exe,extra=[]):
 p=subprocess.run([CXX,*flags,*extra,str(src),'-o',str(exe)],capture_output=True,text=True)
 assert p.returncode==0,p.stderr

def run(exe,data=''):
 p=subprocess.run([str(exe)],input=data,capture_output=True,text=True,env=env,timeout=120)
 assert p.returncode==0,p.stderr
 return p.stdout
core={}
for form in ['header','ndebug','copied']:
 src=ROOT/'tests/mo.cpp'
 if form=='copied':
  src=out/'core.cpp'
  a=candidate(rows[0],rows[0]['requires'],components)['program'].split('int main()')[0]
  b=candidate(rows[1],rows[1]['requires'],components)['program'].split('int main()')[0]
  src.write_text((ROOT/'tests/mo.cpp').read_text().replace('#include "../src/compact/tree_mo.hpp"',a).replace('#include "../src/compact/rollback_mo.hpp"',b))
 exe=out/('core-'+form)
 compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
 core[form]=run(exe).strip()
 print(mode,form,core[form],flush=True)
rng=random.Random(354355)
cases={r['id']:[] for r in rows}
for t in range(100):
 n=rng.randint(1,60);m=100
 a=[rng.randint(-10**12,10**12) if t%3==0 else rng.randrange(6) for _ in range(n)]
 edges=[(v,rng.randrange(v)) for v in range(1,n)]
 g=[[] for _ in range(n)]
 for u,v in edges:g[u].append(v);g[v].append(u)
 queries=[];answers=[]
 for _ in range(m):
  u=rng.randrange(n);v=rng.randrange(n);queries.append((u,v))
  parent={u:-1};todo=[u]
  for x in todo:
   for y in g[x]:
    if y not in parent:parent[y]=x;todo.append(y)
  seen=set();x=v
  while x!=-1:seen.add(a[x]);x=parent[x]
  answers.append(len(seen))
 data=f'{n} {m}\n'+' '.join(map(str,a))+'\n'+''.join(f'{u+1} {v+1}\n' for u,v in edges+queries)
 cases['example-354'].append((data,answers))
 n=rng.randint(1,80);a=[rng.randrange(1,10) if t%2 else rng.randrange(1,2*10**9) for _ in range(n)]
 queries=[];answers=[]
 for _ in range(m):
  l=rng.randrange(n);r=rng.randrange(l+1,n+1);queries.append((l,r));first={};best=0
  for i in range(l,r):
   first.setdefault(a[i],i);best=max(best,i-first[a[i]])
  answers.append(best)
 data=f'{n}\n'+' '.join(map(str,a))+f'\n{m}\n'+''.join(f'{l+1} {r}\n' for l,r in queries)
 cases['example-355'].append((data,answers))
# Maximum problem sizes with independent closed-form answers.
n=40000;m=100000
qs=[(rng.randrange(n),rng.randrange(n)) for _ in range(m)]
data=f'{n} {m}\n'+' '.join(map(str,range(n)))+'\n'+''.join(f'{i} {i+1}\n' for i in range(1,n))+''.join(f'{u+1} {v+1}\n' for u,v in qs)
cases['example-354'].append((data,[abs(u-v)+1 for u,v in qs]))
n=m=200000
qs=[]
for _ in range(m):
 l=rng.randrange(n);r=rng.randrange(l+1,n+1);qs.append((l,r))
data=f'{n}\n'+' '.join(['1']*n)+f'\n{m}\n'+''.join(f'{l+1} {r}\n' for l,r in qs)
cases['example-355'].append((data,[r-l-1 for l,r in qs]))
usage={}
for row in rows:
 forms={}
 for form in ['header','ndebug','expanded','copied']:
  src=ROOT/row['driver'];exe=out/(row['id']+'-'+form)
  if form in ['expanded','copied']:
   src=exe.with_suffix('.cpp')
   src.write_text(row['program'] if form=='expanded' else candidate(row,row['requires'],components)['program'])
  compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
  for data,want in cases[row['id']]:
   got=list(map(int,run(exe,data).split()))
   assert got==want,(row['id'],form,data[:100],got[:10],want[:10])
  forms[form]=len(cases[row['id']])
  print(mode,row['id'],form,'PASS',forms[form],flush=True)
 usage[row['id']]={'program_sha256':row['program_sha256'],'forms':forms}
assert hashes=={p:sha((ROOT/p).read_bytes()) for p in paths}
report={'status':'pass','mode':mode,'source_sha256':hashes,'core':core,'usage':usage,'scope':'Independent path BFS and interval scan; mixed vertex/edge core; repeated runs and varied blocks; maximum-size chain and constant array. No online AC implied.'}
(ROOT/f'verification/mo-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
