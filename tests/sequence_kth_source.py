"""Full source protocol oracle and reproducible unsplayed-query degeneration."""
from pathlib import Path
import hashlib,itertools,json,os,random,subprocess,sys,tempfile
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot


def encode(values, ops):
    a=values[:]
    lines=[str(len(a)),' '.join(map(str,a)),str(len(ops))]
    last=0
    answers=[]
    for op,args in ops:
        lines.append(op+' '+' '.join(str(x^last) for x in args))
        if op=='Q':
            l,r,k=args
            last=sorted(a[l-1:r])[k-1]
            answers.append(last)
        elif op=='M':
            pos,val=args
            a[pos-1]=val
        else:
            pos,val=args
            a.insert(pos-1,val)
    return '\n'.join(lines)+'\n',answers


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT)
    out=Path(tempfile.mkdtemp(prefix='sequence-kth-source-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha=lambda x:hashlib.sha256(x).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],scope='Source audit only; personalized implementation, handbook and official/online verification remain incomplete.')
    def compile(name,text):
        cpp=out/(name+'.cpp');cpp.write_text(text);exe=out/name
        command=[CXX,*flags,str(cpp),'-o',str(exe)]
        p=subprocess.run(command,capture_output=True,text=True)
        if p.returncode:raise RuntimeError(p.stderr)
        return exe,dict(name=name,command=command,source_sha256=sha(text.encode()),binary_sha256=sha(exe.read_bytes()),compiler_stderr=p.stderr)
    def run(exe,data):
        p=subprocess.run([str(exe)],input=data,capture_output=True,text=True,env=env,timeout=120)
        if p.returncode or p.stderr:raise RuntimeError((p.returncode,p.stderr))
        return p.stdout
    cases=[]
    for n in range(1,6):
        for a in itertools.product([0,1,100000],repeat=n):
            ops=[]
            for l in range(1,n+1):
                for r in range(l,n+1):
                    for k in range(1,r-l+2):
                        ops.append(('Q',[l,r,k]))
            for pos in range(1,n+1):
                ops.extend([('M',[pos,100000]),('Q',[pos,pos,1]),('M',[pos,0]),('Q',[1,n,1]),('Q',[1,n,n])])
            ops.extend([('I',[1,0]),('I',[n+2,100000]),('Q',[1,n+2,1]),('Q',[1,n+2,n+2])])
            cases.append(encode(list(a),ops))
    exhaustive=len(cases)
    rng=random.Random(30652026)
    for _ in range(120):
        n=rng.randrange(1,50);a=[rng.randrange(100001) for _ in range(n)];ops=[]
        for i in range(250):
            op=rng.choice('QMI')
            if op=='Q':
                l=rng.randrange(1,n+1);r=rng.randrange(l,n+1)
                ops.append((op,[l,r,rng.randrange(1,r-l+2)]))
            elif op=='M':
                ops.append((op,[rng.randrange(1,n+1),rng.choice([0,100000,rng.randrange(100001)])]))
            else:
                ops.append((op,[rng.choice([1,n+1,rng.randrange(1,n+2)]),rng.randrange(100001)]));n+=1
        cases.append(encode(a,ops))
    fixture=(ROOT/'tests/fixtures/sequence_kth_sources/kuangbin.inc').read_text()
    prelude='#include <bits/stdc++.h>\nusing namespace std;\n'
    exe,entry=compile('original',prelude+fixture)
    data=''.join(x[0] for x in cases);want=sum((x[1] for x in cases),[])
    got=run(exe,data)
    assert list(map(int,got.split()))==want
    entry.update(datasets=len(cases),queries=len(want),input_sha256=sha(data.encode()),output_sha256=sha(got.encode()),multicase_reset=True)
    report['programs'].append(entry);print('original',len(cases),len(want),'PASS',flush=True)
    # Counter only: preserve original control flow, comparisons, topology and returns.
    anchor='while(x != null){'
    assert fixture.count(anchor)==1
    counted=fixture.replace(anchor,anchor+'\n++query_visits;')
    assert counted.count('int main()')==1
    counted=counted.replace('int main()','int source_main()')
    probe=(ROOT/'tests/sequence_kth_source_probe.cpp').read_text()
    exe,entry=compile('query-visits',prelude+'long long query_visits = 0;\n'+counted+probe)
    got=run(exe,'');rows=[list(map(int,s.split())) for s in got.splitlines()]
    assert [r[0] for r in rows]==[16,64,256,1024,4096]
    assert all(r[1]==r[0] and r[2]==20*r[0] and r[3]>=20*r[0] for r in rows)
    entry.update(columns=['n','left_chain_height','twenty_rank_queries_visits','twenty_full_range_kth_queries_visits'],measurements=rows,instrumentation='Only one visit-counter increment inside original Splay::query loop; rename original main. No splay or algorithm fix.')
    report['programs'].append(entry);print('degeneration',rows,flush=True)
    after=snapshot(ROOT);assert before==after
    report.update(source_after_sha256=after,exhaustive_datasets=exhaustive,random_datasets=120,passed=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json',flush=True)

if __name__=='__main__':
    main()
