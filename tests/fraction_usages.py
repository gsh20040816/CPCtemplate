from pathlib import Path
from fractions import Fraction
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
rows=[r for r in records() if r['id'] in ['example-441','example-442']]
rng=random.Random(20261012)
cases={r['id']:[] for r in rows}
for _ in range(300):
    terms=[(rng.randrange(-1000,1001),rng.randrange(1,13)) for _ in range(rng.randrange(1,11))]
    data=''.join((str(n) if i==0 else f'{n:+}')+'/'+str(d) for i,(n,d) in enumerate(terms))
    assert len(data)<=100
    answer=Fraction()
    for n,d in terms:
        answer+=Fraction(n,d)
        assert -(1<<31)<=answer.numerator<(1<<31) and answer.denominator<(1<<31)
    cases['example-441'].append((data+'\n',[str(answer)]))
lines=[];want=[]
for i in range(500):
    n,m=(rng.randrange(-10**100,10**100) for _ in range(2))
    d,e=(rng.randrange(1,10**100)*rng.choice([-1,1]) for _ in range(2))
    op=rng.choice(['+','-','*','/','<'])
    a,b=Fraction(n,d),Fraction(m,e)
    c={'+':lambda:a+b,'-':lambda:a-b,'*':lambda:a*b,'/':lambda:a/b,'<':lambda:(a>b)-(a<b)}[op]()
    lines.append(f'{n} {d} {op} {m} {e}');want.append(str(c))
cases['example-442'].append((str(len(lines))+'\n'+'\n'.join(lines)+'\n',want))
out=ROOT/'build/fraction';report={'scope':'P1572 complete expression parser and arbitrary-precision API; Python Fraction oracle on exact header and printed forms, no online AC.','runs':[]}
for row in rows:
    assert (ROOT/row['snippet_file']).read_text()==row['snippet']
    for form,source in {'header':'#include "'+str(ROOT/row['driver'])+'"\n','printed':row['program']}.items():
        cpp=out/(row['id']+'-'+form+'.cpp');cpp.write_text(source)
        for mode,flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
            if Path('/opt/homebrew/include/boost').exists():flags+=['-I/opt/homebrew/include']
            exe=cpp.with_suffix('.'+mode)
            subprocess.run([CXX,'-std=c++20',*flags,str(cpp),'-o',str(exe)],check=True)
            env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
            for data,expected in cases[row['id']]:
                r=subprocess.run([str(exe)],input=data,capture_output=True,text=True,env=env,timeout=30)
                assert r.returncode==0 and not r.stderr,r.stderr
                assert r.stdout.split()==expected,(data,r.stdout,expected)
            report['runs'].append(dict(example=row['id'],form=form,mode=mode,cases=len(cases[row['id']]),source_sha256=hashlib.sha256(source.encode()).hexdigest()))
            print(row['id'],form,mode,'PASS',flush=True)
report['files']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/compact/fraction.hpp','verify/luogu/P1572.compact.cpp','verify/api/fraction.compact.cpp','tests/fraction_usages.py']}
(ROOT/'verification/fraction-usages.json').write_text(json.dumps(report,indent=2)+'\n')
