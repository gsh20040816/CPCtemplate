#!/usr/bin/env python3
"""Sparse/dense 2D Fenwick: independent point scan, matrix oracle and complete inputs."""
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


def main():
    if not __debug__:
        raise RuntimeError('Python checks must stay enabled')
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='fenwick2d-' + mode + '-', dir=ROOT / 'build'))
    before = snapshot(ROOT)
    probe = (ROOT / 'tests/fenwick2d_probe.cpp').read_text()
    parts = extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))
    core = '\n'.join(next(x['code'] for x in parts if x['symbol'] == symbol) for symbol in ['Fenwick2D','RectangleFenwick'])
    headers = ['algorithm', 'cassert', 'climits', 'iostream', 'array', 'utility', 'vector']
    prelude = ''.join('#include <' + x + '>\n' for x in headers) + 'using namespace std;\n'
    copied = prelude + core + '\n' + probe.replace('#include "../src/compact/fenwick2d.hpp"', '').replace('#include "../src/compact/rectangle_fenwick.hpp"', '')
    flags = ['-std=c++20', '-Wall', '-Wextra'] + (['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    report = dict(mode=mode, source_before_sha256=before, compiler=str(compiler), compiler_sha256=sha(compiler.read_bytes()), flags=flags, programs=[], mutants=[], applications=[])
    def compile(name, source, extra=()):
        cpp, exe = out / (name + '.cpp'), out / name
        cpp.write_text(source)
        command = [CXX, *flags, *extra, str(cpp), '-o', str(exe)]
        subprocess.run(command, capture_output=True, check=True)
        return exe, dict(name=name, compile_command=command, source_sha256=sha(cpp.read_bytes()), binary_sha256=sha(exe.read_bytes()))
    reference = None
    for form, source in [('header', '#include "' + str(ROOT / 'tests/fenwick2d_probe.cpp') + '"\n'), ('copied', copied)]:
        for nd in [False, True]:
            name = form + ('-ndebug' if nd else '-assert')
            exe, entry = compile(name, source, ['-DNDEBUG'] if nd else [])
            p = subprocess.run([str(exe)], capture_output=True, env=env, timeout=600)
            assert p.returncode == 0 and not p.stderr, (name, p.returncode, p.stderr[-1000:])
            assert p.stdout.startswith(b'PASS ') and p.stdout.endswith(b' checks\n'), p.stdout
            if reference is None:
                reference = p.stdout
            assert p.stdout == reference
            entry.update(output_sha256=sha(p.stdout), result=p.stdout.decode().strip())
            report['programs'].append(entry)
            if not nd:
                bad = subprocess.run([str(exe), 'invalid'], capture_output=True, env=env, timeout=30)
                assert bad.returncode != 0 and b'Assertion' in bad.stderr, (name, bad.returncode, bad.stderr)
                entry['unregistered_pair_rejected_with_asserts'] = True
            print(name, entry['result'], flush=True)
    mutations = [
        ('closed-x-prefix', 'int i = lower_bound(xs.begin(), xs.end(), x) - xs.begin();', 'int i = upper_bound(xs.begin(), xs.end(), x) - xs.begin();'),
        ('closed-y-prefix', 'int j = lower_bound(ys[i].begin(), ys[i].end(), y) - ys[i].begin();', 'int j = upper_bound(ys[i].begin(), ys[i].end(), y) - ys[i].begin();'),
        ('omit-update-ancestors', 'for (; j < (int)bit[i].size(); j += j & -j) bit[i][j] += v;', 'if (i == k) for (; j < (int)bit[i].size(); j += j & -j) bit[i][j] += v;'),
        ('wrong-corner-sign', 'corner(r, d, -v);', 'corner(r, d, v);'),
        ('omit-xy-moment', 'a[0] * x * y - a[1] * y - a[2] * x + a[3]', 'a[0] * x * y - a[1] * y - a[2] * x'),
        ('wrong-y-coefficient', 'a[0] * x * y - a[1] * y - a[2] * x + a[3]', 'a[0] * x * y - a[1] * x - a[2] * x + a[3]'),
    ]
    for name, old, new in mutations:
        assert copied.count(old) == 1, name
        exe, entry = compile(name, copied.replace(old, new), ['-DNDEBUG'])
        p = subprocess.run([str(exe)], capture_output=True, env=env, timeout=180)
        assert p.returncode == 0 and not p.stderr and p.stdout == b'ORACLE_REJECT\n', (name,p.returncode,p.stdout,p.stderr[-1000:])
        entry.update(output_sha256=sha(p.stdout),independent_oracle_rejected=True)
        report['mutants'].append(entry)
    rng=random.Random(45142026)
    sparse=[('official-sample','4 5\n0 0 1\n0 2 10\n2 0 100\n2 2 1000\n1 0 0 2 3\n1 0 0 3 3\n0 2 2 10000\n0 1 1 100000\n1 1 1 3 3\n',[11,1111,111000])]
    dense=[]
    for case in range(160):
        n=rng.randrange(1,45)
        initial=[(rng.randrange(20),rng.randrange(20),rng.randrange(1000000001)) for _ in range(n)]
        points=initial[:]
        ops,ans=[],[]
        for step in range(240):
            if rng.randrange(3)==0:
                p=(rng.randrange(20),rng.randrange(20),rng.randrange(1000000001))
                points.append(p)
                ops.append('0 '+' '.join(map(str,p)))
            else:
                l,r=sorted(rng.sample(range(22),2))
                d,u=sorted(rng.sample(range(22),2))
                ops.append(f'1 {l} {d} {r} {u}')
                ans.append(sum(w for x,y,w in points if l<=x<r and d<=y<u))
        inp=f'{n} {len(ops)}\n'+''.join(f'{x} {y} {w}\n' for x,y,w in initial)+'\n'.join(ops)+'\n'
        sparse.append((f'point-random-{case}',inp,ans))
        n,m=rng.randrange(1,13),rng.randrange(1,13)
        a=[[0]*m for _ in range(n)]
        ops,ans=[],[]
        for step in range(220):
            l,r=sorted(rng.sample(range(n+1),2))
            d,u=sorted(rng.sample(range(m+1),2))
            if rng.randrange(2)==0:
                v=rng.randrange(-500,501)
                ops.append(f'L {l+1} {d+1} {r} {u} {v}')
                for i in range(l,r):
                    for j in range(d,u):a[i][j]+=v
            else:
                ops.append(f'k {l+1} {d+1} {r} {u}')
                ans.append(sum(a[i][j] for i in range(l,r) for j in range(d,u)))
        dense.append((f'grid-random-{case}',f'X {n} {m}\n'+'\n'.join(ops)+'\n',ans))
    n,q=100000,100000
    for kind in [0,1]:
        initial=[(i*1000,(i if kind==0 else n-1-i)*1000,1000000000) for i in range(n)]
        extra={0:0,n//2:0,n-1:0}
        ops,ans=[],[]
        for step in range(q):
            if step%3==0:
                i=rng.choice(list(extra))
                extra[i]+=1000000000
                x,y,_=initial[i]
                ops.append(f'0 {x} {y} 1000000000')
            else:
                l,r=sorted(rng.sample(range(n+1),2))
                d,u=sorted(rng.sample(range(n+1),2))
                ops.append(f'1 {l*1000} {d*1000} {r*1000} {u*1000}')
                lo,hi=(d,u) if kind==0 else (n-u,n-d)
                want=max(0,min(r,hi)-max(l,lo))*1000000000
                want+=sum(v for i,v in extra.items() if l<=i<r and d<=(i if kind==0 else n-1-i)<u)
                ans.append(want)
        inp=f'{n} {q}\n'+''.join(f'{x} {y} {w}\n' for x,y,w in initial)+'\n'.join(ops)+'\n'
        sparse.append((f'point-max-{kind}',inp,ans))
    # n,m are official maxima; each queried matrix is either zero, 500, or
    # 1000 on a fixed rectangle. Final sums fit int32; moment arithmetic need not.
    for kind in [0,1]:
        n=m=2048
        l=d=0 if kind==0 else 1000
        r=u=2048
        ops,ans=[],[]
        level=0
        for step in range(200000):
            part=step%6
            if part in [0,1,3,4]:
                v=500 if part<2 else -500
                # Full-grid case uses only one positive layer to meet int32.
                if kind==0 and part in [1,4]:v=0
                level+=v
                ops.append(f'L {l+1} {d+1} {r} {u} {v}')
            else:
                a,c=sorted(rng.sample(range(n+1),2))
                b,e=sorted(rng.sample(range(m+1),2))
                ops.append(f'k {a+1} {b+1} {c} {e}')
                want=max(0,min(c,r)-max(a,l))*max(0,min(e,u)-max(b,d))*level
                assert -(1<<31)<=want<(1<<31)
                ans.append(want)
        dense.append((f'grid-max-{kind}',f'X {n} {m}\n'+'\n'.join(ops)+'\n',ans))
    for example,datasets in [('example-246',sparse),('example-247',dense)]:
        row=next(r for r in records() if r['id']==example)
        symbol=row['symbol']
        own=next(x['code'] for x in parts if x['symbol']==symbol)
        for form,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('bundle',row['program']),('minimal-copy',prelude+own+'\n'+row['snippet'])]:
            name=example+'-'+form
            exe,entry=compile(name,source)
            entry['runs']=[]
            for label,inp,want in datasets:
                data=inp.encode()
                p=subprocess.run([str(exe)],input=data,capture_output=True,env=env,timeout=180)
                assert p.returncode==0 and not p.stderr,(name,label,p.returncode,p.stderr[-1000:])
                assert p.stdout.split()==[str(x).encode() for x in want],(name,label,p.stdout[:300])
                entry['runs'].append(dict(case=label,input_sha256=sha(data),output_sha256=sha(p.stdout),passed=True))
            report['applications'].append(entry)
            print(name,len(datasets),'inputs PASS',flush=True)
    report.update(source_after_sha256=snapshot(ROOT),passed=True,complete_input_counts={'point_add_rectangle_sum':len(sparse),'P4514':len(dense)},scope='Local independent point-scan and direct matrix oracle, half-open/signed/extreme coordinate tests, int128 extensions, copies/reinitialization, 200000 registered sparse points and 2048-square grid. Header/copied assert/NDEBUG, six mutants and three forms of each full input program. Not online AC, full-library runtime or LeakSanitizer.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Fenwick2D',mode,'PASS:',out/'report.json')

if __name__=='__main__':
    main()
