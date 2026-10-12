from pathlib import Path
import sys,subprocess,random,math,json,hashlib
from compiler_config import CXX
sys.set_int_max_str_digits(0)
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from usage_examples import expand
out=root/'build/bigint';rng=random.Random(1134)
cases={k:[] for k in ['P1480','P2142','P1303','1134']}
for i in range(65):
 a=rng.randrange(10**rng.randint(1,500));b=rng.randrange(1,10**rng.randint(1,500));d=rng.randint(1,10**9)
 cases['P1480'].append((f'{a}\n{d}\n',str(a//d)))
 cases['P2142'].append((f'{a+1}\n{b}\n',str(a+1-b)))
 cases['P1303'].append((f'{a}\n{b}\n',str(a*b)))
for a,b in [(0,1),(10**5000,10**9),(10**5000-1,999999937),(1,10**9)]:cases['P1480'].append((f'{a}\n{b}\n',str(a//b)))
for a,b in [(1,1),(10**10086,1),(1,10**10086),(10**10000-1,10**10000-1)]:cases['P2142'].append((f'{a}\n{b}\n',str(a-b)))
for a,b in [(0,10**2000),(10**2000,10**2000),(10**2000-1,10**2000-1),(1,1)]:cases['P1303'].append((f'{a}\n{b}\n',str(a*b)))
ns=list(range(101))+[0,100,1,50];cases['1134']=[('\n'.join(map(str,ns))+'\n-1\n', '\n'.join(str(math.comb(2*n,n)//(n+1)) for n in ns))]
report={}
for key,data in cases.items():
 f=root/('verify/hdu/' if key=='1134' else 'verify/luogu/')/(key+'.compact.cpp');cpp=out/(key+'.cpp');cpp.write_text(expand(f.read_text(),f.parent,set()))
 for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
  exe=out/(key+'-'+mode);subprocess.run([CXX,'-std=c++20',*flags,str(cpp),'-o',str(exe)],check=True)
  for text,want in data:
   r=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,timeout=10);assert not r.stderr
   assert r.stdout.split()==want.split(),(key,text[:100],r.stdout[:100],want[:100])
  report[key+'-'+mode]={'status':'pass','inputs':len(data),'program_sha256':hashlib.sha256(cpp.read_bytes()).hexdigest()};print(key,mode,'PASS',flush=True)
(root/'verification/big-integer-driver.json').write_text(json.dumps(report,indent=2)+'\n')
