from pathlib import Path
import hashlib,json,os,random,subprocess,sys
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from usage_examples import records
out=root/'build/divide-segment-tree'
out.mkdir(parents=True,exist_ok=True)
rng=random.Random(459)
cases={'example-458':[],'example-459':[]}
for name in cases:
 for trial in range(80):
  api=name=='example-458'
  n=rng.randrange(0 if api else 1,51)
  a=[rng.randrange(1000) for _ in range(n)]
  initial=a[:];ops=[];truth=[]
  for _ in range(180):
   if api:
    l,r=sorted([rng.randrange(n+1),rng.randrange(n+1)])
    kind=rng.randrange(4)
    if kind==3:
     ops.append(f'3 {l} {r}');truth.append(sum(a[l:r]));continue
    x=rng.randrange(1001) if kind==1 else rng.randrange(1,21)
    if kind==0:
     x=rng.randrange(-20,21)
     if l<r:x=max(x,-min(a[l:r]))
    ops.append(f'{kind} {l} {r} {x}')
    for i in range(l,r):a[i]=a[i]+x if kind==0 else x if kind==1 else a[i]//x
   else:
    l=rng.randrange(n);r=rng.randrange(l+1,n+1);kind=rng.randrange(1,4)
    if kind==3:
     ops.append(f'3 {l+1} {r}');truth.append(sum(a[l:r]));continue
    x=rng.randrange(2,21) if kind==1 else rng.randrange(1,1001)
    ops.append(f'{kind} {l+1} {r} {x}')
    for i in range(l,r):a[i]=a[i]//x if kind==1 else x
  cases[name].append((f'{n} {len(ops)}\n'+' '.join(map(str,initial))+'\n'+'\n'.join(ops)+'\n',truth))
cases['example-459'] += [('3 5\n2 5 6\n3 1 3\n1 2 3 2\n3 1 2\n2 1 2 3\n3 1 3\n',[13,4,9]),('6 11\n10 3 5 20 6 7\n3 1 6\n1 2 4 3\n3 1 3\n2 1 4 10\n3 3 6\n1 3 6 2\n2 1 4 5\n3 1 6\n2 1 3 100\n1 2 5 6\n3 1 4\n',[51,12,33,26,132])]
cases['example-458'].append(('4 7\n0 1000000000000 999999999999 1\n2 0 4 9223372036854775807\n3 0 4\n1 0 4 1000000000000\n0 1 3 -1000000000000\n3 0 4\n2 0 4 1\n3 0 4\n',[0,2000000000000,2000000000000]))
# Full official N limit with independently obvious uniform sums.
cases['example-459'].append(('500000 5\n'+'100000 '*500000+'\n3 1 500000\n1 1 500000 2\n3 1 500000\n2 2 499999 1\n3 1 500000\n',[50000000000,25000000000,599998]))
report=dict(scope='Header and exact printed drivers: independent Python arrays, both official ABC256Ex samples and N=500000 synthetic boundary; no online AC.',runs=[])
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for row in records():
 if row['id'] not in cases:continue
 for form in ['header','printed']:
  source=root/row['driver'] if form=='header' else out/(row['id']+'.cpp')
  if form=='printed':source.write_text(row['program'])
  for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
   exe=out/f"{row['id']}-{form}-{mode}"
   subprocess.run([CXX,'-std=c++20',*flags,str(source),'-o',str(exe)],check=True)
   for data,expected in cases[row['id']]:
    r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=30)
    assert r.returncode==0 and not r.stderr and list(map(int,r.stdout.split()))==expected,(row['id'],mode,data[:80],r.stdout,r.stderr)
   report['runs'].append(dict(id=row['id'],form=form,mode=mode,cases=len(cases[row['id']]),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),program_sha256=row['program_sha256']))
   print(row['id'],form,mode,'PASS',flush=True)
(root/'verification/divide-segment-protocols.json').write_text(json.dumps(report,indent=2)+'\n')
