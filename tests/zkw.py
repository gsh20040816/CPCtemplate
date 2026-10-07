"""Independent feasible-flow enumeration and P3381 printed-program checks."""
import hashlib,itertools,json,os,platform,random,resource,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records

def oracle(n,s,t,e):
    best=(-1,0)
    for f in itertools.product(*(range(c+1) for u,v,c,w in e)):
        b=[0]*(n+1);cost=0
        for (u,v,c,w),x in zip(e,f):b[u]+=x;b[v]-=x;cost+=x*w
        if b[s]!=-b[t] or any(b[u] for u in range(1,n+1) if u not in (s,t)):continue
        if b[s]>best[0] or b[s]==best[0] and cost<best[1]:best=(b[s],cost)
    return best

def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT)
    out=Path(tempfile.mkdtemp(prefix='zkw-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    if platform.system()=='Darwin':flags+=['-Wl,-stack_size,0x20000000']
    else:
        _,hard=resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha=lambda b:hashlib.sha256(b).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],stack_mib=512,scope='Recursive zkw and independent feasible integer-flow certificates. P3381 usage tested separately; no online AC/rank.')
    def compile(name,s,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(s)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True);assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,command=cmd,source_sha256=sha(s.encode()),binary_sha256=sha(exe.read_bytes()),compiler_stderr=p.stderr.decode(),runs=[])
    def run(exe,raw='',args=()):
        p=subprocess.run([str(exe),*args],input=raw.encode(),capture_output=True,timeout=180,env=env)
        assert p.returncode==0 and not p.stderr,(p.returncode,p.stderr[-1500:]);return p.stdout.decode()
    prelude='#include <cassert>\n#include <bits/stdc++.h>\nusing namespace std;\n'
    core='struct ZkwFlow'+(ROOT/'src/compact/zkw_flow.hpp').read_text().split('struct ZkwFlow',1)[1]
    probe=(ROOT/'tests/zkw.cpp').read_text().replace('#include "../src/compact/zkw_flow.hpp"','')
    probe=probe.replace('"fixtures/zkw_sources/','"'+str(ROOT/'tests/fixtures/zkw_sources')+'/')
    copied=prelude+core+probe
    for form,s in [('header','#include "'+str(ROOT/'tests/zkw.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            exe,entry=compile(form+('-ndebug' if release else '-assert'),s,['-DNDEBUG'] if release else [])
            result=run(exe).strip();assert result.startswith('PASS '),result
            entry['result']=result;report['programs'].append(entry);print(entry['name'],result,flush=True)
    for name,a,b in [('wrong-used','e[id].initial - e[id].cap','e[id].cap - e[id].initial'),('omit-reverse','e[id ^ 1].cap += take;',';'),('assume-zero-sink-potential','(h[t] - h[s])','(-h[s])')]:
        assert a in core
        exe,entry=compile(name,prelude+core.replace(a,b)+probe,['-DNDEBUG'])
        result=run(exe,args=['small-only']).strip();assert result=='ORACLE_REJECT',(name,result)
        entry['oracle_rejected']=True;report['mutants'].append(entry);print(name,'REJECT',flush=True)
    rng=random.Random(322);cases=[]
    for i in range(180):
        n=2+rng.randrange(5);s,t=rng.sample(range(1,n+1),2);e=[]
        for j in range(1+i%8):
            u,v=rng.sample(range(1,n+1),2);e.append((u,v,rng.randrange(3),rng.randrange(8)))
        cases.append((n,s,t,e,oracle(n,s,t,e)))
    e=[]
    for u in range(2,502):e.extend([(1,u,1,u-2),(u,5000,1,0)])
    e += [(1,5000,0,1000)]*(50000-len(e))
    cases.append((5000,1,5000,e,(500,499*500//2)))
    e=[(u,u+1,1,0) for u in range(1,5000)]+[(1,5000,0,1000)]*45001
    cases.append((5000,1,5000,e,(1,0)))
    row=next(r for r in records() if r['id']=='example-322')
    for form,s,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy',prelude+core+row['snippet'],[]),('ndebug',prelude+core+row['snippet'],['-DNDEBUG'])]:
        exe,entry=compile('322-'+form,s,extra)
        for n,s,t,e,want in cases:
            raw=f'{n} {len(e)} {s} {t}\n'+''.join(f'{u} {v} {c} {w}\n' for u,v,c,w in e)
            output=run(exe,raw);assert tuple(map(int,output.split()))==want,(want,output)
            entry['runs'].append(dict(input_sha256=sha(raw.encode()),output_sha256=sha(output.encode()),expected=want,passed=True))
        report['programs'].append(entry);print(entry['name'],len(cases),'PASS',flush=True)
    if mode=='sanitizer':
        exe,entry=compile('source-product',copied,['-DNDEBUG'])
        p=subprocess.run([str(exe),'source-product'],capture_output=True,timeout=30,env=env)
        diag=p.stderr.decode();assert p.returncode!=0 and 'signed integer overflow' in diag,diag
        entry.update(expected_failure=True,returncode=p.returncode,diagnostic=diag)
        report['source_product']=entry;print('source int product overflow reproduced',flush=True)
    after=snapshot(ROOT);assert before==after
    report.update(source_after_sha256=after,passed=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',out/'report.json',flush=True)

if __name__=='__main__':main()
