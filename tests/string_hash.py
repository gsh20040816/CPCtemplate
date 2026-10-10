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
out=ROOT/'build/string-hash'/mode
out.mkdir(parents=True,exist_ok=True)
flags=['-std=c++20','-O1' if san else '-O2']
if san:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
rows=[r for r in records() if r['id'] in ['example-368','example-369']]
paths=['src/compact/string_hash.hpp','tests/string_hash.cpp','tests/string_hash.py','docs/catalog.json','docs/usage-examples.json']+[r['driver'] for r in rows]
sha=lambda b:hashlib.sha256(b).hexdigest()
hashes={p:sha((ROOT/p).read_bytes()) for p in paths}
components={r['symbol']:r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
def compile(src,exe,extra=[]):
 r=subprocess.run([CXX,*flags,*extra,str(src),'-o',str(exe)],capture_output=True,text=True)
 assert r.returncode==0,r.stderr
def run(exe,data=''):
 r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=90)
 assert r.returncode==0,r.stderr
 return r.stdout
prefix=candidate(rows[0],['StringHash'],components)['program'].split('int main()')[0]
core_source=(ROOT/'tests/string_hash.cpp').read_text().replace('#include "../src/compact/string_hash.hpp"',prefix)
core={}
for form in ['header','ndebug','copied']:
 src=ROOT/'tests/string_hash.cpp'
 exe=out/('core-'+form)
 if form=='copied':
  src=exe.with_suffix('.cpp');src.write_text(core_source)
 compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
 core[form]=run(exe).strip();print(mode,form,core[form],flush=True)
rng=random.Random(3370)
cases={r['id']:[] for r in rows}
for it in range(24):
 strings=[''.join(rng.choices('abAB019',k=rng.randrange(1,30))) for _ in range(100)]
 strings+=rng.choices(strings,k=100)
 cases['example-368'].append((str(len(strings))+'\n'+'\n'.join(strings)+'\n',[len(set(strings))]))
strings=['a'*1490+str(i) for i in range(10000)]
cases['example-368'].append(('10000\n'+'\n'.join(strings)+'\n',[10000]))
def truth(s,b):
 return [sum((ord(c)+1)*pow(b[j],len(s)-1-i,m) for i,c in enumerate(s))%m for j,m in enumerate([1000000007,1000000009])]
for it in range(50):
 s=''.join(rng.choices('ab AB019',k=it))
 b=[rng.randrange(257,1000000006),rng.randrange(257,1000000008)]
 queries=[];want=[]
 for k in range(40):
  l,r=sorted(rng.choices(range(len(s)+1),k=2));a,z=sorted(rng.choices(range(len(s)+1),k=2))
  queries.append(f'{l} {r} {a} {z}')
  for t in [s[l:r],s[l:r][::-1],s[l:r]+s[a:z]]:want+=truth(t,b)
 cases['example-369'].append((s+'\n'+f'{b[0]} {b[1]}\n40\n'+'\n'.join(queries)+'\n',want))
usage={}
for row in rows:
 forms={}
 for form in ['header','ndebug','expanded','copied']:
  src=ROOT/row['driver'];exe=out/(row['id']+'-'+form)
  if form in ['expanded','copied']:
   src=exe.with_suffix('.cpp');src.write_text(row['program'] if form=='expanded' else candidate(row,['StringHash'],components)['program'])
  compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
  for data,want in cases[row['id']]:
   got=list(map(int,run(exe,data).split()));assert got==want,(row['id'],form,data[:100],got[:10],want[:10])
  forms[form]=len(cases[row['id']]);print(mode,row['id'],form,'PASS',forms[form],flush=True)
 usage[row['id']]=dict(program_sha256=row['program_sha256'],forms=forms)
mutants={}
if not san:
 for name,old,new in [('reverse-offset','int x = n - r;','int x = n - l;'),('join-exponent','pw[len_b][j]','pw[0][j]'),('unsigned-byte','(unsigned char)s[i]','s[i]'),('missing-normalization','(x + mod[j]) % mod[j]','x % mod[j]')]:
  assert old in core_source
  src=out/('mutant-'+name+'.cpp');exe=src.with_suffix('')
  src.write_text(core_source.replace(old,new));compile(src,exe)
  r=subprocess.run([str(exe)],capture_output=True,timeout=90)
  assert r.returncode!=0,name
  mutants[name]='detected'
assert hashes=={p:sha((ROOT/p).read_bytes()) for p in paths}
report=dict(status='pass',mode=mode,source_sha256=hashes,core=core,usage=usage,mutants=mutants,scope='Polynomial arithmetic, exact string set oracle and API contracts only; explicit collision retained. Does not prove collision-free equality or online AC.')
(ROOT/f'verification/string-hash-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
