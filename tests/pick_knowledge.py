#!/usr/bin/env python3
"""Pick migration and exact lattice enumeration; holes are Python-only models."""
from fractions import Fraction
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from usage_examples import records
from compiler_config import CXX


def sha(x):return hashlib.sha256(x).hexdigest()
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def area2(p):return sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1]))
def on(a,b,q):return cross(a,b,q)==0 and min(a[0],b[0])<=q[0]<=max(a[0],b[0]) and min(a[1],b[1])<=q[1]<=max(a[1],b[1])
def intersects(a,b,c,d):
    if any([on(a,b,c),on(a,b,d),on(c,d,a),on(c,d,b)]):return True
    return cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0

def simple(p):
    n=len(p)
    if n<3 or len(set(p))!=n or area2(p)==0:return False
    return not any(intersects(p[i],p[(i+1)%n],p[j],p[(j+1)%n]) for i in range(n) for j in range(i+1,n) if j!=i+1 and not(i==0 and j==n-1))

def locate(p,q):
    inside=False;x,y=q
    for a,b in zip(p,p[1:]+p[:1]):
        if on(a,b,q):return 0
        if (a[1]>y)!=(b[1]>y):
            at=Fraction(a[0])+Fraction((y-a[1])*(b[0]-a[0]),b[1]-a[1])
            if at>x:inside=not inside
    return 1 if inside else -1

def enumerate_lattice(rings):
    outer=rings[0];inside=boundary=0
    for x in range(min(p[0] for p in outer),max(p[0] for p in outer)+1):
        for y in range(min(p[1] for p in outer),max(p[1] for p in outer)+1):
            locations=[locate(r,(x,y)) for r in rings]
            if 0 in locations:boundary+=1
            elif locations[0]==1 and all(z==-1 for z in locations[1:]):inside+=1
    return inside,boundary

def valid_hole_domain(rings):
    if not all(simple(r) for r in rings):return False
    for i,a in enumerate(rings):
        for b in rings[i+1:]:
            if any(intersects(u,v,x,y) for u,v in zip(a,a[1:]+a[:1]) for x,y in zip(b,b[1:]+b[:1])):return False
    return all(locate(rings[0],h[0])==1 and all(j==i or locate(q,h[0])==-1 for j,q in enumerate(rings[1:])) for i,h in enumerate(rings[1:]))

def formula(rings,omit_holes=False):
    s=abs(area2(rings[0]))-sum(abs(area2(r)) for r in rings[1:])
    b=sum(math.gcd(abs(a[0]-c[0]),abs(a[1]-c[1])) for p in rings for a,c in zip(p,p[1:]+p[:1]))
    assert (s-b)%2==0
    return (s-b+2)//2-(0 if omit_holes else len(rings)-1),b


def main():
    if not __debug__:raise RuntimeError('Independent exact checks require Python assertions')
    fixture=ROOT/'tests/fixtures/pick-knowledge';migration=json.loads((fixture/'manifest.json').read_text());old=(fixture/'legacy-section.tex').read_text();assert sha(old.encode())==migration['original_sha256']
    assert migration['source_commit']=='1c1146887ef154ac17a8ad0cf627018cfa4bf0c2'
    assert migration['source']=='docs/mathematics.tex'
    source=(ROOT/'docs/mathematics.tex').read_text();a=source.index('\\section{数值算法与几何}');b=source.index('\\section{线性递推：',a)
    assert old.count(migration['removed_formula'])==old.count(migration['removed_index'])==1
    assert source[a:b]==old.replace(migration['removed_formula'],'').replace(migration['removed_index'],'')
    assert len(re.findall(r'^\\section\{',(ROOT/'docs/mathematics-legacy.tex').read_text(),re.M))==70
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal';out=Path(tempfile.mkdtemp(prefix='pick-knowledge-'+mode+'-',dir=ROOT/'build'));before=snapshot(ROOT);cases=[];rng=random.Random(20261004)
    def add(name,p,expected=None,reference='bounding-box lattice enumeration with exact ray parity'):
        p=list(p)
        if expected is None:assert simple(p),name;expected=enumerate_lattice([p])
        assert formula([p])==tuple(expected),name
        cases.append(dict(name=name,p=p,expected=list(expected),reference=reference))
    grid=list(itertools.product(range(3),repeat=2))
    for n in range(3,6):
        for chosen in itertools.combinations(grid,n):
            for tail in itertools.permutations(chosen[1:]):
                if tail[0]>tail[-1]:continue
                p=[chosen[0],*tail]
                if simple(p):
                    name=f'grid-{n}-{len(cases)}';expected=enumerate_lattice([p]);add(name,p,expected)
                    add(name+'-reverse',p[::-1],expected,'orientation reversal of enumerated polygon')
                    add(name+'-rotate',p[1:]+p[:1],expected,'cyclic start of enumerated polygon')
    bases=[[(0,0),(4,0),(4,1),(1,1),(1,4),(0,4)],[(0,0),(5,0),(5,5),(4,5),(4,1),(1,1),(1,5),(0,5)],[(0,0),(1,0),(3,0),(3,2),(0,2)],[(0,0),(2,1),(1,2)]]
    for k,p in enumerate(bases):
        for c in range(12):
            dx,dy=rng.randrange(-5,6),rng.randrange(-5,6)
            q=[(x+2*y+dx,y+dy) if c%2 else (y+dx,-x+dy) for x,y in p]
            add(f'concave-transform-{k}-{c}',q)
    sample=(fixture/'cses-sample.in').read_text().split();n=int(sample[0]);p=list(zip(map(int,sample[1::2]),map(int,sample[2::2])));assert n==4 and enumerate_lattice([p])==(6,8);add('official-sample',p)
    for limit in [10**9,10**12]:
        p=[(-limit,-limit),(limit,-limit),(limit,limit),(-limit,limit)]
        expected=((2*limit-1)**2,8*limit)
        add(f'extreme-square-{limit}',p,expected,'closed-form axis-aligned square')
        add(f'extreme-square-reverse-{limit}',p[::-1],expected,'closed-form reversed square')
    m=25000;p=[(x,0) for x in range(m)]+[(m,y) for y in range(m)]+[(x,m) for x in range(m,0,-1)]+[(0,y) for y in range(m,0,-1)]
    assert len(p)==100000 and len(set(p))==100000
    add('max-collinear-boundary',p,((m-1)**2,4*m),'100000 distinct collinear boundary vertices of a square')
    # Domain/proof counterexamples; deliberately not fed to the simple-ring driver.
    assert enumerate_lattice([[(0,0),(2,1),(1,2)]])==(1,3)
    bow=[(0,0),(2,2),(0,2),(2,0)];assert not simple(bow) and formula([bow])[0]==-3
    assert not simple([(0,0),(1,0),(2,0)])
    positive_bow=[(0,0),(10,10),(0,10),(2,0)]
    assert not simple(positive_bow) and formula([positive_bow])==(29,24)
    hole_bases=[([[(0,0),(4,0),(4,4),(0,4)],[(1,1),(3,1),(3,3),(1,3)]],(0,24)),([[(0,0),(8,0),(8,6),(0,6)],[(1,1),(2,1),(2,2),(1,2)],[(5,2),(7,2),(7,4),(5,4)]],(22,40))]
    holes=[]
    for rings,expected in hole_bases:
        for k in range(24):
            dx,dy=rng.randrange(-4,5),rng.randrange(-4,5)
            shifted=[[(x+dx,y+dy) for x,y in (r[::-1] if (k+j)%2 else r)] for j,r in enumerate(rings)]
            assert valid_hole_domain(shifted)
            got=enumerate_lattice(shifted);assert got==expected and formula(shifted)==expected
            assert formula(shifted,omit_holes=True)!=expected
            holes.append(dict(rings=shifted,expected=expected,h=len(rings)-1))
    assert not valid_hole_domain([[(0,0),(6,0),(6,6),(0,6)],[(1,1),(5,1),(5,5),(1,5)],[(2,2),(4,2),(4,4),(2,4)]])
    assert not valid_hole_domain([[(0,0),(4,0),(4,4),(0,4)],[(0,1),(1,1),(1,2),(0,2)]])
    (out/'hole-cases.json').write_text(json.dumps(holes,indent=2)+'\n')
    def encode(items,batch=True):return ((str(len(items))+'\n' if batch else '')+''.join(str(len(t['p']))+'\n'+''.join(f'{x} {y}\n' for x,y in t['p']) for t in items)).encode()
    data=encode(cases);(out/'cases.in').write_bytes(data);(out/'expected.json').write_text(json.dumps([{k:v for k,v in t.items() if k!='p'} for t in cases],indent=2)+'\n')
    row=next(r for r in records() if r['id']=='example-238');snippet=row['snippet'];assert snippet.count('    int n;')==1
    bulk=snippet.replace('    int n;','    int q;\n    cin >> q;\n    while (q--)\n    {\n    int n;',1);i=bulk.rfind('}');bulk=bulk[:i]+'    }\n'+bulk[i:]
    components={x['symbol']:x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    prelude='#include <algorithm>\n#include <cassert>\n#include <cstdlib>\n#include <cstdint>\n#include <iostream>\n#include <numeric>\n#include <string>\n#include <tuple>\n#include <vector>\nusing namespace std;\n'
    core=components['IntegerPlane']+'\n'+components['polygon_area2']+'\n'
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2']);env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),flags=flags,environment={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')},input_sha256=sha(data),expected_sha256=sha((out/'expected.json').read_bytes()),hole_cases_sha256=sha((out/'hole-cases.json').read_bytes()),hole_cases=len(holes),hole_scope='Python formula and independent enumeration only; no C++ holes API',programs=[],applications=[],mutants=[])
    def check(output,items):assert list(map(int,output.split()))==[v for t in items for v in t['expected']]
    def compile(name,text,ndebug=False):
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(text);cmd=[CXX,*flags,*(['-DNDEBUG'] if ndebug else []),str(cpp),'-o',str(exe)];subprocess.run(cmd,check=True,capture_output=True)
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()))
    for form,text in [('header','#include "'+str(ROOT/'src/compact/polygon_area2.hpp')+'"\n'+bulk),('copied',prelude+core+bulk)]:
        for nd in [False,True]:
            exe,entry=compile(form+('-ndebug' if nd else '-assert'),text,nd);run=subprocess.run([str(exe)],input=data,capture_output=True,env=env,timeout=120);assert run.returncode==0 and not run.stderr,run.stderr[-1000:];check(run.stdout,cases);(out/(entry['name']+'.out')).write_bytes(run.stdout);entry.update(cases=len(cases),output_sha256=sha(run.stdout),adapter='exact registered main wrapped in a batch loop');report['programs'].append(entry)
    formal=[t for t in cases if max(abs(v) for p in t['p'] for v in p)<=10**9]
    forced=[t for t in formal if t['name'].startswith(('official','extreme','max-'))]
    names={t['name'] for t in forced};pool=[t for t in formal if t['name'] not in names]
    selected=rng.sample(pool,min(60,len(pool)))+forced
    assert len({t['name'] for t in selected})==len(selected)
    for form,text in [('direct','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('copied',prelude+core+snippet)]:
        exe,entry=compile('application-'+form,text);entry['runs']=[]
        for j,t in enumerate(selected):
            inp=encode([t],False);(out/f'application-{j}.in').write_bytes(inp);run=subprocess.run([str(exe)],input=inp,capture_output=True,env=env,timeout=60);assert run.returncode==0 and not run.stderr;check(run.stdout,[t]);(out/f'{entry["name"]}-{j}.out').write_bytes(run.stdout);entry['runs'].append(dict(case=t['name'],input_sha256=sha(inp),output_sha256=sha(run.stdout)))
        report['applications'].append(entry)
    mutants=[('missing-orientation','if (s < 0) s = -s;',''),('double-area-as-area','I s = polygon_area2(p),','I s = polygon_area2(p) / 2,'),('double-count-endpoints','b += gcd(','b += 1 + gcd('),('missing-euler','(s - b + 2) / 2','(s - b) / 2'),('wrong-boundary-sign','(s - b + 2) / 2','(s + b + 2) / 2'),('narrow-area','I s = polygon_area2(p),','I s = (long long)polygon_area2(p),'),('narrow-output','print((s - b + 2) / 2);','print((long long)((s - b + 2) / 2));')]
    small=cases[:30]+cases[-6:];negative=encode(small);(out/'mutations.in').write_bytes(negative)
    for name,old,new in mutants:
        assert bulk.count(old)==1;exe,entry=compile(name,prelude+core+bulk.replace(old,new),True);run=subprocess.run([str(exe)],input=negative,capture_output=True,env=env,timeout=60);assert run.returncode==0 and not run.stderr,(name,run.stderr[-1000:]);rejected=False
        try:check(run.stdout,small)
        except (AssertionError,ValueError):rejected=True
        assert rejected,name
        (out/(name+'.out')).write_bytes(run.stdout);entry.update(output_sha256=sha(run.stdout),independently_rejected=True);report['mutants'].append(entry)
    report.update(source_after_sha256=snapshot(ROOT),passed=True,scope='Existing area interface and exact Pick usage; positive simple-ring cases, separate Python holes model, no new geometry kernel or online AC. 1e12 coordinates are library-domain extensions, not official CSES inputs. No full-suite or LSan claim.')
    assert before==report['source_after_sha256'];(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(f'Pick {mode}: {len(cases)} simple polygons x four bulk forms, {len(selected)} formal inputs x three programs, {len(holes)} Python hole cases PASS; {out.relative_to(ROOT)}/report.json')


if __name__=='__main__':main()
