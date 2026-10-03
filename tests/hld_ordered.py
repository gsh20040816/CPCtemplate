"""Exact ordered paths, noncommutative affine use, and copied-context checks."""
import argparse, hashlib, json, os, random, resource, subprocess, sys, tempfile, time
from collections import deque
from pathlib import Path
if not __debug__:
    raise RuntimeError('Run this test without Python optimization')
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from usage_examples import records
from audit_copy_context import extract_components
from run_provenance import snapshot
MOD=998244353


def path(g,u,v):
    parent=[-1]*len(g);parent[u]=u;q=deque([u])
    while q:
        a=q.popleft()
        if a==v:break
        for b in g[a]:
            if parent[b]<0:parent[b]=a;q.append(b)
    ans=[]
    while v!=u:ans.append(v);v=parent[v]
    return [u]+ans[::-1]


def make_small(rng,n,queries,zero=False):
    edges=[(v,rng.randrange(v)) for v in range(1,n)];rng.shuffle(edges)
    g=[[] for _ in range(n)]
    for u,v in edges:g[u].append(v);g[v].append(u)
    f=[(rng.randrange(0 if zero else 1,MOD),rng.randrange(MOD)) for _ in range(n)]
    lines=[f'{n} {queries}']+[f'{a} {b}' for a,b in f]+[f'{u} {v}' for u,v in edges];answers=[]
    for i in range(queries):
        if i%3==0:
            p=rng.randrange(n);a=rng.randrange(0 if zero else 1,MOD);b=rng.randrange(MOD)
            if zero and i%6==0:a=0
            lines.append(f'0 {p} {a} {b}');f[p]=(a,b)
        else:
            u=rng.randrange(n);v=rng.randrange(n);x=rng.randrange(MOD)
            lines.append(f'1 {u} {v} {x}')
            for p in path(g,u,v):a,b=f[p];x=(a*x+b)%MOD
            answers.append(x)
    return '\n'.join(lines)+'\n','\n'.join(map(str,answers))+'\n'


def large_case(kind):
    n=q=200000;lines=[f'{n} {q}'];answers=[]
    if kind=='chain':
        lines+=['1 1']*n;lines += [f'{i-1} {i}' for i in range(1,n)];last=1
        for i in range(q):
            if i%4==0:
                last=i%MOD;lines.append(f'0 {n-1} 1 {last}')
            else:
                u,v=(0,n-1) if i%2 else (n-1,0)
                lines.append(f'1 {u} {v} {i}');answers.append((i+n-1+last)%MOD)
    elif kind=='star':
        f=[((i+1)%MOD,(i*37)%MOD) for i in range(n)]
        lines += [f'{a} {b}' for a,b in f];lines += [f'0 {i}' for i in range(1,n)]
        for i in range(q):
            if i%5==0:
                p=(i*71)%n;f[p]=(i+1,i*3);lines.append(f'0 {p} {i+1} {i*3}')
            else:
                u=(i*17)%n;v=(i*31)%n;x=i;lines.append(f'1 {u} {v} {x}')
                seq=[u] if u==v else [u,v] if not u or not v else [u,0,v]
                for p in seq:a,b=f[p];x=(a*x+b)%MOD
                answers.append(x)
    else:
        lines+=['2 3']*n;lines += [f'{(i-1)//2} {i}' for i in range(1,n)]
        for i in range(q):
            u=(i*173+11)%n;v=(i*317+97)%n;x=i
            lines.append(f'1 {u} {v} {x}')
            a,b=u+1,v+1;k=1
            while a!=b:
                if a>b:a//=2
                else:b//=2
                k+=1
            power=pow(2,k,MOD);answers.append((power*x+3*(power-1))%MOD)
    return '\n'.join(lines)+'\n','\n'.join(map(str,answers))+'\n'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sanitizer',action='store_true');args=ap.parse_args()
    san=args.sanitizer or os.environ.get('SANITIZE')=='1' or os.environ.get('CPC_SANITIZE')=='1';mode='sanitizer' if san else 'normal'
    before=snapshot(ROOT);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    source=(ROOT/'src/compact/tree.hpp').read_text();old=(ROOT/'tests/fixtures/ordered-hld/original.hpp').read_text()
    cut=source.index('    // Emit u-to-v order;');assert source[:cut].rstrip()+'\n};\n'==old
    out=Path(tempfile.mkdtemp(prefix='hld-ordered-'+mode+'-',dir=ROOT/'build'))
    compiler=Path(subprocess.check_output(['which',CXX],text=True).strip()).resolve();frontend=Path(subprocess.check_output([CXX,'-print-prog-name=cc1plus'],text=True).strip()).resolve();ch,fh=sha(compiler),sha(frontend)
    flags=['-std=c++20']+(['-O1','-g','-fsanitize=address,undefined'] if san else ['-O2'])
    soft,hard=resource.getrlimit(resource.RLIMIT_STACK);target=524288*1024 if hard==resource.RLIM_INFINITY else min(524288*1024,hard)
    def limits():
        resource.setrlimit(resource.RLIMIT_STACK,(target,hard))
        _,c=resource.getrlimit(resource.RLIMIT_CORE);resource.setrlimit(resource.RLIMIT_CORE,(0,c))
    commands=[]
    def run(cmd,data=None,expected=0):
        start=time.monotonic();p=subprocess.run(cmd,input=data,text=True,capture_output=True,cwd=ROOT,preexec_fn=limits,timeout=180)
        index=len(commands);files={}
        for name,value in [('stdin',data),('stdout',p.stdout),('stderr',p.stderr)]:
            if value is not None:
                f=out/f'{index}.{name}';f.write_text(value);files[name]=str(f.relative_to(ROOT));files[name+'_sha256']=sha(f)
        commands.append(dict(command=list(map(str,cmd)),returncode=p.returncode,seconds=time.monotonic()-start,**files))
        assert p.returncode==expected,(cmd,p.returncode,p.stderr[:1200])
        if data is not None and expected==0:assert not p.stderr,p.stderr
        return p.stdout
    prelude='#include <algorithm>\n#include <array>\n#include <bit>\n#include <cassert>\n#include <iostream>\n#include <numeric>\n#include <queue>\n#include <random>\n#include <utility>\n#include <vector>\nusing namespace std;\n'
    components={x['symbol']:x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    body=(ROOT/'tests/hld_ordered.cpp').read_text().split('long long trees',1)[1]
    minimal=prelude+components['HLD']+'\nlong long trees'+body
    core_results={}
    for name,text in [('header',(ROOT/'tests/hld_ordered.cpp').read_text().replace('../src/',str(ROOT/'src')+'/')),('copied',minimal)]:
        src=out/f'core-{name}.cpp';src.write_text(text);exe=src.with_suffix('');run([CXX,*flags,'-pedantic-errors',str(src),'-o',str(exe)])
        stdout=run([str(exe)],'');assert '765632 exact directed vertex/edge paths' in stdout
        core_results[name]=dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),binary=str(exe.relative_to(ROOT)),binary_sha256=sha(exe),stdout=stdout.strip())
    # Deliberately wrong versions must fail the actual exact-order oracle.
    prefix,tail=minimal.split('    template <class F> void path_ordered',1)
    variants={
        'reverse-common-chain':('work(dfn[v] + edge, dfn[u], true);','work(dfn[v] + edge, dfn[u], false);'),
        'wrong-down-buffer-order':('down.rbegin(); it != down.rend();','down.begin(); it != down.end();'),
        'keep-lca-in-edge-mode':('dfn[v] + edge','dfn[v] + 0')}
    for name,(a,b) in variants.items():
        assert a in tail;text=prefix+'    template <class F> void path_ordered'+tail.replace(a,b)
        src=out/f'mutant-{name}.cpp';src.write_text(text);exe=src.with_suffix('');run([CXX,*flags,str(src),'-o',str(exe)])
        run([str(exe)],'',expected=-6)
        assert 'actual == expected' in (out/Path(commands[-1]['stderr']).name).read_text()
    rng=random.Random(231);cases=[]
    for i in range(100):cases.append(('official-small',*make_small(rng,1+i%35,80)))
    for i in range(10):cases.append(('extension-zero-multiplier',*make_small(rng,1+i,40,True)))
    # Independent hand certificate with several buffered v-side segments.
    functions=[(i,i+1) for i in range(1,16)];edges=[(i//2-1,i-1) for i in range(2,16)]
    data='15 6\n'+'\n'.join(f'{a} {b}' for a,b in functions)+'\n'+'\n'.join(f'{u} {v}' for u,v in edges)+'\n1 10 14 0\n1 14 10 0\n1 10 10 10\n0 0 17 19\n1 10 14 0\n1 14 10 0\n'
    cases.append(('official-directed-certificate',data,'43711\n40503\n122\n729466\n683013\n'))
    for kind in ['chain','star','binary']:cases.append(('official-max-'+kind,*large_case(kind)))
    row=next(r for r in records() if r['id']=='example-231')
    forms={'direct':(ROOT/row['driver']).read_text().replace('../../src/',str(ROOT/'src')+'/'),'expanded':row['program'],'copied':prelude+'\n'.join(components[s] for s in row['requires'])+'\n'+row['snippet']}
    reports={}
    for name,text in forms.items():
        src=out/f'program-{name}.cpp';src.write_text(text);exe=src.with_suffix('');run([CXX,*flags,str(src),'-o',str(exe)])
        timings=[]
        for category,data,want in cases:
            output=run([str(exe)],data)
            assert output.split()==want.split(),(name,category,output[:200],want[:200])
            expected_file=out/f'{len(commands)-1}.expected';expected_file.write_text(want)
            commands[-1]['category']=category;commands[-1]['expected']=str(expected_file.relative_to(ROOT));commands[-1]['expected_sha256']=sha(expected_file)
            timings.append({'category':category,'seconds':commands[-1]['seconds']})
        reports[name]=dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),binary=str(exe.relative_to(ROOT)),binary_sha256=sha(exe),cases=len(cases),official_inputs=sum(not c[0].startswith('extension') for c in cases),extension_inputs=sum(c[0].startswith('extension') for c in cases),timings=timings)
    wrong=forms['copied'].replace('b[0] * a[1] + b[1]','a[0] * b[1] + a[1]')
    assert wrong!=forms['copied']
    src=out/'mutant-affine-order.cpp';src.write_text(wrong);exe=src.with_suffix('')
    run([CXX,*flags,str(src),'-o',str(exe)])
    bad=run([str(exe)],'2 1\n2 1\n3 4\n0 1\n1 0 1 1\n')
    assert bad.split()==['15'] and bad.split()!=['13'], 'Affine-order negative control changed'
    assert snapshot(ROOT)==before and ch==sha(compiler) and fh==sha(frontend)
    report=dict(mode=mode,passed=True,source_before_sha256=before,source_after_sha256=snapshot(ROOT),compiler=str(compiler),compiler_sha256=ch,frontend=str(frontend),frontend_sha256=fh,compiler_version=subprocess.check_output([CXX,'--version'],text=True).strip(),environment={k:os.environ.get(k) for k in ['CXX','ASAN_OPTIONS','UBSAN_OPTIONS','CPC_SANITIZE','SANITIZE']},flags=flags,stack=dict(inherited_soft=soft,hard=hard,child_soft=target),core=core_results,negative_mutations=len(variants),affine_order_negative_control=True,programs=reports,commands=commands,scope='Exact ordered paths and affine composition for the actual HLD and printed/copied programs. Three n=q=200000 shapes per form; zero multiplier cases are extra-domain extensions, not official LC inputs. Local timings with explicitly raised stack, not online AC or a speed rank; no full-suite/LeakSanitizer claim.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(f'Ordered HLD {mode}: two core forms, three rejected mutations, {len(cases)} complete inputs x three forms PASS; report {out.relative_to(ROOT)}/report.json',flush=True)

if __name__=='__main__':main()
