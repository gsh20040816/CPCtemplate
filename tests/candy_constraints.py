"""P3275: enumerate original five relations, minimum assignments, SCC order and certificates."""
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


def satisfied(x,op,a,b):
    u,v = x[a-1],x[b-1]
    if op == 1:
        return u == v
    if op == 2:
        return u < v
    if op == 3:
        return u >= v
    if op == 4:
        return u > v
    return u <= v


def cases():
    cs = []
    def append(name,n,ops,want=None):
        if want is None:
            want = min((sum(x) for x in itertools.product(range(1,n+1),repeat=n) if all(satisfied(x,*op) for op in ops)),default=-1)
        raw = f'{n} {len(ops)}\n'+''.join(f'{op} {a} {b}\n' for op,a,b in ops)
        cs.append((name,raw,want,n,ops))
    for op in range(1,6):
        append(f'self-{op}',1,[(op,1,1)])
    relations = list(itertools.product(range(1,6),range(1,3),range(1,3)))
    for i,pair in enumerate(itertools.product(relations,repeat=2)):
        append(f'all-n2-relation-pairs-{i}',2,list(pair))
    for op,a,b in itertools.product(range(1,6),range(1,4),range(1,4)):
        append(f'n3-single-{op}-{a}-{b}',3,[(op,a,b)])
    rng = random.Random(3275)
    for i in range(150):
        n = 1+i%5
        if i%2:
            planted = [rng.randrange(1,n+1) for _ in range(n)]
            allowed = [op for op in itertools.product(range(1,6),range(1,n+1),range(1,n+1)) if satisfied(planted,*op)]
            ops = [rng.choice(allowed) for _ in range(1+i%20)]
        else:
            ops = [(rng.randrange(1,6),rng.randrange(1,n+1),rng.randrange(1,n+1)) for _ in range(1+i%20)]
        append(f'brute-random-{i}',n,ops)
    n = 100000
    append('max-deep-strict-chain',n,[(2,u,u+1) for u in range(1,n)]+[(5,1,n)],n*(n+1)//2)
    append('max-reverse-strict-chain',n,[(4,u,u+1) for u in range(1,n)]+[(3,1,n)],n*(n+1)//2)
    append('max-one-zero-scc',n,[(1,u,u+1) for u in range(1,n)]+[(1,1,n)],n)
    append('max-strict-cycle',n,[(2,u,u+1) for u in range(1,n)]+[(2,n,1)],-1)
    append('max-late-positive-in-zero-scc',n,[(1,u,u+1) for u in range(1,n)]+[(2,1,n)],-1)
    append('max-parallel-constraints',n,[(2,1,n)]*n,n+1)
    ops = [(1,u,u+1) for u in range(1,n,2)]+[(2,u,u+2) for u in range(1,n-1,2)]
    ops.append((5,1,n))
    append('max-chain-of-two-vertex-sccs',n,ops,(n//2)*(n//2+1))
    return cs


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='candy-constraints-'+mode+'-',dir=ROOT/'build'))
    flags = ['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    if platform.system() == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    else:
        _,hard = resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard != -1 else 512<<20,hard))
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    row = next(r for r in records() if r['id'] == 'example-300')
    header = (ROOT/'src/compact/tarjan.hpp').read_text().replace('#pragma once\n','')
    sha = lambda data: hashlib.sha256(data).hexdigest()
    report = dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],local_stack_mib=512,scope='P3275 application only. All n=2 ordered pairs of five relations; n=1/3 singles; 150 independent integer-enumerated n<=5 inputs; seven maximum-scale cases; per-original-vertex optimal assignment certificate. Existing Tarjan unchanged; local only.')
    def compile(name,source,extra=()):
        cpp,exe = out/(name+'.cpp'),out/name
        cpp.write_text(source)
        cmd = [CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p = subprocess.run(cmd,capture_output=True)
        assert p.returncode == 0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    def run(exe,raw):
        p = subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=180)
        assert p.returncode == 0,(exe,p.returncode,p.stderr[-1000:])
        return p
    cs = cases()
    for form,source,extra in [('driver','#include "'+str(ROOT/row['driver'])+'"\n',[]),('expanded',row['program'],[]),('minimal-copy','#include <iostream>\n#include <array>\n#include <utility>\n'+header+'\n'+row['snippet'],[]),('ndebug',row['program'],['-DNDEBUG'])]:
        exe,entry = compile(form,source,extra)
        for name,raw,want,n,ops in cs:
            p = run(exe,raw)
            assert not p.stderr and p.stdout.split() == [str(want).encode()],(form,name,p.stdout[:500],want,p.stderr[-1000:])
            entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),output_sha256=sha(p.stdout),passed=True))
        report['programs'].append(entry)
        print(form,len(cs),'PASS',flush=True)
    for name,old,new in [
        ('strict-edge-direction','else if (op == 2) add(a, b, 1);','else if (op == 2) add(b, a, 1);'),
        ('no-positive-cycle-check','if (w)\n','if (false)\n'),
        ('wrong-scc-order','for (int u = t.cnt; u >= 1; u--)','for (int u = 1; u <= t.cnt; u++)'),
        ('zero-lower-bound','vector<int> dis(t.cnt + 1, 1);','vector<int> dis(t.cnt + 1, 0);'),
        ('count-scc-once','for (int u = 1; u <= n; u++) sum += dis[t.bel[u]];','for (int u = 1; u <= t.cnt; u++) sum += dis[u];'),
        ('drop-strictness','else if (op == 2) add(a, b, 1);','else if (op == 2) add(a, b, 0);'),
        ('one-way-equality','add(b, a, 0);\n        }','/* omitted */\n        }')]:
        assert row['program'].count(old) == 1,name
        exe,entry = compile(name,row['program'].replace(old,new),['-DNDEBUG'])
        rejected = False
        for case,raw,want,n,ops in cs:
            p = run(exe,raw)
            assert not p.stderr,p.stderr[-1000:]
            if p.stdout.split() != [str(want).encode()]:
                entry.update(rejecting_case=case,independent_oracle_rejected=True)
                rejected = True
                break
        assert rejected,name
        report['mutants'].append(entry)
        print(name,'ORACLE_REJECT',flush=True)
    needle="    cout << sum << '\\n';"
    assert row['program'].count(needle) == 1
    source = row['program'].replace(needle,"    for (int u = 1; u <= n; u++) cerr << dis[t.bel[u]] << ' ';\n"+needle)
    exe,entry = compile('per-vertex-certificate',source)
    for case,raw,want,n,ops in cs:
        p = run(exe,raw)
        assert p.stdout.split() == [str(want).encode()]
        if want == -1:
            assert not p.stderr
        else:
            x = list(map(int,p.stderr.split()))
            assert len(x) == n and min(x) >= 1 and max(x) <= n
            assert sum(x) == want and all(satisfied(x,*op) for op in ops),case
        entry['runs'].append(dict(case=case,input_sha256=sha(raw.encode()),certificate_sha256=sha(p.stderr),passed=True))
    report['programs'].append(entry)
    print('per-vertex-certificate',len(cs),'PASS',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before == report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:',out/'report.json',flush=True)

if __name__ == '__main__':
    main()
