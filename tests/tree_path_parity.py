"""Full source-protocol and HLD/lazy composition checked by direct path XOR."""
from pathlib import Path
import hashlib,itertools,json,os,platform,random,resource,subprocess,sys,tempfile
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot
from usage_examples import records

def prufer(n,code):
    d=[1]*n
    for u in code:d[u]+=1
    e=[]
    for v in code:
        u=d.index(1);e.append((u,v,0));d[u]-=1;d[v]-=1
    last=[u for u in range(n) if d[u]==1]
    if len(last)==2:e.append((*last,0))
    return e

def oracle(n,edges,bits):
    g=[[] for _ in range(n)]
    for i,(u,v,w) in enumerate(edges):g[u].append((v,i));g[v].append((u,i))
    answer=0
    for s in range(n):
        seen=[False]*n;seen[s]=True;q=[(s,0)]
        for u,x in q:
            answer+=x
            for v,i in g[u]:
                if not seen[v]:seen[v]=True;q.append((v,x^bits[i]))
    return answer

def encode(n,edges,ops,answers):
    names=[f'node_{n-u:06d}' for u in range(n)]
    data=f'{n}\n'+' '.join(names)+'\n'
    data+=''.join(f'{names[u]} {names[v]} {w}\n' for u,v,w in edges)
    data+=str(len(ops))+'\n'+''.join('Query\n' if x is None else f'Change {x+1}\n' for x in ops)
    return data,answers

def small(n,edges,ops):
    bits=[w for u,v,w in edges];ans=[]
    for x in ops:
        if x is None:ans.append(oracle(n,edges,bits))
        else:bits[x]^=1
    return encode(n,edges,ops,ans)

def pack(cases):
    raw=str(len(cases))+'\n'+''.join(x[0] for x in cases)
    want=''.join(f'Case #{i}:\n'+''.join(str(v)+'\n' for v in c[1]) for i,c in enumerate(cases,1))
    return raw,want

def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal';before=snapshot(ROOT)
    out=Path(tempfile.mkdtemp(prefix='tree-parity-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    if platform.system()=='Darwin':flags+=['-Wl,-stack_size,0x20000000']
    else:
        _,hard=resource.getrlimit(resource.RLIMIT_STACK);resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy();env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha=lambda b:hashlib.sha256(b).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],stack_mib=512,scope='HDU5039 source protocol only, no official statement/AC claim. Source printf format adapted from %I64d to %lld only.')
    def compile(name,text,extra=()):
        cpp=out/(name+'.cpp');exe=out/name;cpp.write_text(text);cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
        return exe,dict(name=name,command=cmd,source_sha256=sha(text.encode()),binary_sha256=sha(exe.read_bytes()),compiler_stderr=p.stderr,runs=[])
    def run(exe,data):
        p=subprocess.run([str(exe)],input=data,capture_output=True,text=True,env=env,timeout=180)
        assert p.returncode==0 and not p.stderr,(p.returncode,p.stderr[-2500:]);return p.stdout
    cases=[];rng=random.Random(50392026)
    for n in range(1,6):
        for code in itertools.product(range(n),repeat=max(0,n-2)):
            edges=prufer(n,code);rng.shuffle(edges)
            edges=[(v,u,w) if rng.randrange(2) else (u,v,w) for u,v,w in edges]
            ops=[None];previous=0
            for i in range(1,1<<(n-1)):
                gray=i^(i>>1);edge=(gray^previous).bit_length()-1
                ops += [edge,None,edge,edge,None];previous=gray
            cases.append(small(n,edges,ops))
    for _ in range(180):
        n=rng.randrange(1,26);edges=[(rng.randrange(v),v,rng.randrange(2)) for v in range(1,n)]
        rng.shuffle(edges);edges=[(v,u,w) if rng.randrange(2) else (u,v,w) for u,v,w in edges]
        ops=[None if n==1 or i%3==0 else rng.randrange(n-1) for i in range(120)]
        cases.append(small(n,edges,ops))
    inputs=[('small-multicase',*pack(cases))]
    for n in [30000,100000]:
        for shape in ['chain','star']:
            edges=[(v-1 if shape=='chain' else 0,v,0) for v in range(1,n)]
            # Single flipped edge cuts off exactly n-v chain vertices or one leaf.
            ops=[None];answers=[0]
            for v in [1,n//2,n-1]:
                count=n-v if shape=='chain' else 1
                ops += [v-1,None,v-1,None]
                answers += [2*count*(n-count),0]
            # Keep many edges toggled at once; distinct star leaves or chain prefixes.
            current=[0]*(n-1)
            for _ in range(200):
                edge=rng.randrange(n-1);current[edge]^=1;ops += [edge,None]
                if shape=='star':one=sum(current)
                else:
                    parity=0;one=0
                    for bit in current:parity^=bit;one+=parity
                answers.append(2*one*(n-one))
            inputs.append((str(n)+'-'+shape,*pack([encode(n,edges,ops,answers),small(1,[],[None,None])])))
    row=next(r for r in records() if r['id']=='example-324');prelude='#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'
    h=(ROOT/'src/compact/tree.hpp').read_text();h='struct HLD'+h.split('struct HLD',1)[1]
    lazy=(ROOT/'src/compact/lazy_segtree.hpp').read_text().split('// BEGIN lazy_segtree',1)[1].split('// END lazy_segtree',1)[0]
    copied=prelude+h+lazy+row['snippet']
    for form,text,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy',copied,[]),('ndebug',copied,['-DNDEBUG'])]:
        exe,entry=compile('324-'+form,text,extra)
        for name,data,want in inputs:
            got=run(exe,data);assert got==want,(form,name,got[:200],want[:200])
            entry['runs'].append(dict(name=name,input_sha256=sha(data.encode()),output_sha256=sha(got.encode()),queries=sum(line.isdigit() for line in want.splitlines())))
        report['programs'].append(entry);print(entry['name'],'PASS',flush=True)
    for name,a,b in [('undirected-count','2LL * zero * one','1LL * zero * one'),('closed-range','l + h.siz[x], true','l + h.siz[x] - 1, true'),('or-composition','return f ^ g;','return f | g;')]:
        assert copied.count(a)==1
        exe,entry=compile(name,copied.replace(a,b),['-DNDEBUG']);got=run(exe,inputs[0][1]);assert got!=inputs[0][2]
        entry['oracle_rejected']=True;report['mutants'].append(entry);print(name,'REJECT',flush=True)
    source=(ROOT/'tests/fixtures/tree_parity_sources/kuangbin.inc').read_text()
    assert source.count('%I64d')==1
    source=prelude+'namespace Original {\n'+source.replace('%I64d','%lld')+'\n}\nint main() { return Original::main(); }\n'
    exe,entry=compile('source',source)
    for name,data,want in inputs[:3]:
        got=run(exe,data);assert got==want,(name,got[:300],want[:300])
        entry['runs'].append(dict(name=name,input_sha256=sha(data.encode()),output_sha256=sha(got.encode())))
    report['source']=entry;print('original source PASS',flush=True)
    after=snapshot(ROOT);assert before==after
    report.update(source_after_sha256=after,small_datasets=len(cases),small_queries=sum(len(c[1]) for c in cases),passed=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json',flush=True)

if __name__=='__main__':main()
