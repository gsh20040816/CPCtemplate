#!/usr/bin/env python3
"""Complete-graph Prim, cut certificates, ties and signed64 Manhattan MST."""
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from usage_examples import records
from compiler_config import CXX


def sha(data):
    return hashlib.sha256(data).hexdigest()


def distance(p,q):
    return abs(p[0]-q[0])+abs(p[1]-q[1])


def prim(points):
    n=len(points)
    if not n:return 0
    best=[None]*n;best[0]=0;seen=[False]*n;total=0
    for _ in range(n):
        u=min((i for i in range(n) if not seen[i] and best[i] is not None),key=lambda i:best[i])
        seen[u]=True;total+=best[u]
        for v in range(n):
            if not seen[v]:
                d=distance(points[u],points[v])
                if best[v] is None or d<best[v]:best[v]=d
    return total


def tree_check(points,edges,weight,expected):
    n=len(points);assert len(edges)==max(0,n-1)
    parent=list(range(n));size=[1]*n
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    cost=0
    for u,v in edges:
        assert 0<=u<n and 0<=v<n
        a,b=find(u),find(v);assert a!=b
        if size[a]<size[b]:a,b=b,a
        parent[b]=a;size[a]+=size[b]
        cost+=distance(points[u],points[v])
    assert len({find(i) for i in range(n)})==bool(n)
    assert cost==weight==expected,(cost,weight,expected)


def main():
    if not __debug__:raise RuntimeError('Exact reference checks require assertions')
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='manhattan-mst-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT);cases=[];rng=random.Random(20261003);cache={}
    def add(name,points,expected=None,oracle='complete-graph dense Prim'):
        points=list(points)
        if expected is None:
            key=tuple(sorted(points))
            if key not in cache:cache[key]=prim(points)
            expected=cache[key]
        cases.append(dict(name=name,points=points,expected=expected,oracle=oracle))
    grid=list(itertools.product(range(-1,2),repeat=2))
    for n in range(7):
        for k,ids in enumerate(itertools.combinations_with_replacement(range(9),n)):
            p=[grid[i] for i in ids];add(f'grid-{n}-{k}',p)
            if n>1:
                rng.shuffle(p);add(f'shuffled-grid-{n}-{k}',p)
    for p in [[(0,0),(2,0),(1,1)],[(0,0),(2,2),(4,0)],[(0,0),(2,-2),(4,0)]]:
        for k,q in enumerate(itertools.permutations(p)):add(f'closed-boundary-{p}-{k}',q)
    lo,hi=-(1<<63),(1<<63)-1
    special=[lo,lo+1,-1,0,1,hi-1,hi]
    for k in range(300):
        n=rng.randrange(41)
        p=[(rng.choice(special),rng.choice(special)) if k%3==0 else
           (rng.randrange(-50,51),rng.randrange(-50,51)) for _ in range(n)]
        add(f'random-{k}',p)
        if k<50:
            add(f'axis-swap-{k}',[(y,x) for x,y in p])
            add(f'complement-reflection-{k}',[(-x-1,-y-1) for x,y in p])
    add('signed64-corners',itertools.product([lo,hi],repeat=2))
    add('signed64-near-center',[(lo,lo),(hi,hi),(lo,hi),(hi,lo),(-1,-1),(0,0)])
    n=200000
    add('large-horizontal',((i,0) for i in range(n)),n-1,'ordered adjacent unit gaps and projection lower bound')
    add('large-antidiagonal',((i,1000000000-i) for i in range(n)),2*(n-1),'ordered adjacent gaps of2 and projection lower bound')
    add('large-fullwidth-vertical',((0,-9000000000000000000+i*90000000000000) for i in range(n)),(n-1)*90000000000000,'ordered adjacent exact signed64 gaps; total exceeds signed64')
    add('large-identical-extreme',[(lo,hi)]*n,0,'all pair distances zero')
    add('large-unit-grid',((i%400,i//400) for i in range(n)),n-1,'unit-edge spanning grid and positive integer distance lower bound')
    add('large-two-clusters',[(0,0)]*(n//2)+[(1000000000,1000000000)]*(n//2),2000000000,'zero intra-cluster edges and one mandatory inter-cluster edge')
    # Record data independently of the C++ implementation; no candidate algorithm in oracle.
    data=str(len(cases))+'\n'
    for t in cases:data+=str(len(t['points']))+'\n'+''.join(f'{x} {y}\n' for x,y in t['points'])
    (out/'cases.in').write_text(data)
    (out/'expected.json').write_text(json.dumps([{k:v for k,v in t.items() if k!='points'} for t in cases],indent=2)+'\n')
    components={x['symbol']:x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    prelude='#include <algorithm>\n#include <cassert>\n#include <climits>\n#include <iostream>\n#include <map>\n#include <numeric>\n#include <string>\n#include <tuple>\n#include <utility>\n#include <vector>\nusing namespace std;\n'
    core=components['dsu']+'\n'+components['ManhattanMST']
    probe=(ROOT/'tests/manhattan_mst_probe.cpp').read_text()
    copied=prelude+core+'\n'+'\n'.join(probe.splitlines()[1:])
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),flags=flags,input_sha256=sha(data.encode()),environment={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')},programs=[],mutants=[])
    def check(output,selected=cases):
        lines=iter(output.decode().splitlines());cuts=0
        for t in selected:
            p=t['points'];n=len(p)
            header=list(map(int,next(lines).split()));assert len(header)==6
            nn,w,m,k,unchanged,repeat=header
            assert nn==n and m==max(0,n-1) and unchanged==repeat==1
            edges=[tuple(map(int,next(lines).split())) for _ in range(m)]
            assert all(len(e)==2 for e in edges)
            tree_check(p,edges,w,t['expected'])
            assert 0<=k<=4*max(0,n-1)
            candidates=[tuple(map(int,next(lines).split())) for _ in range(k)]
            for e in candidates:
                assert len(e)==3
                d,u,v=e;assert 0<=u<n and 0<=v<n and u!=v
                assert d==distance(p[u],p[v])
            if n<=8:
                complete=[(distance(p[u],p[v]),u,v) for u in range(n) for v in range(u)]
                for mask in range(1,1<<max(0,n-1)):
                    crosses=lambda u,v:bool((mask>>u)&1)!=bool((mask>>v)&1)
                    assert min(d for d,u,v in candidates if crosses(u,v))==min(d for d,u,v in complete if crosses(u,v))
                    cuts+=1
            else:assert k==0
        assert next(lines,None) is None
        return cuts
    for form,text in [('header','#include "'+str(ROOT/'tests/manhattan_mst_probe.cpp')+'"\n'),('copied',copied)]:
        for ndebug in (False,True):
            name=form+('-ndebug' if ndebug else '-assert');cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(text)
            cmd=[CXX,*flags,*(['-DNDEBUG'] if ndebug else []),str(cpp),'-o',str(exe)]
            subprocess.run(cmd,check=True,capture_output=True)
            run=subprocess.run([str(exe)],input=data.encode(),capture_output=True,env=env,timeout=600)
            assert run.returncode==0 and not run.stderr,(name,run.returncode,run.stderr[-1000:])
            cuts=check(run.stdout);(out/(name+'.out')).write_bytes(run.stdout)
            report['programs'].append(dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),output_sha256=sha(run.stdout),cases=len(cases),cut_minimum_certificates=cuts,large_cases=6,repeat_checked='n<=8 only'))
    # Keep mutation inputs small; the independent oracle is otherwise unchanged.
    selected=cases[:40]+[t for t in cases if t['name'].startswith('closed-boundary') or t['name']=='signed64-corners']
    negative_data=str(len(selected))+'\n'+''.join(str(len(t['points']))+'\n'+''.join(f'{x} {y}\n' for x,y in t['points']) for t in selected)
    (out/'mutations.in').write_text(negative_data)
    mutations=[('missing-direction','dir < 4','dir < 3'),('strict-diagonal','if (dx < dy)','if (dx <= dy)'),('skip-equal-y','sweep.lower_bound(','sweep.upper_bound('),('wrong-weight','dx + dy, i, j','dx - dy, i, j'),('narrow-coordinates','vector<int> id(n);','for (auto &[x, y] : p) x = int(x), y = int(y);\n        vector<int> id(n);')]
    for name,old,new in mutations:
        assert copied.count(old)==1
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(copied.replace(old,new))
        subprocess.run([CXX,*flags,str(cpp),'-o',str(exe)],check=True,capture_output=True)
        run=subprocess.run([str(exe)],input=negative_data.encode(),capture_output=True,env=env,timeout=30)
        rejected=run.returncode!=0
        if rejected:assert b'r.edges.size() == points.size() - 1' in run.stderr,run.stderr
        else:
            assert not run.stderr
            try:check(run.stdout,selected)
            except (AssertionError,ValueError,StopIteration):rejected=True
        assert rejected,name
        (out/(name+'.out')).write_bytes(run.stdout);(out/(name+'.stderr')).write_bytes(run.stderr)
        report['mutants'].append(dict(name=name,returncode=run.returncode,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),output_sha256=sha(run.stdout),stderr_sha256=sha(run.stderr),rejected=True))
    report.update(source_after_sha256=snapshot(ROOT),passed=True,scope='Complete-graph Prim and cut oracles plus six large closed-form families. Empty/full signed64 cases are API extensions, not online AC or full-suite certification; no LSan claim.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Manhattan MST {mode}: {len(cases)} point sets x four forms, {cuts} small cuts per form PASS; {out.relative_to(ROOT)}/report.json')


if __name__=='__main__':main()
