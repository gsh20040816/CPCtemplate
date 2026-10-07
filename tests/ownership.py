#!/usr/bin/env python3
"""Historical labels and independent multiset vectors, with ownership audits."""
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from usage_examples import records
from compiler_config import CXX


def sha(data):
    return hashlib.sha256(data).hexdigest()


def datasets():
    rng = random.Random(34025494)
    dsu, seg = [], []
    for case in range(100):
        n = rng.randrange(1, 25)
        versions = [list(range(n))]
        ops, ans = [], []
        for step in range(240):
            op = rng.randrange(1, 4)
            a = versions[-1][:]
            x, y = rng.randrange(n), rng.randrange(n)
            if op == 2:
                k = rng.randrange(len(versions))
                a = versions[k][:]
                ops.append(f'2 {k}')
            elif op == 1:
                u, v = a[x], a[y]
                a = [v if z == u else z for z in a]
                ops.append(f'1 {x+1} {y+1}')
            else:
                ops.append(f'3 {x+1} {y+1}')
                ans.append(int(a[x] == a[y]))
            versions.append(a)
        dsu.append((f'branch-{case}', f'{n} 240\n' + '\n'.join(ops) + '\n', ans))
        a = [[rng.randrange(6) for _ in range(n)]]
        initial = a[0][:]
        active = [0]
        ops, ans = [], []
        for step in range(240):
            op = rng.randrange(5)
            p = rng.choice(active)
            if op == 1 and len(active) == 1:
                op = 0
            if op == 0:
                l, r = sorted([rng.randrange(n), rng.randrange(n)])
                b = [0]*n
                for i in range(l,r+1):
                    b[i],a[p][i] = a[p][i],0
                a.append(b)
                active.append(len(a)-1)
                ops.append(f'0 {p+1} {l+1} {r+1}')
            elif op == 1:
                t = rng.choice([i for i in active if i != p])
                a[p] = [x+y for x,y in zip(a[p],a[t])]
                a[t] = [0]*n
                active.remove(t)
                ops.append(f'1 {p+1} {t+1}')
            elif op == 2:
                x,q = rng.randrange(1,241),rng.randrange(n)
                a[p][q] += x
                ops.append(f'2 {p+1} {x} {q+1}')
            elif op == 3:
                l,r = sorted([rng.randrange(n),rng.randrange(n)])
                ops.append(f'3 {p+1} {l+1} {r+1}')
                ans.append(sum(a[p][l:r+1]))
            else:
                k = rng.randrange(1,min(sum(a[p])+2,200001))
                ops.append(f'4 {p+1} {k}')
                prefix = 0
                want = -1
                for i,x in enumerate(a[p]):
                    prefix += x
                    if prefix >= k:
                        want = i+1
                        break
                ans.append(want)
        seg.append((f'multiset-{case}',f'{n} 240\n'+ ' '.join(map(str,initial))+'\n'+'\n'.join(ops)+'\n',ans))
    n,m = 100000,200000
    ops = [f'1 1 {i}' for i in range(2,n+1)]
    # Version i of the initial chain connects exactly vertices 1..i+1.
    threshold = n
    ans = []
    while len(ops)<m:
        if len(ops)%3 == 0:
            k=rng.randrange(n)
            ops.append(f'2 {k}')
            threshold=k+1
        else:
            x,y = rng.randrange(1,n+1),rng.randrange(1,n+1)
            ops.append(f'3 {x} {y}')
            ans.append(int(x==y or max(x,y)<=threshold))
    dsu.append(('maximum-branches',f'{n} {m}\n'+'\n'.join(ops)+'\n',ans))
    n=m=200000
    ops,ans=[],[]
    next_set=2
    for step in range(m//5):
        ops.extend([f'0 1 2 {n}',f'3 {next_set} 1 {n}',f'4 {next_set} {m}',f'1 1 {next_set}',f'3 1 1 {n}'])
        ans.extend([(n-1)*m,2,n*m])
        next_set+=1
    seg.append(('maximum-counts',f'{n} {m}\n'+' '.join([str(m)]*n)+'\n'+'\n'.join(ops)+'\n',ans))
    n,m=100000,200000
    ops=['0 1 1 1']+[f'2 2 1 {i}' for i in range(1,n+1)]+['1 1 2']
    ans=[]
    while len(ops)<m:
        if len(ops)%2:
            ops.append(f'3 1 1 {n}')
            ans.append(2*n)
        else:
            ops.append(f'4 1 {2*n}')
            ans.append(n)
    seg.append(('dense-overlap-meld',f'{n} {m}\n'+' '.join(['1']*n)+'\n'+'\n'.join(ops)+'\n',ans))
    return dsu,seg


def main():
    if not __debug__:
        raise RuntimeError('Python checks must stay enabled')
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='ownership-' + mode + '-', dir=ROOT / 'build'))
    before = snapshot(ROOT)
    probe = (ROOT / 'tests/ownership_probe.cpp').read_text()
    parts = extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))
    core = '\n'.join(next(x['code'] for x in parts if x['symbol'] == s) for s in ['PersistentDSU','MergeSplitTree'])
    prelude = ''.join('#include <'+s+'>\n' for s in ['algorithm','cassert','climits','iostream','numeric','random','stdexcept','utility','vector'])+'using namespace std;\n'
    copied = prelude+core+'\n'+probe.replace('#include "../src/compact/persistent_dsu.hpp"','').replace('#include "../src/compact/merge_split_tree.hpp"','')
    flags = ['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env = os.environ.copy()
    if mode=='sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),flags=flags,programs=[],mutants=[],applications=[])
    def compile(name,source,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name
        cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()))
    reference=None
    for form,source in [('header','#include "'+str(ROOT/'tests/ownership_probe.cpp')+'"\n'),('copied',copied)]:
        for nd in [False,True]:
            name=form+('-ndebug' if nd else '-assert')
            exe,entry=compile(name,source,['-DNDEBUG'] if nd else [])
            p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=600)
            assert p.returncode==0 and not p.stderr and p.stdout.startswith(b'PASS '),(name,p.returncode,p.stdout,p.stderr[-1000:])
            if reference is None:reference=p.stdout
            assert reference==p.stdout
            entry.update(result=p.stdout.decode().strip(),output_sha256=sha(p.stdout))
            report['programs'].append(entry)
            print(name,entry['result'],flush=True)
    mutations=[
        ('in-place-version','int p = t.size();\n        t.push_back(node);','int p = old;'),
        ('wrong-root-size','set(p, 0, n, y, a + b)','set(p, 0, n, y, b)'),
        ('no-balancing','if (a < b)','if (false)'),
        ('keep-consumed-root','root[src] = 0;','root[src] = root[dst];'),
        ('closed-split-end','r <= a) return {p, 0};','r < a) return {p, 0};'),
        ('kth-equality','if (k <= left)','if (k < left)'),
        ('lost-free-node','free.push_back(p);','/* lost node */'),
    ]
    # A boundary mutation that stays terminating: include coordinate r when possible.
    mutations[4]=('closed-split-end','cut(root[s], 0, n, l, r)','cut(root[s], 0, n, l, r < n ? r + 1 : r)')
    for name,old,new in mutations:
        assert copied.count(old)==1,(name,copied.count(old))
        exe,entry=compile(name,copied.replace(old,new),['-DNDEBUG'])
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=600)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        entry.update(independent_oracle_rejected=True,output_sha256=sha(p.stdout))
        report['mutants'].append(entry)
        print(name,'rejected',flush=True)
    ds,ms=datasets()
    for example,data in [('example-248',ds),('example-249',ms)]:
        row=next(r for r in records() if r['id']==example)
        own=next(x['code'] for x in parts if x['symbol']==row['symbol'])
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('bundle',row['program']),('minimal-copy',prelude+own+'\n'+row['snippet'])]:
            name=example+'-'+form
            exe,entry=compile(name,source)
            entry['runs']=[]
            for label,inp,want in data:
                raw=inp.encode()
                p=subprocess.run([str(exe)],input=raw,capture_output=True,env=env,timeout=180)
                assert p.returncode==0 and not p.stderr,(name,label,p.returncode,p.stderr[-1000:])
                assert p.stdout.split()==[str(x).encode() for x in want],(name,label,p.stdout[:200])
                entry['runs'].append(dict(case=label,input_sha256=sha(raw),output_sha256=sha(p.stdout),passed=True))
            report['applications'].append(entry)
            print(name,len(data),'inputs PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT),complete_input_counts={'P3402':len(ds),'P5494':len(ms)},scope='Local label-array and count-array oracles; immutable history, balancing, exclusive ownership and free-pool audit, LLONG_MAX extensions, recycling and object copies; header/copied assert/NDEBUG and seven semantic mutants; three complete input forms including published maximum sizes and dense overlapping meld. No official samples, online AC, ranking, full-library runtime or LeakSanitizer claim.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('ownership',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':
    main()
