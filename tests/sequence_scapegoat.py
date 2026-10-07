"""Recursive sequence scapegoat: structural invariants, CF decoding and source."""
from pathlib import Path
import hashlib,itertools,json,os,random,subprocess,sys,tempfile,time
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot
from usage_examples import records


def encode(values, operations):
    a=values[:]
    n=len(a)
    last=0
    lines=[str(n),' '.join(map(str,a)),str(len(operations))]
    answers=[]
    for op,l,r,k in operations:
        coded=[(v-last-1)%n+1 for v in (l,r)]
        if op==2:
            coded.append((k-last-1)%n+1)
        lines.append(' '.join(map(str,[op,*coded])))
        if l>r:
            l,r=r,l
        if op==1:
            x=a.pop(r-1)
            a.insert(l-1,x)
        else:
            last=a[l-1:r].count(k)
            answers.append(last)
    return '\n'.join(lines)+'\n',answers


def large(shape):
    n=100000
    a=[1]*n if shape=='same' else list(range(1,n+1))
    ops=[]
    want=[]
    last=0
    shift=0
    for step in range(100000):
        if step%2==0:
            l,r=(1,n) if shape!='singleton' else (step%n+1,step%n+1)
            shift+=(shape!='singleton')
            code=[(v-last-1)%n+1 for v in (l,r)]
            ops.append('1 '+' '.join(map(str,code)))
        else:
            l=step*997%n+1
            r=step*37%n+1
            if l>r:
                l,r=r,l
            k=(step*13%n)+1
            if shape=='same':
                k=1 if step%4==1 else n
                ans=r-l+1 if k==1 else 0
            else:
                pos=(k-1+shift)%n+1
                ans=int(l<=pos<=r)
            code=[(v-last-1)%n+1 for v in (l,r,k)]
            ops.append('2 '+' '.join(map(str,code)))
            last=ans
            want.append(ans)
    return str(n)+'\n'+' '.join(map(str,a))+'\n100000\n'+'\n'.join(ops)+'\n',want


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT)
    out=Path(tempfile.mkdtemp(prefix='sequence-scapegoat-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    digest=lambda x:hashlib.sha256(x).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='CF455D application locally tested, no online AC/ranking/resource pass claim.')
    def compile(name,text,extra=()):
        cpp=out/(name+'.cpp');cpp.write_text(text);exe=out/name
        command=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(command,capture_output=True,text=True)
        if p.returncode:raise RuntimeError(p.stderr)
        return exe,dict(name=name,command=command,source_sha256=digest(text.encode()),binary_sha256=digest(exe.read_bytes()),compiler_stderr=p.stderr,runs=[])
    def run(exe,data=''):
        start=time.monotonic()
        p=subprocess.run([str(exe)],input=data,capture_output=True,text=True,env=env,timeout=240)
        return p,time.monotonic()-start
    prelude='#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'
    core='struct SequenceScapegoat'+(ROOT/'src/compact/sequence_scapegoat.hpp').read_text().split('struct SequenceScapegoat',1)[1]
    probe=(ROOT/'tests/sequence_scapegoat.cpp').read_text().replace('#include "../src/compact/sequence_scapegoat.hpp"','')
    for name,text,extra in [('core-header','#include "'+str(ROOT/'tests/sequence_scapegoat.cpp')+'"\n',[]),('core-copy',prelude+core+probe,[]),('core-ndebug',prelude+core+probe,['-DNDEBUG'])]:
        exe,entry=compile(name,text,extra);p,elapsed=run(exe)
        if p.returncode or p.stderr or '14595 exhaustive modifications; 30000 random operations; recycling PASS' not in p.stdout:raise RuntimeError((name,p.stdout,p.stderr))
        entry.update(result=p.stdout,seconds=elapsed);report['programs'].append(entry);print(name,'PASS',flush=True)
    rng=random.Random(4552026);cases=[]
    for n in range(1,5):
        for v in itertools.product(range(1,min(3,n)+1),repeat=n):
            ops=[]
            for l in range(1,n+1):
                for r in range(l,n+1):
                    ops.append((1,r,l,0))
                    ops.extend((2,l,r,k) for k in range(1,n+1))
            cases.append(encode(list(v),ops))
    for _ in range(80):
        n=rng.randrange(1,65);v=[rng.randrange(1,n+1) for _ in range(n)]
        ops=[(1 if i%3 else 2,rng.randrange(1,n+1),rng.randrange(1,n+1),rng.randrange(1,n+1)) for i in range(180)]
        cases.append(encode(v,ops))
    cases += [('7\n6 6 2 7 4 2 5\n7\n1 3 6\n2 2 4 2\n2 2 4 7\n2 2 2 5\n1 2 6\n1 1 4\n2 1 7 3\n',[2,1,0,0]),('8\n8 4 2 2 7 7 8 8\n8\n1 8 8\n2 8 1 7\n1 8 1\n1 7 3\n2 8 8 3\n1 1 4\n1 2 7\n1 4 5\n',[2,0])]
    small_count=len(cases)
    cases += [large(x) for x in ['same','unique','singleton']]
    row=next(x for x in records() if x['id']=='example-326')
    texts=[('usage-driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('usage-expanded',row['program'],[]),('usage-minimal',prelude+core+row['snippet'],[]),('usage-ndebug',prelude+core+row['snippet'],['-DNDEBUG']),('source',prelude+(ROOT/'tests/fixtures/sequence_scapegoat_sources/kuangbin.inc').read_text(),[])]
    for name,text,extra in texts:
        exe,entry=compile(name,text,extra)
        for i,(data,want) in enumerate(cases):
            p,elapsed=run(exe,data)
            if p.returncode or p.stderr or list(map(int,p.stdout.split()))!=want:raise RuntimeError((name,i,p.returncode,p.stderr,p.stdout[:100]))
            entry['runs'].append(dict(case=i,input_sha256=digest(data.encode()),output_sha256=digest(p.stdout.encode()),queries=len(want),seconds=elapsed))
        if name=='source':
            data=''.join(x[0] for x in cases[:small_count]);want=sum((x[1] for x in cases[:small_count]),[])
            p,elapsed=run(exe,data)
            if p.returncode or p.stderr or list(map(int,p.stdout.split()))!=want:raise RuntimeError(('source-multicase',p.stderr))
            entry['multicase_reset']=True
        report['programs'].append(entry);print(name,'PASS',len(cases),'cases; large seconds',[round(x['seconds'],3) for x in entry['runs'][-3:]],flush=True)
    for name,old,new in [('wrong-insertion-position','insert(l - 1, x);','insert(l, x);'),('omit-key-decode','k = (k + ans - 1) % n + 1;','k = k;'),('ignore-tombstone','int offset = left + a[u].live;','int offset = left + 1;')]:
        text=prelude+core+row['snippet'];assert text.count(old)==1
        exe,entry=compile(name,text.replace(old,new),['-DNDEBUG']);rejected=False
        for data,want in cases[:small_count]:
            p,elapsed=run(exe,data)
            if p.returncode or p.stderr:raise RuntimeError(('mutant did not fail cleanly',name,p.stderr))
            if list(map(int,p.stdout.split()))!=want:rejected=True;break
        assert rejected,name
        entry['oracle_rejected']=True;report['mutants'].append(entry);print(name,'REJECT',flush=True)
    after=snapshot(ROOT);assert before==after,'Source changed during test'
    report.update(source_after_sha256=after,small_cases=small_count,large_cases=3,passed=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json',flush=True)

if __name__=='__main__':
    main()
