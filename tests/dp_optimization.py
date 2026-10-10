#!/usr/bin/env python3
import hashlib,itertools,json,os,random,subprocess,sys
from pathlib import Path
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from usage_examples import records
from audit_copy_context import candidate,extract_components
san='--sanitize' in sys.argv
mode='sanitizer' if san else 'normal'
out=ROOT/'build/dp-optimization'/mode
out.mkdir(parents=True,exist_ok=True)
flags=['-std=c++20','-O1' if san else '-O2']
if san:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
rows=[r for r in records() if r['symbol'] in ['MonotoneHull','monotone_dp_layer','wqs_independent_set']]
paths=['src/compact/monotone_hull.hpp','src/compact/monotone_dp.hpp','src/compact/wqs_independent_set.hpp','tests/dp_optimization.cpp','tests/dp_optimization.py','docs/catalog.json','docs/usage-examples.json']+[r['driver'] for r in rows]
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
 src=ROOT/'tests/dp_optimization.cpp';exe=out/('core-'+form)
 if form=='copied':
  text=src.read_text()
  for row,stem in zip(rows,['monotone_hull','monotone_dp','wqs_independent_set']):
   prefix=candidate(row,row['requires'],components)['program'].split('int main()')[0]
   text=text.replace('#include "../src/compact/'+stem+'.hpp"',prefix)
  src=exe.with_suffix('.cpp');src.write_text(text)
 compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
 core[form]=run(exe).strip();print(mode,form,core[form],flush=True)
rng=random.Random(23651484)
cases={r['id']:[] for r in rows}
for _ in range(100):
 n=rng.randrange(1,12);s=rng.randrange(6);t=[rng.randrange(1,9) for i in range(n)];c=[rng.randrange(1,9) for i in range(n)]
 best=10**30
 for mask in range(1<<(n-1)):
  time=0;value=0;start=0
  for i in range(n):
   if i==n-1 or mask>>i&1:
    time+=s+sum(t[start:i+1]);value+=time*sum(c[start:i+1]);start=i+1
  best=min(best,value)
 cases['example-360'].append((f'{n}\n{s}\n'+''.join(f'{x} {y}\n' for x,y in zip(t,c)),[best]))
for _ in range(100):
 n=rng.randrange(1,16);k=rng.randrange(1,n+1);a=[[0]*n for i in range(n)]
 for i in range(n):
  for j in range(i):a[i][j]=a[j][i]=rng.randrange(10)
 cost=lambda l,r:sum(a[i][j] for i in range(l,r) for j in range(l,i))
 dp=[0]+[10**30]*n
 for g in range(k):dp=[10**30]+[min(dp[j]+cost(j,i) for j in range(i)) for i in range(1,n+1)]
 cases['example-361'].append((f'{n} {k}\n'+'\n'.join(' '.join(map(str,row)) for row in a)+'\n',[dp[n]]))
for _ in range(100):
 n=rng.randrange(2,17);k=rng.randrange(1,n//2+1);a=[rng.randrange(-100,101) for i in range(n)];best=0
 for mask in range(1<<n):
  if mask&(mask<<1) or mask.bit_count()>k:continue
  best=max(best,sum(a[i] for i in range(n) if mask>>i&1))
 cases['example-362'].append((f'{n} {k}\n'+' '.join(map(str,a))+'\n',[best]))
n=5000
cases['example-360'].append((f'{n}\n0\n'+'1 1\n'*n,[n*(n+1)//2]))
n=4000;k=800
cases['example-361'].append((f'{n} {k}\n'+'\n'.join(' '.join('0' if i==j else '1' for j in range(n)) for i in range(n))+'\n',[8000]))
n=300000;k=n//2
cases['example-362'].append((f'{n} {k}\n'+'1000000 '*n+'\n',[k*1000000]))
for _ in range(100):
 n=rng.randrange(1,12);k=rng.randrange(1,n+1);x=[rng.randrange(1,41) for i in range(n)]
 best=min(sum(min(abs(v-x[j]) for j in selected) for v in x) for selected in itertools.combinations(range(n),k))
 cases['example-363'].append((f'{n} {k}\n'+' '.join(map(str,x))+'\n',[best]))
n=3000;k=300
cases['example-363'].append((f'{n} {k}\n'+' '.join(map(str,range(1,n+1)))+'\n',[7500]))
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
report=dict(status='pass',mode=mode,source_sha256=hashes,core=core,usage=usage,scope='Independent exhaustive batching, quadratic partition DP and exhaustive nonadjacent subsets; monotone hull brute scans; maximum-scale applications. Online acceptance separately recorded.')
(ROOT/f'verification/dp-optimization-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
