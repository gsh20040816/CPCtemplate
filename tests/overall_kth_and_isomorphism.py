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
out=ROOT/'build/overall-kth'/mode
out.mkdir(parents=True,exist_ok=True)
flags=['-std=c++20','-O1' if san else '-O2']
if sys.platform=='darwin': flags+=['-Wl,-stack_size,0x10000000']
if san: flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
rows=[r for r in records() if r['symbol'] in ['OverallKth','TreeIsomorphism']]
paths=['src/compact/overall_kth.hpp','src/compact/tree_isomorphism.hpp','src/compact/data_structure.hpp','tests/overall_kth.cpp','tests/tree_isomorphism.cpp','tests/overall_kth_and_isomorphism.py','docs/catalog.json','docs/usage-examples.json']+[r['driver'] for r in rows]
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
for row,stem in zip(rows,['overall_kth','tree_isomorphism']):
 core[row['symbol']]={}
 for form in ['header','ndebug','copied']:
  src=ROOT/f'tests/{stem}.cpp';exe=out/(stem+'-'+form)
  if form=='copied':
   copied=candidate(row,row['requires'],components)['program'].split('int main()')[0]
   src=exe.with_suffix('.cpp')
   src.write_text((ROOT/f'tests/{stem}.cpp').read_text().replace(f'#include "../src/compact/{stem}.hpp"',copied))
  compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
  core[row['symbol']][form]=run(exe).strip()
  print(mode,stem,form,core[row['symbol']][form],flush=True)
rng=random.Random(356357)
cases={r['id']:[] for r in rows}
for t in range(150):
 n=rng.randint(1,50);a=[rng.randrange(8) for _ in range(n)];initial=a[:];ops=[];want=[]
 for _ in range(150):
  if rng.randrange(2):
   p=rng.randrange(n);v=rng.randrange(8) if t%2 else rng.randrange(10**9+1)
   a[p]=v;ops.append(f'C {p+1} {v}')
  else:
   l=rng.randrange(n);r=rng.randrange(l+1,n+1);k=rng.randrange(1,r-l+1)
   ops.append(f'Q {l+1} {r} {k}');want.append(sorted(a[l:r])[k-1])
 data=f'{n} {len(ops)}\n'+' '.join(map(str,initial))+'\n'+'\n'.join(ops)+'\n'
 cases['example-356'].append((data,want))
n=m=100000
ops=[];want=[]
for i in range(m//2):
 ops.append(f'C {i+1} {n+i}');k=1 if i%2 else n;ops.append(f'Q 1 {n} {k}')
 want.append(i+1 if k==1 else n+i)
data=f'{n} {m}\n'+' '.join(map(str,range(n)))+'\n'+'\n'.join(ops)+'\n'
cases['example-356'].append((data,want))
ops=[];want=[]
for _ in range(m):
 l=rng.randrange(n);r=rng.randrange(l+1,n+1);k=rng.randrange(1,r-l+1)
 ops.append(f'Q {l+1} {r} {k}');want.append(l+k-1)
data=f'{n} {m}\n'+' '.join(map(str,range(n)))+'\n'+'\n'.join(ops)+'\n'
cases['example-356'].append((data,want))
# Independent string canonicalization, trying every root rather than centroids.
def canonical(g,u,p):
 return '('+''.join(sorted(canonical(g,v,u) for v in g[u] if v!=p))+')'
for t in range(40):
 trees=[];lines=['50'];want=[];first={}
 for i in range(50):
  if trees and rng.randrange(2):
   g=trees[rng.randrange(len(trees))]
   perm=list(range(len(g)));rng.shuffle(perm);h=[[] for _ in g]
   for u in range(len(g)):
    for v in g[u]:h[perm[u]].append(perm[v])
   g=h
  else:
   n=rng.randrange(1,51);g=[[] for _ in range(n)]
   for v in range(1,n):
    u=rng.randrange(v);g[u].append(v);g[v].append(u)
  trees.append(g);key=min(canonical(g,u,-1) for u in range(len(g)))
  first.setdefault(key,i+1);want.append(first[key])
  root=rng.randrange(len(g));parent=[-2]*len(g);parent[root]=-1;todo=[root]
  for u in todo:
   for v in g[u]:
    if parent[v]==-2:parent[v]=u;todo.append(v)
  lines.append(str(len(g))+' '+' '.join(str(p+1) for p in parent))
 cases['example-357'].append(('\n'.join(lines)+'\n',want))
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
report=dict(status='pass',mode=mode,source_sha256=hashes,core=core,usage=usage,scope='Independent sorted interval and exact bracket-string oracles; all labeled trees through six vertices; repeated runs, signed64 extremes, two n=m=100000 kth stresses and 100000-node tree stress. No online AC inferred.')
(ROOT/f'verification/overall-kth-isomorphism-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
