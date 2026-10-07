"""Independent Floyd/state and edge-witness checks for BellmanFord and printed programs."""
import hashlib
import json
import os
from pathlib import Path
import platform
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


def oracle(n, edges, s):
    f = [[None]*n for _ in range(n)]
    for u in range(n):
        f[u][u] = 0
    for u, v, w in edges:
        f[u-1][v-1] = w if f[u-1][v-1] is None else min(f[u-1][v-1], w)
    for k in range(n):
        for u in range(n):
            for v in range(n):
                if f[u][k] is not None and f[k][v] is not None:
                    d = f[u][k]+f[k][v]
                    if f[u][v] is None or d < f[u][v]:
                        f[u][v] = d
    ans = []
    for v in range(n):
        if any(f[k][k] < 0 and (s == 0 or f[s-1][k] is not None) and f[k][v] is not None for k in range(n)):
            ans.append('-INF')
        elif s:
            ans.append('INF' if f[s-1][v] is None else f[s-1][v])
        else:
            ans.append(min(f[k][v] for k in range(n) if f[k][v] is not None))
    return ans


def cases():
    sample = [(1,2,2),(1,3,3),(2,3,-5),(2,4,1),(3,4,2)]
    graphs = [('aoj-sample-1',4,sample,1), ('aoj-sample-2',4,sample+[(4,2,0)],1),
              ('aoj-sample-3',4,sample,2), ('cses-sample',4,[(1,2,1),(2,4,1),(3,1,1),(4,1,-3),(4,3,-2)],0),
              ('disconnected-cycle',5,[(1,2,3),(3,4,-2),(4,3,1),(4,5,0)],1),
              ('empty',1,[],1)]
    rng = random.Random(1197)
    for i in range(90):
        n = 1+i%9
        e = [(rng.randrange(n)+1,rng.randrange(n)+1,rng.randrange(-10,11)) for _ in range(i%35)]
        graphs.append((f'random-{i}',n,e,rng.randrange(n+1)))
    return graphs


def edge_walk(ids, edges):
    assert ids and all(0 <= i < len(edges) for i in ids)
    route = [edges[ids[0]][0]]
    weight = 0
    for i in ids:
        u,v,w = edges[i]
        assert route[-1] == u
        route.append(v)
        weight += w
    return route, weight


def check_api(output, n, edges, s, want):
    lines = output.splitlines()
    assert len(lines) == n+1
    for v, (line, expected) in enumerate(zip(lines, want),1):
        if isinstance(expected, str):
            assert line == expected
            continue
        tokens = list(map(int,line.split()))
        value, count, *ids = tokens
        assert value == expected and count == len(ids)
        if ids:
            route, weight = edge_walk(ids, edges)
            assert route[-1] == v and (s == 0 or route[0] == s)
            assert len(set(route)) == len(route) and weight == value
        else:
            assert value == 0 and (s == 0 or s == v)
    c, count, *ids = lines[-1].split()
    ids = list(map(int,ids))
    assert c == 'C' and int(count) == len(ids)
    assert bool(ids) == ('-INF' in want)
    if ids:
        route, weight = edge_walk(ids,edges)
        assert route[0] == route[-1] and weight < 0
        assert len(set(route[:-1])) == len(route)-1
        assert want[route[0]-1] == '-INF'


def check_cses(output, n, edges, want):
    tokens = output.split()
    if '-INF' not in want:
        assert tokens == ['NO']
        return
    assert tokens[0] == 'YES'
    route = list(map(int,tokens[1:]))
    assert 2 <= len(route) <= n+1 and route[0] == route[-1]
    assert len(set(route[:-1])) == len(route)-1
    best = {}
    for u,v,w in edges:
        best[u,v] = min(best.get((u,v),w),w)
    assert all((u,v) in best for u,v in zip(route,route[1:]))
    assert sum(best[u,v] for u,v in zip(route,route[1:])) < 0


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='bellman-ford-'+mode+'-',dir=ROOT/'build'))
    flags = ['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    if platform.system() == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    header = (ROOT/'src/compact/bellman_ford.hpp').read_text().replace('#pragma once\n','')
    probe = (ROOT/'tests/bellman_ford_probe.cpp').read_text()
    copied = header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    sha = lambda data: hashlib.sha256(data).hexdigest()
    report = dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='All directed graphs n<=3, absent/-1/0/1 edges, every source and super-source; independent Floyd, influence and edge-witness certificates; signed64 extremes and 2500 vertices; local only.')
    def compile(name,source,extra=()):
        cpp,exe = out/(name+'.cpp'),out/name
        cpp.write_text(source)
        cmd = [CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p = subprocess.run(cmd,capture_output=True)
        assert p.returncode == 0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    def run(exe,raw=''):
        p = subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=600)
        assert p.returncode == 0 and not p.stderr,(exe,p.returncode,p.stdout[:500],p.stderr[-1000:])
        return p.stdout.decode()
    for form,source in [('header','#include "'+str(ROOT/'tests/bellman_ford_probe.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            exe,entry = compile(form+('-ndebug' if release else '-assert'),source,['-DNDEBUG'] if release else [])
            start = time.monotonic()
            result = run(exe)
            assert result.splitlines()[-1].startswith('PASS '),result
            entry.update(result=result.strip(),elapsed_seconds=time.monotonic()-start,output_sha256=sha(result.encode()))
            report['programs'].append(entry)
            print(entry['name'],result.strip(),flush=True)
    for name,old,new in [
        ('unreachable-relaxation','dis[u] == inf || ','false || '),
        ('wrong-single-source','dis.assign(n + 1, s ? inf : 0);','dis.assign(n + 1, 0);'),
        ('stale-negative-state','neg.assign(n + 1, 0);','if (neg.empty()) neg.assign(n + 1, 0);'),
        ('no-negative-propagation','while (!q.empty())','while (false && !q.empty())'),
        ('reversed-path','reverse(ids.begin(), ids.end());','/* omitted */'),
        ('reversed-cycle','reverse(cycle.begin(), cycle.end());','/* omitted */')]:
        assert header.count(old) == 1,name
        exe,entry = compile(name,copied.replace(old,new),['-DNDEBUG'])
        p = subprocess.run([str(exe),'small-only'],capture_output=True,env=env,timeout=600)
        assert p.returncode == 0 and not p.stderr and p.stdout == b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry['independent_oracle_rejected'] = True
        report['mutants'].append(entry)
        print(name,'ORACLE_REJECT',flush=True)
    for example in ['example-293','example-294','example-295']:
        cs = []
        for name,n,edges,s in cases():
            if example == 'example-293':
                s = max(1,s)
                # AOJ official domain forbids self loops and parallel edges.
                edges = list({(u,v):(u,v,w) for u,v,w in edges if u != v}.values())
            if example == 'example-294':
                s = 0
            cs.append((name,n,edges,s,oracle(n,edges,s)))
        n = 1000 if example == 'example-293' else 2500
        w = 10000 if example == 'example-293' else 10**9
        edges = [(u,u+1,w) for u in range(n-1,0,-1)]
        s = 0 if example == 'example-294' else 1
        cs.append(('large-reverse-chain',n,edges,s,[0]*n if s == 0 else [i*w for i in range(n)]))
        cs.append(('large-negative-cycle',n,[(u,v,-1) for u,v,_ in edges]+[(n,1,0)],s,['-INF']*n))
        if example == 'example-295':
            for s in [0,1,2,3]:
                e = [(1,1,-1),(1,2,2**63-1),(2,3,2**63-1)]
                cs.append((f'extreme-propagation-{s}',3,e,s,oracle(3,e,s)))
            e = [(1,2,2**63-1),(2,3,2**63-1),(4,5,-2**63),(5,6,-2**63)]
            for s in [0,1,4]:
                cs.append((f'int128-finite-{s}',6,e,s,oracle(6,e,s)))
        row = next(r for r in records() if r['id'] == example)
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('minimal-copy','#include <iostream>\n#include <string>\n'+header+'\n'+row['snippet'])]:
            exe,entry = compile(example+'-'+form,source)
            for name,n,edges,s,want in cs:
                if example == 'example-293':
                    raw = f'{n} {len(edges)} {s-1}\n'+''.join(f'{u-1} {v-1} {w}\n' for u,v,w in edges)
                else:
                    raw = f'{n} {len(edges)}'+(f' {s}' if example == 'example-295' else '')+'\n'+''.join(f'{u} {v} {w}\n' for u,v,w in edges)
                result = run(exe,raw)
                if example == 'example-293':
                    assert result.splitlines() == (['NEGATIVE CYCLE'] if '-INF' in want else list(map(str,want))),(example,name,result[:500])
                elif example == 'example-294':
                    check_cses(result,n,edges,want)
                else:
                    check_api(result,n,edges,s,want)
                entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),output_sha256=sha(result.encode()),passed=True))
            report['programs'].append(entry)
            print(example,form,len(cs),'PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before == report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:',out/'report.json',flush=True)

if __name__ == '__main__':
    main()
