"""Compile original kuangbin Manhattan/rank program, no POJ statement claim."""
import hashlib,json,os,platform,random,resource,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot


def prim(p):
    n=len(p);dis=[10**100]*n;used=[False]*n;dis[0]=0;w=[]
    for i in range(n):
        u=min((v for v in range(n) if not used[v]),key=lambda v:dis[v])
        used[u]=True
        if i:w.append(dis[u])
        for v in range(n):
            if not used[v]:dis[v]=min(dis[v],sum(abs(a-b) for a,b in zip(p[u],p[v])))
    return sorted(w)


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT)
    out=Path(tempfile.mkdtemp(prefix='manhattan-source-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    if platform.system()=='Darwin':flags+=['-Wl,-stack_size,0x20000000']
    else:
        _,hard=resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha=lambda b:hashlib.sha256(b).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],stack_mib=512,scope='Local upstream source and rank semantics; POJ original statement inaccessible, no online AC/rank.')
    def compile(name,s,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(s)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True);assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,command=cmd,source_sha256=sha(s.encode()),binary_sha256=sha(exe.read_bytes()),compiler_stderr=p.stderr.decode(),runs=[])
    def run(exe,raw='',args=()):
        p=subprocess.run([str(exe),*args],input=raw.encode(),capture_output=True,timeout=300,env=env)
        assert p.returncode==0 and not p.stderr,(p.returncode,p.stderr[-1000:]);return p.stdout.decode()
    prelude='#include <cassert>\n#include <bits/stdc++.h>\nusing namespace std;\n'
    ds=(ROOT/'src/compact/data_structure.hpp').read_text()
    core='struct dsu'+ds.split('struct dsu',1)[1].split('\n};',1)[0]+'\n};\n'
    s=(ROOT/'src/compact/manhattan_mst.hpp').read_text()
    core+='struct ManhattanMST'+s.split('struct ManhattanMST',1)[1]
    probe=(ROOT/'tests/manhattan_source_audit.cpp').read_text().replace('#include "../src/compact/manhattan_mst.hpp"','')
    probe=probe.replace('"fixtures/manhattan_sources/','"'+str(ROOT/'tests/fixtures/manhattan_sources')+'/')
    copied=prelude+core+probe
    for form,s in [('header','#include "'+str(ROOT/'tests/manhattan_source_audit.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            exe,entry=compile(form+('-ndebug' if release else '-assert'),s,['-DNDEBUG'] if release else [])
            result=run(exe).strip();assert result.startswith('PASS '),result
            entry['result']=result;report['programs'].append(entry);print(entry['name'],result,flush=True)
    rng=random.Random(419)
    cases=[]
    for i in range(160):
        n=2+rng.randrange(9);p=[(rng.randrange(-100,101),rng.randrange(-100,101)) for _ in range(n)]
        w=prim(p)
        for k in (1,n//2,n-1):cases.append((p,k,w[n-k-1]))
    for p in [[(0,0)]*7,[(i*i,0) for i in range(10)],[(0,0),(2,0),(1,1)]]:
        w=prim(p)
        for k in range(1,len(p)):cases.append((p,k,w[len(p)-k-1]))
    raw=''.join(f'{len(p)} {k}\n'+''.join(f'{x} {y}\n' for x,y in p) for p,k,w in cases)+'0 0\n'
    expected=[w for p,k,w in cases]
    adapter=(ROOT/'tests/fixtures/manhattan_sources/current-rank-main.inc').read_text()
    for name,s in [('upstream-main',prelude+(ROOT/'tests/fixtures/manhattan_sources/kuangbin.inc').read_text()),('current-adapter',prelude+core+adapter)]:
        exe,entry=compile(name,s)
        output=run(exe,raw);assert list(map(int,output.split()))==expected
        entry.update(testcases=len(cases),input_sha256=sha(raw.encode()),output_sha256=sha(output.encode()))
        report['programs'].append(entry);print(name,len(cases),'PASS',flush=True)
    for name,a,b in [('ascending-rank','w[n - k - 1]','w[k - 1]'),('sum-not-rank','w[n - k - 1]','tree.weight')]:
        assert a in adapter
        exe,entry=compile(name,prelude+core+adapter.replace(a,b),['-DNDEBUG'])
        output=run(exe,raw);assert list(map(int,output.split()))!=expected
        entry['oracle_rejected']=True;report['mutants'].append(entry);print(name,'REJECT',flush=True)
    if mode=='sanitizer':
        exe,entry=compile('source-int-boundary',copied,['-DNDEBUG'])
        p=subprocess.run([str(exe),'source-int-overflow'],capture_output=True,timeout=30,env=env)
        diag=p.stderr.decode();assert p.returncode!=0 and 'signed integer overflow' in diag,diag
        entry.update(expected_failure=True,returncode=p.returncode,diagnostic=diag)
        report['source_numeric_boundary']=entry;print('source int subtraction boundary reproduced',flush=True)
    after=snapshot(ROOT);assert before==after
    report.update(source_after_sha256=after,passed=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',out/'report.json',flush=True)

if __name__=='__main__':main()
