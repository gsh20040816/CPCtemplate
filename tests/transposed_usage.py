from pathlib import Path
import hashlib
import json
import os
import random
import subprocess
import sys
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from usage_examples import records
out=root/'build/transposed-usage'
out.mkdir(parents=True,exist_ok=True)
row=next(r for r in records() if r['id']=='example-455')
rng=random.Random(455)
p=998244353
cases=[]
for n,m in [(0,0),(0,4),(4,0),(1,1),(1,257),(257,1),(127,128),(128,129),(257,65)]+[(rng.randrange(50),rng.randrange(50)) for _ in range(100)]:
    a=[rng.randrange(-2**63,2**63) for _ in range(n)]
    b=[rng.randrange(-2**63,2**63) for _ in range(m)]
    if n>1:a[0],a[-1]=-2**63,2**63-1
    data=f'{n} {m}\n'+' '.join(map(str,a))+'\n'+' '.join(map(str,b))+'\n'
    truth=[sum(a[i+j]*b[j] for j in range(min(m,n-i)))%p for i in range(n)] if n and m else []
    cases.append((data,[len(truth)]+truth))
# Rectangular scale with closed-form descending overlap counts.
n,m=131072,65537
cases.append((f'{n} {m}\n'+'1 '*n+'\n'+'1 '*m+'\n',[n]+[min(m,n-i) for i in range(n)]))
report=dict(scope='Exact printed and header transposed-convolution usage; independent Python integers, signed64 limits, empty inputs, unequal shapes and analytic overlap counts. No online AC.',runs=[])
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for form in ['printed','header']:
    source=out/'printed.cpp' if form=='printed' else root/row['driver']
    if form=='printed':source.write_text(row['program'])
    for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
        exe=out/f'{form}-{mode}'
        subprocess.run([CXX,'-std=c++20',*flags,str(source),'-o',str(exe)],check=True)
        for data,truth in cases:
            r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=60)
            assert r.returncode==0 and not r.stderr and list(map(int,r.stdout.split()))==truth,(form,mode,data[:80],r.stderr)
        report['runs'].append(dict(form=form,mode=mode,cases=len(cases),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
        print(form,mode,len(cases),'PASS',flush=True)
report['program_sha256']=row['program_sha256']
paths=['tests/transposed_usage.py','verify/api/transposed_convolution.compact.cpp','src/compact/ntt_convolution.hpp','src/compact/number_theory.hpp']
report['files']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/transposed-usage.json').write_text(json.dumps(report,indent=2)+'\n')
