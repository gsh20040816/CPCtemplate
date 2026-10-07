"""Tree-path composition: BFS path oracles, exhaustive labelled trees and exact output."""
import hashlib
import itertools
import json
import os
import platform
from pathlib import Path
import random
import resource
import subprocess
import sys
import tempfile
import time
from collections import deque
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from audit_copy_context import extract_components
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records


def path(n, edges, u, v):
    g = [[] for _ in range(n)]
    for i, (a, b, _) in enumerate(edges):
        g[a].append((b, i)); g[b].append((a, i))
    parent = [None] * n; parent[u] = (u, -1); q = deque([u])
    while q:
        a = q.popleft()
        for b, i in g[a]:
            if parent[b] is None:
                parent[b] = (a, i); q.append(b)
    vertices = [v]; ids = []
    while v != u:
        v, i = parent[v]; vertices.append(v); ids.append(i)
    return vertices[::-1], ids[::-1]


def prufer(n, code):
    degree = [1] * n
    for x in code: degree[x] += 1
    edges = []
    for x in code:
        y = next(i for i in range(n) if degree[i] == 1)
        edges.append((x, y, len(edges) + 1)); degree[x] -= 1; degree[y] -= 1
    if n > 1:
        a, b = [i for i in range(n) if degree[i] == 1]; edges.append((a, b, n))
    return edges


def small(kind, n, edges, rng, exhaustive=False):
    # Reverse input endpoints and permute input edge indices independently of root/vertex IDs.
    edges = [(b, a, w) if rng.randrange(2) else (a, b, w) for a, b, w in edges]
    rng.shuffle(edges)
    weights = [rng.randrange(-100, 101) for _ in edges]
    values = [rng.randrange(-1000, 1001) for _ in range(n)]
    raw = []; want = []
    pairs = list(itertools.product(range(n), repeat=2)) if exhaustive else [(rng.randrange(n), rng.randrange(n)) for _ in range(150)]
    ops = []
    if kind == 281:
        raw = [' '.join(map(str, values))] + [f'{a+1} {b+1}' for a, b, _ in edges]
    else:
        raw = [f'{a+1} {b+1} {weights[i]}' for i, (a, b, _) in enumerate(edges)]
    for step, (u, v) in enumerate(pairs):
        vertices, ids = path(n, edges, u, v)
        if kind == 281:
            x = rng.randrange(1000001); sign = 1 if step % 2 else -1
            ops.append(f'{"I" if sign > 0 else "D"} {u+1} {v+1} {x}')
            for a in vertices: values[a] += sign * x
            for a in range(n) if exhaustive else [u, v, rng.randrange(n)]:
                ops.append(f'Q {a+1}'); want.append(values[a])
        elif kind == 282:
            if edges:
                i = step % len(edges); x = rng.choice([-(1 << 63), (1 << 63)-1, -100, 0, 100])
                ops.append(f'CHANGE {i+1} {x}'); weights[i] = x
            ops.append(f'QUERY {u+1} {v+1}')
            want.append(max((weights[i] for i in ids), default=0))
        else:
            ops.append(f'DIST {u+1} {v+1}'); want.append(sum(weights[i] for i in ids))
            for k in range(1, len(vertices)+1) if exhaustive else sorted(set([1, len(vertices), rng.randrange(1, len(vertices)+1)])):
                ops.append(f'KTH {u+1} {v+1} {k}'); want.append(vertices[k-1]+1)
    if kind == 281:
        raw = [f'{n} {n-1} {len(ops)}'] + raw + ops
    else: raw = [str(n)] + raw + ops + ['DONE']
    return '\n'.join(raw)+'\n', ''.join(str(x)+'\n' for x in want) + ('\n' if kind == 283 else '')


def large(kind, shape):
    n = 50000 if kind == 281 else 10000
    edges = [(i-1 if shape == 'chain' else 0, i, 100000) for i in range(1, n)]
    q = 50000 if kind == 281 else 100000
    ops = []; want = []
    if kind == 281:
        raw = [f'{n} {n-1} {q}', ' '.join(['1000000000000']*n)] + [f'{a+1} {b+1}' for a,b,_ in edges]
        inc = 0
        for i in range(q):
            if i % 2 == 0:
                ops.append(f'I 1 {n} 1000000'); inc += 1000000
            else:
                u = 1 if i % 4 == 1 else n//2
                ops.append(f'Q {u}')
                want.append(10**12 + (inc if shape == 'chain' or u in [1,n] else 0))
    elif kind == 282:
        raw = [str(n)] + [f'{b+1} {a+1} {w}' for a,b,w in edges]
        w = 100000
        for i in range(q):
            if i % 3 == 0:
                w = 100001+i; ops.append(f'CHANGE {n-1} {w}')
            else:
                u = 1 if shape == 'chain' else 2
                ops.append(f'QUERY {n} {u}'); want.append(w)
        ops.append('DONE')
    else:
        raw = [str(n)] + [f'{b+1} {a+1} {w}' for a,b,w in edges]
        for i in range(q):
            u, v = ((1,n) if i % 2 else (n,1)) if shape == 'chain' else (n,2)
            count = n if shape == 'chain' else 3
            if i % 3 == 0:
                ops.append(f'DIST {u} {v}'); want.append((count-1)*100000)
            else:
                k = i % count + 1; ops.append(f'KTH {u} {v} {k}')
                want.append((k if u == 1 else n+1-k) if shape == 'chain' else [n,1,2][k-1])
        ops.append('DONE')
    inp='\n'.join(raw+ops)+'\n'
    if kind != 281: inp = '1\n\n'+inp
    return inp, ''.join(str(x)+'\n' for x in want)+ ('\n' if kind == 283 else '')


def cases(kind):
    rng = random.Random(kind); result = []
    if kind == 282:
        result.append(('official', '1\n\n3\n1 2 1\n2 3 2\nQUERY 1 2\nCHANGE 1 3\nQUERY 1 2\nDONE\n', '1\n3\n'))
    if kind == 283:
        result.append(('official','1\n\n6\n1 2 1\n2 4 1\n2 5 2\n1 3 1\n3 6 2\nDIST 4 6\nKTH 4 6 4\nDONE\n','5\n3\n\n'))
    trees=[]
    for n in range(1,6):
        for code in itertools.product(range(n), repeat=max(0,n-2)):
            trees.append(small(kind,n,prufer(n,code),rng,True))
    # Batch at most 20 independent trees per input, respecting both SPOJ t bounds.
    for i in range(0,len(trees),20):
        batch=trees[i:i+20];inp='\n'.join(x for x,_ in batch)
        if kind != 281: inp=str(len(batch))+'\n\n'+inp
        result.append((f'exhaustive-labelled-trees-{i}',inp,''.join(y for _,y in batch)))
    for i in range(60):
        batch=[]
        for n in [1+i%17,2+i%13,1]:
            edges=[(v,rng.randrange(v),1) for v in range(1,n)]
            batch.append(small(kind,n,edges,rng))
        inp='\n'.join(x for x,_ in batch)
        if kind != 281: inp='3\n\n'+inp
        result.append((f'random-reset-{i}',inp,''.join(y for _,y in batch)))
    for shape in ['chain','star']:
        inp,out=large(kind,shape);result.append((f'large-{shape}',inp,out))
    return result


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT);out=Path(tempfile.mkdtemp(prefix='tree-path-usages-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    _,hard=resource.getrlimit(resource.RLIMIT_STACK)
    darwin=platform.system()=='Darwin'
    target=512*1024*1024 if darwin or hard==resource.RLIM_INFINITY else min(512*1024*1024,hard)
    if darwin: flags += ['-Wl,-stack_size,0x20000000']
    def limits():resource.setrlimit(resource.RLIMIT_STACK,(target,hard))
    components={x['symbol']:x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    prelude=''.join('#include <'+s+'>\n' for s in ['algorithm','cassert','iostream','limits','optional','string','utility','vector'])+'using namespace std;\n'
    report=dict(mode=mode,source_before_sha256=before,scope='Only new tree-path compositions; independent BFS paths, all labelled trees through n=5, mutations, chain/star stress. No online verdict, resource-pass, or full-library rerun.',stack_bytes=target,programs=[],mutants=[])
    sha=lambda x:hashlib.sha256(x).hexdigest()
    def compile(name,source,ndebug=False):
        cpp=out/(name+'.cpp');cpp.write_text(source);exe=out/name
        cmd=[CXX,*flags,*(['-DNDEBUG'] if ndebug else []),str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True);assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    allrows={r['id']:r for r in records()}
    for kind in [281,282,283]:
        row=allrows[f'example-{kind}'];cs=cases(kind)
        minimal=prelude+'\n'.join(components[s] for s in row['requires'])+'\n'+row['snippet']
        sources=[('driver','#include "'+str(ROOT/row['driver'])+'"\n',False),('expanded',row['program'],False),('minimal-copy',minimal,False),('minimal-ndebug',minimal,True)]
        for form,source,ndebug in sources:
            exe,entry=compile(f'{kind}-{form}',source,ndebug)
            for name,raw,want in cs:
                start=time.monotonic();p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,timeout=180,env=env,preexec_fn=None if darwin else limits)
                assert p.returncode==0 and not p.stderr,(kind,form,name,p.returncode,p.stderr[-1000:])
                assert p.stdout.decode()==want,(kind,form,name,p.stdout[:500],want[:500])
                entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start,passed=True))
            report['programs'].append(entry);print(kind,form,len(cs),'PASS',flush=True)
        mutations={281:[('omit-diff-end','bit.add(r + 1, -x);',';'),('omit-decrease',"if (op == 'D') x = -x;",';')],282:[('wrong-endpoint','h.dep[a[i]] > h.dep[b[i]]','h.dep[a[i]] < h.dep[b[i]]'),('include-lca','}, true);','}, false);')],283:[('edge-count-as-weight','(d[u] - d[p]) + (d[v] - d[p])','h.distance(u, v)'),('reverse-kth','a + b + 1 - k','0')]}
        for name,old,new in mutations[kind]:
            assert minimal.count(old)==1,(kind,old)
            exe,entry=compile(f'{kind}-mutant-{name}',minimal.replace(old,new),True)
            for case,raw,want in cs:
                if case.startswith('large'):continue
                p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,timeout=180,env=env,preexec_fn=None if darwin else limits)
                assert p.returncode==0 and not p.stderr,(kind,name,p.returncode,p.stderr[-500:])
                if p.stdout.decode()!=want:
                    entry.update(independent_oracle_rejected=True,case=case,input_sha256=sha(raw.encode()),expected_sha256=sha(want.encode()),actual_sha256=sha(p.stdout));break
            else:raise AssertionError((kind,name,'survived'))
            report['mutants'].append(entry);print(kind,name,'ORACLE_REJECT',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
