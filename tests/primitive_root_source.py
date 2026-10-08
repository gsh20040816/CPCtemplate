#!/usr/bin/env python3
"""Complete issue11 source protocol against direct cycles and candidate scans."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from usage_examples import records
from audit_copy_context import candidate,extract_components

def cycle_roots(n):
    units=sum(math.gcd(a,n)==1 for a in range(1,n))
    result=[]
    for a in range(1,n):
        if math.gcd(a,n)!=1:
            continue
        v=a%n;k=1
        while v!=1:
            v=v*a%n;k+=1
        if k==units:
            result.append(a)
    return result

def candidate_roots(n):
    # Candidate scan is independent of finding one generator then powering it.
    factors=[];left=n;p=2;phi=n
    while p*p<=left:
        if left%p==0:
            phi=phi//p*(p-1)
            while left%p==0:
                left//=p
        p+=1
    if left>1:
        phi=phi//left*(left-1)
    left=phi;p=2
    while p*p<=left:
        if left%p==0:
            factors.append(p)
            while left%p==0:
                left//=p
        p+=1
    if left>1:
        factors.append(left)
    return [a for a in range(1,n) if math.gcd(a,n)==1 and all(pow(a,phi//p,n)!=1 for p in factors)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sanitize',action='store_true');args=ap.parse_args()
    mode='sanitizer' if args.sanitize else 'normal'
    out=ROOT/'build/primitive-source'/mode;out.mkdir(parents=True,exist_ok=True)
    row=next(r for r in records() if r['id']=='example-48')
    sha=lambda b:hashlib.sha256(b).hexdigest()
    paths=['src/compact/primitive_root.hpp','src/compact/mod64.hpp','tests/primitive_root_source.py','tests/fixtures/primitive_root_sources/issue11.cpp','verify/luogu/P6091.compact.cpp','tools/usage_examples.py','tools/audit_copy_context.py']
    snapshot={p:sha((ROOT/p).read_bytes()) for p in paths}
    roots={n:cycle_roots(n) for n in range(2,601)}
    large=[999983,999979,10**6,531441,354294,524288,390625,781250,999999]
    for n in large:
        roots[n]=candidate_roots(n)
    cases=[(n,d) for n in range(2,601) for d in (1,1+n%199,200)]
    cases += [(n,200) for n in large]
    # n=2/4, no-root moduli, output index d-1, and empty line even if roots exist.
    batches=[]
    for start in range(0,len(cases),10):
        batch=cases[start:start+10]
        assert sum(len(roots[n][d-1::d]) for n,d in batch)<=100000
        data=str(len(batch))+'\n'+''.join(f'{n} {d}\n' for n,d in batch)
        want=[]
        for n,d in batch:
            want.extend([[len(roots[n])],roots[n][d-1::d]])
        batches.append((data,want))
    flags=['-std=c++20','-O1' if args.sanitize else '-O2','-Wformat=2','-Werror=format']
    if args.sanitize:
        flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
    components={r['symbol']:r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    programs=[]
    for form in ('source','header','ndebug','expanded','copied'):
        exe=out/form
        src=ROOT/('tests/fixtures/primitive_root_sources/issue11.cpp' if form=='source' else row['driver'])
        if form in ('expanded','copied'):
            src=exe.with_suffix('.cpp');src.write_text(row['program'] if form=='expanded' else candidate(row,row['requires'],components)['program'])
        p=subprocess.run([CXX,*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],text=True,capture_output=True)
        assert p.returncode==0,p.stderr
        for data,want in batches:
            p=subprocess.run([str(exe)],input=data,text=True,capture_output=True,timeout=60,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
            assert p.returncode==0,p.stderr
            lines=p.stdout.splitlines()
            assert len(lines)==len(want),(form,data[:80],len(lines),len(want))
            assert [list(map(int,line.split())) for line in lines]==want,(form,data[:80])
        programs.append(dict(form=form,cases=len(cases),source_sha256=sha(src.read_bytes())))
    assert all(sha((ROOT/p).read_bytes())==v for p,v in snapshot.items())
    report=dict(mode=mode,cases=len(cases),small_moduli=599,large_moduli=large,source_lines=123,programs=programs,snapshot=snapshot,usage='example-48',program_sha256=row['program_sha256'],source_adaptations='None; original formatter verified by -Wformat=2 -Werror=format on LP64 GNU C++.',scope='Complete original multi-test protocol; all roots counted and sorted sampling checked with required empty lines. No new online AC.')
    (ROOT/f'verification/primitive-root-source-{mode}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(mode,len(cases),'cases, original source and four current-program forms PASS',flush=True)
if __name__=='__main__':
    main()
