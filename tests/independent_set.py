"""Independent vertex-subset optima, grid models and printed scheme certificates."""
import functools
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import resource
import subprocess
import sys
import tempfile
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records


def brute(n, edges):
    adj = [0]*n
    for u,v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    @functools.lru_cache(None)
    def go(mask):
        if not mask:
            return 0
        u = (mask & -mask).bit_length()-1
        rest = mask & ~(1 << u)
        return max(go(rest), 1+go(rest & ~adj[u]))
    return go((1 << n)-1)


def knight(n, blocked):
    cells = [(i,j) for i in range(1,n+1) for j in range(1,n+1) if (i,j) not in blocked]
    edges = [(u,v) for u,(x,y) in enumerate(cells) for v,(a,b) in enumerate(cells[:u])
             if {abs(x-a),abs(y-b)} == {1,2}]
    return brute(len(cells),edges)


def cases():
    groups = {309:[],310:[],311:[]}
    rng = random.Random(3355311)
    def board(name,n,blocked,known=None):
        want = knight(n,blocked) if known is None else known
        raw = f'{n} {len(blocked)}\n'+''.join(f'{x} {y}\n' for x,y in sorted(blocked))
        groups[309].append((name,raw,want,None))
    for n in range(1,4):
        for mask in range((1 << (n*n))-1):
            blocked = {(u//n+1,u%n+1) for u in range(n*n) if mask>>u&1}
            board(f'all-small-{n}-{mask}',n,blocked)
    for i in range(80):
        n = 4+i%2
        blocked = {(x,y) for x in range(1,n+1) for y in range(1,n+1) if rng.randrange(3)==0}
        board(f'knight-random-{i}',n,blocked)
    board('max-open-4x2-tile-matching',200,set(),20000)
    board('max-one-color',200,{(x,y) for x in range(1,201) for y in range(1,201) if (x+y)%2},20000)
    board('max-one-cell',200,{(x,y) for x in range(1,201) for y in range(1,201) if (x,y)!=(200,200)},1)
    def graph(name,n,m,edges,known=None):
        want = brute(n+m,[(u-1,n+v-1) for u,v in edges]) if known is None else known
        raw = f'{n} {m} {len(edges)}\n'+''.join(f'{u} {v}\n' for u,v in edges)
        groups[310].append((name,raw,want,(n,m,edges)))
    for n,m in [(0,0),(0,4),(4,0),(2,4),(4,2)]:
        graph(f'empty-{n}-{m}',n,m,[])
    graph('isolates-and-one-edge',2,3,[(1,2),(1,2)])
    graph('two-stars-opposite',3,3,[(1,1),(1,2),(2,3),(3,3)])
    for i in range(150):
        n,m = rng.randrange(1,7),rng.randrange(1,7)
        edges = [(rng.randrange(1,n+1),rng.randrange(1,m+1)) for _ in range(i%25)]
        graph(f'multigraph-{i}',n,m,edges)
    n = 100000
    graph('max-sparse-path',n,n,[(u,u+1) for u in range(1,n)]+[(u,u) for u in range(1,n+1)],n)
    graph('max-isolated-right',0,n,[],n)
    def coins(name,n,edges,known=None):
        want = 2*n-brute(2*n,[(u-1,n+v-1) for u,v in edges]) if known is None else known
        chosen = set(edges)
        raw = str(n)+'\n'+''.join(''.join('o' if (u,v) in chosen else '.' for v in range(1,n+1))+'\n' for u in range(1,n+1))
        groups[311].append((name,raw,want,(n,n,edges)))
    coins('statement',3,[(1,3),(2,1),(2,3)])
    for n in range(1,4):
        for mask in range(1 << (n*n)):
            coins(f'all-small-{n}-{mask}',n,[(u+1,v+1) for u in range(n) for v in range(n) if mask>>(u*n+v)&1])
    for i in range(60):
        n = 4+i%3
        coins(f'random-{i}',n,[(u,v) for u in range(1,n+1) for v in range(1,n+1) if rng.randrange(3)==0])
    coins('max-complete',100,[(u,v) for u in range(1,101) for v in range(1,101)],100)
    coins('max-diagonal',100,[(u,u) for u in range(1,101)],100)
    coins('max-one-column',100,[(u,17) for u in range(1,101)],1)
    coins('max-empty',100,[],0)
    return groups


def check(k,case,output):
    name,raw,want,data = case
    if k == 309:
        assert list(map(int,output.split())) == [want],name
        return
    lines = output.splitlines()
    if k == 310:
        assert len(lines) == 3 and list(map(int,lines[0].split())) == [want],name
        n,m,edges = data
        a,b = [list(map(int,s.split())) for s in lines[1:]]
        assert a and b and a[0] == len(a)-1 and b[0] == len(b)-1,name
        a,b = a[1:],b[1:]
        assert a == sorted(set(a)) and b == sorted(set(b)),name
        assert all(1<=u<=n for u in a) and all(1<=v<=m for v in b),name
        assert len(a)+len(b) == want,name
        x,y = set(a),set(b)
        assert all(u not in x or v not in y for u,v in edges),name
    else:
        n,m,edges = data
        assert len(lines) == want+1 and list(map(int,lines[0].split())) == [want],name
        x,y = set(),set()
        for line in lines[1:]:
            a = list(map(int,line.split()))
            assert len(a)==2 and a[0] in [1,2] and 1<=a[1]<=n,name
            s = x if a[0]==1 else y
            assert a[1] not in s,name
            s.add(a[1])
        assert all(u in x or v in y for u,v in edges),name


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='independent-set-'+mode+'-',dir=ROOT/'build'))
    flags = ['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    if platform.system() == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    else:
        _,hard = resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha = lambda data: hashlib.sha256(data).hexdigest()
    report = dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],local_stack_mib=512,scope='Independent vertex-subset optimum; knight geometry independent of board coloring; minimum cover edge certificates. Local only.')
    def compile(name,source,extra=()):
        cpp,exe = out/(name+'.cpp'),out/name
        cpp.write_text(source)
        cmd = [CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p = subprocess.run(cmd,capture_output=True)
        assert p.returncode == 0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    def run(exe,raw='',args=()):
        p = subprocess.run([str(exe),*args],input=raw.encode(),capture_output=True,env=env,timeout=300)
        assert p.returncode == 0 and not p.stderr,(exe,p.returncode,p.stdout[:500],p.stderr[-1000:])
        return p.stdout.decode()
    text = (ROOT/'src/compact/graph.hpp').read_text()
    matching = 'struct BipartiteMatching'+text.split('struct BipartiteMatching',1)[1].split('struct Lowlink',1)[0]
    helper = (ROOT/'src/compact/independent_set.hpp').read_text().split('// BEGIN independent_set\n',1)[1].split('// END independent_set',1)[0]
    includes = '#include <algorithm>\n#include <cassert>\n#include <queue>\n#include <utility>\n#include <vector>\n#include <iostream>\n#include <string>\nusing namespace std;\n'
    core = includes+matching+helper
    probe = (ROOT/'tests/independent_set_probe.cpp').read_text()
    copied = '#include <random>\n#include <stdexcept>\n'+core+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    for form,source in [('header','#include "'+str(ROOT/'tests/independent_set_probe.cpp')+'"\n'),('copied',copied)]:
        for release in (False,True):
            exe,entry = compile(form+('-ndebug' if release else '-assert'),source,['-DNDEBUG'] if release else [])
            start = time.monotonic()
            result = run(exe)
            assert result.startswith('PASS '),result
            entry.update(result=result.strip(),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry)
            print(entry['name'],result.strip(),flush=True)
    for name,old,new in [
        ('skip-solve','    g.solve();','    /* omitted */'),
        ('left-not-complement','x[u] = false','x[u] = true'),
        ('right-not-complement','y[v] = false','y[v] = true'),
        ('omit-last-left','u <= g.n','u < g.n'),
        ('return-cover','return {left, right};','return {a, b};')]:
        assert old in helper,name
        source = copied.replace(helper,helper.replace(old,new),1)
        exe,entry = compile(name,source,['-DNDEBUG'])
        result = run(exe,args=('small-only',))
        assert result == 'ORACLE_REJECT\n',(name,result)
        entry['independent_oracle_rejected'] = True
        report['mutants'].append(entry)
        print(name,'ORACLE_REJECT',flush=True)
    groups = cases()
    for k,cs in groups.items():
        row = next(r for r in records() if r['id'] == f'example-{k}')
        minimal = includes+matching+(helper if k!=311 else '')+row['snippet']
        for form,source,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy',minimal,[]),('ndebug',row['program'],['-DNDEBUG'])]:
            exe,entry = compile(f'{k}-{form}',source,extra)
            for case in cs:
                output = run(exe,case[1])
                check(k,case,output)
                entry['runs'].append(dict(case=case[0],input_sha256=sha(case[1].encode()),output_sha256=sha(output.encode()),passed=True))
            report['programs'].append(entry)
            print(k,form,len(cs),'PASS',flush=True)
    for k,name,old,new in [
        (309,'bishop-not-knight','{1, 2}, {1, -2}, {-1, 2}, {-1, -2}','{1, 1}, {1, -1}, {-1, 1}, {-1, -1}'),
        (309,'obstacles-as-isolates','if (id[x][y] != -1)','if (true)'),
        (310,'swap-side-schemes','auto [a, b] = independent_set(g);','auto [b, a] = independent_set(g);'),
        (311,'swap-row-column','for (int u : a) cout << 1','for (int u : a) cout << 2')]:
        row = next(r for r in records() if r['id'] == f'example-{k}')
        assert old in row['snippet']
        source = row['program'].replace(row['snippet'],row['snippet'].replace(old,new))
        exe,entry = compile(name,source,['-DNDEBUG'])
        rejected = False
        for case in groups[k]:
            output = run(exe,case[1])
            try:
                check(k,case,output)
            except AssertionError:
                rejected = True
                entry.update(rejecting_case=case[0],independent_oracle_rejected=True)
                break
        assert rejected,name
        report['mutants'].append(entry)
        print(name,'ORACLE_REJECT',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before == report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:',out/'report.json',flush=True)

if __name__ == '__main__':
    main()
