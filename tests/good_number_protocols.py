from pathlib import Path
import hashlib,json,os,random,subprocess,sys,time
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from usage_examples import records
out=root/'build/good-number-sum'
rng=random.Random(160006998)
cases=[('1256133','17'),('9544715561','525'),('239923','5'),('1218633757639','976272'),('999124554','99')]
while len(cases)<105:
 a=''.join(rng.choice('123456789') for _ in range(rng.randrange(1,16)))
 b=''.join(rng.choice('123456789') for _ in range(rng.randrange(1,16)))
 x=str(int(a)+int(b))
 if '0' in x:continue
 prefix=''.join(rng.choice('123456789') for _ in range(rng.randrange(20)))
 suffix=''.join(rng.choice('123456789') for _ in range(rng.randrange(20)))
 cases.append((prefix+a+b+suffix,x))
cases += [('1'*500000,'2'*200000),('1'*500000,'2')]

def exact_sum(a,b):
 result=[];carry=0;i=len(a)-1;j=len(b)-1
 while i>=0 or j>=0 or carry:
  v=carry
  if i>=0:v+=ord(a[i])-48;i-=1
  if j>=0:v+=ord(b[j])-48;j-=1
  result.append(chr(48+v%10));carry=v//10
 return ''.join(reversed(result))

row=next(r for r in records() if r['id']=='example-460')
report=dict(scope='Exact printed and header CF1598G drivers: four official examples, legal original-overflow witness, 100 constructed cases and two maximum-text synthetic cases. Output verified by independent decimal addition. No online AC.',runs=[])
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for form in ['header','printed']:
 source=root/row['driver'] if form=='header' else out/'printed.cpp'
 if form=='printed':source.write_text(row['program'])
 for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
  exe=out/(form+'-'+mode)
  subprocess.run([CXX,'-std=c++20',*flags,str(source),'-o',str(exe)],check=True)
  start=time.monotonic()
  for s,x in cases:
   p=subprocess.run([str(exe)],input=s+'\n'+x+'\n',text=True,capture_output=True,env=env,timeout=30)
   assert p.returncode==0 and not p.stderr,(form,mode,p.returncode,p.stderr)
   a,b,c,d=map(int,p.stdout.split())
   assert 1<=a<=b<c<=d<=len(s) and c==b+1,(s[:60],x[:60],p.stdout)
   assert exact_sum(s[a-1:b],s[c-1:d])==x,(s[:60],x[:60],p.stdout)
  report['runs'].append(dict(form=form,mode=mode,cases=len(cases),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),program_sha256=row['program_sha256'],elapsed_seconds=time.monotonic()-start))
  print(form,mode,len(cases),'independent decimal-output cases PASS',flush=True)
(root/'verification/good-number-protocols.json').write_text(json.dumps(report,indent=2)+'\n')
