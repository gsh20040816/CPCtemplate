from pathlib import Path
import random,subprocess,hashlib,json,sys
from compiler_config import CXX
sys.set_int_max_str_digits(0)
root=Path(__file__).resolve().parents[1];out=root/'build/bigint';out.mkdir(exist_ok=True)
rng=random.Random(812)
lines=[];expected=[]
def add(op,a,b=None):
 lines.append(f'{op} {a}'+(' '+str(b) if b is not None else '')+'\n')
 x=int(a);y=int(b) if b is not None else 0
 if op in ('parse','int'):v=x
 elif op=='neg':v=-x
 elif op=='add':v=x+y
 elif op=='sub':v=x-y
 elif op=='mul':v=x*y
 elif op=='chain':v=x*x
 elif op=='pow':v=pow(x,y)
 elif op=='cmp':v=f'{(x>y)-(x<y)} {(abs(x)>abs(y))-(abs(x)<abs(y))}'
 elif op=='div':
  q=abs(x)//abs(y)*(-1 if (x<0)!=(y<0) else 1);v=f'{q} {x-q*y}'
 expected.append(str(v))
values=[0,1,-1,10**9-1,10**9,10**9+1,10**18-1,10**18,2**63-1,-2**63]
values+=list(range(-20,21))
for a in values:
 for b in values:
  for op in ['add','sub','mul','cmp','chain']:add(op,a,b)
for a in ['0','-0','+0','0000000000000000','-000001000000000','+0001000000001']:
 for op in ['parse','neg']:add(op,a)
for a in [-(2**63),2**63-1,0,1,-1]:add('int',a)
for i in range(1000):
 n=rng.randrange(1,350);m=rng.randrange(1,350)
 a=rng.randrange(10**n)*rng.choice([-1,1]);b=rng.randrange(10**m)*rng.choice([-1,1])
 for op in ['add','sub','mul','cmp','chain']:add(op,a,b)
 for d in [1,-1,2147483647,-2147483648,rng.choice([-1,1])*rng.randint(1,2147483647)]:add('div',a,d)
for a in range(-12,13):
 for e in range(40):add('pow',a,e)
for a in [0,1,-1]:add('pow',a,4294967295)
for n in [9,18,500,5000,5001,100000]:
 a=10**n-1
 for op,b in [('add',1),('sub',10**(n-1)),('mul',0),('mul',-1),('div',-2147483648),('cmp',a)]:add(op,a,b)
for n in [500,5000]:
 a=10**n-1;add('mul',a,a);add('chain',a,-a)
text=''.join(lines);(out/'cases.in').write_text(text);(out/'expected.txt').write_text('\n'.join(expected)+'\n')
header=(root/'src/compact/big_integer.hpp').read_text();core=header.split('// BEGIN BigInteger\n')[1].split('// END BigInteger')[0]
probe=(root/'tests/big_integer.cpp').read_text();copied='#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'+core+probe[probe.index('void check'):]
(out/'copied.cpp').write_text(copied)
report={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
 for form in ['header','ndebug','copied']:
  src=out/'copied.cpp' if form=='copied' else root/'tests/big_integer.cpp';exe=out/(mode+'-'+form)
  subprocess.run([CXX,'-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
  r=subprocess.run([str(exe)],input=text,text=True,capture_output=True,timeout=90,check=True);assert not r.stderr,r.stderr
  actual=r.stdout.splitlines();assert len(actual)==len(expected)
  for i,(a,b) in enumerate(zip(actual,expected)):
   assert a==b,(mode,form,i,lines[i][:100],a[:100],b[:100])
  report[mode+'-'+form]={'status':'pass','cases':len(lines)};print(mode,form,len(lines),'PASS',flush=True)
report['source_sha256']=hashlib.sha256(header.encode()).hexdigest();report['oracle']='Python int exact signed arithmetic; truncation-to-zero division derived from unsigned quotient; invariant and immutability checks; 100000-digit linear and 5000x5000-digit product tests'
(root/'verification/big-integer-local.json').write_text(json.dumps(report,indent=2)+'\n')
