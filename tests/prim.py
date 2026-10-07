"""Matrix Prim source audit and independent minimum spanning forest certificates."""
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
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records


import itertools

def components(n,e):
    g=[[] for _ in range(n)]
    for u,v,w in e:
        g[u].append(v)
        g[v].append(u)
    label=[-1]*n
    c=0
    for s in range(n):
        if label[s]>=0:
            continue
        label[s]=c
        q=[s]
        for u in q:
            for v in g[u]:
                if label[v]<0:
                    label[v]=c
                    q.append(v)
        c+=1
    return c,label


def optimum(n,e):
    c,label=components(n,e)
    best=None
    for ids in itertools.combinations(range(len(e)),n-c):
        f=[e[i] for i in ids]
        if components(n,f)==(c,label):
            w=sum(x[2] for x in f)
            best=w if best is None else min(best,w)
    assert best is not None
    return c,best


def cases():
    groups={316:[],317:[]}
    rng=random.Random(316317)
    def add(k,name,n,e,known=None):
        c,w=known if known is not None else optimum(n,e)
        if k==316:
            assert c==1
            mat=[[-1]*n for _ in range(n)]
            for u,v,z in e:
                if mat[u][v]==-1 or z<mat[u][v]:
                    mat[u][v]=mat[v][u]=z
            raw=str(n)+'\n'+''.join(' '.join(map(str,row))+'\n' for row in mat)
        else:
            raw=f'{n} {len(e)}\n'+''.join(f'{u} {v} {z}\n' for u,v,z in e)
        groups[k].append((name,raw,n,e,c,w))
    for i in range(100):
        n=1+i%6
        e=[(v-1,v,rng.randrange(11)) for v in range(1,n)]
        e += [(rng.randrange(n),rng.randrange(n),rng.randrange(11)) for _ in range(i%6)]
        add(316,f'connected-{i}',n,e)
        e=[(rng.randrange(n),rng.randrange(n),rng.randrange(-5,6)) for _ in range(i%12)]
        add(317,f'signed-multigraph-{i}',n,e)
    e=[(u,v,2000) for u in range(100) for v in range(u+1,100)]
    add(316,'max-complete',100,e,(1,99*2000))
    add(316,'max-zero-chain',100,[(v-1,v,0) for v in range(1,100)],(1,0))
    add(316,'official-sample',5,[(0,1,2),(0,2,3),(0,3,1),(1,3,4),(2,3,1),(2,4,1),(3,4,3)])
    add(317,'empty',0,[])
    add(317,'negative-wide',4,[(0,1,-(1<<63)),(1,2,-(1<<63)),(0,2,(1<<63)-1)])
    add(317,'positive-wide',3,[(0,1,(1<<63)-1),(1,2,(1<<63)-1)])
    add(317,'minus-one-valid',2,[(0,1,-1)])
    n=2000
    e=[(v,v-1,-(1<<63)) for v in range(n-1,0,-1)]+[(v,v,-(1<<63)) for v in range(n)]
    e.append((0,n-1,(1<<63)-1))
    add(317,'large-chain-and-loops',n,e,(1,-(n-1)*(1<<63)))
    add(317,'large-isolated',n,[],(n,0))
    return groups


def check(k,case,output):
    name,raw,n,e,c,w=case
    if k==316:
        assert output.strip()==str(w),name
        return
    a=list(map(int,output.split()))
    assert a[:2]==[c,w] and len(a)==n+2,name
    pre=a[2:]
    assert sum(p==-1 for p in pre)==c,name
    weights={}
    for u,v,z in e:
        weights[u,v]=weights[v,u]=min(weights.get((u,v),z),z)
    f=[]
    for v,u in enumerate(pre):
        if u==-1:
            continue
        assert 0<=u<n and u!=v and (u,v) in weights,name
        f.append((u,v,weights[u,v]))
        seen=set()
        x=v
        while x!=-1:
            assert 0<=x<n and x not in seen,name
            seen.add(x)
            x=pre[x]
    assert sum(z for u,v,z in f)==w and components(n,f)==components(n,e),name


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='prim-'+mode+'-',dir=ROOT/'build'))
    flags = ['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    if platform.system() == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    else:
        _,hard = resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha = lambda data: hashlib.sha256(data).hexdigest()
    report = dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],local_stack_mib=512,scope='Minimum spanning forests; independent edge subset optimum and spanning certificates. Local only.')
    def compile(name,source,extra=()):
        cpp,exe = out/(name+'.cpp'),out/name
        cpp.write_text(source)
        cmd = [CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p = subprocess.run(cmd,capture_output=True)
        assert p.returncode == 0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    def run(exe,raw='',args=()):
        p = subprocess.run([str(exe),*args],input=raw.encode(),capture_output=True,env=env,timeout=300)
        assert p.returncode == 0 and not p.stderr,(exe,p.returncode,p.stdout[:500],p.stderr[-1000:])
        return p.stdout.decode()
    header=(ROOT/'src/compact/prim.hpp').read_text().replace('#pragma once\n','')
    probe=(ROOT/'tests/prim_probe.cpp').read_text()
    copied=header+'\n'+probe.replace('#include "../src/compact/prim.hpp"','')
    copied=copied.replace('"fixtures/prim_sources/','"'+str(ROOT/'tests/fixtures/prim_sources')+'/')
    for form,source in [('header','#include "'+str(ROOT/'tests/prim_probe.cpp')+'"\n'),('copied',copied)]:
        for release in (False,True):
            exe,entry=compile(form+('-ndebug' if release else '-assert'),source,['-DNDEBUG'] if release else [])
            start=time.monotonic()
            result=run(exe)
            assert result.startswith('PASS '),result
            entry.update(result=result.strip(),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry)
            print(entry['name'],result.strip(),flush=True)
    for name,old,new in [
        ('last-parallel-edge','min(cost[u][v], I(w))','I(w)'),
        ('directed-only','cost[u][v] = cost[v][u] =','cost[u][v] ='),
        ('omit-total-reset','weight = 0;\n        int cnt','/* reset omitted */\n        int cnt'),
        ('omit-parent','pre[v] = u;','pre[v] = -1;'),
        ('drop-negative-edges','cost[u][v] < d[v]','cost[u][v] >= 0 && cost[u][v] < d[v]'),
        ('wrong-component-count','return cnt;','return 1;')]:
        assert old in header,name
        source=copied.replace(header,header.replace(old,new),1)
        exe,entry=compile(name,source,['-DNDEBUG'])
        result=run(exe,args=('small-only',))
        assert result=='ORACLE_REJECT\n',(name,result)
        entry['independent_oracle_rejected']=True
        report['mutants'].append(entry)
        print(name,'ORACLE_REJECT',flush=True)
    groups=cases()
    for k,cs in groups.items():
        row=next(r for r in records() if r['id']==f'example-{k}')
        for form,source,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy','#include <iostream>\n#include <string>\n'+header+'\n'+row['snippet'],[]),('ndebug',row['program'],['-DNDEBUG'])]:
            exe,entry=compile(f'{k}-{form}',source,extra)
            for case in cs:
                output=run(exe,case[1])
                check(k,case,output)
                entry['runs'].append(dict(case=case[0],input_sha256=sha(case[1].encode()),output_sha256=sha(output.encode()),passed=True))
            report['programs'].append(entry)
            print(k,form,len(cs),'PASS',flush=True)
    row=next(r for r in records() if r['id']=='example-316')
    exe,entry=compile('zero-as-absent',row['program'].replace('w != -1','w > 0'),['-DNDEBUG'])
    for case in groups[316]:
        output=run(exe,case[1])
        try:
            check(316,case,output)
        except AssertionError:
            entry.update(rejecting_case=case[0],independent_oracle_rejected=True)
            break
    else:
        raise AssertionError('zero-edge mutant survived')
    report['mutants'].append(entry)
    fixture=(ROOT/'tests/fixtures/prim_sources/wida.inc').read_text()
    source='#include <bits/stdc++.h>\nusing namespace std;\n#define ms(a,b) memset(a,b,sizeof(a))\n'+fixture
    exe,entry=compile('wida-original-driver',source)
    for name,raw,expected in [('negative','2 1\n1 2 -1\n','-1'),('disconnected','2 0\n','impossible'),('self-loop','1 1\n1 1 -9\n','0')]:
        output=run(exe,raw)
        assert output.strip()==expected
        entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),output=output))
    report['upstream_driver']=entry
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:',out/'report.json',flush=True)

if __name__=='__main__':
    main()
