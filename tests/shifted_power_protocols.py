from pathlib import Path
import hashlib
import json
import math
import os
import random
import subprocess
import sys
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from usage_examples import records
row = next(r for r in records() if r['id'] == 'example-454')
out = root/'build/wida-mul-audit'
rng = random.Random(454)
P = 998244353
cases = []
for i in range(100):
    n = rng.randrange(150)
    small = rng.randrange(35)
    m = small + P*rng.randrange(10**9)
    expected = [math.comb(n,j)*sum(pow(k,n-j,P) for k in range(1,small+1))%P for j in range(n+1)]
    cases.append((f'{n} {m}\n',expected))
for m in [0,1,P-1,P,2**64-1]:
    cases.append((f'1 {m}\n',[(m*(m+1)//2)%P,m%P]))
report = dict(scope='Exact printed and header API programs; Python binomial expansion over short sums plus full-period identity, uint64 endpoints. No online AC.',runs=[])
env = dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for form in ['printed','header']:
    if form == 'printed':
        source = out/'shifted-printed.cpp'
        source.write_text(row['program'])
    else:
        source = root/row['driver']
    for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
        exe=out/f'protocol-{form}-{mode}'
        subprocess.run([CXX,'-std=c++20',*flags,str(source),'-o',str(exe)],check=True)
        for data,expected in cases:
            r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=30)
            assert r.returncode == 0 and not r.stderr and list(map(int,r.stdout.split())) == expected,(form,mode,data,r.stderr)
        report['runs'].append(dict(form=form,mode=mode,cases=len(cases),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
        print(form,mode,len(cases),'PASS',flush=True)
report['program_sha256']=row['program_sha256']
(root/'verification/shifted-power-protocols.json').write_text(json.dumps(report,indent=2)+'\n')
