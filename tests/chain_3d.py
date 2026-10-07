#!/usr/bin/env python3
"""Three-dimensional chain DP: independent oracles, copied forms and source model."""
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


def chain_cases():
    rng=random.Random(272)
    cases=[]
    pool=[-(1<<63),-1,0,1,(1<<63)-1]
    for test in range(100):
        n=test%31;mod=[1,2,17,1<<30,(1<<31)-1][test%5];strict=test%2
        p=[tuple(rng.choice(pool) for _ in range(3)) for _ in range(n)]
        order=sorted(range(n),key=lambda i:(p[i],i))
        length=[1]*n;ways=[1%mod]*n;parent=[-1]*n
        for v in order:
            for u in order:
                ok=all(p[u][d]<p[v][d] if strict else p[u][d]<=p[v][d] for d in range(3))
                if not ok or (not strict and (p[u],u)>=(p[v],v)):continue
                if length[u]+1>length[v]:length[v]=length[u]+1;ways[v]=ways[u];parent[v]=u
                elif length[u]+1==length[v]:ways[v]=(ways[v]+ways[u])%mod;parent[v]=min(parent[v],u)
        best=max(length,default=0);ends=[i for i in range(n) if length[i]==best]
        count=sum(ways[i] for i in ends)%mod if n else 1%mod
        path=[];v=ends[0] if ends else -1
        while v!=-1:path.append(v);v=parent[v]
        want=[best,count,*reversed(path)]
        for i in range(n):want.extend([length[i],ways[i],parent[i]])
        raw=f'{n} {mod} {strict}\n'+''.join(' '.join(map(str,v))+'\n' for v in p)
        cases.append((f'chain-{test}',raw,want))
    return cases


def source_cases():
    cases=[]
    for name,raw,want in chain_cases():
        lines=raw.splitlines();n,mod,strict=map(int,lines[0].split())
        if not n:continue
        p=[tuple(map(int,line.split())) for line in lines[1:]]
        states=[]
        for v in sorted(p):
            old=[state for q,state in states if all(q[d]<=v[d] for d in range(3))]
            length=max((s[0] for s in old),default=0)
            ways=sum(s[1] for s in old if s[0]==length)%(1<<30) if old else 1
            states.append((v,(length+1,ways)))
        length=max(s[0] for q,s in states)
        count=sum(s[1] for q,s in states if s[0]==length)%(1<<30)
        cases.append((name,'1\n'+str(n)+'\n'+'\n'.join(lines[1:])+'\n',[length,count]))
    return cases


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='chain-3d-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT)
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    header=(ROOT/'src/compact/chain_3d.hpp').read_text().replace('#pragma once\n','')
    probe=(ROOT/'tests/chain_3d_probe.cpp').read_text()
    copied=header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='Independent quadratic DAG DP and exhaustive subset chains, original-ID path, strict/weak boundaries and modulus zero; local API/source model only, HDU4742 statement unverified.')
    def compile(name,source,extra=()):
        cpp=out/(name+'.cpp');exe=out/name;cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    for form,source in [('header','#include "'+str(ROOT/'tests/chain_3d_probe.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            name=form+('-ndebug' if release else '-assert')
            exe,entry=compile(name,source,['-DNDEBUG'] if release else [])
            start=time.monotonic();p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
            assert p.returncode==0 and not p.stderr and p.stdout.startswith(b'PASS '),(name,p.returncode,p.stdout,p.stderr[-1000:])
            entry.update(result=p.stdout.decode().strip(),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry);print(name,entry['result'],flush=True)
    for name,old,new in [
        ('right-too-early','self(self, l, mid);','self(self, l, mid);\n            self(self, mid, r);'),
        ('no-x-groups','if (!strict || p[order[i]][0] != p[order[i - 1]][0])','if (true)'),
        ('wrong-y','p[u][1] >= p[v][1]','p[u][1] > p[v][1]'),
        ('wrong-z','z[v] - strict','z[v]'),
        ('no-clear','bit[t] = State{};','/* stale */;'),
        ('zero-unreachable','if (!best.len) continue;','if (!best.ways) continue;')]:
        assert copied.count(old)==1
        exe,entry=compile(name,copied.replace(old,new),['-DNDEBUG'])
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=300)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry.update(independent_oracle_rejected=True);report['mutants'].append(entry);print(name,'ORACLE_REJECT',flush=True)
    for example,cases in [('example-272',chain_cases()),('example-273',source_cases())]:
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
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('chain-3d',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
