"""Signed-tree active diameter: independent BFS distances and endpoint certificates."""
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import resource
import subprocess
import sys
import tempfile
import time
from collections import deque
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records


def matrix(n, edges):
    g=[[] for _ in range(n)]
    for u,v,w in edges:g[u].append((v,w));g[v].append((u,w))
    ds=[]
    for s in range(n):
        d=[None]*n;d[s]=0;q=deque([s])
        while q:
            u=q.popleft()
            for v,w in g[u]:
                if d[v] is None:d[v]=d[u]+w;q.append(v)
        ds.append(d)
    return ds


def random_cases(api):
    rng=random.Random(285 if api else 284);cases=[]
    for test in range(70):
        n=1+test%25;edges=[(v,rng.randrange(v),rng.randrange(-1000,1001)) for v in range(1,n)];rng.shuffle(edges)
        ds=matrix(n,edges);on=[not api]*n;ops=[];want=[]
        for step in range(160):
            if step%3:
                u=rng.randrange(n)
                if api:
                    on[u]=bool(rng.randrange(2));ops.append(f'0 {u} {int(on[u])}')
                else:on[u]=not on[u];ops.append(f'C {u+1}')
            else:
                ops.append('1' if api else 'A');vertices=[i for i in range(n) if on[i]]
                best=max((ds[u][v] for u in vertices for v in vertices),default=None)
                if api:want.append((best,vertices))
                else:want.append('They have disappeared.' if best is None else str(best))
        raw=(f'{n} {len(ops)}\n' if api else f'{n}\n')+''.join(f'{u+int(not api)} {v+int(not api)} {w}\n' for u,v,w in edges)
        if not api:raw+=str(len(ops))+'\n'
        raw+='\n'.join(ops)+'\n'
        cases.append((f'random-{test}',raw,(ds,want) if api else '\n'.join(want)+'\n'))
    return cases


def official_cases():
    cases=[('official','3\n1 2 1\n1 3 1\n7\nA\nC 1\nA\nC 2\nA\nC 3\nA\n','2\n2\n0\nThey have disappeared.\n')]
    n=q=100000
    for shape in ['chain','negative-chain','signed-star']:
        edges=[(u-1 if shape!='signed-star' else 0,u,1 if shape=='chain' else -1 if shape=='negative-chain' else 1000 if u%2 else -1000) for u in range(1,n)]
        ops=[];want=[];left=0;on=[True]*n;positive=n//2;count=n
        for i in range(q):
            if i%2==0:
                u=i//2;on[u]=False;count-=1;positive-=u%2;ops.append(f'C {u+1}');left=u+1
            else:
                ops.append('A')
                best=n-1-left if shape=='chain' else 0 if shape=='negative-chain' else 2000 if positive>=2 else 1000 if positive and on[0] else 0
                want.append('They have disappeared.' if not count else str(best))
        raw=str(n)+'\n'+''.join(f'{u+1} {v+1} {w}\n' for u,v,w in edges)+str(q)+'\n'+'\n'.join(ops)+'\n'
        cases.append((shape,raw,'\n'.join(want)+'\n'))
    return cases+random_cases(False)


def check_api(output, expectation):
    ds,want=expectation;lines=output.splitlines();assert len(lines)==len(want)
    for line,(best,active) in zip(lines,want):
        if best is None:assert line=='-1';continue
        vals=list(map(int,line.split()));assert len(vals)==3
        d,u,v=vals;assert u in active and v in active and d==best and ds[u][v]==d


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT);out=Path(tempfile.mkdtemp(prefix='centroid-diameter-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    if platform.system()=='Darwin':flags+=['-Wl,-stack_size,0x20000000']
    else:
        _,hard=resource.getrlimit(resource.RLIMIT_STACK);resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    header=(ROOT/'src/compact/centroid_diameter.hpp').read_text().replace('#pragma once\n','')
    probe=(ROOT/'tests/centroid_diameter_probe.cpp').read_text();copied=header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    sha=lambda x:hashlib.sha256(x).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='Signed tree diameter and certificate, labelled trees, all active subsets, independent BFS distances, signed64 limits, idempotence/copy/rebuild and 100000-vertex recursive stress. QTREE4 full protocol; local evidence only.',local_stack_mib=512)
    def compile(name,source,extra=()):
        cpp=out/(name+'.cpp');cpp.write_text(source);exe=out/name
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True);assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    for form,source in [('header','#include "'+str(ROOT/'tests/centroid_diameter_probe.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            name=form+('-ndebug' if release else '-assert');exe,entry=compile(name,source,['-DNDEBUG'] if release else [])
            start=time.monotonic();p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=600)
            assert p.returncode==0 and not p.stderr and p.stdout.splitlines()[-1].startswith(b'PASS '),(name,p.returncode,p.stdout,p.stderr[-1000:])
            entry.update(result=p.stdout.decode().strip(),elapsed_seconds=time.monotonic()-start,output_sha256=sha(p.stdout));report['programs'].append(entry)
            print(name,entry['result'],flush=True)
    for name,old,new in [
        ('same-branch-twice','auto [y, v, b] = *it;','auto [y, v, b] = *top[c].rbegin();'),
        ('stale-global-best','if (auto old = candidate(c)) best.erase(*old);',';'),
        ('omit-erase','else bag[b].erase({d, u});','else {}'),
        ('no-self-pair','return Item{0, u, u};','return nullopt;'),
        ('ignore-negative-inner-edge','sum(d, w), c, b','sum(d, max(0LL, w)), c, b'),
        ('minimum-global','*best.rbegin();','*best.begin();')]:
        assert header.count(old)==1,(name,old)
        exe,entry=compile(name,copied.replace(old,new),['-DNDEBUG'])
        p=subprocess.run([str(exe),'small-only'],capture_output=True,env=env,timeout=180)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry['independent_oracle_rejected']=True;report['mutants'].append(entry);print(name,'ORACLE_REJECT',flush=True)
    for example,cs in [('example-284',official_cases()),('example-285',random_cases(True))]:
        row=next(r for r in records() if r['id']==example)
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('minimal-copy','#include <iostream>\n'+header+'\n'+row['snippet'])]:
            exe,entry=compile(example+'-'+form,source)
            for name,raw,want in cs:
                start=time.monotonic();p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=180)
                assert p.returncode==0 and not p.stderr,(example,form,name,p.returncode,p.stderr[-1000:])
                if example=='example-285':check_api(p.stdout.decode(),want)
                else:assert p.stdout.decode()==want,(example,form,name,p.stdout[:300],want[:300])
                entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start,passed=True))
            report['programs'].append(entry);print(example,form,len(cs),'PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT));assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
