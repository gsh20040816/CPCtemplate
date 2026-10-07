"""Mergeable Splay: fixed handles, independent partitions, order statistics and graph applications."""
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
from graph_queries import cases as graph_cases, check as check_mean


def island_cases():
    rng = random.Random(3224)
    cases = []
    for test in range(80):
        n = 1+test%40
        a = list(range(1,n+1))
        rng.shuffle(a)
        edges = [(rng.randrange(n),rng.randrange(n)) for _ in range(1+test%n)]
        adj = [set() for _ in a]
        for u,v in edges:
            adj[u].add(v)
            adj[v].add(u)
        ops, want = [], []
        for _ in range(200):
            u,v = rng.randrange(n),rng.randrange(n)
            if rng.randrange(3)==0:
                ops.append(f'B {u+1} {v+1}')
                adj[u].add(v)
                adj[v].add(u)
            else:
                k = 1+rng.randrange(n)
                ops.append(f'Q {u+1} {k}')
                queue,seen = [u],{u}
                for x in queue:
                    for y in adj[x]:
                        if y not in seen:
                            seen.add(y)
                            queue.append(y)
                group = sorted(seen,key=lambda x:a[x])
                want.append(group[k-1]+1 if k<=len(group) else -1)
        raw=f'{n} {len(edges)}\n'+' '.join(map(str,a))+'\n'+''.join(f'{u+1} {v+1}\n' for u,v in edges)+str(len(ops))+'\n'+'\n'.join(ops)+'\n'
        cases.append((f'random-{test}',raw,want))
    n,q = 100000,300000
    raw=f'{n} {n}\n'+' '.join(map(str,range(n,0,-1)))+'\n'+''.join(f'{i} {i+1}\n' for i in range(1,n))+f'1 {n}\n{q}\n'
    ops,want=[],[]
    for i in range(q):
        if i%3==0:
            ops.append(f'B {i%n+1} {n-i%n}')
        else:
            k=(i*7919)%n+1
            ops.append(f'Q {i%n+1} {k}')
            want.append(n+1-k)
    cases.append(('max-connected-reversed-weights',raw+'\n'.join(ops)+'\n',want))
    raw=f'{n} 1\n'+' '.join(map(str,range(1,n+1)))+f'\n1 1\n{q}\n'
    ops,want=[],[]
    for u in range(2,n+1):
        ops.extend([f'B {u-1} {u}',f'Q {u} {u}',f'Q {u} {min(n,u+1)}'])
        want.extend([u,-1 if u<n else n])
    while len(ops)<q:
        ops.append(f'Q 1 {n}')
        want.append(n)
    cases.append(('max-growing-chain',raw+'\n'.join(ops)+'\n',want))
    return cases


def api_cases():
    rng = random.Random(292)
    cases=[]
    for test in range(80):
        n=1+test%30
        initial=[rng.choice([-2,-1,0,1,2,-(1<<63),(1<<63)-1]) for _ in range(n)]
        values=initial[:]
        labels=list(range(n))
        ops,want=[],[]
        for i in range(300):
            op,x=rng.randrange(4),rng.randrange(n)
            if op==0:
                y=rng.randrange(n)
                ops.append(f'0 {x} {y}')
                u,v=labels[x],labels[y]
                want.append(int(u!=v))
                labels=[u if z==v else z for z in labels]
            elif op==1:
                value=rng.choice([-2,-1,0,1,2,-(1<<63),(1<<63)-1])
                ops.append(f'1 {x} {value}')
                values[x]=value
            else:
                group=sorted((u for u in range(n) if labels[u]==labels[x]),key=lambda u:(values[u],u))
                if op==2:
                    k=rng.choice([-(1<<63),0,1,len(group),len(group)+1,(1<<63)-1])
                    ops.append(f'2 {x} {k}')
                    if 1<=k<=len(group):
                        id=group[k-1]
                        want.extend([id,values[id]])
                    else:want.append(-1)
                else:
                    ops.append(f'3 {x}')
                    want.extend([len(group),group.index(x)+1])
        cases.append((f'mixed-{test}',f'{n} {len(ops)}\n'+' '.join(map(str,initial))+'\n'+'\n'.join(ops)+'\n',want))
    return cases+[('empty','0 0\n',[])]


def main():
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before=snapshot(ROOT)
    out=Path(tempfile.mkdtemp(prefix='merge-splay-'+mode+'-',dir=ROOT/'build'))
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    if platform.system()=='Darwin':flags+=['-Wl,-stack_size,0x20000000']
    else:
        _,hard=resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    header=(ROOT/'src/compact/merge_splay.hpp').read_text().replace('#pragma once\n','')
    probe=(ROOT/'tests/merge_splay_probe.cpp').read_text()
    copied=header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    sha=lambda data:hashlib.sha256(data).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],local_stack_mib=512,
                scope='Fixed-ID ordered Splay forest. All set partitions n<=6; ternary values n<=4 and signed extrema; independent membership/sorted-ID/rank and BST certificates, no allocation growth; 100000-element merges and changes. Complete UVA1479/P3224/API; local only.')
    def compile(name,source,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name
        cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    for form,source in [('header','#include "'+str(ROOT/'tests/merge_splay_probe.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            name=form+('-ndebug' if release else '-assert')
            exe,entry=compile(name,source,['-DNDEBUG'] if release else [])
            start=time.monotonic()
            p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=600)
            assert p.returncode==0 and not p.stderr and p.stdout.splitlines()[-1].startswith(b'PASS '),(name,p.returncode,p.stdout,p.stderr[-1000:])
            entry.update(result=p.stdout.decode().strip(),elapsed_seconds=time.monotonic()-start,output_sha256=sha(p.stdout))
            report['programs'].append(entry)
            print(name,entry['result'],flush=True)
    for name,old,new in [
        ('reversed-id-ties','pair{a[x].val, x} < pair{a[y].val, y}','pair{a[x].val, -x} < pair{a[y].val, -y}'),
        ('no-merge','transfer(y, x);','(void)y;'),
        ('rank-offset','return a[a[x].ch[0]].siz + 1;','return a[a[x].ch[0]].siz;'),
        ('id-offset','return x - 1;','return x;'),
        ('drop-right-on-change','a[root].ch[1] = r;','a[root].ch[1] = 0;'),
        ('no-value-change','a[x] = Node{{0, 0}, 0, 1, val};','a[x] = Node{{0, 0}, 0, 1, a[x].val};')]:
        assert header.count(old)==1,(name,old)
        exe,entry=compile(name,copied.replace(old,new),['-DNDEBUG'])
        p=subprocess.run([str(exe),'small-only'],capture_output=True,env=env,timeout=180)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry['independent_oracle_rejected']=True
        report['mutants'].append(entry)
        print(name,'ORACLE_REJECT',flush=True)
    # Count actual transferred nodes; every successful union must move exactly the smaller set.
    marked=header.replace('struct MergeSplay','long long moved = 0;\nstruct MergeSplay',1).replace('if (!u) return;\n        int l','if (!u) return;\n        moved++;\n        int l',1)
    movement=marked+'''
#include <iostream>
#include <random>
int main()
{
    int n = 100000;
    MergeSplay t(vector<long long>(n, 0));
    long long total = 0;
    for (int width = 1; width < n; width *= 2)
        for (int u = 0; u + width < n; u += 2 * width)
        {
            int count = min(t.size(u), t.size(u + width));
            long long before = moved;
            if (!t.merge(u, u + width) || moved - before != count) return 1;
            total += count;
        }
    for (int u = 0; u < n; u++)
    {
        t.set(u, -u);
        if (t.merge(0, u)) return 1;
    }
    if (moved != total || total > (long long)n * 17) return 1;
    std::cout << "PASS " << total << " transferred nodes\\n";
}
'''
    exe,entry=compile('small-to-large-movement',movement,['-DNDEBUG'])
    p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=180)
    assert p.returncode==0 and not p.stderr and p.stdout.startswith(b'PASS ')
    entry['result']=p.stdout.decode().strip()
    report['programs'].append(entry)
    print(entry['result'],flush=True)
    groups=[('example-290',graph_cases()),('example-291',island_cases()),('example-292',api_cases())]
    for example,cs in groups:
        row=next(r for r in records() if r['id']==example)
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('minimal-copy','#include <iostream>\n#include <iomanip>\n'+header+'\n'+row['snippet'])]:
            exe,entry=compile(example+'-'+form,source)
            for name,raw,want in cs:
                start=time.monotonic()
                p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=180)
                assert p.returncode==0 and not p.stderr,(example,form,name,p.returncode,p.stderr[-1000:])
                ok=check_mean(p.stdout.decode(),want) if example=='example-290' else list(map(int,p.stdout.split()))==want
                assert ok,(example,form,name,p.stdout[:300],str(want)[:300])
                entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start,passed=True))
            report['programs'].append(entry)
            print(example,form,len(cs),'PASS',flush=True)
    row=next(r for r in records() if r['id']=='example-290')
    needle='if (id) sum += t.value(*id);'
    assert row['program'].count(needle)==1
    traced=row['program'].replace(needle,'cerr << (id ? t.value(*id) : 0) << "\\n";\n                '+needle)
    exe,entry=compile('uva-query-trace',traced)
    for name,raw,want in groups[0][1]:
        p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=180)
        assert p.returncode==0 and check_mean(p.stdout.decode(),want)
        assert list(map(int,p.stderr.split()))==[x for ans in want for x in reversed(ans)],name
        entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),trace_sha256=sha(p.stderr),passed=True))
    report['programs'].append(entry)
    print('uva-query-trace',len(groups[0][1]),'PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
