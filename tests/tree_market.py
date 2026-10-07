"""Independent tree-distance ownership oracle, original source, and printed API."""
from pathlib import Path
import hashlib,json,os,platform,random,resource,subprocess,sys,tempfile
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot
from usage_examples import records

def oracle(n,edges,market):
    g=[[] for _ in range(n)]
    for u,v,w in edges:g[u].append((v,w));g[v].append((u,w))
    ds=[]
    for s in range(n):
        d=[None]*n;d[s]=0;queue=[s]
        for u in queue:
            for v,w in g[u]:
                if d[v] is None:d[v]=d[u]+w;queue.append(v)
        ds.append(d)
    old=[min(((ds[v][m],m) for m in range(n) if market[m]),default=(10**100,n)) for v in range(n)]
    return [0 if market[x] else sum((ds[v][x],x)<old[v] for v in range(n)) for x in range(n)]

def raw(n,edges,market):
    return str(n)+'\n'+''.join(f'{u+1} {v+1} {w}\n' for u,v,w in edges)+' '.join(map(str,market))+'\n'

def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT);out=Path(tempfile.mkdtemp(prefix='tree-market-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    if platform.system()=='Darwin':flags+=['-Wl,-stack_size,0x20000000']
    else:
        _,hard=resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy();env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha=lambda b:hashlib.sha256(b).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],stack_mib=512,scope='Source-model/API only. No official HDU/online AC verification.')
    def compile(name,text,extra=()):
        cpp=out/(name+'.cpp');exe=out/name;cpp.write_text(text)
        command=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(command,capture_output=True,text=True)
        if p.returncode:raise RuntimeError(p.stderr)
        return exe,dict(name=name,command=command,source_sha256=sha(text.encode()),binary_sha256=sha(exe.read_bytes()),compiler_stderr=p.stderr)
    def run(exe,data='',args=()):
        p=subprocess.run([str(exe),*args],input=data,capture_output=True,text=True,env=env,timeout=180)
        if p.returncode or p.stderr:raise RuntimeError((p.returncode,p.stderr[-2000:]))
        return p.stdout
    prelude='#include <bits/stdc++.h>\nusing namespace std;\n'
    core='struct TreeMarket'+(ROOT/'src/compact/tree_market.hpp').read_text().split('struct TreeMarket',1)[1]
    probe=(ROOT/'tests/tree_market.cpp').read_text().replace('#include "../src/compact/tree_market.hpp"','')
    for form,text in [('header','#include "'+str(ROOT/'tests/tree_market.cpp')+'"\n'),('copied',prelude+core+probe)]:
        for release in [False,True]:
            exe,entry=compile(form+('-ndebug' if release else '-assert'),text,['-DNDEBUG'] if release else [])
            result=run(exe).strip()
            if result!='PASS 10376 scenarios 320758 checks':raise RuntimeError(result)
            entry['result']=result;report['programs'].append(entry);print(entry['name'],result,flush=True)
    for name,a,b in [('wrong-tie-id','Key{d, u}','Key{d, -u}'),('add-subtree','count(nodes, -1);','count(nodes, 1);'),('wrong-threshold','best[u].first - d','best[u].first + d')]:
        assert core.count(a)==1
        exe,entry=compile(name,prelude+core.replace(a,b)+probe,['-DNDEBUG'])
        result=run(exe,args=['small']).strip();assert result=='ORACLE_REJECT',(name,result)
        entry['oracle_rejected']=True;report['mutants'].append(entry);print(name,'REJECT',flush=True)
    rng=random.Random(323);cases=[]
    for case in range(240):
        n=1+rng.randrange(20);edges=[(rng.randrange(v),v,rng.randrange(5)) for v in range(1,n)]
        markets=[rng.randrange(2) for _ in range(n)]
        cases.append((raw(n,edges,markets),max(oracle(n,edges,markets))))
    source_cases=list(cases)
    for shape in range(3):
        n=100000;edges=[(0 if shape==1 else v-1,v,0 if shape==2 else 1) for v in range(1,n)]
        market=[0]*n;market[n-1 if shape==2 else 0]=1
        cases.append((raw(n,edges,market),n if shape==2 else 1 if shape==1 else n-1))
    source_cases+=cases[240:]
    # Current implementation supports distances exceeding signed64.
    edges=[(0,1,2**63-1),(1,2,2**63-1),(2,3,2**63-1)];market=[1,0,0,0]
    cases.append((raw(4,edges,market),max(oracle(4,edges,market))))
    row=next(r for r in records() if r['id']=='example-323')
    for form,text,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy',prelude+core+row['snippet'],[]),('ndebug',prelude+core+row['snippet'],['-DNDEBUG'])]:
        exe,entry=compile('323-'+form,text,extra);data=''.join(c[0] for c in cases);result=run(exe,data)
        assert list(map(int,result.split()))==[c[1] for c in cases]
        entry.update(datasets=len(cases),input_sha256=sha(data.encode()),output_sha256=sha(result.encode()))
        report['programs'].append(entry);print(entry['name'],len(cases),'PASS',flush=True)
    original=prelude+'namespace Original {\n'+(ROOT/'tests/fixtures/tree_market_sources/kuangbin.inc').read_text()+'\n}\nint main() { return Original::main(); }\n'
    exe,entry=compile('source',original);data=''.join(c[0] for c in source_cases);result=run(exe,data)
    assert list(map(int,result.split()))==[c[1] for c in source_cases]
    entry.update(datasets=len(source_cases),input_sha256=sha(data.encode()),output_sha256=sha(result.encode()))
    # INF blocks propagation even though both edge/path values fit signed int.
    w=0x3f3f3f3f+1;edges=[(0,1,w),(1,2,w)];market=[1,0,0];data=raw(3,edges,market)
    got=int(run(exe,data));want=max(oracle(3,edges,market));assert got!=want
    entry['inf_counterexample']=dict(input=data,source_result=got,expected=want)
    if mode=='sanitizer':
        data=raw(4,[(0,1,2**30),(1,2,2**30),(2,3,2**30)],[1,0,0,0])
        p=subprocess.run([str(exe)],input=data,capture_output=True,text=True,env=env,timeout=30)
        assert p.returncode and 'signed integer overflow' in p.stderr,p.stderr
        entry['distance_overflow']=dict(input=data,returncode=p.returncode,diagnostic=p.stderr)
    report['source']=entry;print('source comparisons and boundary probes PASS',flush=True)
    after=snapshot(ROOT);assert before==after
    report.update(source_after_sha256=after,passed=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json',flush=True)

if __name__=='__main__':main()
