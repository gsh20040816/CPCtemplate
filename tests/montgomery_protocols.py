from pathlib import Path
import hashlib
import json
import os
import random
import subprocess
import sys
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records
row = next(r for r in records() if r['id'] == 'example-448')
assert (ROOT / row['snippet_file']).read_text() == row['snippet']
OUT = ROOT / 'build/montgomery'
rng = random.Random(63381475)
p = 998244353
cases = [(a,b,k) for a in [-(1<<63),-1,0,1,(1<<63)-1] for b in [0,1,2,p,-p] for k in [0,1,p-1,(1<<64)-1]]
cases += [(rng.randrange(-(1<<63),1<<63),rng.randrange(-(1<<63),1<<63),rng.randrange(1<<64)) for _ in range(4000)]
data = str(len(cases))+'\n'+''.join(f'{a} {b} {k}\n' for a,b,k in cases)
expected = [( (a+b)%p,(a-b)%p,a*b%p,pow(a,k,p),pow(b,-1,p) if b%p else -1) for a,b,k in cases]
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
report={'scope':'Python arbitrary-precision oracle; complete header and printed programs; no online AC','runs':[]}
for form,source in [('header','#include "'+str(ROOT/row['driver'])+'"\n'),('printed',row['program'])]:
    cpp=OUT/('protocol-'+form+'.cpp');cpp.write_text(source)
    for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
        exe=OUT/(form+'-'+mode)
        subprocess.run([CXX,'-std=c++20',*flags,str(cpp),'-o',str(exe)],check=True)
        r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=60)
        assert r.returncode==0 and not r.stderr,r.stderr
        got=[tuple(map(int,line.split())) for line in r.stdout.splitlines()]
        assert got==expected
        report['runs'].append(dict(form=form,mode=mode,cases=len(cases),source_sha256=hashlib.sha256(source.encode()).hexdigest()))
        print(form,mode,len(cases),'Python checks PASS',flush=True)
(ROOT/'verification/montgomery-protocols.json').write_text(json.dumps(report,indent=2)+'\n')
