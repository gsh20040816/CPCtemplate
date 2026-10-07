#!/usr/bin/env python3
"""Enumerate matchings and independently check every fixed-cardinality LP certificate."""
import argparse
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]

def oracle(n, m, edges):
    rows = [dict() for _ in range(n)]
    for x,y,w in edges:
        rows[x][y] = max(rows[x].get(y,w), w)
    best = [None] * (min(n,m)+1)
    def dfs(x, used, k, value):
        if x == n:
            if best[k] is None or best[k] < value:
                best[k] = value
            return
        dfs(x+1, used, k, value)
        for y,w in rows[x].items():
            if not (used >> y & 1):
                dfs(x+1, used | (1<<y), k+1, value+w)
    dfs(0,0,0,0)
    while best[-1] is None:
        best.pop()
    return best

def validate(case, line):
    n,m,edges,limit,expected = case
    values = list(map(int,line.split()))
    k = values.pop(0)
    assert k == min(limit,len(expected)-1), (case,k)
    assert values[:k+1] == expected[:k+1], (case,values[:k+1])
    values = values[k+1:]
    l,r = values[:n],values[n:n+m]
    h = values[n+m]
    lx,ly = values[n+m+1:n+m+1+n],values[n+m+1+n:]
    assert len(ly)==m
    graph = {}
    for x,y,w in edges:
        graph[x,y] = max(graph.get((x,y),w),w)
    assert sum(y != -1 for y in l)==k and sum(x != -1 for x in r)==k
    total=0
    for x,y in enumerate(l):
        assert -1 <= y < m
        assert lx[x]>=h
        if y==-1:
            assert lx[x]==h
        else:
            assert r[y]==x and (x,y) in graph
            assert lx[x]+ly[y]==graph[x,y]
            total+=graph[x,y]
    for y,x in enumerate(r):
        assert -1 <= x < n and ly[y]>=0
        if x==-1:
            assert ly[y]==0
        else:
            assert l[x]==y
    for (x,y),w in graph.items():
        assert lx[x]+ly[y]>=w
    assert total==expected[k]
    assert sum(v-h for v in lx)+sum(ly)+k*h==total
    # Discrete concavity is a useful necessary property, not the oracle.
    assert all(expected[j]-expected[j-1]>=expected[j+1]-expected[j] for j in range(1,len(expected)-1))

def cases():
    rng=random.Random(20261008)
    result=[]
    for n in range(4):
        for m in range(4):
            for a in it.product((None,-2,3),repeat=n*m):
                e=[(x,y,a[x*m+y]) for x in range(n) for y in range(m) if a[x*m+y] is not None]
                expected=oracle(n,m,e)
                for limit in range(min(n,m)+1):
                    result.append((n,m,e,limit,expected))
    for _ in range(450):
        n,m=rng.randrange(7),rng.randrange(7)
        e=[]
        for x in range(n):
            for y in range(m):
                if rng.randrange(3):
                    w=rng.choice((-(1<<63),(1<<63)-1,-10**9,-1,0,1,10**9))
                    e.append((x,y,w))
                    if rng.randrange(3)==0:
                        e.append((x,y,rng.randrange(-50,51)))
        expected=oracle(n,m,e)
        for limit in range(min(n,m)+2):
            result.append((n,m,e,limit,expected))
    n=180
    e=[(x,y,10**15+x if x==y else -10**15) for x in range(n) for y in range(n)]
    expected=[0]
    for k in range(1,n+1):
        expected.append(k*10**15+k*(2*n-k-1)//2)
    result.append((n,n,e,n,expected))
    # Many isolated vertices and a non-square graph with maximum cardinality 1.
    result.append((300,170,[(299,169,-(1<<63))],170,[0,-(1<<63)]))
    return result

def pack(cases):
    return str(len(cases))+'\n'+''.join(f'{n} {m} {len(e)} {limit}\n'+''.join(f'{x} {y} {w}\n' for x,y,w in e) for n,m,e,limit,_ in cases)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--sanitize',action='store_true')
    args=ap.parse_args()
    mode='sanitizer' if args.sanitize else 'normal'
    out=ROOT/'build/assignment-spectrum'/mode
    out.mkdir(parents=True,exist_ok=True)
    sha=lambda x:hashlib.sha256(x).hexdigest()
    tracked=['src/compact/assignment_spectrum.hpp','tests/assignment_spectrum_probe.cpp','tests/assignment_spectrum.py','tests/fixtures/assignment_spectrum_sources/wida.inc']
    snapshot={p:sha((ROOT/p).read_bytes()) for p in tracked}
    flags=['-std=c++20','-O1' if args.sanitize else '-O2']
    if args.sanitize:
        flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
    dataset=cases()
    data=pack(dataset)
    reports=[]
    def run(name,program,data):
        source=out/(name+'.cpp')
        source.write_text(program)
        exe=source.with_suffix('')
        command=[CXX,*flags,str(source),'-o',str(exe)]
        subprocess.run(command,check=True,capture_output=True)
        proc=subprocess.run([str(exe)],input=data,text=True,capture_output=True,timeout=180,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
        assert proc.returncode==0,(name,proc.stderr[-3000:])
        reports.append(dict(name=name,program_sha256=sha(program.encode()),input_sha256=sha(data.encode()),output_sha256=sha(proc.stdout.encode()),binary_sha256=sha(exe.read_bytes()),command=command))
        return proc.stdout
    program=(ROOT/'tests/assignment_spectrum_probe.cpp').read_text().replace('#include "../src/compact/assignment_spectrum.hpp"',(ROOT/'src/compact/assignment_spectrum.hpp').read_text())
    for form in ('assert','ndebug'):
        result=run('probe-'+form,('#define NDEBUG\n' if form=='ndebug' else '')+program,data).splitlines()
        assert len(result)==len(dataset)
        for case,line in zip(dataset,result):validate(case,line)
        print(form,len(dataset),'independent optimum/witness/certificate cases PASS',flush=True)
    mutants=[('single-root','                    relax(x);','                {\n                    relax(x);\n                    break;\n                }'),('no-reverse-cost','answer -= w[x][old];','answer -= 0;'),('wrong-slack-sign','lx[x] + ly[y] - w[x][y]','lx[x] + ly[y] + w[x][y]')]
    small=dataset[:1000]+[c for c in dataset if c[0]==3 and c[1]==3][:5000]
    mutation_results=[]
    for name,old,new in mutants:
        assert old in program
        result=run('mutant-'+name,program.replace(old,new,1),pack(small)).splitlines()
        detected=0
        for case,line in zip(small,result):
            try:validate(case,line)
            except AssertionError:detected+=1
        assert detected,name
        mutation_results.append(dict(name=name,detected=detected))
    # Upstream supports complete nonnegative nx<=ny inputs only.
    source_cases=[]
    for n,m in ((0,0),(0,3),(1,3),(2,2),(2,3),(3,3)):
        for a in it.product((0,1,3),repeat=n*m):
            e=[(x,y,a[x*m+y]) for x in range(n) for y in range(m)]
            source_cases.append((n,m,e,oracle(n,m,e)))
    raw=(ROOT/'tests/fixtures/assignment_spectrum_sources/wida.inc').read_text()
    prefix='#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'
    driver=r'''
int main() {
 int t; cin >> t;
 while(t--) {
  int n,m; cin>>n>>m;
  vector<vector<long long>> a(n,vector<long long>(m));
  for(auto &row:a) for(auto &v:row) cin>>v;
  MaxAssignment<long long> g;
  auto answer=g.solve(n,m,a);
  cout<<answer<<' ';
  for(auto v:g.weights()) cout<<v<<' ';
  for(auto v:g.assignment()) cout<<v<<' ';
  auto [lx,ly]=g.labels();
  for(auto v:lx) cout<<v<<' ';
  for(auto v:ly) cout<<v<<' ';
  cout<<'\n';
 }
}
'''
    source_input=str(len(source_cases))+'\n'+''.join(f'{n} {m}\n'+' '.join(str(w) for _,_,w in e)+'\n' for n,m,e,_ in source_cases)
    result=run('wida-source',prefix+raw+driver,source_input).splitlines()
    assert len(result)==len(source_cases)
    for (n,m,e,expected),line in zip(source_cases,result):
        v=list(map(int,line.split()))
        assert v[0]==expected[-1] and v[1:n+2]==expected
        l=v[n+2:2*n+2];lx=v[2*n+2:3*n+2];ly=v[3*n+2:]
        assert len(set(l))==n and len(ly)==m
        assert sum(lx)+sum(ly)==expected[-1] and all(x>=0 for x in ly)
        for x,y,w in e:
            assert lx[x]+ly[y]>=w
            if l[x]==y:assert lx[x]+ly[y]==w
    print(len(source_cases),'complete upstream matrices PASS',flush=True)
    assert snapshot=={p:sha((ROOT/p).read_bytes()) for p in tracked}
    report=dict(mode=mode,cases=len(dataset),source_cases=len(source_cases),snapshot=snapshot,programs=reports,mutants=mutation_results,online_ac=False)
    (ROOT/f'verification/assignment-spectrum-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
