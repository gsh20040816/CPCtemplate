from compiler_config import CXX
from pathlib import Path
import math,os,random,subprocess
root=Path(__file__).resolve().parents[1]
flags=['-std=c++20','-O2']
if os.environ.get('SANITIZE')=='1':flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined']
exe={}
for name in ['primality_test','sum_of_floor_of_linear']:
 exe[name]=root/('build/lc-'+name)
 subprocess.run([CXX,*flags,str(root/('verify/library_checker/'+name+'.compact.cpp')),'-o',str(exe[name])],check=True)
def run(name,lines,expected):
 r=subprocess.run([str(exe[name])],input='\n'.join(lines)+'\n',text=True,capture_output=True,check=True,timeout=60)
 assert not r.stderr,r.stderr
 assert r.stdout.splitlines()==expected,name
rng=random.Random(804712)
sieve=[True]*100001
sieve[0]=sieve[1]=False
for p in range(2,math.isqrt(100000)+1):
 if sieve[p]:
  for n in range(p*p,100001,p):sieve[n]=False
values=list(range(1,99001));truth=[sieve[n] for n in values]
# Proth certificates: a^((N-1)/2)=-1 forces every prime divisor to be
# 1 mod 2^k, hence larger than sqrt(N) for N=3*2^k+1, k>=2.
certified=[]
for k in range(30,59):
 n=3*(1<<k)+1
 for a in range(2,32):
  if pow(a,(n-1)//2,n)==n-1:
   assert (1<<k)**2>n
   certified.append((n,a));values.append(n);truth.append(True);break
assert certified
factors=[999999937,1000003,1000033,999983]
for n in factors:assert all(n%d for d in range(2,math.isqrt(n)+1))
for a in factors:
 for b in factors:
  assert a*b<=10**18
  values.append(a*b);truth.append(False)
values.append(10**18);truth.append(False)
while len(values)<100000:
 n=rng.randrange(1,100001);values.append(n);truth.append(sieve[n])
run('primality_test',[str(len(values)),*map(str,values)],['Yes' if b else 'No' for b in truth])
cases=[];want=[]
for n in range(1,16):
 for m in range(1,16):
  for a in range(m):
   for b in range(m):
    cases.append((n,m,a,b));want.append(sum((a*i+b)//m for i in range(n)))
while len(cases)<100000:
 n=rng.randrange(1,10**9+1);m=rng.randrange(1,10**9+1)
 if len(cases)%7==0:
  cases.append((n,m,0,m-1));want.append(0)
 else:
  q,r=divmod(n,m)
  cases.append((n,m,m-1,m-1));want.append(n*(n-1)//2-m*q*(q-1)//2-q*r)
run('sum_of_floor_of_linear',[str(len(cases)),*[' '.join(map(str,c)) for c in cases]],list(map(str,want)))
print('LC number drivers: sieve/Proth certificates, factored composites, exhaustive floor cases and 100000-query closed forms PASS')
