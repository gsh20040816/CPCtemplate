"""Kruskal source audit and independent minimum spanning forest certificates."""
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
    groups={314:[],315:[]}
    rng=random.Random(314315)
    def add(k,name,n,e,known=None):
        c,w=known if known is not None else optimum(n,e)
        off=1 if k==314 else 0
        raw=f'{n} {len(e)}\n'+''.join(f'{u+off} {v+off} {w}\n' for u,v,w in e)
        groups[k].append((name,raw,n,e,c,w))
    for i in range(100):
        n=1+i%6
        e=[(rng.randrange(n),rng.randrange(n),rng.randrange(1,11)) for _ in range(1+i%12)]
        add(314,f'multigraph-{i}',n,e)
        e=[(u,v,w-5) for u,v,w in e]
        add(315,f'signed-multigraph-{i}',n,e)
    n=5000
    e=[(v-1,v,10000) for v in range(1,n)]
    e += [(0,0,1)]*(200000-len(e))
    add(314,'max-chain',n,e,(1,(n-1)*10000))
    e=[(v-1,v,1) for v in range(1,n-1)]
    e += [(0,0,1)]*(200000-len(e))
    add(314,'max-disconnected',n,e,(2,n-2))
    add(315,'empty',0,[])
    add(315,'negative-wide',4,[(0,1,-(1<<63)),(1,2,-(1<<63)),(0,2,(1<<63)-1)])
    add(315,'positive-wide',3,[(0,1,(1<<63)-1),(1,2,(1<<63)-1)])
    add(315,'minus-one-valid',2,[(0,1,-1)])
    n=200000
    e=[(v,v-1,-(1<<63)) for v in range(n-1,0,-1)]+[(v,v,-(1<<63)) for v in range(n)]
    e.append((0,n-1,(1<<63)-1))
    add(315,'large-chain-and-loops',n,e,(1,-(n-1)*(1<<63)))
    return groups


def check(k,case,output):
    name,raw,n,e,c,w=case
    if k==314:
        assert output.strip()==(str(w) if c==1 else 'orz'),name
        return
    a=list(map(int,output.split()))
    assert a[:3]==[c,w,n-c] and len(a)==3+n-c,name
    ids=a[3:]
    assert len(set(ids))==len(ids) and all(0<=i<len(e) for i in ids),name
    f=[e[i] for i in ids]
    assert sum(x[2] for x in f)==w and components(n,f)==components(n,e),name
    assert ids==sorted(ids,key=lambda i:(e[i][2],i)),name


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='kruskal-'+mode+'-',dir=ROOT/'build'))
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
    core=(ROOT/'src/compact/kruskal.hpp').read_text().replace('#pragma once\n','')
    ds=(ROOT/'src/compact/data_structure.hpp').read_text().split('struct RollbackDSU')[0].replace('#pragma once\n','')
    header=ds+'\n'+core.replace('#include "data_structure.hpp"','')
    probe=(ROOT/'tests/kruskal_probe.cpp').read_text()
    copied=header+'\n'+probe.replace('#include "../src/compact/kruskal.hpp"','')
    copied=copied.replace('"fixtures/kruskal_sources/','"'+str(ROOT/'tests/fixtures/kruskal_sources')+'/')
    for form,source in [('header','#include "'+str(ROOT/'tests/kruskal_probe.cpp')+'"\n'),('copied',copied)]:
        for release in (False,True):
            exe,entry=compile(form+('-ndebug' if release else '-assert'),source,['-DNDEBUG'] if release else [])
            start=time.monotonic()
            result=run(exe)
            assert result.startswith('PASS '),result
            entry.update(result=result.strip(),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry)
            print(entry['name'],result.strip(),flush=True)
    for name,old,new in [
        ('descending-order','tie(e[a].w, a) < tie(e[b].w, b)','tie(e[a].w, a) > tie(e[b].w, b)'),
        ('omit-total-reset','weight = 0;\n        int cnt','/* reset omitted */\n        int cnt'),
        ('omit-ids-reset','ids.clear();','/* reset omitted */'),
        ('drop-negative-edges','if (u == v) continue;','if (u == v || w < 0) continue;'),
        ('wrong-original-id','ids.push_back(id);','ids.push_back(0);'),
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
        for form,source,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy',header+'\n'+row['snippet'],[]),('ndebug',row['program'],['-DNDEBUG'])]:
            exe,entry=compile(f'{k}-{form}',source,extra)
            for case in cs:
                output=run(exe,case[1])
                check(k,case,output)
                entry['runs'].append(dict(case=case[0],input_sha256=sha(case[1].encode()),output_sha256=sha(output.encode()),passed=True))
            report['programs'].append(entry)
            print(k,form,len(cs),'PASS',flush=True)
    row=next(r for r in records() if r['id']=='example-314')
    exe,entry=compile('ignore-disconnected',row['program'].replace('if (g.run() != 1)','if (g.run() < 0)'),['-DNDEBUG'])
    for case in groups[314]:
        output=run(exe,case[1])
        try:
            check(314,case,output)
        except AssertionError:
            entry.update(rejecting_case=case[0],independent_oracle_rejected=True)
            break
    else:
        raise AssertionError('disconnect mutant survived')
    report['mutants'].append(entry)
    report['upstream_assertion_reproducers']=[]
    for variant in ['online','print']:
        fixture=(ROOT/f'tests/fixtures/kruskal_sources/wida-{variant}.inc').read_text()
        for release in (False,True):
            for connected in (False,True):
                source='#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'+fixture+'\nint main() { Tree g(2);'+('g.add(1,2,7);' if connected else '')+'cout << g.kruskal() << "\\n"; }\n'
                exe,entry=compile(f'wida-{variant}-{release}-{connected}',source,['-DNDEBUG'] if release else [])
                def no_core():
                    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
                p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=30,preexec_fn=no_core)
                if connected and not release:
                    assert p.returncode != 0 and b'cnt < n - 1' in p.stderr,(p.returncode,p.stderr)
                else:
                    assert p.returncode == 0 and not p.stderr and p.stdout.strip()==(b'7' if connected else b'0')
                entry.update(connected=connected,ndebug=release,returncode=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode(),expected_behavior_observed=True)
                report['upstream_assertion_reproducers'].append(entry)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:',out/'report.json',flush=True)

if __name__=='__main__':
    main()
