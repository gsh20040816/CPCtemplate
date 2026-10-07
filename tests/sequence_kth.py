"""Exact dynamic sequence rank/kth vs independent lists and source protocol."""
from pathlib import Path
import hashlib,json,os,random,subprocess,sys,tempfile,time
from compiler_config import CXX
from sequence_kth_source import encode
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot
from usage_examples import records


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT);out=Path(tempfile.mkdtemp(prefix='sequence-kth-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha=lambda x:hashlib.sha256(x).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='New core and source-model driver; handbook API327; official/online verification pending.')
    def compile(name,text,extra=()):
        cpp=out/(name+'.cpp');cpp.write_text(text);exe=out/name
        command=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(command,capture_output=True,text=True)
        if p.returncode:raise RuntimeError(p.stderr)
        return exe,dict(name=name,command=command,source_sha256=sha(text.encode()),binary_sha256=sha(exe.read_bytes()),compiler_stderr=p.stderr)
    def run(exe,data=''):
        start=time.monotonic();p=subprocess.run([str(exe)],input=data,capture_output=True,text=True,env=env,timeout=240)
        return p,time.monotonic()-start
    prelude='#include <bits/stdc++.h>\n#include <cassert>\n#include <ext/pb_ds/assoc_container.hpp>\n#include <ext/pb_ds/tree_policy.hpp>\nusing namespace std;\n'
    ost=(ROOT/'src/compact/ordered_set.hpp').read_text().split('// BEGIN ost')[1].split('// END ost')[0]
    core='struct SequenceKth'+(ROOT/'src/compact/sequence_kth.hpp').read_text().split('struct SequenceKth',1)[1]
    probe=(ROOT/'tests/sequence_kth.cpp').read_text().replace('#include "../src/compact/sequence_kth.hpp"','')
    for name,text,extra in [('core-header','#include "'+str(ROOT/'tests/sequence_kth.cpp')+'"\n',[]),('core-copy',prelude+ost+core+probe,[]),('core-ndebug',prelude+ost+core+probe,['-DNDEBUG'])]:
        exe,entry=compile(name,text,extra);p,seconds=run(exe)
        if p.returncode or p.stderr or '9000 random operations PASS' not in p.stdout:raise RuntimeError((name,p.stdout,p.stderr))
        entry.update(result=p.stdout,seconds=seconds);report['programs'].append(entry);print(name,p.stdout.strip(),flush=True)
    rng=random.Random(3065327);cases=[]
    for _ in range(200):
        n=rng.randrange(1,35);a=[rng.choice([0,1,100000,rng.randrange(100001)]) for _ in range(n)];ops=[]
        for i in range(180):
            if i%3==0:
                l=rng.randrange(1,n+1);r=rng.randrange(l,n+1);ops.append(('Q',[l,r,rng.randrange(1,r-l+2)]))
            elif i%3==1:
                ops.append(('M',[rng.randrange(1,n+1),rng.choice([0,100000,rng.randrange(100001)])]))
            else:
                ops.append(('I',[rng.choice([1,n+1,rng.randrange(1,n+2)]),rng.randrange(100001)]));n+=1
        cases.append(encode(a,ops))
    small=(''.join(x[0] for x in cases),sum((x[1] for x in cases),[]))
    # Sorted initial sequence plus repeated full-range minimum is the source degeneration case.
    large=[]
    for shape in ['sorted','same']:
        n=30000;a=list(range(n)) if shape=='sorted' else [7]*n
        ops=[('Q',[1,n,1]) for _ in range(300)]
        ops += [('M',[i+1,100000]) for i in range(1000)]
        ops += [('Q',[1,n,1]),('Q',[1,n,n])]
        ops += [('I',[1,0]) for _ in range(1000)]
        ops += [('Q',[1,n+1000,1000]),('Q',[1,n+1000,n+1000])]
        large.append(encode(a,ops))
    expanded=out/'expanded.cpp'
    subprocess.run([sys.executable,'tools/bundle.py','verify/api/sequence_kth.compact.cpp',str(expanded)],cwd=ROOT,check=True)
    text=expanded.read_text()
    row=next(x for x in records() if x['id']=='example-327')
    snippet=(ROOT/'verify/api/sequence_kth.compact.cpp').read_text();snippet=snippet[snippet.index('int main()'):]
    for name,source,extra in [('driver','#include "'+str(ROOT/'verify/api/sequence_kth.compact.cpp')+'"\n',[]),('expanded',row['program'],[]),('minimal',prelude+ost+core+snippet,[]),('ndebug',prelude+ost+core+snippet,['-DNDEBUG'])]:
        exe,entry=compile(name,source,extra);entry['runs']=[]
        for i,(data,want) in enumerate([small,*large]):
            p,seconds=run(exe,data)
            if p.returncode or p.stderr or list(map(int,p.stdout.split()))!=want:raise RuntimeError((name,i,p.returncode,p.stderr,p.stdout[:100]))
            entry['runs'].append(dict(input_sha256=sha(data.encode()),output_sha256=sha(p.stdout.encode()),queries=len(want),seconds=seconds))
        report['programs'].append(entry);print(name,'PASS',flush=True)
    mutant_cases = {
        'strict-instead-inclusive': encode([0, 3], [('Q', [1, 2, 1])]),
        'wrong-insert-position': encode([1, 3], [('I', [1, 2]), ('Q', [1, 1, 1])]),
        'omit-modification': encode([1, 3], [('M', [1, 5]), ('Q', [1, 2, 1])]),
    }
    for name,old,new in [('strict-instead-inclusive','equal ? (int)a.size() : 0','0'),('wrong-insert-position','tree.insert(x - 1, y);','tree.insert(x, y);'),('omit-modification','a[u].keys.erase(old);','a[u].keys.erase({x, old.second});')]:
        mutant=prelude+ost+core+snippet;assert mutant.count(old)==1
        exe,entry=compile(name,mutant.replace(old,new),['-DNDEBUG'])
        data,want=mutant_cases[name]
        p,seconds=run(exe,data)
        if p.returncode or p.stderr or list(map(int,p.stdout.split()))==want:raise RuntimeError(('mutant not cleanly rejected',name,p.stderr))
        entry['oracle_rejected']=True;report['mutants'].append(entry);print(name,'REJECT',flush=True)
    after=snapshot(ROOT);assert before==after
    report.update(source_after_sha256=after,small_datasets=200,large_datasets=2,passed=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json',flush=True)

if __name__=='__main__':
    main()
