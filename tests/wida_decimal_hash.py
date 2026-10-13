from pathlib import Path
import hashlib,json,os,random,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
out=root/'build/wida-string-tail'
out.mkdir(parents=True,exist_ok=True)
source=root/'tests/fixtures/wida_decimal_hash/main.cpp'
b=source.read_bytes()
assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='d9dd2ab9343e2271981645a9eb52c0010b605a13'
samples=[('1256133','17'),('9544715561','525'),('239923','5'),('1218633757639','976272')]
witness=('999124554','99')
# The last four digits give adjacent 45 and 54, both good numbers.
assert int(witness[0][5:7])+int(witness[0][7:9])==int(witness[1])
assert '0' not in ''.join(witness)
rng=random.Random(1598)
lcp_cases=[witness,('',''),('abc',''),('','abc')]
for _ in range(1000):
 s=''.join(rng.choice('129') for _ in range(rng.randrange(100)))
 t=''.join(rng.choice('129') for _ in range(rng.randrange(30)))
 lcp_cases.append((s,t))
truth=[]
for s,t in lcp_cases:
 p=[]
 for i in range(len(s)):
  k=0
  while k<len(t) and i+k<len(s) and s[i+k]==t[k]:k+=1
  p.append(k)
 truth.append(p)
data=''.join(s+'\n'+t+'\n' for s,t in lcp_cases)
paths=['tests/wida_decimal_hash.py','tests/wida_decimal_lcp.cpp','tests/fixtures/wida_decimal_hash/main.cpp','src/compact/exkmp.hpp','src/compact/string.hpp']
report=dict(scope='Exact CF1598G WIDA source official samples and legal deterministic out-of-bounds witness. Current exkmp only compared with literal LCP; full decimal application replacement is not implemented. No new online AC.',runs=[])
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
 exe=out/('original-'+mode)
 subprocess.run([CXX,'-std=c++20',*flags,str(source),'-o',str(exe)],check=True)
 for s,x in samples:
  p=subprocess.run([str(exe)],input=s+'\n'+x+'\n',text=True,capture_output=True,env=env,timeout=30)
  assert p.returncode==0 and not p.stderr,(mode,s,p.returncode,p.stderr)
  a,b,c,d=map(int,p.stdout.split())
  assert 1<=a<=b<c<=d<=len(s) and c==b+1,(s,p.stdout)
  assert int(s[a-1:b])+int(s[c-1:d])==int(x),(s,x,p.stdout)
 report['runs'].append(dict(mode=mode,task='source_official_samples',cases=4,passed=True))
 if mode=='sanitizer':
  p=subprocess.run([str(exe)],input='\n'.join(witness)+'\n',text=True,capture_output=True,env=env,timeout=30)
  assert p.returncode!=0 and 'heap-buffer-overflow' in p.stderr,(p.returncode,p.stdout,p.stderr)
  report['runs'].append(dict(mode=mode,task='source_legal_witness',input=witness,valid_answer=[6,7,8,9],returncode=p.returncode,stderr=p.stderr))
 exe=out/('current-lcp-'+mode)
 subprocess.run([CXX,'-std=c++20',*flags,str(root/'tests/wida_decimal_lcp.cpp'),'-o',str(exe)],check=True)
 p=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=30)
 assert p.returncode==0 and not p.stderr and [list(map(int,l.split())) for l in p.stdout.splitlines()]==truth,(mode,p.returncode,p.stderr)
 report['runs'].append(dict(mode=mode,task='current_lcp_only',cases=len(lcp_cases),passed=True))
 print(mode,'4 source samples and',len(lcp_cases),'literal LCP cases PASS',flush=True)
assert report['files']=={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/wida-decimal-hash.json').write_text(json.dumps(report,indent=2)+'\n')
