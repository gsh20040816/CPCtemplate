"""DAG path oracle, full copied programs and independent route certificates; local only."""
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
sys.path.insert(0, str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records


def reference(n, edges, s):
    # Recursive color search and enumeration, deliberately no topological DP.
    g = [[] for _ in range(n+1)]
    for u,v,w in edges:
        g[u].append((v,w))
    color = [0]*(n+1)
    def visit(u):
        color[u] = 1
        for v,w in g[u]:
            if color[v] == 1 or (color[v] == 0 and not visit(v)):
                return False
        color[u] = 2
        return True
    if any(color[u] == 0 and not visit(u) for u in range(1,n+1)):
        return None
    best = [None]*(n+1)
    def walk(u,total):
        best[u] = total if best[u] is None else max(best[u],total)
        for v,w in g[u]:
            walk(v,total+w)
    for u in range(1,n+1):
        if not s or u == s:
            walk(u,0)
    return best


def cases():
    rng = random.Random(18071680)
    groups = {k:[] for k in (301,302,303)}
    def add(name,n,edges,s=1,kinds=(301,302,303),known=None):
        for k in kinds:
            e = [(u,v,1 if k == 302 else w) for u,v,w in edges]
            start = s if k == 303 else 1
            best = known[k] if known is not None else reference(n,e,start)
            raw = f'{n} {len(e)}'+(f' {s}' if k == 303 else '')+'\n'
            raw += ''.join(f'{u} {v}'+(f' {w}' if k != 302 else '')+'\n' for u,v,w in e)
            groups[k].append((name,raw,n,e,start,best))
    add('unreachable-positive-tail',4,[(2,3,100000),(3,4,100000)])
    add('negative-answer',4,[(1,2,-7),(2,4,-9),(1,4,-100)])
    add('nonzero-indegree-source',4,[(2,1,3),(1,3,2),(3,4,1)])
    add('arbitrary-topological-numbering',5,[(1,4,2),(4,2,3),(2,3,-7),(3,5,8)])
    add('parallel-best-not-first',3,[(1,2,-8),(1,2,-1),(2,3,-7),(2,3,-10)])
    add('zero-ties',4,[(1,2,0),(1,3,0),(2,4,0),(3,4,0)])
    add('singleton',1,[],kinds=(301,303))
    for i in range(100):
        n = 2+i%7
        order = list(range(1,n+1))
        rng.shuffle(order)
        e = [(order[a],order[b],rng.randrange(-100000,100001)) for a in range(n) for b in range(a+1,n) if rng.randrange(3)]
        if not e:
            e = [(order[0],order[1],0)]
        if i%3 == 0:
            e += [(e[0][0],e[0][1],rng.randrange(-100000,100001))]
        rng.shuffle(e)
        add(f'permuted-dag-{i}',n,e,s=i%(n+1))
    for i in range(60):
        n = 1+i%7
        e = [(rng.randrange(n)+1,rng.randrange(n)+1,rng.choice([-(1<<63),(1<<63)-1,-1,0,1])) for _ in range(i%12)]
        add(f'general-graph-{i}',n,e,s=i%(n+1),kinds=(303,))
    extreme = [(1,2,-(1<<63)),(2,3,-(1<<63)),(4,5,(1<<63)-1),(5,6,(1<<63)-1)]
    for s in (0,1,4):
        add(f'wide-integer-{s}',6,extreme,s=s,kinds=(303,))
    add('disconnected-cycle',4,[(1,2,0),(3,4,-1),(4,3,-1)],kinds=(303,))
    n = 1500
    edges = [(u,u+1,-100000) for u in range(1,n)]
    edges += [(1,2,-100000)]*(50000-len(edges))
    add('max-p1807-negative-chain',n,edges,kinds=(301,),known={301:[None]+[-100000*(u-1) for u in range(1,n+1)]})
    n = 100000
    edges = [(u,u+1,1) for u in range(1,n)]
    edges += [(1,2,1)]*(200000-len(edges))
    add('max-flight-chain',n,edges,kinds=(302,),known={302:[None]+list(range(n))})
    edges = [(u,u-1,(1<<63)-1) for u in range(n,1,-1)]
    add('max-reverse-wide-chain',n,edges,s=n,kinds=(303,),known={303:[None]+[(n-u)*((1<<63)-1) for u in range(1,n+1)]})
    # API prints all paths: avoid quadratic output for the chain by testing
    # its core separately; the complete API maximum case uses a star instead.
    groups[303].pop()
    edges = [(n,u,(1<<63)-1) for u in range(1,n)]
    add('max-wide-star',n,edges,s=n,kinds=(303,),known={303:[None]+[((1<<63)-1) if u<n else 0 for u in range(1,n+1)]})
    return groups


def check(k,case,output):
    name,raw,n,e,s,best = case
    words = output.split()
    if k == 301:
        assert words == [str(-1 if best[n] is None else best[n])],name
    elif k == 302:
        if best[n] is None:
            assert words == ['IMPOSSIBLE'],name
        else:
            a = list(map(int,words))
            assert a[0] == best[n]+1 and len(a) == a[0]+1,name
            path = a[1:]
            assert path[0] == 1 and path[-1] == n and len(set(path)) == len(path),name
            allowed = {(u,v) for u,v,w in e}
            assert all((u,v) in allowed for u,v in zip(path,path[1:])),name
    elif best is None:
        assert words == ['CYCLIC'],name
    else:
        lines = output.splitlines()
        assert len(lines) == n,name
        for v,line in enumerate(lines,1):
            a = line.split()
            if best[v] is None:
                assert a == ['INF'],(name,v)
                continue
            b = list(map(int,a))
            assert len(b) >= 2 and b[0] == best[v] and b[1] == len(b)-2 and b[1] < n,(name,v)
            ids = b[2:]
            assert all(0 <= i < len(e) for i in ids),(name,v)
            u = e[ids[0]][0] if ids else v
            assert not s or u == s,(name,v)
            seen = {u}
            total = 0
            for i in ids:
                x,y,w = e[i]
                assert x == u and y not in seen,(name,v)
                total += w
                seen.add(y)
                u = y
            assert u == v and total == best[v],(name,v)


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='dag-longest-'+mode+'-',dir=ROOT/'build'))
    flags = ['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    sha = lambda data: hashlib.sha256(data).hexdigest()
    report = dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='DAG signed longest paths; independent recursive cycle search and full path enumeration, original edge/vertex certificates; local only, no online verdict.')
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
    header = (ROOT/'src/compact/dag_longest.hpp').read_text().replace('#pragma once\n','')
    probe = (ROOT/'tests/dag_longest_probe.cpp').read_text()
    copied = header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    for form,source in [('header','#include "'+str(ROOT/'tests/dag_longest_probe.cpp')+'"\n'),('copied',copied)]:
        for release in (False,True):
            exe,entry = compile(form+('-ndebug' if release else '-assert'),source,['-DNDEBUG'] if release else [])
            start = time.monotonic()
            result = run(exe)
            assert result.startswith('PASS '),result
            entry.update(result=result.strip(),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry)
            print(entry['name'],result.strip(),flush=True)
    for name,old,new in [
        ('unreachable-arithmetic','dis[u] != -inf && ',' '),
        ('wrong-source','if (!s || u == s)','if (true)'),
        ('zero-initial-distance','dis.assign(n + 1, -inf);','dis.assign(n + 1, 0);'),
        ('source-only-queue','if (!deg[u]) ord.push_back(u);','if (!deg[u] && (!s || u == s)) ord.push_back(u);'),
        ('ignore-cycle','valid = (int)ord.size() == n;','valid = true;'),
        ('wrong-weight','dis[u] + w','dis[u] - w'),
        ('stale-order','ord.clear();','/* omitted */'),
        ('reversed-path','reverse(ids.begin(), ids.end());','/* omitted */')]:
        assert old in header,name
        # Only mutate the header, never mutate the independent oracle.
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
        for form,source,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy','#include <iostream>\n#include <string>\n'+header+'\n'+row['snippet'],[]),('ndebug',row['program'],['-DNDEBUG'])]:
            exe,entry = compile(f'{k}-{form}',source,extra)
            for case in cs:
                output = run(exe,case[1])
                check(k,case,output)
                entry['runs'].append(dict(case=case[0],input_sha256=sha(case[1].encode()),output_sha256=sha(output.encode()),passed=True))
            report['programs'].append(entry)
            print(k,form,len(cs),'PASS',flush=True)
    for k,name,old,new in [
        (301,'negative-is-unreachable','t.dis[n] == -DagLongest::inf','t.dis[n] < 0'),
        (302,'edge-count-not-cities','p.size() + 1','p.size()'),
        (302,'wrong-route-endpoints','t.e[id].v','t.e[id].u')]:
        row = next(r for r in records() if r['id'] == f'example-{k}')
        assert row['snippet'].count(old) == 1
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
