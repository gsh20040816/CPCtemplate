#!/usr/bin/env python3
"""Static rectangle minima/deletion and independent chronological shooting simulation."""
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot
from usage_examples import records
from compiler_config import CXX


def sha(x):return hashlib.sha256(x).hexdigest()


def api_cases():
    rng=random.Random(274);cases=[];pool=[-(1<<63),-1,0,1,(1<<63)-1]
    for test in range(60):
        n=test%35;p=[tuple(rng.choice(pool) for _ in range(3)) for _ in range(n)];alive=[True]*n;ops=[];want=[]
        for step in range(100):
            if n and step%3==0:
                id=rng.randrange(n);alive[id]=False;ops.append(f'1 {id}')
            else:
                x1,y1,x2,y2=[rng.choice(pool) for _ in range(4)]
                ids=[i for i,(x,y,k) in enumerate(p) if alive[i] and x1<=x<=x2 and y1<=y<=y2]
                want.append(min(ids,key=lambda i:(p[i][2],i)) if ids else -1)
                ops.append(f'2 {x1} {y1} {x2} {y2}')
        raw=f'{n} {len(ops)}\n'+''.join(' '.join(map(str,v))+'\n' for v in p)+'\n'.join(ops)+'\n'
        cases.append((f'api-{test}',raw,want))
    return cases


def shooting_cases():
    rng=random.Random(44);cases=[]
    for test in range(100):
        n=1+test%40;m=1+test%60;zs=rng.sample(range(1,10000001),n);rect=[]
        for z in zs:
            x1,x2=sorted(rng.sample(range(16),2));y1,y2=sorted(rng.sample(range(16),2));rect.append((x1,x2,y1,y2,z))
        shots=[(rng.randrange(16),rng.randrange(16)) for _ in range(m)]
        if test%3==0:shots=[(rect[0][0],rect[0][2])]*m
        alive=[True]*n;want=[]
        for x,y in shots:
            hit=[i for i,(xl,xr,yl,yr,z) in enumerate(rect) if alive[i] and xl<=x<=xr and yl<=y<=yr]
            id=min(hit,key=lambda i:rect[i][4]) if hit else -1
            want.append(id+1)
            if id!=-1:alive[id]=False
        raw=str(n)+'\n'+''.join(' '.join(map(str,r))+'\n' for r in rect)+str(m)+'\n'+''.join(f'{x} {y}\n' for x,y in shots)
        cases.append((f'shooting-{test}',raw,want))
    cases.append(('official-sample','2\n1 4 1 4 1\n2 5 2 6 2\n4\n0 0\n3 3\n4 5\n3 5\n',[0,1,2,0]))
    n=100000
    raw=str(n)+'\n'+''.join(f'0 10000000 0 10000000 {n-i}\n' for i in range(n))+str(n)+'\n'+'0 10000000\n'*n
    cases.append(('100000-overlap',raw,list(range(n,0,-1))))
    raw=str(n)+'\n'+''.join(f'{2*i} {2*i+1} 0 1 {n-i}\n' for i in range(n))+str(n)+'\n'+''.join(f'{2*i} 0\n' for i in range(n))
    cases.append(('100000-disjoint',raw,list(range(1,n+1))))
    return cases


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='kd-min-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT)
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    header=(ROOT/'src/compact/kd_min.hpp').read_text().replace('#pragma once\n','')
    probe=(ROOT/'tests/kd_min_probe.cpp').read_text()
    copied=header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='Independent live multiset rectangle oracle and chronological shot-by-shot target simulation. Official CF44G statement checked; local application, no online verdict or formal template coverage claim.')
    def compile(name,source,extra=()):
        cpp=out/(name+'.cpp');exe=out/name;cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    for form,source in [('header','#include "'+str(ROOT/'tests/kd_min_probe.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            name=form+('-ndebug' if release else '-assert')
            exe,entry=compile(name,source,['-DNDEBUG'] if release else [])
            start=time.monotonic();p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
            assert p.returncode==0 and not p.stderr and p.stdout.startswith(b'PASS '),(name,p.returncode,p.stdout,p.stderr[-1000:])
            entry.update(result=p.stdout.decode().strip(),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry);print(name,entry['result'],flush=True)
    for name,old,new in [
        ('no-delete','a[id].alive = false;','a[id].alive = true;'),
        ('wrong-tie','return min(x, y);','return max(x, y);'),
        ('open-boundary','high[d] < a[u].low[d]','high[d] <= a[u].low[d]'),
        ('dead-summary','a[u].best = a[u].alive ? u : -1;','a[u].best = u;'),
        ('no-ancestor-update','u = a[u].fa) pull(u);','u = -1) pull(u);')]:
        assert copied.count(old)==1
        exe,entry=compile(name,copied.replace(old,new),['-DNDEBUG'])
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry.update(independent_oracle_rejected=True);report['mutants'].append(entry);print(name,'ORACLE_REJECT',flush=True)
    for example,cases in [('example-274',api_cases()),('example-275',shooting_cases())]:
        row=next(r for r in records() if r['id']==example)
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('minimal-copy','#include <iostream>\n'+header+'\n'+row['snippet'])]:
            exe,entry=compile(example+'-'+form,source)
            for name,raw,want in cases:
                start=time.monotonic();p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=300)
                assert p.returncode==0 and not p.stderr,(example,form,name,p.returncode,p.stderr[-1000:])
                assert list(map(int,p.stdout.split()))==want,(example,form,name)
                entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start,passed=True))
            report['programs'].append(entry);print(example,form,len(cases),'PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('kd-min',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
