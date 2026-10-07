"""Compile upstream matching sources and compare with independent subset DP."""
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
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records


def optimum(n,m,e):
    masks={0}
    for u in range(n):
        nxt=set(masks)
        for mask in masks:
            for x,v in e:
                if x==u and not (mask>>v&1):
                    nxt.add(mask|(1<<v))
        masks=nxt
    return max(mask.bit_count() for mask in masks)


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT)
    out=Path(tempfile.mkdtemp(prefix='matching-source-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    if platform.system()=='Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    else:
        _,hard=resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy()
    if mode=='sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha=lambda s:hashlib.sha256(s).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],stack_mib=512,scope='Source mapping audit. Local only; randomized upstream HK order retained, no performance/ranking claim.')
    def compile(name,s,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name
        cpp.write_text(s)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(s.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    def run(exe,raw='',args=()):
        p=subprocess.run([str(exe),*args],input=raw.encode(),capture_output=True,timeout=300,env=env)
        assert p.returncode==0 and not p.stderr,(exe,p.returncode,p.stderr[-1000:])
        return p.stdout.decode()
    probe=(ROOT/'tests/matching_source_audit.cpp').read_text()
    graph=(ROOT/'src/compact/graph.hpp').read_text()
    core='struct BipartiteMatching'+graph.split('struct BipartiteMatching',1)[1].split('\n};',1)[0]+'\n};\n'
    copied='#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'+core+'\n'+probe.replace('#include "../src/compact/graph.hpp"','')
    copied=copied.replace('"fixtures/matching_sources/','"'+str(ROOT/'tests/fixtures/matching_sources')+'/')
    for form,source in [('header','#include "'+str(ROOT/'tests/matching_source_audit.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            exe,entry=compile(form+('-ndebug' if release else '-assert'),source,['-DNDEBUG'] if release else [])
            result=run(exe)
            assert result.startswith('PASS '),result
            entry['result']=result.strip()
            report['programs'].append(entry)
            print(entry['name'],result.strip(),flush=True)
    for name,old,new in [('missing-right-partner','r[v] = u;','r[v] = 0;'),('missing-cover-right','right.push_back(v);','(void)v;'),('return-increment','answer += (l[u] != 0);','answer += 0;')]:
        assert old in core
        exe,entry=compile(name,copied.replace(core,core.replace(old,new),1),['-DNDEBUG'])
        result=run(exe,args=('small-only',))
        assert result=='ORACLE_REJECT\n',(name,result)
        entry['independent_oracle_rejected']=True
        report['mutants'].append(entry)
        print(name,'REJECT',flush=True)
    rng=random.Random(2026100802)
    cases=[]
    for i in range(180):
        n=1+i%7
        m=1+(i//7)%7
        e=[(rng.randrange(n),rng.randrange(m)) for _ in range(i%40)]
        cases.append((n,m,e,optimum(n,m,e)))
    cases += [(1,1,[(0,0)],1),(4,3,[],0),(500,500,[(u,v) for u in range(500) for v in range(500)],500)]
    programs=[]
    for kind in ['kuhn','hk']:
        source='#include <bits/stdc++.h>\nusing namespace std;\n'+(ROOT/f'tests/fixtures/matching_sources/wida-{kind}.inc').read_text()
        programs.append(('wida-'+kind,source,kind))
    row=next(r for r in records() if r['id']=='example-35')
    programs += [('p3386-driver','#include "'+str(ROOT/row['driver'])+'"\n','count'),('p3386-expanded',row['program'],'count')]
    for name,source,kind in programs:
        exe,entry=compile(name,source)
        for n,m,e,want in cases:
            raw=f'{n} {m} {len(e)}\n'+''.join(f'{u+1} {v+1}\n' for u,v in e)
            output=run(exe,raw)
            a=list(map(int,output.split()))
            assert a and a[0]==want
            if kind=='hk':
                assert len(a)==1+2*want
                pairs=list(zip(a[1::2],a[2::2]))
                assert len({u for u,v in pairs})==want and len({v for u,v in pairs})==want
                edges=set(e)
                assert all(0<=u<n and 0<=v<m and (u,v) in edges for u,v in pairs)
            else:
                assert len(a)==1
            entry['runs'].append(dict(input_sha256=sha(raw.encode()),output_sha256=sha(output.encode()),expected=want,passed=True))
        report['programs'].append(entry)
        print(name,len(cases),'PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',out/'report.json',flush=True)

if __name__=='__main__':
    main()
