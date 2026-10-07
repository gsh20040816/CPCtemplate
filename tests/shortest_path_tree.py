"""Enumerated shortest-path spanning trees and complete original-edge certificates."""
import hashlib
import itertools
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
            for a,b in [(u,v),(v,u)]:
                if d[a] is not None and (new[b] is None or new[b]>d[a]+w):
                    new[b] = d[a]+w
        d = new
    return d


def certificate(n,e,s,d,ids):
    reached = sum(x is not None for x in d)
    if len(ids)!=reached-1 or len(set(ids))!=len(ids) or any(i<0 or i>=len(e) for i in ids):
        return None
    g = [[] for _ in range(n+1)]
    total = 0
    for i in ids:
        u,v,w = e[i]
        g[u].append((v,w))
        g[v].append((u,w))
        total += w
    got = [None]*(n+1)
    got[s] = 0
    q = [s]
    for u in q:
        for v,w in g[u]:
            if got[v] is None:
                got[v] = got[u]+w
                q.append(v)
    return total if got == d else None


def optimum(n,e,s,d):
    candidates = (certificate(n,e,s,d,ids) for ids in itertools.combinations(range(len(e)),sum(x is not None for x in d)-1))
    return min(w for w in candidates if w is not None)


def cases():
    groups = {307:[],308:[]}
    rng = random.Random(545307)
    def add(k,name,n,e,s,known=None):
        d,w = known if known is not None else (distances(n,e,s),None)
        if w is None:
            w = optimum(n,e,s,d)
        raw = f'{n} {len(e)}'+(f' {s}' if k==308 else '')+'\n'+''.join(f'{u} {v} {x}\n' for u,v,x in e)
        if k==307:
            raw += str(s)+'\n'
        groups[k].append((name,raw,n,e,s,d,w))
    add(307,'statement',3,[(1,2,1),(2,3,1),(1,3,2)],3)
    add(307,'shortest-tree-not-mst',3,[(1,2,2),(1,3,2),(2,3,1)],1)
    add(307,'min-entry-not-first',4,[(1,2,100),(1,3,200),(2,4,200),(3,4,100)],1)
    for i in range(100):
        n = 1+i%6
        order = list(range(1,n+1))
        rng.shuffle(order)
        pairs = [(order[j],order[rng.randrange(j)]) for j in range(1,n)]
        used = {tuple(sorted(p)) for p in pairs}
        others = [(u,v) for u in range(1,n+1) for v in range(u+1,n+1) if (u,v) not in used]
        rng.shuffle(others)
        pairs += others[:max(0,9-len(pairs))]
        e = [(u,v,rng.randrange(1,11)) for u,v in pairs]
        rng.shuffle(e)
        add(307,f'positive-simple-{i}',n,e,1+rng.randrange(n))
        e = [(1+rng.randrange(n),1+rng.randrange(n),rng.randrange(5)) for _ in range(i%11)]
        add(308,f'zero-multigraph-{i}',n,e,1+rng.randrange(n))
    add(308,'equal-distance-zero-cycle',5,[(1,2,5),(1,3,5),(2,3,0),(3,4,0),(4,2,0)],1)
    add(308,'zero-component-cheapest-entry',5,[(1,2,10),(1,3,1),(3,4,9),(2,4,0),(4,5,0)],1)
    add(308,'zero-root-not-component-first',4,[(1,2,0),(2,3,0),(3,1,0),(3,4,7)],3)
    add(308,'full-signed64-positive',4,[(1,2,(1<<63)-1),(2,3,(1<<63)-1),(3,4,(1<<63)-1)],4)
    n = 300000
    e = [(u,u+1,1000000000) for u in range(1,n)]+[(1,n,1000000000)]
    d = [None]+[min(u-1,n-u+1)*1000000000 for u in range(1,n+1)]
    add(307,'max-cycle-all-positive',n,e,1,(d,(n-1)*1000000000))
    e = [(1,u,1000000000) for u in range(2,n+1)]+[(2,3,1)]
    add(307,'max-star-not-mst',n,e,1,([None,0]+[1000000000]*(n-1),(n-1)*1000000000))
    e = [(1,u,0) for u in range(2,n+1)]
    add(308,'max-zero-star-root-last',n,e,n,([None]+[0]*n,0))
    return groups


def check(k,case,output):
    name,raw,n,e,s,d,w = case
    if k==307:
        a = list(map(int,output.split()))
        assert a and a[0]==w,name
        assert certificate(n,e,s,d,[i-1 for i in a[1:]])==w,name
        return
    lines = output.splitlines()
    assert len(lines)==n+1,name
    head = list(map(int,lines[0].split()))
    assert len(head)>=3 and head[:3]==[sum(x is not None for x in d),w,len(head)-3],name
    chosen = set(head[3:])
    assert certificate(n,e,s,d,head[3:])==w,name
    for v,line in enumerate(lines[1:],1):
        if d[v] is None:
            assert line=='INF',name
            continue
        a = list(map(int,line.split()))
        assert len(a)>=2 and a[:2]==[d[v],len(a)-2] and a[1]<n,name
        u,total,seen = s,0,{s}
        for id in a[2:]:
            assert id in chosen,name
            x,y,c = e[id]
            assert u in (x,y),name
            u = y if x==u else x
            assert u not in seen,name
            seen.add(u)
            total+=c
        assert u==v and total==d[v],name


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='shortest-tree-'+mode+'-',dir=ROOT/'build'))
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
    report = dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],local_stack_mib=512,scope='Minimum-weight shortest-path tree on reachable vertices; zero components, original edges, exhaustive spanning-tree subsets independent of Dijkstra/component optimization. Local only.')
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
    header = (ROOT/'src/compact/shortest_path_tree.hpp').read_text().replace('#pragma once\n','')
    probe = (ROOT/'tests/shortest_path_tree_probe.cpp').read_text()
    copied = header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    for form,source in [('header','#include "'+str(ROOT/'tests/shortest_path_tree_probe.cpp')+'"\n'),('copied',copied)]:
        for release in (False,True):
            exe,entry = compile(form+('-ndebug' if release else '-assert'),source,['-DNDEBUG'] if release else [])
            start = time.monotonic()
            result = run(exe)
            assert result.startswith('PASS '),result
            entry.update(result=result.strip(),elapsed_seconds=time.monotonic()-start)
            report['programs'].append(entry)
            print(entry['name'],result.strip(),flush=True)
    for name,old,new in [
        ('maximum-entry','e[id].w < e[b].w','e[id].w > e[b].w'),
        ('wrong-total','weight += w;','weight += 1;'),
        ('wrong-reached','return reached;','return n;'),
        ('missing-parent','pre[v] = id;','pre[v] = -1;'),
        ('reversed-path','reverse(p.begin(), p.end());','/* omitted */')]:
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
    for k,name,old,new in [
        (307,'zero-based-output','id + 1','id'),
        (307,'wrong-requested-root','t.run(s);','t.run(1);')]:
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
