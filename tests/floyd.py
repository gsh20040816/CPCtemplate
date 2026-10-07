"""All-source synchronous Bellman-Ford oracles and full Floyd driver certificates."""
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records


def reference(n,e):
    matrix = []
    for s in range(1,n+1):
        d = [None]*(n+1)
        d[s] = 0
        for step in range(n):
            next = d[:]
            for u,v,w in e:
                if d[u] is not None and (next[v] is None or d[u]+w < next[v]):
                    next[v] = d[u]+w
            if step == n-1 and next != d:
                return None
            d = next
        matrix.append(d[1:])
    return matrix


def cases():
    rng = random.Random(11672)
    groups = {k:[] for k in (304,305,306)}
    def add(k,name,n,e,queries=None,known=False):
        if queries is None:
            queries = [(u,v) for u in range(1,n+1) for v in range(1,n+1)]
        directed = e+[(v,u,w) for u,v,w in e] if k == 305 else e
        best = reference(n,directed) if known is False else known
        raw = f'{n} {len(e)}'+(f' {len(queries)}' if k != 304 else '')+'\n'
        raw += ''.join(f'{u-(k==304)} {v-(k==304)} {w}\n' for u,v,w in e)
        if k != 304:
            raw += ''.join(f'{u} {v}\n' for u,v in queries)
        groups[k].append((name,raw,n,e,queries,best))
    add(304,'aoj-statement',4,[(1,2,1),(1,3,5),(2,3,2),(2,4,4),(3,4,1),(4,3,7)])
    add(304,'disconnected-negative-cycle',4,[(2,3,-1),(3,2,0)])
    add(305,'parallel-bidirectional',3,[(1,2,20),(1,2,3),(2,3,5)])
    add(306,'parallel-and-self',4,[(1,1,0),(1,2,9),(1,2,-3),(2,3,7),(3,3,10)])
    add(306,'unreachable-negative-tail',4,[(2,3,-10),(3,4,-20)])
    for i in range(100):
        n = 1+i%8
        possible = [(u,v) for u in range(1,n+1) for v in range(1,n+1) if u != v]
        rng.shuffle(possible)
        e = [(u,v,rng.randrange(-20,21)) for u,v in possible[:i%25]]
        if i%2:
            h = [0]+[rng.randrange(-20,21) for _ in range(n)]
            e = [(u,v,rng.randrange(10)+h[v]-h[u]) for u,v,w in e]
        add(304,f'directed-{i}',n,e)
        add(306,f'api-{i}',n,e+([(1,1,0)] if i%3 == 0 else []))
        positive = [(u,v,rng.randrange(1,1000000001)) for u,v in possible[:max(1,i%25)]] or [(1,1,1)]
        if i%3 == 0:
            positive += [(positive[0][0],positive[0][1],1)]
        add(305,f'undirected-{i}',n,positive)
    e = [(1,2,-(1<<63)),(2,3,-(1<<63)),(4,5,(1<<63)-1),(5,6,(1<<63)-1)]
    add(306,'signed64-extremes',6,e)
    add(306,'negative-self-loop',4,[(4,4,-(1<<63))])
    add(306,'zero-cycle-ties',4,[(1,2,0),(2,3,0),(3,1,0),(2,4,5),(3,4,5)])
    n = 100
    e = [(u,u+1,-20000000) for u in range(1,n)]
    best = [[-20000000*(v-u) if v>=u else None for v in range(n)] for u in range(n)]
    add(304,'max-negative-chain',n,e,known=best)
    e = [(u,v,20000000) for u in range(1,n+1) for v in range(1,n+1) if u != v]
    add(304,'max-dense',n,e,known=[[0 if u==v else 20000000 for v in range(n)] for u in range(n)])
    n = 500
    queries = [(rng.randrange(n)+1,rng.randrange(n)+1) for _ in range(100000)]
    e = [(u,u+1,1000000000) for u in range(1,n)]
    e += [(1,2,1000000000)]*(n*n-len(e))
    add(305,'max-chain-road-query-counts',n,e,queries,known=[[abs(u-v)*1000000000 for v in range(n)] for u in range(n)])
    e = [(u,v,1000000000) for u in range(1,n+1) for v in range(u+1,n+1)]
    e += [(1,2,1000000000)]*(n*n-len(e))
    add(305,'max-dense-road-query-counts',n,e,queries,known=[[0 if u==v else 1000000000 for v in range(n)] for u in range(n)])
    n = 150
    e = [(u,u-1,-(1<<63)) for u in range(n,1,-1)]
    queries = [(n,u) for u in range(1,n+1)]+[(1,n),(n,n)]
    best = [[-(1<<63)*(u-v) if u>=v else None for v in range(n)] for u in range(n)]
    add(306,'wide-reverse-chain',n,e,queries,known=best)
    add(306,'late-negative-pivot',n,e+[(1,n,(1<<63)-1)],queries,known=None)
    n = 120
    e = [(u,v,-(1<<63)) for u in range(1,n+1) for v in range(1,n+1) if u != v]
    add(306,'dense-extreme-negative-cycle',n,e,[(1,n)],known=None)
    return groups


def check(k,case,output):
    name,raw,n,e,queries,best = case
    if best is None:
        assert output.split() == ['NEGATIVE','CYCLE'],name
    elif k == 304:
        lines = output.splitlines()
        assert len(lines) == n,name
        for row,want in zip(lines,best):
            assert row.split() == ['INF' if d is None else str(d) for d in want],name
    elif k == 305:
        assert output.split() == [str(-1 if best[u-1][v-1] is None else best[u-1][v-1]) for u,v in queries],name
    else:
        lines = output.splitlines()
        assert len(lines) == len(queries),name
        for (s,t),line in zip(queries,lines):
            want = best[s-1][t-1]
            if want is None:
                assert line == 'INF',name
                continue
            a = list(map(int,line.split()))
            assert len(a)>=2 and a[0]==want and a[1]==len(a)-2 and a[1]<n,name
            ids = a[2:]
            u,total,seen = s,0,{s}
            for id in ids:
                assert 0<=id<len(e),name
                x,y,w = e[id]
                assert x==u and y not in seen,name
                seen.add(y)
                total+=w
                u=y
            assert u==t and total==want,name


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='floyd-'+mode+'-',dir=ROOT/'build'))
    flags = ['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha = lambda data: hashlib.sha256(data).hexdigest()
    report = dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='Floyd APSP with negative-pivot early exit; independent synchronous Bellman-Ford, original-edge certificates, full AOJ/CSES/API programs; local only.')
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
    header = (ROOT/'src/compact/floyd.hpp').read_text().replace('#pragma once\n','')
    probe = (ROOT/'tests/floyd_probe.cpp').read_text()
    copied = header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    for form,source in [('header','#include "'+str(ROOT/'tests/floyd_probe.cpp')+'"\n'),('copied',copied)]:
        for release in (False,True):
            exe,entry = compile(form+('-ndebug' if release else '-assert'),source,['-DNDEBUG'] if release else [])
            start = time.monotonic()
            result = run(exe)
            assert result.startswith('PASS '),result
            entry.update(result=result.strip(),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry)
            print(entry['name'],result.strip(),flush=True)
    for name,old,new in [
        ('unreachable-left','if (dis[u][k] == inf) continue;','/* omitted */'),
        ('unreachable-right','dis[k][v] != inf && ',' '),
        ('nonminimum-parallel','if (w < dis[u][v])','if (true)'),
        ('positive-diagonal','dis[u][u] = 0;','dis[u][u] = 1;'),
        ('missing-negative-cycle','if (dis[k][k] < 0) return false;','/* omitted */'),
        ('wrong-first-edge','nxt[u][v] = nxt[u][k];','nxt[u][v] = nxt[k][v];'),
        ('last-pivot-skipped','k <= n; k++','k < n; k++')]:
        assert old in header,name
        source = copied.replace(header,header.replace(old,new),1)
        exe,entry = compile(name,source,['-DNDEBUG'])
        result = run(exe,args=('small-only',))
        assert result == 'ORACLE_REJECT\n',(name,result)
        entry['independent_oracle_rejected'] = True
        report['mutants'].append(entry)
        print(name,'ORACLE_REJECT',flush=True)
    groups = cases()
    for k,cs in groups.items():
        row = next(r for r in records() if r['id'] == f'example-{k}')
        for form,source,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy','#include <iostream>\n#include <string>\n#include <algorithm>\n'+header+'\n'+row['snippet'],[]),('ndebug',row['program'],['-DNDEBUG'])]:
            exe,entry = compile(f'{k}-{form}',source,extra)
            for case in cs:
                output = run(exe,case[1])
                check(k,case,output)
                entry['runs'].append(dict(case=case[0],input_sha256=sha(case[1].encode()),output_sha256=sha(output.encode()),passed=True))
            report['programs'].append(entry)
            print(k,form,len(cs),'PASS',flush=True)
    for k,name,old,new in [
        (304,'negative-means-unreachable','t.dis[u][v] == Floyd::inf','t.dis[u][v] < 0'),
        (305,'one-way-roads','        t.add(v, u, w);','        // omitted'),
        (305,'all-queries-reversed-index','t.dis[u][v]','t.dis[u][u]')]:
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
