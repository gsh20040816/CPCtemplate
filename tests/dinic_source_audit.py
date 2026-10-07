"""Audit the unchanged 70-line kuangbin Dinic fragment."""
import hashlib,json,os,platform,resource,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot

def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT)
    out=Path(tempfile.mkdtemp(prefix='dinic-source-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    if platform.system()=='Darwin':flags+=['-Wl,-stack_size,0x20000000']
    else:
        _,hard=resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha=lambda b:hashlib.sha256(b).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],numeric_boundaries=[],scope='Local source equivalence within documented domain; no online AC or rank.')
    def compile(name,s,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name
        cpp.write_text(s)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,command=cmd,source_sha256=sha(s.encode()),binary_sha256=sha(exe.read_bytes()),compiler_stderr=p.stderr.decode())
    def run(exe):
        p=subprocess.run([str(exe)],capture_output=True,timeout=180,env=env)
        assert p.returncode==0 and not p.stderr,(p.returncode,p.stderr[-1000:])
        return p.stdout.decode().strip()
    prelude='#include <cassert>\n#include <bits/stdc++.h>\nusing namespace std;\n'
    core=(ROOT/'src/compact/flow.hpp').read_text().split('struct Dinic',1)[1]
    core='struct Dinic'+core.split('\n};',1)[0]+'\n};\n'
    probe=(ROOT/'tests/dinic_source_audit.cpp').read_text().replace('#include "../src/compact/flow.hpp"','')
    probe=probe.replace('"fixtures/dinic_sources/','"'+str(ROOT/'tests/fixtures/dinic_sources')+'/')
    copied=prelude+core+probe
    for form,s in [('header','#include "'+str(ROOT/'tests/dinic_source_audit.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            exe,entry=compile(form+('-ndebug' if release else '-assert'),s,['-DNDEBUG'] if release else [])
            result=run(exe)
            assert result.startswith('PASS '),result
            entry['result']=result;report['programs'].append(entry)
            print(entry['name'],result,flush=True)
    for name,a,b in [('wrong-used','e[id].initial - e[id].cap','e[id].cap - e[id].initial'),('omit-reverse','e[id ^ 1].cap += d;',';'),('cut-omits-source','if (dep[u] >= 0)','if (dep[u] > 0)')]:
        assert a in core
        exe,entry=compile(name,prelude+core.replace(a,b)+probe,['-DNDEBUG'])
        result=run(exe);assert result=='ORACLE_REJECT',(name,result)
        entry['oracle_rejected']=True;report['mutants'].append(entry)
        print(name,'REJECT',flush=True)
    exe,entry=compile('source-boundaries',copied,['-DNDEBUG'])
    p=subprocess.run([str(exe),'source-inf'],capture_output=True,timeout=30,env=env)
    assert p.returncode==0 and not p.stderr,(p.returncode,p.stderr)
    got=list(map(int,p.stdout.split()));assert got==[0x3f3f3f3f+1,0x3f3f3f3f+2],got
    report['source_inf']=dict(**entry,returned_value=got[0],infeasible_edge_flow=got[1],capacity=0x3f3f3f3f+1)
    print('source INF infeasible edge flow reproduced',flush=True)
    if mode=='sanitizer':
        p=subprocess.run([str(exe),'source-nodes'],capture_output=True,timeout=30,env=env)
        diag=p.stderr.decode();assert p.returncode!=0 and 'global-buffer-overflow' in diag,diag
        report['numeric_boundaries'].append(dict(**entry,case='source-nodes',expected_failure=True,returncode=p.returncode,diagnostic=diag))
        print('source n+1 memset overflow reproduced',flush=True)
    after=snapshot(ROOT);assert before==after
    report.update(source_after_sha256=after,passed=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',out/'report.json',flush=True)

if __name__=='__main__':main()
