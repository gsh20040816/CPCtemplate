#!/usr/bin/env python3
"""TSUBSTR: literal tree-path oracle, custom alphabets and exact empty lines."""
import hashlib,json,os,random,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from usage_examples import records
from compiler_config import CXX

def sha(data):return hashlib.sha256(data).hexdigest()

def datasets():
    out=[];rng=random.Random(201204);alphabet='abcdefghijklmnopqrstuvwxyz'
    def add(name,s,edges,queries,want):
        raw=f'{len(s)} {len(queries)}\n{s}\n'+''.join(f'{u+1} {v+1}\n' for u,v in edges)+''.join(f'{a} {k}\n' for a,k in queries)
        expected=str(want[0])+'\n'+''.join(x+'\n' for x in want[1:])
        out.append((name,raw,expected))
    add('official-sample','abcbbaca',[(0,1),(1,2),(0,3),(3,4),(3,5),(3,6),(0,7)],[(alphabet,5),(alphabet,1),('bcadefghijklmnopqrstuvwxyz',5),(alphabet,100)],[12,'aba','','ba','-1'])
    for turn in range(200):
        n=rng.randrange(1,22);s=''.join(rng.choice('abc' if turn%2 else alphabet) for _ in range(n))
        par=[-1]+[rng.randrange(i) for i in range(1,n)]
        subs={''}
        for end in range(n):
            t='';u=end
            while u!=-1:
                t=s[u]+t;subs.add(t);u=par[u]
        edges=[(i,par[i]) for i in range(1,n)];rng.shuffle(edges)
        edges=[(v,u) if rng.randrange(2) else (u,v) for u,v in edges]
        queries=[];answers=[]
        for rep in range(3):
            a=list(alphabet);rng.shuffle(a);a=''.join(a)
            words=sorted(subs,key=lambda t:tuple(a.index(c) for c in t))
            for k in [*range(1,len(words)+2),9223372036854775807]:
                queries.append((a,k));answers.append(words[k-1] if k<=len(words) else '-1')
        add(f'random-{turn}',s,edges,queries,[len(subs),*answers])
    n=250000
    queries=[(alphabet,1),(alphabet,2),(alphabet,n+1),(alphabet,n+2),(alphabet,9223372036854775807)]
    add('max-chain-repetitive-stress','a'*n,[(i-1,i) for i in range(1,n)],queries,[n+1,'','a','a'*n,'-1','-1'])
    s='a'+'b'*(n-1)
    # Lexicographic list: empty, a, ab,...,ab^(n-1),b,...,b^(n-1).
    queries=[(alphabet,1),(alphabet,2),(alphabet,n+1),(alphabet,n+2),(alphabet,2*n),(alphabet,2*n+1)]
    add('max-clone-heavy-stress',s,[(i-1,i) for i in range(1,n)],queries,[2*n,'','a',s,'b','b'*(n-1),'-1'])
    add('max-star-repeated-stress','a'*n,[(0,i) for i in range(1,n)],[(alphabet,1),(alphabet,3),(alphabet,4)],[3,'','aa','-1'])
    # Random-label star satisfies the original random-letter promise.
    s=''.join(rng.choice(alphabet) for _ in range(n))
    words=sorted({'',s[0],*s[1:],*(s[0]+c for c in s[1:])})
    queries=[(alphabet,k) for k in range(1,len(words)+2)]
    add('max-star-random-letters',s,[(0,i) for i in range(1,n)],queries,[len(words),*words,'-1'])
    # Max Q and maximum valid signed-64-bit rank, total output below800KB.
    queries=[(alphabet,[1,2,3,9223372036854775807][i%4]) for i in range(50000)]
    add('max-query-count','z',[],queries,[2,*['' if k==1 else 'z' if k==2 else '-1' for _,k in queries]])
    # A random-label complete binary tree: enumerate ancestor paths directly.
    n=16383;s=''.join(rng.choice(alphabet) for _ in range(n));subs={''}
    for v in range(n):
        t='';u=v
        while u>=0:
            t=s[u]+t;subs.add(t);u=(u-1)//2
    queries=[];answers=[]
    for a in [alphabet,alphabet[::-1]]:
        words=sorted(subs,key=lambda t:tuple(a.index(c) for c in t))
        for k in [1,2,len(words)//2,len(words),len(words)+1]:
            queries.append((a,k));answers.append(words[k-1] if k<=len(words) else '-1')
    add('binary-tree-random-letters',s,[((i-1)//2,i) for i in range(1,n)],queries,[len(subs),*answers])
    return out

def main():
    if not __debug__:raise RuntimeError('Checks must stay enabled')
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='tsubstr-'+mode+'-',dir=ROOT/'build'));before=snapshot(ROOT)
    row=next(r for r in records() if r['id']=='example-261')
    parts=extract_components(json.load(open(ROOT/'docs/catalog.json')))
    core='\n'.join(next(x['code'] for x in parts if x['symbol']==s) for s in row['requires'])
    prelude=''.join('#include <'+s+'>\n' for s in ['algorithm','array','cassert','climits','iostream','optional','queue','string','utility','vector'])+'using namespace std;\n'
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),source_before_sha256=before,programs=[],mutants=[])
    data=datasets()
    def compile(name,source):
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(source)
        cmd=[CXX,*flags,str(cpp),'-o',str(exe)];p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()))
    for name,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('bundle',row['program']),('minimal-copy',prelude+core+'\n'+row['snippet'])]:
        exe,entry=compile(name,source);entry['runs']=[]
        for label,raw,want in data:
            p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=180)
            assert p.returncode==0 and not p.stderr,(name,label,p.returncode,p.stderr[-1000:])
            assert p.stdout.decode()==want,(name,label,p.stdout[:100],want[:100])
            entry['runs'].append(dict(case=label,input_sha256=sha(raw.encode()),output_sha256=sha(p.stdout),passed=True))
        report['programs'].append(entry);print(name,len(data),'exact-output inputs PASS',flush=True)
    copied=prelude+core+'\n'+row['snippet']
    for name,old,new in [('omit-root-letter',"state[0] = sam.add(0, s[0] - 'a');",'state[0] = 0;'),('omit-empty-count',"cout << sam.distinct() + 1 << '\\n';","cout << sam.distinct() << '\\n';"),('rank-offset','index.kth(k - 1, alphabet)','index.kth(k, alphabet)'),('ignore-alphabet','index.kth(k - 1, alphabet)','index.kth(k - 1)'),('lose-empty-line',"if (k == 1) cout << '\\n';",'if (k == 1) cout << "";')]:
        assert copied.count(old)==1,(name,copied.count(old))
        exe,entry=compile(name,copied.replace(old,new));label,raw,want=data[0]
        p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=60)
        assert p.returncode==0 and not p.stderr and p.stdout.decode()!=want,(name,p.returncode,p.stderr)
        entry.update(independent_oracle_rejected=True,output_sha256=sha(p.stdout));report['mutants'].append(entry)
    report.update(passed=True,case_count=len(data),source_after_sha256=snapshot(ROOT),scope='Official API statement and sample; literal ancestor-descendant vertex-label paths, arbitrary input edge order, repeated trie labels, random letters, maximum250000 vertices and50000 queries, LLONG_MAX k, exact empty-line output. Repetitive maximal cases are additional stress beyond random-letter promise. Three full program forms and five semantic driver mutants. No online AC/rank or original1s runtime claim.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('TSUBSTR',mode,'PASS:',out/'report.json',flush=True)
if __name__=='__main__':main()
