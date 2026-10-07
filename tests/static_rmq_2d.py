#!/usr/bin/env python3
"""Two-dimensional static RMQ: independent rectangle scan, stable positions and corners source model."""
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
    rng=random.Random(279);cases=[];pool=[-(1<<63),-1,0,1,(1<<63)-1]
    for test in range(60):
        n=1+test%14;m=1+test%11;a=[[rng.choice(pool) for _ in range(m)] for _ in range(n)];ops=[];want=[]
        for step in range(100):
            x1=rng.randrange(n);y1=rng.randrange(m);x2=rng.randrange(x1+1,n+1);y2=rng.randrange(y1+1,m+1)
            points=[(x,y) for x in range(x1,x2) for y in range(y1,y2)]
            lo=min(points,key=lambda t:(a[t[0]][t[1]],t));hi=min(points,key=lambda t:(-a[t[0]][t[1]],t))
            want.extend([*lo,*hi]);ops.append(f'{x1} {y1} {x2} {y2}')
        raw=f'{n} {m} {len(ops)}\n'+''.join(' '.join(map(str,row))+'\n' for row in a)+'\n'.join(ops)+'\n'
        cases.append((f'api-{test}',raw,want))
    cases.extend([('empty','0 0 0\n',[]),('zero-cols','3 0 0\n',[])])
    return cases


def corner_cases():
    rng=random.Random(280);cases=[]
    for test in range(60):
        inputs=[];want=[]
        for dataset in range(3):
            n=1+test%13;m=1+test%9;a=[[rng.randrange(-5,6) for _ in range(m)] for _ in range(n)];ops=[]
            for step in range(100):
                x1,x2=rng.randrange(n),rng.randrange(n);y1,y2=rng.randrange(m),rng.randrange(m)
                ops.append(f'{x1+1} {y1+1} {x2+1} {y2+1}')
                x1,x2=sorted([x1,x2]);y1,y2=sorted([y1,y2])
                best=max(a[x][y] for x in range(x1,x2+1) for y in range(y1,y2+1))
                want.extend([best,'yes' if best in [a[x1][y1],a[x1][y2],a[x2][y1],a[x2][y2]] else 'no'])
            inputs.append(f'{n} {m}\n'+''.join(' '.join(map(str,row))+'\n' for row in a)+str(len(ops))+'\n'+'\n'.join(ops)+'\n')
        cases.append((f'corners-{test}',''.join(inputs),want))
    n=m=305;grid=[[x*m+y for y in range(m)] for x in range(n)];ops=[];want=[]
    for i in range(100000):
        x1,x2=sorted([i%n,(i*13+1)%n]);y1,y2=sorted([(i*3)%m,(i*17+1)%m])
        ops.append(f'{x1+1} {y1+1} {x2+1} {y2+1}');want.extend([grid[x2][y2],'yes'])
    raw=f'{n} {m}\n'+''.join(' '.join(map(str,row))+'\n' for row in grid)+str(len(ops))+'\n'+'\n'.join(ops)+'\n'
    cases.append(('305-square-100000-queries',raw,want))
    return cases


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='static-rmq-2d-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT)
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    header=(ROOT/'src/compact/static_rmq_2d.hpp').read_text().replace('#pragma once\n','')
    probe=(ROOT/'tests/static_rmq_2d_probe.cpp').read_text()
    copied=header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='Independent full rectangle scan, binary-grid exhaustion, stable min/max positions and 305-square analytic stress; kuangbin corners source model only, no original judge or online verdict claim.')
    def compile(name,source,extra=()):
        cpp=out/(name+'.cpp');exe=out/name;cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    for form,source in [('header','#include "'+str(ROOT/'tests/static_rmq_2d_probe.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            name=form+('-ndebug' if release else '-assert')
            exe,entry=compile(name,source,['-DNDEBUG'] if release else [])
            start=time.monotonic();p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
            assert p.returncode==0 and not p.stderr and p.stdout.startswith(b'PASS '),(name,p.returncode,p.stdout,p.stderr[-1000:])
            entry.update(result=p.stdout.decode().strip(),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry);print(name,entry['result'],flush=True)
    for name,old,new in [
        ('wrong-tie','return min(x, y);','return max(x, y);'),
        ('vertical-self','id + (1 << (k - 1)) * m','id'),
        ('horizontal-self','id + (1 << (l - 1))','id'),
        ('omit-bottom','int id = better(top, bottom);','int id = top;'),
        ('omit-right','y2 -= 1 << l;','y2 = y1;')]:
        assert header.count(old)==1
        exe,entry=compile(name,copied.replace(old,new,1),['-DNDEBUG'])
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry.update(independent_oracle_rejected=True);report['mutants'].append(entry);print(name,'ORACLE_REJECT',flush=True)
    for example,cases in [('example-279',api_cases()),('example-280',corner_cases())]:
        row=next(r for r in records() if r['id']==example)
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('minimal-copy','#include <iostream>\n'+header+'\n'+row['snippet'])]:
            exe,entry=compile(example+'-'+form,source)
            for name,raw,want in cases:
                start=time.monotonic();p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=300)
                assert p.returncode==0 and not p.stderr,(example,form,name,p.returncode,p.stderr[-1000:])
                assert p.stdout.decode().split()==list(map(str,want)),(example,form,name)
                entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start,passed=True))
            report['programs'].append(entry);print(example,form,len(cases),'PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('static-rmq-2d',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
