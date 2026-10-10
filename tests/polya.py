#!/usr/bin/env python3
import hashlib,itertools,json,math,os,random,subprocess,sys
from pathlib import Path
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from usage_examples import records
from audit_copy_context import candidate,extract_components,topological_closure
san='--sanitize' in sys.argv
mode='sanitizer' if san else 'normal';out=ROOT/'build/polya'/mode;out.mkdir(parents=True,exist_ok=True)
flags=['-std=c++20','-O1' if san else '-O2']
if Path('/opt/homebrew/include/boost').exists():flags+=['-I/opt/homebrew/include']
if san:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
rows=[r for r in records() if r['id'] in [f'example-{i}' for i in range(364,368)]]
paths=['src/compact/polya.hpp','tests/polya.cpp','tests/polya.py','docs/catalog.json','docs/usage-examples.json']+[r['driver'] for r in rows]
sha=lambda b:hashlib.sha256(b).hexdigest();hashes={p:sha((ROOT/p).read_bytes()) for p in paths}
from template_dependencies import dependencies
components={r['symbol']:r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
deps=dependencies(list(components.values()))
def compile(src,exe,extra=[]):
 r=subprocess.run([CXX,*flags,*extra,str(src),'-o',str(exe)],capture_output=True,text=True);assert r.returncode==0,r.stderr
def run(exe,data=''):
 r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=120);assert r.returncode==0,r.stderr;return r.stdout
core={}
for form in ['header','ndebug','copied']:
 src=ROOT/'tests/polya.cpp';exe=out/('core-'+form)
 if form=='copied':
  prefix=candidate(rows[0],['BurnsideAverage','permutation_cycles','necklace_colorings'],components)['program'].split('int main()')[0]
  src=exe.with_suffix('.cpp');src.write_text((ROOT/'tests/polya.cpp').read_text().replace('#include "../src/compact/polya.hpp"',prefix))
 compile(src,exe,['-DNDEBUG'] if form=='ndebug' else []);core[form]=run(exe).strip();print(mode,form,core[form],flush=True)
rng=random.Random(1446);cases={r['id']:[] for r in rows}
ns=list(range(1,201))
want=[sum(n**math.gcd(n,k) for k in range(n))//n%1000000007 for n in ns]
cases['example-364'].append((str(len(ns))+'\n'+'\n'.join(map(str,ns))+'\n',want))
n=999999937;mod=1000000007
want=(pow(n,n,mod)+(n-1)*n)*pow(n,mod-2,mod)%mod
cases['example-364'].append(('1000\n'+(str(n)+'\n')*1000,[want]*1000))
def orbit_count(n,c,group,counts=None):
 seen=set()
 for a in itertools.product(range(c),repeat=n):
  if counts is not None and [a.count(i) for i in range(c)]!=counts:continue
  seen.add(min(tuple(a[p[i]] for i in range(n)) for p in group))
 return len(seen)
for _ in range(100):
 n=rng.randrange(1,8);c=rng.randrange(4);mod=rng.randrange(1,41)
 rot=[[(i+k)%n for i in range(n)] for k in range(n)]
 dih=rot+[[(k-i)%n for i in range(n)] for k in range(n)]
 cases['example-366'].append((f'{n} {c} {mod}\n',[orbit_count(n,c,rot)%mod,orbit_count(n,c,dih)%mod]))
for it in range(100):
 n=rng.randrange(0,9);p=list(range(n));rng.shuffle(p);ident=list(range(n));group=[ident];q=p[:]
 while q!=ident:
  group.append(q);q=[p[x] for x in q]
 colors=rng.randrange(1,4);mod=rng.randrange(1,51)
 cases['example-367'].append((f'{n} {len(group)} {colors} {mod}\n'+'\n'.join(' '.join(map(str,p)) for p in group)+'\n',[orbit_count(n,colors,group)%mod]))
 counts=[0,0,0]
 for i in range(n):counts[rng.randrange(3)]+=1
 actual=group if it%2 else group[1:]
 data=' '.join(map(str,counts))+f' {len(actual)} 97\n'+'\n'.join(' '.join(str(x+1) for x in p) for p in actual)+'\n'
 cases['example-365'].append((data,[orbit_count(n,3,group,counts)%97]))
n=60;group=[[(i+k)%n for i in range(n)] for k in range(1,n)]
fixed=[]
for k in range(n):
 c=math.gcd(n,k);length=n//c
 fixed.append(math.factorial(c)//math.factorial(20//length)**3 if 20%length==0 else 0)
cases['example-365'].append(('20 20 20 59 97\n'+'\n'.join(' '.join(str(x+1) for x in p) for p in group)+'\n',[sum(fixed)//60%97]))
cases['example-366'].append(('1000000000 1 1000000007\n',[1,1]))
cases['example-367'].append(('0 1 0 6\n\n',[1]))
usage={}
for row in rows:
 forms={}
 for form in ['header','ndebug','expanded','copied']:
  src=ROOT/row['driver'];exe=out/(row['id']+'-'+form)
  if form in ['expanded','copied']:
   src=exe.with_suffix('.cpp');src.write_text(row['program'] if form=='expanded' else candidate(row,topological_closure(row['requires'],deps),components)['program'])
  compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
  for data,want in cases[row['id']]:
   got=list(map(int,run(exe,data).split()));assert got==want,(row['id'],form,data[:200],got[:10],want[:10])
  forms[form]=len(cases[row['id']]);print(mode,row['id'],form,'PASS',forms[form],flush=True)
 usage[row['id']]=dict(program_sha256=row['program_sha256'],forms=forms)
assert hashes=={p:sha((ROOT/p).read_bytes()) for p in paths}
report=dict(status='pass',mode=mode,source_sha256=hashes,core=core,usage=usage,scope='Exhaustive orbit representatives, permutation connected-component oracle, cpp_int arithmetic and exact fixed-inventory formulas; four full program forms. Online evidence separate.')
(ROOT/f'verification/polya-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
