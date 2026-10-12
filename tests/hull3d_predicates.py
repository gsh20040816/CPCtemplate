"""Exact Fraction signs for binary64 inputs, including cancellation and nextafter."""
from pathlib import Path
from fractions import Fraction as F
import random, math, subprocess, json, hashlib
root=Path(__file__).resolve().parents[1]
build=root/'build/hull3d'
rng=random.Random(88327)
cases=[]
for k in range(6000):
    scale=math.ldexp(1.0,rng.randrange(-80,81))
    p=[[rng.randrange(-10000,10001)*scale for _ in range(3)] for _ in range(3)]
    if k%3==0:
        p.append([p[0][i]+p[1][i]-p[2][i] for i in range(3)])
        if k%2:
            j=rng.randrange(3)
            p[3][j]=math.nextafter(p[3][j],math.inf if k%4==1 else -math.inf)
    elif k%3==1:
        p.append([rng.randrange(-10000,10001)*scale for _ in range(3)])
    else:
        p[2]=[p[0][i]+2*(p[1][i]-p[0][i]) for i in range(3)]
        p.append([rng.randrange(-10000,10001)*scale for _ in range(3)])
    cases.append(p)
# Coordinates with vastly different exponents and subtraction tails.
for k in range(2000):
    cases.append([[math.ldexp(rng.uniform(1,2),rng.randrange(-90,91))*(-1 if rng.randrange(2) else 1) for _ in range(3)] for _ in range(4)])
def sign(x): return (x>0)-(x<0)
def expected(p):
    a,b,c,d=[[F(x) for x in q] for q in p]
    x=[u-v for u,v in zip(b,a)];y=[u-v for u,v in zip(c,a)];z=[u-v for u,v in zip(d,a)]
    n=[x[(i+1)%3]*y[(i+2)%3]-x[(i+2)%3]*y[(i+1)%3] for i in range(3)]
    return [sign(sum(u*v for u,v in zip(n,z)))]+[sign(v) for v in n]
truth=[expected(p) for p in cases]
# Decimal expansion is exact for each binary64 value, even when parsed as extended precision.
from decimal import Decimal
text=str(len(cases))+'\n'+''.join(' '.join(str(Decimal(x)) for p in q for x in p)+'\n' for q in cases)
results={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
    exe=build/f'predicates-{mode}'
    subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-ffp-contract=off',*flags,str(root/'tests/hull3d_predicates.cpp'),'-o',str(exe)],check=True)
    out=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,timeout=90)
    assert not out.stderr,out.stderr
    rows=[list(map(int,s.split())) for s in out.stdout.splitlines()]
    assert len(rows)==len(truth)
    for i,(a,b) in enumerate(zip(rows,truth)): assert a==b,(mode,i,a,b,cases[i])
    results[mode]='pass'
    print(mode,len(cases),'PASS',flush=True)
(root/'verification/hull3d-predicates.json').write_text(json.dumps(dict(status='pass',cases=len(cases),oracle='Fraction determinant of exact binary64 values, transferred through exact decimal expansion',forms=results,source_sha256=hashlib.sha256((root/'src/compact/hull3d.hpp').read_bytes()).hexdigest()),indent=2)+'\n')
