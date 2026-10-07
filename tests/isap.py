"""Independent cut enumeration, original-source comparisons and printed driver."""
import hashlib,json,os,platform,random,resource,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records

def oracle(n,s,t,e):
    return min(sum(c for u,v,c in e if mask>>(u-1)&1 and not(mask>>(v-1)&1)) for mask in range(1<<n) if mask>>(s-1)&1 and not(mask>>(t-1)&1))

def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT)
    out=Path(tempfile.mkdtemp(prefix='isap-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    if platform.system()=='Darwin':flags+=['-Wl,-stack_size,0x20000000']
    else:
        _,hard=resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha=lambda b:hashlib.sha256(b).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],stack_mib=512,scope='Recursive ISAP, local only. P3376 official driver separate from broader API cases; no online AC/rank.')
    def compile(name,s,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name
        cpp.write_text(s)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,command=cmd,source_sha256=sha(s.encode()),binary_sha256=sha(exe.read_bytes()),compiler_stderr=p.stderr.decode(),runs=[])
    def run(exe,raw='',args=()):
        p=subprocess.run([str(exe),*args],input=raw.encode(),capture_output=True,timeout=180,env=env)
        assert p.returncode==0 and not p.stderr,(p.returncode,p.stderr[-1500:])
        return p.stdout.decode()
    prelude='#include <cassert>\n#include <bits/stdc++.h>\nusing namespace std;\n'
    core='struct Isap'+(ROOT/'src/compact/isap.hpp').read_text().split('struct Isap',1)[1]
    probe=(ROOT/'tests/isap.cpp').read_text().replace('#include "../src/compact/isap.hpp"','')
    probe=probe.replace('"fixtures/isap_sources/','"'+str(ROOT/'tests/fixtures/isap_sources')+'/')
    copied=prelude+core+probe
    for form,s in [('header','#include "'+str(ROOT/'tests/isap.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            exe,entry=compile(form+('-ndebug' if release else '-assert'),s,['-DNDEBUG'] if release else [])
            result=run(exe).strip();assert result.startswith('PASS '),result
            entry['result']=result;report['programs'].append(entry)
            print(entry['name'],result,flush=True)
    for name,a,b in [('wrong-bfs-direction','!e[id ^ 1].cap || dep[v] != n','!e[id].cap || dep[v] != n'),('omit-reverse','e[id ^ 1].cap += take;',';'),('wrong-used','e[id].initial - e[id].cap','e[id].cap - e[id].initial')]:
        assert a in core
        exe,entry=compile(name,prelude+core.replace(a,b)+probe,['-DNDEBUG'])
        result=run(exe,args=['small-only']).strip();assert result=='ORACLE_REJECT',(name,result)
        entry['oracle_rejected']=True;report['mutants'].append(entry)
        print(name,'REJECT',flush=True)
    rng=random.Random(321)
    cases=[]
    for i in range(200):
        n=2+rng.randrange(7);s,t=rng.sample(range(1,n+1),2)
        e=[(1+rng.randrange(n),1+rng.randrange(n),rng.randrange(20)) for j in range(1+i%25)]
        cases.append((n,s,t,e,oracle(n,s,t,e)))
    e=[(1,200,2**31-1)]*5000
    cases.append((200,1,200,e,5000*(2**31-1)))
    e=[(i,i+1,2**31-1) for i in range(1,200)]+[(1,1,2**31-1)]*4801
    cases.append((200,1,200,e,2**31-1))
    cases.append((4,4,3,[(4,2,30),(4,3,20),(2,3,20),(2,1,30),(1,3,40)],50))
    row=next(r for r in records() if r['id']=='example-321')
    for form,s,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy',prelude+core+row['snippet'],[]),('ndebug',prelude+core+row['snippet'],['-DNDEBUG'])]:
        exe,entry=compile('321-'+form,s,extra)
        for n,s,t,e,want in cases:
            raw=f'{n} {len(e)} {s} {t}\n'+''.join(f'{u} {v} {c}\n' for u,v,c in e)
            output=run(exe,raw)
            assert output.split()==[str(want)],(want,output)
            entry['runs'].append(dict(input_sha256=sha(raw.encode()),output_sha256=sha(output.encode()),expected=want,passed=True))
        report['programs'].append(entry);print(entry['name'],len(cases),'PASS',flush=True)
    if mode=='sanitizer':
        exe,entry=compile('source-disconnected',copied,['-DNDEBUG'])
        p=subprocess.run([str(exe),'source-disconnected'],capture_output=True,timeout=30,env=env)
        diag=p.stderr.decode();assert p.returncode!=0 and 'index -1 out of bounds' in diag,diag
        entry.update(expected_failure=True,returncode=p.returncode,diagnostic=diag)
        report['source_disconnected']=entry
        print('source gap[-1] reproduced',flush=True)
    after=snapshot(ROOT);assert before==after
    report.update(source_after_sha256=after,passed=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',out/'report.json',flush=True)

if __name__=='__main__':main()
