"""UVA1479 complete composition: forward BFS oracle versus offline reverse queries."""
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import re
import resource
import subprocess
import sys
import tempfile
import time
from fractions import Fraction
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records
from audit_copy_context import extract_components


def encode(values, edges, ops):
    return f'{len(values)} {len(edges)}\n'+' '.join(map(str, values))+'\n'+''.join(f'{u+1} {v+1}\n' for u,v in edges)+'\n'.join(ops)+'\nE\n'


def forward(values, edges, ops):
    a = values[:]
    active = [True]*len(edges)
    ans = []
    for line in ops:
        fields = line.split()
        op, x = fields[0], int(fields[1])-1
        if op == 'D':
            assert active[x]
            active[x] = False
        elif op == 'C':
            a[x] = int(fields[2])
        else:
            adj = [[] for _ in a]
            for on, (u, v) in zip(active, edges):
                if on:
                    adj[u].append(v)
                    adj[v].append(u)
            seen, queue = {x}, [x]
            for u in queue:
                for v in adj[u]:
                    if v not in seen:
                        seen.add(v)
                        queue.append(v)
            weights = sorted((a[u] for u in seen), reverse=True)
            k = int(fields[2])
            ans.append(weights[k-1] if 1 <= k <= len(weights) else 0)
    assert ans
    return ans


def cases():
    sample = '3 3\n10\n20\n30\n1 2\n2 3\n1 3\nD 3\nQ 1 2\nQ 2 1\nD 2\nQ 3 2\nC 1 50\nQ 1 1\nE\n3 3\n10\n20\n20\n1 2\n2 3\n1 3\nQ 1 1\nQ 1 2\nQ 1 3\nE\n0 0\n'
    out = [('official', sample, [[20,30,0,50],[20,20,10]])]
    rng = random.Random(1479)
    for test in range(100):
        raw, wants = '', []
        for part in range(3):
            n = 1+rng.randrange(15)
            values = [rng.choice([-1000000,-1,0,1,1000000]) for _ in range(n)]
            edges = [(rng.randrange(n),rng.randrange(n)) for _ in range(rng.randrange(30))]
            remaining = list(range(len(edges)))
            ops = []
            for step in range(140):
                op = rng.randrange(3)
                if op == 0 and remaining:
                    index = rng.randrange(len(remaining))
                    ops.append(f'D {remaining.pop(index)+1}')
                elif op == 1:
                    ops.append(f'C {rng.randrange(n)+1} {rng.choice([-1000000,-2,-1,0,1,2,1000000])}')
                else:
                    k = rng.choice([-2147483648,-1,0,1,2,n,n+1,2147483647])
                    ops.append(f'Q {rng.randrange(n)+1} {k}')
            ops.append('Q 1 1')
            raw += encode(values,edges,ops)+'\n'
            wants.append(forward(values,edges,ops))
        out.append((f'random-multitest-{test}',raw+'0 0\n',wants))
    n = 20000
    # Exact official maxima: 60000 D, 200000 C, 200000 Q.
    edges = [(u,(u+d)%n) for d in [1,2,3] for u in range(n)]
    ops = [f'D {i+1}' for i in range(len(edges))]
    want = []
    for i in range(200000):
        x, v = i%n, i-100000
        ops.append(f'C {x+1} {v}')
        ops.append(f'Q {x+1} 1')
        want.append(v)
    out.append(('max-disconnected-changes',encode([0]*n,edges,ops)+'0 0\n',[want]))
    edges = [(i,i+1) for i in range(n-1)]
    ops, want = [], []
    for i in range(n-1):
        ops.append(f'D {i+1}')
        ops.extend([f'Q {i+1} 2',f'Q {i+2} {n-i-1}',f'Q {i+2} {n-i}'])
        want.extend([0,-1000000,0])
    while len(want)<200000:
        ops.append('Q 1 1')
        want.append(-1000000)
    out.append(('max-chain-rejoin',encode([-1000000]*n,edges,ops)+'0 0\n',[want]))
    # Repeated updates while always connected; duplicates and fixed-root merges.
    ops, want = [], []
    for i in range(200000):
        v = 1000000 if i%2==0 else -1000000
        ops.extend([f'C 1 {v}',f'Q 2 {1 if i%2==0 else n}'])
        want.append(v)
    out.append(('max-connected-changes',encode([0]*n,edges,ops)+'0 0\n',[want]))
    return out


def check(out, wants):
    lines = out.splitlines()
    if len(lines) != len(wants):
        return False
    for i,(line, ans) in enumerate(zip(lines,wants),1):
        match = re.fullmatch(r'Case '+str(i)+r': (-?\d+\.\d{6})',line)
        if not match or abs(Fraction(match[1])-Fraction(sum(ans),len(ans))) > Fraction(1,2000000):
            return False
    return True


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='graph-queries-'+mode+'-',dir=ROOT/'build'))
    flags = ['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    if platform.system()=='Darwin':flags+=['-Wl,-stack_size,0x20000000']
    else:
        _,hard=resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard!=-1 else 512<<20,hard))
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    row=next(r for r in records() if r['id']=='example-289')
    inv={x['symbol']:x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    # Only the documented symbols, not the rest of data_structure.hpp.
    parts=[]
    for symbol in ['dsu','MergeSplitTree']:
        parts.append(inv[symbol])
    minimal='#include <algorithm>\n#include <cassert>\n#include <climits>\n#include <iomanip>\n#include <iostream>\n#include <numeric>\n#include <utility>\n#include <vector>\nusing namespace std;\n'+'\n'.join(parts)+'\n'+row['snippet']
    sha=lambda data:hashlib.sha256(data).hexdigest()
    report=dict(mode=mode,source_before_sha256=before,programs=[],mutants=[],scope='Complete UVA1479 driver and independently copied dependencies; forward BFS/sorting per-query oracle, exact rational mean and printed rounding; signed32 k limits and full operation maxima. No online verdict.')
    def compile(name,source,extra=()):
        cpp,exe=out/(name+'.cpp'),out/name
        cpp.write_text(source)
        cmd=[CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        p=subprocess.run(cmd,capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        return exe,dict(name=name,compile_command=cmd,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),runs=[])
    cs=cases()
    for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('minimal-copy',minimal),('minimal-ndebug',minimal)]:
        exe,entry=compile(form,source,['-DNDEBUG'] if form.endswith('ndebug') else [])
        for name,raw,want in cs:
            start=time.monotonic()
            p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=180)
            assert p.returncode==0 and not p.stderr and check(p.stdout.decode(),want),(form,name,p.returncode,p.stdout[:300],p.stderr[-1000:])
            entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),output_sha256=sha(p.stdout),elapsed_seconds=time.monotonic()-start,passed=True))
        report['programs'].append(entry)
        print(form,len(cs),'PASS',flush=True)
    traced=row['program'].replace('if (p != -1) sum += values[p];','cerr << (p == -1 ? 0 : values[p]) << "\\n";\n                if (p != -1) sum += values[p];')
    exe,entry=compile('query-trace',traced)
    for name,raw,want in cs:
        p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=180)
        assert p.returncode==0 and check(p.stdout.decode(),want)
        assert list(map(int,p.stderr.split())) == [x for ans in want for x in reversed(ans)],name
        entry['runs'].append(dict(case=name,input_sha256=sha(raw.encode()),trace_sha256=sha(p.stderr),passed=True))
    report['programs'].append(entry)
    print('query-trace',len(cs),'PASS',flush=True)
    for name,old,new in [
        ('wrong-k-direction','(long long)d.size(r) - y + 1','(long long)y'),
        ('save-new-not-old','swap(a[x], y);','a[x] = y;'),
        ('keep-deleted-edges','if (!deleted[e]) join(e);','join(e);'),
        ('no-restore','a[x] = y;','(void)y;'),
        ('absolute-answer','sum += values[p];','sum += abs(values[p]);')]:
        assert row['program'].count(old)==1,(name,old)
        exe,entry=compile(name,row['program'].replace(old,new),['-DNDEBUG'])
        rejected=None
        for case,raw,want in cs[:101]:
            p=subprocess.run([str(exe)],input=raw.encode(),capture_output=True,env=env,timeout=30)
            assert p.returncode==0 and not p.stderr,(name,p.stderr[-1000:])
            if not check(p.stdout.decode(),want):
                rejected=case
                break
        assert rejected is not None,name
        entry['oracle_reject_case']=rejected
        report['mutants'].append(entry)
        print(name,rejected,'REJECT',flush=True)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:',out/'report.json',flush=True)

if __name__=='__main__':main()
