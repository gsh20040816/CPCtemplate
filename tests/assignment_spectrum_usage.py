#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from compiler_config import CXX
from assignment_spectrum import oracle, validate
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from usage_examples import records
from audit_copy_context import candidate, extract_components

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--sanitize',action='store_true')
    args=ap.parse_args()
    mode='sanitizer' if args.sanitize else 'normal'
    out=ROOT/'build/assignment-spectrum'/('usage-'+mode)
    out.mkdir(parents=True,exist_ok=True)
    sha=lambda x:hashlib.sha256(x).hexdigest()
    rows=[r for r in records() if r['id'] in ('example-332','example-333','example-334')]
    components={r['symbol']:r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    flags=['-std=c++20','-O1' if args.sanitize else '-O2']
    if args.sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
    paths=['src/compact/assignment_spectrum.hpp','tests/assignment_spectrum_usage.py','tests/assignment_spectrum.py','tools/usage_examples.py','tools/audit_copy_context.py','docs/usage-examples.json']+[r['driver'] for r in rows]
    snapshot={p:sha((ROOT/p).read_bytes()) for p in paths}
    rng=random.Random(20261009)
    api=[]
    applications=[]
    for _ in range(100):
        n,m=rng.randrange(7),rng.randrange(7)
        edges=[(x,y,rng.randrange(-10**9,10**9+1)) for x in range(n) for y in range(m) if rng.randrange(3)]
        limit=rng.randrange(min(n,m)+2)
        best=oracle(n,m,edges)
        data=f'{n} {m} {len(edges)} {limit}\n'+''.join(f'{x} {y} {w}\n' for x,y,w in edges)
        api.append((data,(n,m,edges,limit,best)))
        edges=[(x,y,abs(w) or 1) for x,y,w in edges]
        if not edges:edges=[(0,0,1)];n=max(1,n);m=max(1,m)
        edges+=edges[:3]
        best=oracle(n,m,edges)
        data=str(len(edges))+'\n'+''.join(f'{x+1} {y+1} {w}\n' for x,y,w in edges)
        applications.append((data,[len(best)-1]+best[1:]))
    applications += [
        ('3\n1 1 100\n1 20 10\n2 1 1\n',[2,100,11]),
        ('10\n1 4 142135623\n2 6 457513110\n3 1 622776601\n5 1 961524227\n2 2 360679774\n2 4 494897427\n3 7 416573867\n5 2 915026221\n1 7 320508075\n5 3 851648071\n',[4,961524227,1537802822,2032700249,2353208324]),
        ('30000\n'+''.join(f'{i%150+1} {i%150+1} 1000000000\n' for i in range(30000)),[150]+[i*10**9 for i in range(1,151)])
    ]
    formal=[]
    for trial in range(100):
        n=rng.randrange(1,8)
        edges=[(x,y,rng.randrange(-19980731,19980732)) for x in range(n) for y in range(n) if x==y or rng.randrange(2)]
        expected=oracle(n,n,edges)[n]
        data=f'{n} {len(edges)}\n'+''.join(f'{x+1} {y+1} {w}\n' for x,y,w in edges)
        formal.append((data,(n,edges,expected)))
    n=500
    edges=[(x,y,19980731 if x==y else -19980731) for x in range(n) for y in range(n)]
    data=f'{n} {len(edges)}\n'+''.join(f'{x+1} {y+1} {w}\n' for x,y,w in edges)
    formal.append((data,(n,edges,n*19980731)))
    report=[]
    for row in rows:
        for form in ('header','ndebug','expanded','copied'):
            source=ROOT/row['driver']
            exe=out/(row['id']+'-'+form)
            if form in ('expanded','copied'):
                source=exe.with_suffix('.cpp')
                program=row['program'] if form=='expanded' else candidate(row,row['requires'],components)['program']
                source.write_text(program)
            command=[CXX,*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(source),'-o',str(exe)]
            subprocess.run(command,check=True,capture_output=True)
            cases={'example-332':api,'example-333':applications,'example-334':formal}[row['id']]
            outputs=[]
            for data,expected in cases:
                proc=subprocess.run([str(exe)],input=data,text=True,capture_output=True,timeout=30,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
                assert proc.returncode==0,(row['id'],form,proc.stderr)
                outputs.append(proc.stdout)
                if row['id']=='example-333':
                    assert list(map(int,proc.stdout.split()))==expected
                elif row['id']=='example-334':
                    n,edges,best=expected
                    values=list(map(int,proc.stdout.split()))
                    assert len(values)==n+1 and values[0]==best
                    r=[x-1 for x in values[1:]]
                    assert sorted(r)==list(range(n))
                    graph={(x,y):w for x,y,w in edges}
                    assert all((x,y) in graph for y,x in enumerate(r))
                    assert sum(graph[x,y] for y,x in enumerate(r))==best
                else:
                    n,m,edges,limit,best=expected
                    v=list(map(int,proc.stdout.split()))
                    k=v[0]
                    l=v[k+2:k+2+n]
                    r=[-1]*m
                    for x,y in enumerate(l):
                        if y!=-1:
                            assert r[y]==-1
                            r[y]=x
                    v=v[:k+2+n]+r+v[k+2+n:]
                    validate(expected,' '.join(map(str,v)))
            report.append(dict(id=row['id'],form=form,cases=len(cases),program_sha256=sha(source.read_bytes()),binary_sha256=sha(exe.read_bytes()),input_sha256=sha(json.dumps([x[0] for x in cases]).encode()),output_sha256=sha(json.dumps(outputs).encode()),command=command))
            print(row['id'],form,len(cases),'PASS',flush=True)
    assert snapshot=={p:sha((ROOT/p).read_bytes()) for p in paths}
    result=dict(mode=mode,snapshot=snapshot,programs=report,official_source='https://atcoder.jp/contests/abc247/tasks/abc247_g',official_samples=2,online_ac=False)
    (ROOT/f'verification/assignment-spectrum-usage-{mode}.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
