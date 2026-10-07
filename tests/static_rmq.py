#!/usr/bin/env python3
"""Bitmask RMQ: exhaustive intervals, independent segment tree and fixed source models."""
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


def cases_for(example):
    rng=random.Random(276);cases=[]
    for test in range(70):
        n=1+test*3;a=[rng.randrange(1000000001) for _ in range(n)]
        if example=='example-278':a=[rng.choice([-(1<<63),-1,0,1,(1<<63)-1]) for _ in range(n)]
        intervals=[];want=[]
        for q in range(100):
            l=rng.randrange(n);r=rng.randrange(l+1,n+1);intervals.append((l,r))
            if example=='example-276':want.append(min(a[l:r]))
            elif example=='example-277':want.append(max(a[l:r]))
            else:want.extend([min(range(l,r),key=lambda i:(a[i],i)),min(range(l,r),key=lambda i:(-a[i],i))])
        raw=f'{n} {len(intervals)}\n'+' '.join(map(str,a))+'\n'+''.join(f'{l+(example=="example-277")} {r}\n' for l,r in intervals)
        cases.append((f'rmq-{test}',raw,want))
    if example=='example-278':cases.append(('empty','0 0\n',[]))
    else:
        n,q=(100000,2000000) if example=='example-277' else (500000,500000)
        a=list(range(n));ops=[];want=[]
        for i in range(q):
            l=i%n;r=min(n,l+1+i%1000)
            ops.append(f'{l+(example=="example-277")} {r}\n');want.append(r-1 if example=='example-277' else l)
        cases.append(('official-max-shape',f'{n} {q}\n'+' '.join(map(str,a))+'\n'+''.join(ops),want))
    return cases


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='static-rmq-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT)
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    header=(ROOT/'src/compact/static_rmq.hpp').read_text().replace('#pragma once\n','')
    probe=(ROOT/'tests/static_rmq_probe.cpp').read_text()
    copied=header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='Exhaustive ternary arrays, independent all-interval scan and segment tree, deterministic argmin/argmax ties and stateful comparator; official Static RMQ/P3865 adapters locally checked, no online verdict/rank.')
    def compile(name,source,extra=()):
        cpp=out/(name+'.cpp');exe=out/name;cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    for form,source in [('header','#include "'+str(ROOT/'tests/static_rmq_probe.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            name=form+('-ndebug' if release else '-assert')
            exe,entry=compile(name,source,['-DNDEBUG'] if release else [])
            start=time.monotonic();p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
            assert p.returncode==0 and not p.stderr and p.stdout.startswith(b'PASS '),(name,p.returncode,p.stdout,p.stderr[-1000:])
            entry.update(result=p.stdout.decode().strip(),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry);print(name,entry['result'],flush=True)
    for name,old,new in [
        ('wrong-tie','return min(x, y);','return max(x, y);'),
        ('drop-candidates','if (i % b == 0) s = 0;','s = 0;'),
        ('pop-equal','cmp(a[i], a[start + bit_width(s) - 1])','!cmp(a[start + bit_width(s) - 1], a[i])'),
        ('wrong-left-prefix','return l + countr_zero(mask[r - 1] >> (l % b));','return l - l % b + countr_zero(mask[r - 1]);'),
        ('omit-middle','if (x < y)','if (false)')]:
        assert header.count(old)==1
        exe,entry=compile(name,copied.replace(old,new,1),['-DNDEBUG'])
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry.update(independent_oracle_rejected=True);report['mutants'].append(entry);print(name,'ORACLE_REJECT',flush=True)
    for example,cases in [(example,cases_for(example)) for example in ['example-276','example-277','example-278']]:
        row=next(r for r in records() if r['id']==example)
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('minimal-copy','#include <iostream>\n'+header+'\n'+row['snippet'])]:
            exe,entry=compile(example+'-'+form,source)
            for name,raw,want in cases:
                start=time.monotonic();p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=300)
                assert p.returncode==0 and not p.stderr,(example,form,name,p.returncode,p.stderr[-1000:])
                assert list(map(int,p.stdout.split()))==want,(example,form,name)
                entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start,passed=True))
            report['programs'].append(entry);print(example,form,len(cases),'PASS',flush=True)
    print_text=(ROOT/'build/kd-nearest-sources/wida.txt').read_text()
    start=print_text.index('template<class T, class Cmp = less<T>> struct RMQ {',print_text.index('### 基于状压的线性 RMQ 算法'))
    printed=print_text[start:print_text.index('```',start)]
    for source_name,original in [('wida-print',printed),('wida-jiangly',(ROOT/'build/rmq-sources/wida.cpp').read_text())]:
        source='#include <bits/stdc++.h>\nusing namespace std;\n'+original.replace('RMQ','WidaRMQ')+'\n#define CPC_WIDA\n'+copied
        exe,entry=compile(source_name,source)
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
        assert p.returncode==0 and not p.stderr and p.stdout.startswith(b'PASS '),(source_name,p.returncode,p.stdout,p.stderr[-1000:])
        entry.update(result=p.stdout.decode().strip(),output_sha256=sha(p.stdout),upstream_source_sha256=sha(original.encode()))
        report['programs'].append(entry);print(source_name,entry['result'],flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('static-rmq',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
