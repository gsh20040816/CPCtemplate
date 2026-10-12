from pathlib import Path
import hashlib,json,os,random,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/wida-bigint'
out.mkdir(parents=True,exist_ok=True)
b=(root/'tests/fixtures/wida_bigint/bigint.cpp').read_bytes()
assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='fd39b7103c67a148e15a9d09cd508d8bf2efc5c6'
rng=random.Random(176420)
cases=[]
for _ in range(350):
 a=rng.randrange(10**rng.randrange(1,450),10**450)
 b=rng.randrange(1,10**rng.randrange(1,450))
 factor=rng.randrange(1,1000001)
 for op,x,expected in [('+',b,a+b),('*',factor,a*factor),('/',factor,a//factor)]:
  cases.append((f'{op} {a} {x}',str(expected)))
for digits in [1,9,10,99,499,998]:
 a=10**digits-1
 for op,b,expected in [('+',1,a+1),('*',9,a*9),('/',9,a//9)]:
  cases.append((f'{op} {a} {b}',str(expected)))
data='\n'.join(x for x,_ in cases)+'\n'
answer=''.join(f'{y} {y}\n' for _,y in cases)
paths=['tests/wida_bigint.cpp','tests/wida_bigint.py','tests/fixtures/wida_bigint/bigint.cpp','src/compact/big_integer.hpp']
report=dict(scope='Exact WIDA05 positive canonical fixed-capacity arithmetic versus independent Python integers and current BigInteger; separately expected zero/carry/overflow failures and alias wrong answer. No original application or online AC.',runs=[])
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
 exe=out/mode
 subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/wida_bigint.cpp'),'-o',str(exe)],check=True)
 for task in ['normal','alias','current']+(['zero','carry','multiply','divide'] if mode=='sanitizer' else []):
  r=subprocess.run([str(exe),task],input=data if task=='normal' else '',text=True,capture_output=True,env=env,timeout=120)
  if task=='normal':assert r.returncode==0 and not r.stderr and r.stdout==answer,(mode,r.returncode,r.stderr,r.stdout[:200])
  elif task=='alias':assert r.returncode==0 and not r.stderr and r.stdout=='28 18\n',(mode,r.returncode,r.stdout,r.stderr)
  elif task=='current':
   expected='0\n'+str(10**1000)+'\n'+str(9*(2**31-1))+'\n'+str(10**10//(2**31-1))+' '+str(10**10%(2**31-1))+'\n'
   assert r.returncode==0 and not r.stderr and r.stdout==expected,(mode,r.returncode,r.stderr)
  else:
   assert r.returncode!=0 and ('runtime error' in r.stderr or 'AddressSanitizer' in r.stderr),(task,r.returncode,r.stderr)
   if task in ['multiply','divide']:assert 'signed integer overflow' in r.stderr,r.stderr
  report['runs'].append(dict(mode=mode,task=task,returncode=r.returncode,cases=len(cases) if task=='normal' else 4 if task=='current' else 1,stdout_sha256=hashlib.sha256(r.stdout.encode()).hexdigest(),stdout=r.stdout if task!='normal' else f'{len(cases)} Python-checked arithmetic cases PASS',stderr=r.stderr))
  print(mode,task,'PASS' if task in ['normal','current'] else 'expected source limitation reproduced',flush=True)
(root/'verification/wida-bigint.json').write_text(json.dumps(report,indent=2)+'\n')
