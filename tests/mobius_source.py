"""Full kuangbin 2.13 sources versus independent divisor and gcd oracles."""
from pathlib import Path
import hashlib,json,math,random,re,subprocess,sys,time
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
build=root/'build/mobius-source'
build.mkdir(exist_ok=True)
sys.path.insert(0,str(root/'tools'))
from usage_examples import records
text=(root/'build/source-audit/kuangbin.txt').read_text()
a=text.rsplit('     2.13.1 莫比乌斯函数',1)[1].split('     2.13.2 例题')[0]
b=text.rsplit('     2.13.2 例题：BZOJ2301',1)[1].split('     2.14 Baby-Step')[0]
def extract(t,count):
 lines=[]
 for line in t.splitlines():
  m=re.match(r'^\s*(\d+)(?:\s+(.*))?$',line)
  if m:
   assert int(m[1])==len(lines)+1,(m[1],len(lines))
   lines.append(m[2] or '')
  elif lines and line.strip() and 'kuangbin' not in line:
   lines[-1]+=' '+line.strip()
 assert len(lines)==count
 return '\n'.join(lines).replace('−','-')+'\n'
prelude='#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'
original=prelude+extract(b,52)
(build/'original-2301.cpp').write_text(original)
sieve=prelude+extract(a,26)
# The divisor-sum identity fixes every mu(n) uniquely from smaller divisors.
harness=r'''
int main()
{
    vector<int> oracle(MAXN + 1);
    oracle[1] = 1;
    for (int d = 1; d <= MAXN; d++)
        for (int m = d + d; m <= MAXN; m += d)
            oracle[m] -= oracle[d];
    LinearSieve current(MAXN);
    for (int repeat = 0; repeat < 2; repeat++)
    {
        Moblus();
        for (int i = 1; i <= MAXN; i++)
            if (mu[i] != oracle[i] || current.mu[i] != oracle[i]) return 1;
    }
    cout << "1000000 divisor certificates, two initializations PASS\n";
}
'''
include='#include "'+str(root/'src/compact/number_theory.hpp')+'"\n'
(build/'sieve.cpp').write_text(include+sieve+harness)
usage=next(r for r in records() if r['id']=='example-195')['program']
(build/'expanded-2522.cpp').write_text(usage)
sections={r['symbol']:r['code'] for r in json.loads((root/'build/book-sections.json').read_text())}
minimal=prelude+sections['LinearSieve']+'\n'+sections['CoprimePairs']+'\n'+(root/'docs/usage/example-195.cpp').read_text()
(build/'printed-2522.cpp').write_text(minimal)
rng=random.Random(2132301)
def brute(q):
 a,b,c,d,k=q
 return sum(math.gcd(x,y)==k for x in range(a,b+1) for y in range(c,d+1))
cases=[(a,b,c,d,k) for a in range(1,9) for b in range(a,9) for c in range(1,9) for d in range(c,9) for k in range(1,10)]
for _ in range(300):
 a=rng.randint(1,49970);c=rng.randint(1,49970)
 cases.append((a,a+rng.randrange(30),c,c+rng.randrange(30),rng.choice([1,2,3,rng.randint(1,50000)])))
truth=[brute(q) for q in cases]
# Maximum squares use a separate Eratosthenes totient identity.
phi=list(range(50001))
for p in range(2,50001):
 if phi[p]==p:
  for j in range(p,50001,p):phi[j]-=phi[j]//p
prefix=[0]*50001
for i in range(1,50001):prefix[i]=prefix[i-1]+phi[i]
for k in [1,2,3,7,97,49999,50000]:
 cases.append((1,50000,1,50000,k));truth.append(2*prefix[50000//k]-1)
for q in [(1,1,1,50000,1),(49999,50000,1,50000,1),(1,50000,49999,50000,2),(50000,50000,50000,50000,50000)]:
 cases.append(q);truth.append(brute(q))
unique=len(cases)
while len(cases)<50000:
 i=(len(cases)-unique)%unique
 cases.append(cases[i]);truth.append(truth[i])
data=str(len(cases))+'\n'+''.join(' '.join(map(str,q))+'\n' for q in cases)
expected=list(map(str,truth))
forms={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 for form,src in [('sieve',build/'sieve.cpp'),('original',build/'original-2301.cpp'),('driver',root/'verify/luogu/P2522.compact.cpp'),('expanded',build/'expanded-2522.cpp'),('printed',build/'printed-2522.cpp'),('ndebug',build/'printed-2522.cpp')]:
  exe=build/(mode+'-'+form)
  subprocess.run([CXX,'-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
  start=time.monotonic()
  out=subprocess.run([str(exe)],input='' if form=='sieve' else data,text=True,capture_output=True,check=True,timeout=60)
  assert not out.stderr,out.stderr
  if form!='sieve':assert out.stdout.splitlines()==expected,(mode,form)
  forms[mode+'-'+form]=dict(seconds=round(time.monotonic()-start,3),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),stdout_sha256=hashlib.sha256(out.stdout.encode()).hexdigest())
  print(mode,form,'PASS',flush=True)
report=dict(status='pass',source_lines=[26,52],printed_pages=[44,45],physical_pages=[46,47],source_pdf_sha256=hashlib.sha256((root/'build/source-audit/kuangbin.pdf').read_bytes()).hexdigest(),normalization='numbered lines, page headers, wrapped line48, Unicode minus, standard headers only',sieve_domain=1000000,sieve_initializations=2,unique_rectangles=unique,queries=50000,input_sha256=hashlib.sha256(data.encode()).hexdigest(),forms=forms,oracle='Divisor-sum recurrence; exhaustive small gcd rectangles, narrow large-coordinate gcd rectangles, independent Eratosthenes totient square identity')
(root/'verification/mobius-source-local.json').write_text(json.dumps(report,indent=2)+'\n')
