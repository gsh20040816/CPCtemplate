"""FIFO SPFA and direct inequality certificates, with independent small-graph oracles."""
import hashlib
import itertools
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
from bellman_ford import oracle, cases as graph_cases, check_api
from usage_checkers import check_output


def negative_cases():
    rng = random.Random(3385)
    cs = []
    for test in range(70):
        graphs, want = [], []
        for _ in range(10):
            n = 1 + rng.randrange(9)
            raw = [(rng.randrange(n)+1,rng.randrange(n)+1,rng.randrange(-10,11)) for _ in range(1+rng.randrange(30))]
            edges = raw + [(v,u,w) for u,v,w in raw if w >= 0]
            want.append('YES' if '-INF' in oracle(n,edges,1) else 'NO')
            graphs.append(f'{n} {len(raw)}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in raw))
        cs.append((f'random-ten-datasets-{test}','10\n'+''.join(graphs),want))
    cs.append(('disconnected-and-zero-return','3\n3 2\n2 3 -1\n3 2 0\n3 3\n1 2 0\n2 3 -1\n3 2 0\n2 2\n2 1 0\n2 2 -1\n',['NO','YES','YES']))
    n,m = 2000,3000
    raw = [(u,u-1,-1) for u in range(2,n+1)]+[(1,n,10000)]
    raw += [(n,n,0)]*(m-len(raw))
    text = f'{n} {m}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in raw)
    cs.append(('max-ten-feasible','10\n'+text*10,['NO']*10))
    raw[-1] = (n,n,-1)
    text = f'{n} {m}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in raw)
    cs.append(('max-ten-negative','10\n'+text*10,['YES']*10))
    return cs


def difference_cases():
    rng = random.Random(5960)
    cs = []
    for test in range(100):
        n = 2 + test%7
        constraints = [(rng.randrange(n)+1,rng.randrange(n)+1,rng.randrange(-2,3)) for _ in range(1+test%20)]
        constraints = [(u,v,w) for u,v,w in constraints if u != v] or [(1,2,0)]
        if test%3 == 0:
            x = [rng.randrange(-10,11) for _ in range(n)]
            constraints = [(u,v,x[u-1]-x[v-1]+rng.randrange(3)) for u,v,w in constraints]
        feasible = '-INF' not in oracle(n,[(v,u,w) for u,v,w in constraints],0)
        if n <= 3 and test%3:
            brute = any(all(x[u-1]-x[v-1] <= w for u,v,w in constraints) for x in itertools.product(range(-2*n,1),repeat=n))
            assert feasible == brute
        cs.append((f'random-{test}',n,constraints,feasible))
    cs += [('statement',3,[(1,2,3),(2,3,-2),(1,3,1)],True),
           ('disconnected-cycle',4,[(2,3,-1),(3,2,0)],False),
           ('inequality-direction',2,[(1,2,-2)],True)]
    n = 5000
    constraints = [(u-1,u,-10000) for u in range(2,n+1)]
    cs.append(('max-reverse-chain',n,constraints+[(1,n,0)],True))
    cs.append(('max-negative-cycle',n,constraints+[(n,1,0)],False))
    return [(name,f'{n} {len(c)}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in c),{'difference_constraints':feasible}) for name,n,c,feasible in cs]


def farm_cases():
    rng = random.Random(1993)
    cs = []
    def satisfied(x,op,a,b,c):
        delta = x[a-1]-x[b-1]
        return delta >= c if op == 1 else delta <= c if op == 2 else delta == 0
    for test in range(100):
        n = 1+test%3
        ops = [(rng.randrange(1,4),rng.randrange(n)+1,rng.randrange(n)+1,rng.randrange(1,3)) for _ in range(1+test%8)]
        # An integer feasible system has a solution shiftable into [0, n*max(c)].
        feasible = any(all(satisfied(x,*op) for op in ops) for x in itertools.product(range(2*n+1),repeat=n))
        raw = f'{n} {len(ops)}\n'+''.join(f'{op} {a} {b}'+(f' {c}' if op != 3 else '')+'\n' for op,a,b,c in ops)
        cs.append((f'brute-integer-{test}',raw,['Yes' if feasible else 'No']))
    n = 5000
    raw = f'{n} {n}\n'+''.join(f'1 {u} {u-1} 5000\n' for u in range(2,n+1))+f'2 1 {n} 5000\n'
    cs.append(('max-chain-translation',raw,['Yes']))
    cs.append(('max-chain-contradiction',raw.rsplit('2 1 ',1)[0]+f'3 1 {n}\n',['No']))
    cs += [('at-least-direction','2 2\n1 1 2 2\n2 1 2 1\n',['No']),
           ('equality-both-directions','2 2\n1 2 1 1\n3 1 2\n',['No'])]
    return cs


def api_cases():
    graphs = graph_cases()
    e = [(1,2,2**63-1),(2,3,2**63-1),(4,5,-2**63),(5,6,-2**63)]
    for s in [0,1,4]:
        graphs.append((f'int128-{s}',6,e,s))
    return [(name,f'{n} {len(e)} {s}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in e),(n,e,s,oracle(n,e,s))) for name,n,e,s in graphs]


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='spfa-'+mode+'-',dir=ROOT/'build'))
    flags = ['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    if platform.system() == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    header = (ROOT/'src/compact/spfa.hpp').read_text().replace('#pragma once\n','')
    probe = (ROOT/'tests/spfa_probe.cpp').read_text()
    copied = header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    sha = lambda data: hashlib.sha256(data).hexdigest()
    report = dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='FIFO SPFA: exhaustive directed graphs n<=3/all sources, Floyd and original-edge path certificates, repeated runs/add/copy, signed64; P3385, direct P5960 certificates, independently brute-forced P1993 relations. Local only.')
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
    for form,source in [('header','#include "'+str(ROOT/'tests/spfa_probe.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            exe,entry = compile(form+('-ndebug' if release else '-assert'),source,['-DNDEBUG'] if release else [])
            start = time.monotonic()
            result = run(exe)
            assert result.splitlines()[-1].startswith('PASS '),result
            entry.update(result=result.strip(),elapsed_seconds=time.monotonic()-start,output_sha256=sha(result.encode()))
            report['programs'].append(entry)
            print(entry['name'],result.strip(),flush=True)
    for name,old,new in [
        ('wrong-source','if (!s || u == s)','if (true)'),
        ('early-cycle','if (len[v] >= n)','if (len[v] >= n - 1)'),
        ('wrong-weight','dis[u] + w','dis[u] - w'),
        ('stale-distances','dis.assign(n + 1, inf);','if (dis.empty()) dis.assign(n + 1, inf);'),
        ('permanent-visited','in[u] = 0;','in[u] = 1;'),
        ('reversed-path','reverse(ids.begin(), ids.end());','/* omitted */')]:
        assert old in header,name
        exe,entry = compile(name,copied.replace(old,new),['-DNDEBUG'])
        p = subprocess.run([str(exe),'small-only'],capture_output=True,env=env,timeout=600)
        assert p.returncode == 0 and not p.stderr and p.stdout == b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry['independent_oracle_rejected'] = True
        report['mutants'].append(entry)
        print(name,'ORACLE_REJECT',flush=True)
    groups = [('example-296',negative_cases()),('example-297',difference_cases()),('example-298',farm_cases()),('example-299',api_cases())]
    for example,cs in groups:
        row = next(r for r in records() if r['id'] == example)
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('minimal-copy','#include <iostream>\n#include <string>\n'+header+'\n'+row['snippet'])]:
            exe,entry = compile(example+'-'+form,source)
            for name,raw,want in cs:
                result = run(exe,raw)
                if example == 'example-297':
                    check_output(example,mode,raw,result,want)
                elif example == 'example-299':
                    n,e,s,ans = want
                    if '-INF' in ans:
                        assert result.split() == ['NEGATIVE','CYCLE']
                    else:
                        check_api(result+'C 0\n',n,e,s,ans)
                else:
                    assert result.split() == want,(example,name,result[:500],want)
                entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),output_sha256=sha(result.encode()),passed=True))
            report['programs'].append(entry)
            print(example,form,len(cs),'PASS',flush=True)
    # Adapter mutants are judged against original inequalities, not transformed edges.
    for name,example,old,new in [
        ('constraint-edge-direction','example-297','t.add(v, u, w);','t.add(u, v, w);'),
        ('constraint-single-source','example-297','t.run(0)','t.run(1)'),
        ('farm-lower-bound','example-298','t.add(a, b, -c);','t.add(b, a, -c);'),
        ('farm-equality-direction','example-298','t.add(b, a, 0);','/* omitted */')]:
        row = next(r for r in records() if r['id'] == example)
        assert row['program'].count(old) == 1
        exe,entry = compile(name,row['program'].replace(old,new))
        rejected = False
        for case,raw,want in dict(groups)[example]:
            result = run(exe,raw)
            try:
                if example == 'example-297':
                    check_output(example,mode,raw,result,want)
                else:
                    assert result.split() == want
            except (AssertionError,ValueError):
                rejected = True
                entry['rejecting_case'] = case
                break
        assert rejected,name
        entry['independent_oracle_rejected'] = True
        report['mutants'].append(entry)
        print(name,'ORACLE_REJECT',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before == report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:',out/'report.json',flush=True)

if __name__ == '__main__':
    main()
