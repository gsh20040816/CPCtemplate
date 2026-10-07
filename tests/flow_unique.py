"""Enumerate bounded integer flows independently of residual-graph uniqueness."""
import hashlib,itertools,json,os,platform,random,resource,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records


def oracle(n,s,t,edges):
    best=-1;count=0
    for f in itertools.product(*(range(c+1) for u,v,c in edges)):
        b=[0]*(n+1)
        for (u,v,c),x in zip(edges,f):
            b[u]+=x;b[v]-=x
        if any(b[u] for u in range(1,n+1) if u not in (s,t)) or b[s]!=-b[t]:continue
        if b[s]>best:best,count=b[s],0
        if b[s]==best:count+=1
    return best,count==1


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT)
    out=Path(tempfile.mkdtemp(prefix='flow-unique-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    if platform.system()=='Darwin':flags+=['-Wl,-stack_size,0x20000000']
    else:
        _,hard=resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha=lambda b:hashlib.sha256(b).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],stack_mib=512,scope='Local integer flow-vector uniqueness, including circulations. API only, no new online AC/rank.')
    def compile(name,s,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(s)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True);assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,command=cmd,source_sha256=sha(s.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    def run(exe,raw='',args=()):
        p=subprocess.run([str(exe),*args],input=raw.encode(),capture_output=True,timeout=180,env=env)
        assert p.returncode==0 and not p.stderr,(p.returncode,p.stderr[-1000:]);return p.stdout.decode()
    prelude='#include <cassert>\n#include <bits/stdc++.h>\nusing namespace std;\n'
    core=''
    for file,symbol in [('flow','Dinic'),('tarjan','TarjanSCC')]:
        s=(ROOT/f'src/compact/{file}.hpp').read_text();core+='struct '+symbol+s.split('struct '+symbol,1)[1].split('\n};',1)[0]+'\n};\n'
    unique=(ROOT/'src/compact/flow_unique.hpp').read_text().split('// BEGIN flow_unique\n',1)[1].split('// END flow_unique',1)[0]
    probe=(ROOT/'tests/flow_unique_probe.cpp').read_text().replace('#include "../src/compact/flow_unique.hpp"','')
    probe=probe.replace('"fixtures/flow_unique_sources/','"'+str(ROOT/'tests/fixtures/flow_unique_sources')+'/')
    copied=prelude+core+unique+probe
    for form,s in [('header','#include "'+str(ROOT/'tests/flow_unique_probe.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            exe,entry=compile(form+('-ndebug' if release else '-assert'),s,['-DNDEBUG'] if release else [])
            result=run(exe).strip();assert result.startswith('PASS '),result
            entry['result']=result;report['programs'].append(entry);print(entry['name'],result,flush=True)
    for name,a,b in [('count-pair-twice','id += 2','id++'),('count-zero-capacity','if (!e.cap && !g.e[id ^ 1].cap) continue;',';'),('omit-loops','auto e = g.e[id];','auto e = g.e[id]; if (e.from == e.to) continue;'),('miss-unicyclic','== 0) return false','< 0) return false')]:
        assert a in unique
        exe,entry=compile(name,prelude+core+unique.replace(a,b)+probe,['-DNDEBUG'])
        result=run(exe,args=['small-only']);assert result=='ORACLE_REJECT\n',(name,result)
        entry['rejected']=True;report['mutants'].append(entry);print(name,'REJECT',flush=True)
    rng=random.Random(320)
    cases=[]
    for i in range(200):
        n=2+rng.randrange(4);s,t=rng.sample(range(1,n+1),2)
        e=[(rng.randrange(1,n+1),rng.randrange(1,n+1),rng.randrange(3)) for _ in range(i%9)]
        cases.append((n,s,t,e,*oracle(n,s,t,e)))
    cases += [(3,1,2,[(1,2,2**63-1),(3,3,2**63-1)],2**63-1,False),(2,1,2,[(1,2,2**63-1)],2**63-1,True),(3,1,3,[(1,2,1),(1,2,1),(2,3,1)],1,False)]
    n=100000;e=[(u,u+1,1) for u in range(1,n)]
    cases.append((n,1,n,e,1,True))
    row=next(r for r in records() if r['id']=='example-320')
    for form,s,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy',prelude+core+unique+row['snippet'],[]),('ndebug',prelude+core+unique+row['snippet'],['-DNDEBUG'])]:
        exe,entry=compile('320-'+form,s,extra)
        for n,s,t,e,want,uniq in cases:
            raw=f'{n} {len(e)} {s} {t}\n'+''.join(f'{u} {v} {c}\n' for u,v,c in e)
            output=run(exe,raw);a=output.split();assert len(a)==2+len(e)
            assert int(a[0])==want and a[1]==('UNIQUE' if uniq else 'MULTIPLE')
            b=[0]*(n+1)
            for (u,v,c),x in zip(e,map(int,a[2:])):
                assert 0<=x<=c;b[u]+=x;b[v]-=x
            assert b[s]==want and b[t]==-want and all(b[u]==0 for u in range(1,n+1) if u not in (s,t))
            entry['runs'].append(dict(input_sha256=sha(raw.encode()),output_sha256=sha(output.encode()),expected_value=want,unique=uniq,passed=True))
        report['programs'].append(entry);print(entry['name'],len(cases),'PASS',flush=True)
    after=snapshot(ROOT);assert before==after
    report.update(source_after_sha256=after,passed=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',out/'report.json',flush=True)

if __name__=='__main__':main()
