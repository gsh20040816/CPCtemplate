"""Independent assignment-subset oracle for exact printed capacity matching uses."""
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records


def optimum(n,cap,edges):
    adj=[0]*len(cap)
    for u,v in edges:
        adj[v]|=1<<u
    dp={0}
    for v,c in enumerate(cap):
        nxt=set(dp)
        for mask in dp:
            avail=adj[v]&~mask
            sub=avail
            while sub:
                if sub.bit_count()<=c:
                    nxt.add(mask|sub)
                sub=(sub-1)&avail
        dp=nxt
    return max(x.bit_count() for x in dp)


def inputs():
    groups={318:[],319:[]}
    def add(kind,n,cap,edges,want=None):
        if want is None:
            want=optimum(n,cap,edges)
        if kind==318:
            raw=f'{n} {len(cap)} {len(edges)}\n'+' '.join(map(str,cap))+'\n'+''.join(f'{u} {v}\n' for u,v in edges)
        else:
            adj=[[] for _ in range(n)]
            for u,v in edges:
                adj[u].append(v+1)
            raw=f'{len(cap)} {n}\n'+' '.join(map(str,cap))+'\n'+''.join(str(len(a))+' '+ ' '.join(map(str,a))+'\n' for a in adj)
        groups[kind].append((raw,n,cap,edges,want))
    rng=random.Random(318319)
    for i in range(160):
        n=2+rng.randrange(7)
        m=2+rng.randrange(min(5,n)-1)
        cap=[rng.randrange(n+2) for _ in range(m)]
        edges=[(rng.randrange(n),rng.randrange(m)) for _ in range(i%35)]
        add(318,n,cap,edges)
        # Official input has positive demands and nonempty per-question types.
        cap=[max(1,c) for c in cap]
        edges=sorted(set(edges)|{(u,rng.randrange(m)) for u in range(n)})
        add(319,n,cap,edges)
    for n,cap,e,w in [
        (0,[],[],0),(0,[2**63-1],[],0),(3,[],[],0),
        (3,[0,0],[(0,0),(1,1)],0),
        (3,[2**63-1,2**63-1],[(0,0),(1,0),(2,1)],3),
        (1010,[1010],[(u,0) for u in range(1010)],1010),
        (2,[1,1],[(0,1),(0,0),(1,1)],2),
        (3,[2],[(0,0),(0,0),(1,0),(2,0)],2)
    ]:
        add(318,n,cap,e,w)
    n=10000
    e=[(u,v) for u in range(n-1) for v in (u,u+1)]+[(n-1,0)]
    add(318,n,[1]*n,e,n)
    n=1000
    e=[(u,v) for u in range(n) for v in range(20)]
    add(319,n,[50]*20,e,1000)
    add(319,n,[51]*20,e,1000)
    add(319,2,[1,1],[(0,0),(1,0)],1)
    add(319,3,[2,1],[(0,0),(1,0),(2,1)],3)
    # Extended robustness cases, not claims about stated judge limits.
    add(319,2,[2**63-1]*2,[(0,0),(1,1)],2)
    add(319,3,[0,0],[(0,0),(1,0),(2,1)],0)
    return groups


def verify(kind,case,text):
    raw,n,cap,edges,want=case
    if kind==318:
        a=list(map(int,text.split()))
        assert len(a)==1+2*want and a[0]==want
        pairs=list(zip(a[1::2],a[2::2]))
    else:
        if want!=sum(cap):
            assert text.strip()=='No Solution!'
            return
        lines=text.strip().splitlines()
        assert len(lines)==len(cap)
        pairs=[]
        for v,line in enumerate(lines):
            lhs,rhs=line.split(':')
            assert lhs==str(v+1)
            us=[int(x)-1 for x in rhs.split()]
            assert len(us)==cap[v]
            pairs.extend((u,v) for u in us)
    present=set(edges)
    used=set()
    count=[0]*len(cap)
    for u,v in pairs:
        assert 0<=u<n and 0<=v<len(cap) and (u,v) in present and u not in used
        used.add(u)
        count[v]+=1
        assert count[v]<=cap[v]
    assert len(pairs)==want


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT)
    out=Path(tempfile.mkdtemp(prefix='capacity-usage-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    if platform.system()=='Darwin':
        flags+=['-Wl,-stack_size,0x20000000']
    else:
        import resource
        _,hard=resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy()
    if mode=='sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha=lambda b:hashlib.sha256(b).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='Application P2763 and API demo. Local only; extended robustness inputs separately described in test source.')
    flow=(ROOT/'src/compact/flow.hpp').read_text()
    core='struct Dinic'+flow.split('struct Dinic',1)[1].split('\n};',1)[0]+'\n};\n'
    prelude='#include <cassert>\n#include <bits/stdc++.h>\nusing namespace std;\n'
    def compile(name,source,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name
        cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    def run(exe,raw):
        p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,timeout=120,env=env)
        assert p.returncode==0 and not p.stderr,(p.returncode,p.stderr[-1000:])
        return p.stdout.decode()
    groups=inputs()
    rows={int(r['id'].split('-')[1]):r for r in records() if r['id'] in ['example-318','example-319']}
    for kind,row in rows.items():
        for form,s,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy',prelude+core+row['snippet'],[]),('ndebug',prelude+core+row['snippet'],['-DNDEBUG'])]:
            exe,entry=compile(str(kind)+'-'+form,s,extra)
            for case in groups[kind]:
                output=run(exe,case[0]);verify(kind,case,output)
                entry['runs'].append(dict(input_sha256=sha(case[0].encode()),output_sha256=sha(output.encode()),expected_count=case[4],passed=True))
            report['programs'].append(entry)
            print(entry['name'],len(entry['runs']),'PASS',flush=True)
    for name,kind,old,new in [('unit-right',318,'t, c);','t, 1);'),('wrong-scheme',318,'if (g.used(id))','if (!g.used(id))'),('omit-full-flow',319,'g.flow(s, t) != need','(g.flow(s, t), false)')]:
        s=rows[kind]['snippet'];assert old in s
        exe,entry=compile(name,prelude+core+s.replace(old,new),['-DNDEBUG'])
        rejected=False
        for case in groups[kind]:
            output=run(exe,case[0])
            try:
                verify(kind,case,output)
            except (AssertionError,ValueError):
                rejected=True
                entry.update(rejected=True,input_sha256=sha(case[0].encode()))
                break
        assert rejected,name
        report['mutants'].append(entry)
        print(name,'REJECT',flush=True)
    after=snapshot(ROOT);assert before==after
    report.update(passed=True,source_after_sha256=after)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',out/'report.json',flush=True)

if __name__=='__main__':
    main()
