#!/usr/bin/env python3
"""Dynamic KD extraction, recycling invariants and simultaneous moves."""
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


def extract_cases():
    rng=random.Random(270)
    cases=[]
    pool=[-(1<<63),-1,0,1,(1<<63)-1]
    for test in range(80):
        n=test%20
        points=[(rng.choice(pool),rng.choice(pool),rng.randrange(9)) for _ in range(n)]
        initial=list(points)
        lines=[]
        want=[]
        for i in range(200):
            if i%3:
                p=(rng.choice(pool),rng.choice(pool),rng.randrange(9))
                points.append(p)
                lines.append('1 '+' '.join(map(str,p)))
            else:
                x1,y1,x2,y2=[rng.choice(pool) for _ in range(4)]
                gone=[p for p in points if x1<=p[0]<=x2 and y1<=p[1]<=y2]
                points=[p for p in points if not(x1<=p[0]<=x2 and y1<=p[1]<=y2)]
                want.extend([len(gone),*sorted(p[2] for p in gone)])
                lines.append(f'2 {x1} {y1} {x2} {y2}')
        raw=f'{n} {len(lines)}\n'+'\n'.join(' '.join(map(str,p)) for p in initial)+'\n'+'\n'.join(lines)+'\n'
        cases.append((f'extract-{test}',raw,want))
    return cases


def move_cases():
    rng=random.Random(6045)
    cases=[]
    for test in range(80):
        n=1+test%50
        w,h=(1,1) if test==0 else (rng.randrange(1,100),rng.randrange(1,100))
        p=[(rng.randrange(w),rng.randrange(h)) for _ in range(n)]
        initial=list(p)
        ops=[]
        for j in range(50):
            x,y=p[j%n] if j%3==0 else (rng.randrange(-100,101),rng.randrange(-100,101))
            e=[0,1,50,1000000000][j%4]
            coeff=[rng.randrange(1000000001) for _ in range(6)]
            if j%5==0:coeff=[1,0,0,0,1,0]
            if j%5==1:coeff=[0]*6
            a,b,c,d,f,g=coeff
            old=list(p)
            for i,(u,t) in enumerate(old):
                if abs(x-u)+abs(y-t)<=e:
                    p[i]=((u*a+t*b+(i+1)*c)%w,(u*d+t*f+(i+1)*g)%h)
            ops.append(' '.join(map(str,[x,y,e,*coeff])))
        raw=f'{n} {len(ops)} {w} {h}\n'+'\n'.join(f'{x} {y}' for x,y in initial)+'\n'+'\n'.join(ops)+'\n'
        cases.append((f'move-{test}',raw,[v for xy in p for v in xy]))
    n=100000
    raw=f'{n} 2 1000000000 1000000000\n'+'\n'.join(f'{i} {i}' for i in range(n))+'\n0 0 1000000000 0 0 1 0 0 2\n0 0 1000000000 1 0 0 0 1 0\n'
    cases.append(('move-100000',raw,[v for i in range(1,n+1) for v in (i,2*i)]))
    return cases


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='kd-extract-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT)
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    header=(ROOT/'src/compact/kd_range.hpp').read_text().replace('#pragma once\n','')
    probe=(ROOT/'tests/kd_range_probe.cpp').read_text()
    copied=header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='Independent multiset and Python Manhattan-distance oracle; local model only, no UVALive6045 statement or online verdict claim.')
    def compile(name,source,extra=()):
        cpp=out/(name+'.cpp');exe=out/name;cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    for form,source in [('header','#include "'+str(ROOT/'tests/kd_range_probe.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            name=form+('-ndebug' if release else '-assert')
            exe,entry=compile(name,source,['-DNDEBUG'] if release else [])
            start=time.monotonic();p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
            assert p.returncode==0 and not p.stderr and p.stdout.startswith(b'PASS '),(name,p.returncode,p.stdout,p.stderr[-1000:])
            entry.update(result=p.stdout.decode().strip(),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry);print(name,entry['result'],flush=True)
    for name,old,new in [('no-delete','a[u].present = false;','a[u].present = true;'),('lose-id','a[u].item = item;','a[u].item = item;\n        a[u].item.id = 0;'),('lose-free-slot','free.push_back(u);','/* slot lost */')]:
        assert copied.count(old)==1
        exe,entry=compile(name,copied.replace(old,new),['-DNDEBUG'])
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry.update(independent_oracle_rejected=True);report['mutants'].append(entry);print(name,'ORACLE_REJECT',flush=True)
    for example,cases in [('example-270',extract_cases()),('example-271',move_cases())]:
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
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('kd-extract',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
