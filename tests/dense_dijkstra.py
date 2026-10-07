"""Dense and heap Dijkstra source audit with independent shortest-path certificates."""
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
sys.path.insert(0,str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records


def distances(n,e,s):
    d = [None]*(n+1)
    d[s] = 0
    for _ in range(n-1):
        new = d[:]
        for u,v,w in e:
            if d[u] is not None and (new[v] is None or new[v]>d[u]+w):
                new[v] = d[u]+w
        if new == d:
            break
        d = new
    return d


def cases():
    groups = {312:[],313:[]}
    rng = random.Random(312313)
    def add(k,name,n,e,s,known=None):
        d = known if known is not None else distances(n,e,s)
        if k==312:
            assert all(x is not None for x in d[1:]) and s==1
            rows = list(range(1,n+1))
            rng.shuffle(rows)
            g = [[] for _ in range(n+1)]
            for u,v,w in e:
                g[u].append((v,w))
            raw = str(n)+'\n'+''.join(f'{u-1} {len(g[u])}'+''.join(f' {v-1} {w}' for v,w in g[u])+'\n' for u in rows)
        else:
            raw = f'{n} {len(e)} {s}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in e)
        groups[k].append((name,raw,n,e,s,d))
    add(312,'input-row-identity',3,[(1,2,0),(2,3,2),(1,3,7)],1)
    for i in range(100):
        n = 1+i%6
        e = [(u,u+1,rng.randrange(10)) for u in range(1,n)]+[(rng.randrange(1,n+1),rng.randrange(1,n+1),rng.randrange(10)) for _ in range(i%20)]
        rng.shuffle(e)
        add(312,f'reachable-{i}',n,e,1)
        e = [(rng.randrange(1,n+1),rng.randrange(1,n+1),rng.randrange(10)) for _ in range(i%20)]
        add(313,f'multigraph-{i}',n,e,rng.randrange(1,n+1))
    add(312,'max-complete',100,[(u,v,100000) for u in range(1,101) for v in range(1,101)],1,[None,0]+[100000]*99)
    add(312,'max-zero-cycle',100,[(u,u%100+1,0) for u in range(1,101)],1,[None]+[0]*100)
    add(313,'int128-and-unreachable',5,[(1,2,(1<<63)-1),(2,3,(1<<63)-1),(3,4,0),(4,3,0)],1)
    add(313,'parallel-edge-minimum',3,[(2,1,0),(2,1,9),(1,3,2)],2)
    add(313,'root-last-zero-cycle',4,[(4,1,0),(1,2,0),(2,3,0),(3,4,0)],4)
    n=2000
    add(313,'large-matrix-zero-star',n,[(1,v,0) for v in range(2,n+1)],1,[None]+[0]*n)
    return groups


def check(k,case,output):
    name,raw,n,e,s,d = case
    lines = output.splitlines()
    assert len(lines)==n,name
    if k==312:
        assert [list(map(int,l.split())) for l in lines] == [[v-1,d[v]] for v in range(1,n+1)],name
        return
    weights = {}
    for u,v,w in e:
        weights[u,v] = min(weights.get((u,v),w),w)
    for v,line in enumerate(lines,1):
        if d[v] is None:
            assert line == 'INF',name
            continue
        a = list(map(int,line.split()))
        assert len(a)>=3 and a[:2]==[d[v],len(a)-2],name
        p=a[2:]
        assert p[0]==s and p[-1]==v and len(set(p))==len(p)<=n,name
        assert all(1<=u<=n for u in p),name
        assert all((x,y) in weights for x,y in zip(p,p[1:])),name
        assert sum(weights[x,y] for x,y in zip(p,p[1:]))==d[v],name


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='dense-dijkstra-'+mode+'-',dir=ROOT/'build'))
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
    report = dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],local_stack_mib=512,scope='Matrix Dijkstra and audited heap sources; synchronous Bellman-Ford oracle and forward vertex-path certificates. Local only.')
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
    header = (ROOT/'src/compact/dense_dijkstra.hpp').read_text().replace('#pragma once\n','')
    probe = (ROOT/'tests/dense_dijkstra_probe.cpp').read_text()
    copied = '#include "'+str(ROOT/'src/compact/graph.hpp')+'"\n'+header+'\n'+probe.replace('#include "../src/compact/dense_dijkstra.hpp"','').replace('#include "../src/compact/graph.hpp"','')
    copied = copied.replace('"fixtures/dijkstra_sources/', '"'+str(ROOT/'tests/fixtures/dijkstra_sources')+'/')
    for form,source in [('header','#include "'+str(ROOT/'tests/dense_dijkstra_probe.cpp')+'"\n'),('copied',copied)]:
        for release in (False,True):
            exe,entry = compile(form+('-ndebug' if release else '-assert'),source,['-DNDEBUG'] if release else [])
            start = time.monotonic()
            result = run(exe)
            assert result.startswith('PASS '),result
            entry.update(result=result.strip(),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry)
            print(entry['name'],result.strip(),flush=True)
    for name,old,new in [
        ('last-edge-wins','if (x == -1 || w < x) x = w;','x = w;'),
        ('zero-as-absent','cost[u][v] >= 0','cost[u][v] > 0'),
        ('wrong-root','dis[s] = 0;','dis[1] = 0;'),
        ('reverse-path','reverse(p.begin(), p.end());','/* omitted */'),
        ('omit-predecessor','pre[v] = u;','pre[v] = -1;')]:
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
        for form,source,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy','#include <iostream>\n#include <string>\n'+header+'\n'+row['snippet'],[]),('ndebug',row['program'],['-DNDEBUG'])]:
            exe,entry = compile(f'{k}-{form}',source,extra)
            for case in cs:
                output = run(exe,case[1])
                check(k,case,output)
                entry['runs'].append(dict(case=case[0],input_sha256=sha(case[1].encode()),output_sha256=sha(output.encode()),passed=True))
            report['programs'].append(entry)
            print(k,form,len(cs),'PASS',flush=True)
    for k,name,old,new in [(312,'ignore-input-vertex','g.add(u + 1, v + 1, w);','g.add(i + 1, v + 1, w);'),(313,'use-root-one','g.run(s);','g.run(1);')]:
        row = next(r for r in records() if r['id'] == f'example-{k}')
        source = row['program'].replace(row['snippet'],row['snippet'].replace(old,new))
        exe,entry = compile(name,source,['-DNDEBUG'])
        for case in groups[k]:
            output = run(exe,case[1])
            try:
                check(k,case,output)
            except AssertionError:
                entry.update(rejecting_case=case[0],independent_oracle_rejected=True)
                break
        else:
            raise AssertionError(name)
        report['mutants'].append(entry)
        print(name,'ORACLE_REJECT',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before == report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:',out/'report.json',flush=True)

if __name__ == '__main__':
    main()
