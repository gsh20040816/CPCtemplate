#!/usr/bin/env python3
"""DC3 independent suffix/LCP oracles, source semantics and actual copy forms."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from usage_examples import records
from audit_copy_context import candidate,extract_components

def oracle(s):
    n=len(s);sa=sorted(range(n),key=lambda i:s[i:]);rk=[0]*n;lcp=[0]*n
    for r,i in enumerate(sa):
        rk[i]=r
        if r:
            j=sa[r-1];k=0
            while i+k<n and j+k<n and s[i+k]==s[j+k]:
                k+=1
            lcp[r]=k
    return [sa,rk,lcp]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sanitize',action='store_true');args=parser.parse_args()
    mode='sanitizer' if args.sanitize else 'normal'
    out=ROOT/'build/dc3'/mode;out.mkdir(parents=True,exist_ok=True)
    sha=lambda data:hashlib.sha256(data).hexdigest()
    rows=[r for r in records() if r['symbol']=='DC3']
    components={r['symbol']:r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    paths=['src/compact/dc3.hpp','tests/dc3.cpp','tests/dc3.py','tests/fixtures/dc3_sources/kuangbin.cpp','docs/catalog.json','docs/usage-examples.json','tools/usage_examples.py','tools/audit_copy_context.py']+[r['driver'] for r in rows]
    snapshot={p:sha((ROOT/p).read_bytes()) for p in paths}
    flags=['-std=c++20','-O1' if args.sanitize else '-O2']
    if args.sanitize:
        flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
    env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1'}
    def compile(src,exe,extra=()):
        p=subprocess.run([CXX,*flags,*extra,str(src),'-o',str(exe)],text=True,capture_output=True)
        assert p.returncode==0,p.stderr
    def run(exe,data='',timeout=180):
        p=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=timeout)
        assert p.returncode==0,p.stderr
        return p.stdout
    probe=(ROOT/'tests/dc3.cpp').read_text()
    core=[]
    for form in ('header','ndebug','copied'):
        exe=out/('core-'+form);src=ROOT/'tests/dc3.cpp'
        if form=='copied':
            src=exe.with_suffix('.cpp')
            text=probe.replace('#include "../src/compact/dc3.hpp"','#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'+components['DC3']['code'])
            text=text.replace('"fixtures/dc3_sources/kuangbin.cpp"','"'+str(ROOT/'tests/fixtures/dc3_sources/kuangbin.cpp')+'"')
            src.write_text(text)
        compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
        counts=list(map(int,run(exe).split()));assert counts==[63323,62816]
        core.append(dict(form=form,cases=counts[0],source_cases=counts[1],source_sha256=sha(src.read_bytes())))
    rng=random.Random(20261012)
    api=[];formal=[]
    for i in range(100):
        n=rng.randrange(100);alphabet=[1,2,3,256,10000][i%5]
        s=[rng.randrange(alphabet) for _ in range(n)]
        api.append((f'{n} {alphabet}\n'+' '.join(map(str,s))+'\n',oracle(s)))
        text=''.join(chr(97+rng.randrange(3)) for _ in range(max(n,1)))
        formal.append((text+'\n',oracle(text)[0]))
    for s in ([],[0],[255,0,255,255,0],[0,0,0,0],[1,0,1,0,1,0,1]):
        api.append((f'{len(s)} 256\n'+' '.join(map(str,s))+'\n',oracle(s)))
    samples=[]
    for path in sorted((ROOT/'build/library-checker-reference/string/suffixarray/gen').glob('example_*.in')):
        data=path.read_text();s=data.strip();formal.append((data,oracle(s)[0]))
        samples.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path.read_bytes())))
    assert len(samples)==4
    n=500000
    formal.append(('a'*n+'\n',list(range(n-1,-1,-1))))
    formal.append(('ab'*(n//2)+'\n',list(range(n-2,-1,-2))+list(range(n-1,-1,-2))))
    programs=[]
    for row in rows:
        for form in ('header','ndebug','expanded','copied'):
            exe=out/(row['id']+'-'+form);src=ROOT/row['driver']
            if form in ('expanded','copied'):
                src=exe.with_suffix('.cpp');src.write_text(row['program'] if form=='expanded' else candidate(row,row['requires'],components)['program'])
            compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
            cases=formal if row['id']=='example-341' else api
            for data,expected in cases:
                output=run(exe,data)
                if row['id']=='example-341':
                    assert list(map(int,output.split()))==expected,(row['id'],form,data[:100])
                else:
                    lines=output.splitlines();assert len(lines)==3
                    assert [list(map(int,line.split())) for line in lines]==expected,(row['id'],form,data[:100])
            programs.append(dict(id=row['id'],form=form,cases=len(cases),program_sha256=row['program_sha256'] if form=='expanded' else sha(src.read_bytes())))
    mutants=[]
    if not args.sanitize:
        source=candidate(rows[1],rows[1]['requires'],components)['program']
        changes=[('zero-sentinel-collision','a[i] = s[i] + 1;','a[i] = s[i];'),('dummy-not-skipped','int a = extra, b = 0;','int a = 0, b = 0;'),('unstable-radix','for (int i = (int)a.size() - 1; i >= 0; i--)','for (int i = 0; i < (int)a.size(); i++)'),('lcp-original-index','lcp[rk[i]] = k;','lcp[i] = k;')]
        for name,old,new in changes:
            assert old in source
            src=out/(name+'.cpp');src.write_text(source.replace(old,new));exe=src.with_suffix('');compile(src,exe)
            reason=None
            for data,expected in api:
                try:
                    p=subprocess.run([str(exe)],input=data,text=True,capture_output=True,timeout=5)
                except subprocess.TimeoutExpired:
                    reason='timeout';break
                if p.returncode:
                    reason='nonzero_exit';break
                lines=p.stdout.splitlines()
                if len(lines)!=3 or [list(map(int,line.split())) for line in lines]!=expected:
                    reason='wrong_result';break
            assert reason,name
            mutants.append(dict(name=name,killed_by=reason))
    assert all(sha((ROOT/p).read_bytes())==h for p,h in snapshot.items())
    report=dict(mode=mode,core=core,programs=programs,official_samples=samples,mutants=mutants,snapshot=snapshot,large_cases='500000/500001/500002 constant and strictly increasing;10000/10001/10002 random against comparison-sort doubling; formal500000 constant/periodic.',online_ac=False)
    (ROOT/f'verification/dc3-{mode}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(mode,'63323 cases;62816 source comparisons;all core and usage forms PASS; mutants',mutants,flush=True)
if __name__=='__main__':
    main()
