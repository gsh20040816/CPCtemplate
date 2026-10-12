from pathlib import Path
import hashlib
import json
import os
import random
import subprocess
import sys
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from usage_examples import records
rng=random.Random(164128)
# Coefficient of product (1 + q^i x), divided by q^(k(k-1)/2).
# Period blocks are raised as polynomials, with no q-Lucas or binomial calls.
def oracle(n,k,q,p):
    if k>n:return 0
    if q%p==0:return 1
    k=min(k,n-k);q%=p
    period=[];x=1
    while not period or x!=1:
        period.append(x);x=x*q%p
    def mul(a,b):
        c=[0]*min(k+1,len(a)+len(b)-1)
        for i,x in enumerate(a):
            for j,y in enumerate(b[:len(c)-i]):
                c[i+j]=(c[i+j]+x*y)%p
        return c
    block=[1]
    for x in period:block=mul(block,[1,x])
    a=[1];e=n//len(period)
    while e:
        if e&1:a=mul(a,block)
        block=mul(block,block);e//=2
    for x in period[:n%len(period)]:a=mul(a,[1,x])
    return a[k]*pow(pow(q,k*(k-1)//2,p),-1,p)%p
cases=[]
for _ in range(500):
    p=rng.choice([2,3,5,7,11,17,31,97])
    n=rng.getrandbits(64)
    k=rng.randrange(0,21)
    if rng.randrange(2):k=n-k if n>=k else 0
    q=rng.randrange(-(1<<31),1<<31)
    cases.append((n,k,q,p,oracle(n,k,q,p)))
for n in [(1<<64)-1,(1<<63),0,1,2,100]:
    for p in [2,3,5,97]:
        for q in [0,1,-1,p,p-1]:
            for k in [0,min(2,n),n,n+1 if n<(1<<64)-1 else n]:
                cases.append((n,k,q,p,oracle(n,k,q,p)))
row=next(r for r in records() if r['id']=='example-443')
assert (ROOT/row['snippet_file']).read_text()==row['snippet']
data=str(len(cases))+'\n'+''.join(f'{n} {k} {q} {p}\n' for n,k,q,p,w in cases)
expected=[c[-1] for c in cases]
out=ROOT/'build/q-binomial';out.mkdir(exist_ok=True)
report={'scope':'Full unsigned64 n/k, independent truncated generating-product coefficient oracle using polynomial period exponentiation; header/printed, no online AC.','cases_per_form_mode':len(cases),'runs':[]}
for form,source in {'header':'#include "'+str(ROOT/row['driver'])+'"\n','printed':row['program']}.items():
    cpp=out/(form+'.cpp');cpp.write_text(source)
    for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
        exe=out/(form+'-'+mode)
        subprocess.run([CXX,'-std=c++20',*flags,str(cpp),'-o',str(exe)],check=True)
        env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
        r=subprocess.run([str(exe)],input=data,capture_output=True,text=True,env=env,timeout=60)
        assert r.returncode==0 and not r.stderr,r.stderr
        assert list(map(int,r.stdout.split()))==expected
        report['runs'].append(dict(form=form,mode=mode,source_sha256=hashlib.sha256(source.encode()).hexdigest()))
        print(form,mode,len(cases),'coefficient oracles PASS',flush=True)
report['files']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/compact/q_binomial.hpp','verify/api/q_binomial.compact.cpp','tests/q_binomial_protocols.py']}
(ROOT/'verification/q-binomial-protocols.json').write_text(json.dumps(report,indent=2)+'\n')
