#!/usr/bin/env python3
"""Deletion-reachability oracle, full API lifecycle, integration and handwriting copies."""
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

def oracle(n,edges,root):
    g=[[] for _ in range(n)]
    for u,v in edges:
        g[u].append(v)
    def reach(removed):
        seen=set() if root==removed else {root}
        q=list(seen)
        for u in q:
            for v in g[u]:
                if v!=removed and v not in seen:
                    seen.add(v);q.append(v)
        return seen
    seen=reach(-1)
    dom=[set() for _ in range(n)]
    for u in range(n):
        for v in seen-reach(u):
            dom[v].add(u)
    return [root if v==root else max(dom[v]-{v},key=lambda u:len(dom[u])) if v in seen else -1 for v in range(n)]

def disaster(n,edges):
    pred=[set() for _ in range(n)]
    for u,v in edges:
        pred[v].add(u)
    ans=[]
    for removed in range(n):
        dead={removed}
        while True:
            nxt=dead|{v for v in range(n) if pred[v] and pred[v]<=dead}
            if nxt==dead:
                break
            dead=nxt
        ans.append(len(dead)-1)
    return ans

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sanitize',action='store_true');args=ap.parse_args()
    mode='sanitizer' if args.sanitize else 'normal'
    out=ROOT/'build/dag-dominator'/mode;out.mkdir(parents=True,exist_ok=True)
    rows=[r for r in records() if r['symbol']=='DagDominator']
    sha=lambda data:hashlib.sha256(data).hexdigest()
    paths=['src/compact/dag_dominator.hpp','src/compact/dominator_tree.hpp','tests/dag_dominator.cpp','tests/dag_dominator.py','docs/usage-examples.json','docs/catalog.json','tools/usage_examples.py','tools/audit_copy_context.py']+[r['driver'] for r in rows]
    snapshot={p:sha((ROOT/p).read_bytes()) for p in paths}
    flags=['-std=c++20','-O1' if args.sanitize else '-O2']
    if args.sanitize:
        flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
    env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'}
    def compile(src,exe,extra=()):
        p=subprocess.run([CXX,*flags,*extra,str(src),'-o',str(exe)],text=True,capture_output=True)
        assert p.returncode==0,p.stderr
    def run(exe,data='',timeout=180):
        p=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,timeout=timeout)
        assert p.returncode==0,p.stderr
        return list(map(int,p.stdout.split()))
    core=[]
    for form in ('normal','ndebug'):
        exe=out/('core-'+form);compile(ROOT/'tests/dag_dominator.cpp',exe,['-DNDEBUG'] if form=='ndebug' else [])
        core.append(run(exe)[0]);assert core[-1]>200000
    rng=random.Random(20261010)
    api=[];formal=[];application=[]
    for trial in range(150):
        n=rng.randrange(1,16);root=rng.randrange(n);perm=list(range(n));rng.shuffle(perm)
        edges=[(perm[i],perm[j]) for i in range(n) for j in range(i+1,n) if rng.randrange(3)==0]
        parents=oracle(n,edges,root)
        input_api=f'{n} {len(edges)} {root+1}\n'+''.join(f'{u+1} {v+1}\n' for u,v in edges)
        api.append((input_api,[x+1 for x in parents]))
        incoming=[[u+1 for u,v in edges if v==i] for i in range(n)]
        app=str(n)+'\n'+''.join(' '.join(map(str,row+[0]))+'\n' for row in incoming)
        application.append((app,disaster(n,edges)))
        if trial%2:
            edges += [(rng.randrange(n),rng.randrange(n)) for _ in range(n)]
        formal.append((f'{n} {len(edges)} {root}\n'+''.join(f'{u} {v}\n' for u,v in edges),oracle(n,edges,root)))
    api.extend([('3 2 1\n2 3\n3 2\n',[-1]),('1 1 1\n1 1\n',[-1]),('4 4 1\n1 3\n1 3\n2 3\n3 4\n',[1,0,1,3])])
    n=200000
    formal.append((f'{n} {n-1} {n-1}\n'+''.join(f'{i} {i-1}\n' for i in range(1,n)),[min(i+1,n-1) for i in range(n)]))
    # A large cyclic component forces LT fallback without a deep DFS on this host.
    formal.append((f'{n} {n} 0\n0 0\n'+''.join(f'0 {i}\n' for i in range(1,n)),[0]*n))
    n=65534
    application.append((str(n)+'\n0\n'+''.join(f'{i} 0\n' for i in range(1,n)),list(range(n-1,-1,-1))))
    components={r['symbol']:r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    programs=[]
    for row in rows:
        cases={'example-338':api,'example-339':formal,'example-340':application}[row['id']]
        for form in ('header','ndebug','expanded','copied'):
            exe=out/(row['id']+'-'+form);src=ROOT/row['driver']
            if form in ('expanded','copied'):
                src=exe.with_suffix('.cpp')
                src.write_text(row['program'] if form=='expanded' else candidate(row,row['requires'],components)['program'])
            compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
            for data,want in cases:
                assert run(exe,data)==want,(row['id'],form,data[:150])
            programs.append(dict(id=row['id'],form=form,cases=len(cases),program_sha256=row['program_sha256'] if form=='expanded' else sha(src.read_bytes())))
    mutants=[]
    if not args.sanitize:
        source=candidate(rows[0],rows[0]['requires'],components)['program']
        changes=[('last-predecessor','idom[v] = lca(idom[v], u);','idom[v] = u;'),('unreachable-predecessor','if (!idom[u])\n                continue;','if (!idom[u])\n                idom[u] = root;'),('cycle-accepted','if ((int)order.size() != n)','if (false)'),('root-lost','idom[root] = root;','idom[root] = 0;')]
        for name,old,new in changes:
            assert old in source
            src=out/(name+'.cpp');src.write_text(source.replace(old,new));exe=src.with_suffix('');compile(src,exe)
            for data,want in api:
                if run(exe,data)!=want:
                    break
            else:
                raise AssertionError(name)
            mutants.append(name)
    assert all(sha((ROOT/p).read_bytes())==v for p,v in snapshot.items())
    report=dict(mode=mode,core_cases=core,programs=programs,mutants=mutants,snapshot=snapshot,oracle='Vertex deletion reachability for dominators; transitive closure cycle detection; extinction fixed point for application.',online_ac=False)
    (ROOT/f'verification/dag-dominator-{mode}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('snapshot','programs')},ensure_ascii=False),flush=True)
if __name__=='__main__':
    main()
