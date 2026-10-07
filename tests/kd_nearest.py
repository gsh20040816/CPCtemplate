#!/usr/bin/env python3
"""Exact Python-integer nearest/farthest oracles and independent tree invariants."""
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
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot
from usage_examples import records
from compiler_config import CXX


def sha(x):
    return hashlib.sha256(x).hexdigest()


def datasets():
    rng = random.Random(20934347)
    cases = []
    for d in [1, 2, 3, 5, 10]:
        for rep in range(24):
            n = rep * 3
            if rep % 4 == 0:
                p = [tuple(rng.choice([-2147483648, 2147483647, 0]) for _ in range(d)) for _ in range(n)]
            elif rep % 4 == 1:
                p = [(i,) + (0,) * (d - 1) for i in range(n)]
            elif rep % 4 == 2:
                p = [(7,) * d] * n
            else:
                p = [tuple(rng.randrange(-20, 21) for _ in range(d)) for _ in range(n)]
            qs = []
            for j in range(12):
                q = p[j % n] if n and j % 3 == 0 else tuple(rng.randint(-2147483648, 2147483647) for _ in range(d))
                k = [0, min(1, n), n, rng.randrange(n + 1)][j % 4]
                qs.append((q, k, j % 2))
            cases.append((f'd{d}-case{rep}', d, p, qs))
    p = [(-2147483648, 1), (-2147483648, 0), (2147483647, 0)]
    cases.append(('rounding-unit-gap', 2, p, [((2147483647, 0), k, far) for k in [1, 2, 3] for far in [0, 1]]))
    for rep in range(35):
        n = rng.randrange(1, 100)
        p = list(dict.fromkeys((rng.randrange(-100, 101), rng.randrange(-100, 101)) for _ in range(n)))
        qs = [(tuple(rng.randrange(-10**9, 10**9+1) for _ in range(2)), rng.randrange(1, min(20,len(p))+1), 1) for _ in range(20)]
        cases.append((f'p2093-{rep}', 2, p, qs))
    return cases


def serialize(d, p, qs, form):
    points = '\n'.join(' '.join(map(str,x)) for x in p)
    if form == 'p2093':
        return f'{len(p)}\n'+points+f'\n{len(qs)}\n'+'\n'.join(' '.join(map(str, (*q,k))) for q,k,f in qs)+'\n'
    prefix = f'{d}\n{len(p)} {len(qs)}\n' if form == 'core' else f'{len(p)} {d} {len(qs)}\n'
    return prefix+points+'\n'+'\n'.join(' '.join(map(str, (*q,k,f))) for q,k,f in qs)+'\n'


def oracle(p, qs, application=False):
    out = []
    for q,k,far in qs:
        ids = sorted(range(len(p)), key=lambda i: ((-1 if far else 1)*sum((x-y)**2 for x,y in zip(p[i],q)), i))[:k]
        out.extend([ids[-1]+1] if application else ids)
    return out


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='kd-nearest-'+mode+'-', dir=ROOT/'build'))
    before = snapshot(ROOT)
    flags = ['-std=c++20','-Wall','-Wextra'] + (['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env = os.environ.copy()
    if mode=='sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    report = dict(mode=mode, source_before_sha256=before, programs=[], mutants=[], scope='Local only; Python arbitrary-integer brute force, no online AC or worst-case performance guarantee.')
    header = (ROOT/'src/compact/kd_nearest.hpp').read_text().replace('#pragma once\n','')
    probe = (ROOT/'tests/kd_nearest_probe.cpp').read_text()
    copied = header+'\n'+'\n'.join(x for x in probe.splitlines() if not x.startswith('#include "'))
    def compile(name, source, extra=()):
        cpp = out/(name+'.cpp')
        exe = out/name
        cpp.write_text(source)
        cmd = [CXX,*flags,*extra,str(cpp),'-o',str(exe)]
        proc = subprocess.run(cmd,capture_output=True)
        assert proc.returncode==0,proc.stderr.decode()
        return exe,dict(name=name,source_sha256=sha(source.encode()),binary_sha256=sha(exe.read_bytes()),compile_command=cmd,runs=[])
    cases = datasets()
    expected = {name:oracle(p,qs) for name,d,p,qs in cases}
    def execute(exe, entry, cases, form):
        for name,d,p,qs in cases:
            raw=serialize(d,p,qs,form).encode()
            start=time.monotonic()
            proc=subprocess.run([str(exe)],input=raw,capture_output=True,env=env,timeout=180)
            assert proc.returncode==0 and not proc.stderr,(entry['name'],name,proc.returncode,proc.stderr[-1000:])
            want=oracle(p,qs,True) if form=='p2093' else expected[name]
            assert list(map(int,proc.stdout.split()))==want,(entry['name'],name)
            entry['runs'].append(dict(case=name,input_sha256=sha(raw),output_sha256=sha(proc.stdout),elapsed_seconds=time.monotonic()-start,passed=True))
    for form,source in [('header','#include "'+str(ROOT/'tests/kd_nearest_probe.cpp')+'"\n'),('copied',copied)]:
        for release in [False,True]:
            name=form+('-ndebug' if release else '-assert')
            exe,entry=compile(name,source,['-DNDEBUG'] if release else [])
            execute(exe,entry,cases,'core')
            report['programs'].append(entry)
            print(name,len(cases),'PASS',flush=True)
    # Non-crashing wrong answers establish that tie and exact-distance checks matter.
    for name,old,new in [('rounded-distance','using Wide = __int128_t;','using Wide = double;'),('reverse-tie','far ? -dist : dist, u','far ? -dist : dist, -u')]:
        assert header.count(old)==1
        source=header.replace(old,new)+'\n'+next(r['snippet'] for r in records() if r['id']=='example-267')
        source='#include <iostream>\n'+source
        exe,entry=compile(name,source,['-DNDEBUG'])
        rejected=False
        for label,d,p,qs in cases:
            proc=subprocess.run([str(exe)],input=serialize(d,p,qs,'api').encode(),capture_output=True,env=env,timeout=180)
            assert proc.returncode==0 and not proc.stderr
            if list(map(int,proc.stdout.split()))!=expected[label]:
                rejected=True
                entry.update(rejected_by_case=label,independent_oracle_rejected=True)
                break
        assert rejected,name
        report['mutants'].append(entry)
        print(name,'ORACLE_REJECT',flush=True)
    for ex,form in [('example-267','api'),('example-268','p2093')]:
        row=next(r for r in records() if r['id']==ex)
        selected=cases if form=='api' else [x for x in cases if x[0].startswith('p2093-')]
        for kind,source in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('minimal-copy','#include <iostream>\n'+header+'\n'+row['snippet'])]:
            exe,entry=compile(ex+'-'+kind,source)
            execute(exe,entry,selected,form)
            report['programs'].append(entry)
            print(entry['name'],len(selected),'PASS',flush=True)
    # Maximum n and m, distinct collinear points: kth farthest belongs to the first/last k.
    n=100000
    p=[(i,0) for i in range(n)]
    qs=[((i*100003 % 200001-50000,i*37 % 10000),i%20+1,1) for i in range(10000)]
    want=[]
    for q,k,f in qs:
        ids=list(range(k))+list(range(n-k,n))
        ids.sort(key=lambda i:(-sum((x-y)**2 for x,y in zip(p[i],q)),i))
        want.append(ids[k-1]+1)
    row=next(r for r in records() if r['id']=='example-268')
    exe,entry=compile('p2093-max',row['program'])
    raw=serialize(2,p,qs,'p2093').encode()
    start=time.monotonic()
    proc=subprocess.run([str(exe)],input=raw,capture_output=True,env=env,timeout=180)
    assert proc.returncode==0 and not proc.stderr and list(map(int,proc.stdout.split()))==want
    entry.update(input_sha256=sha(raw),output_sha256=sha(proc.stdout),elapsed_seconds=time.monotonic()-start,passed=True)
    report['programs'].append(entry)
    report.update(passed=True,source_after_sha256=snapshot(ROOT))
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('kd-nearest',mode,'PASS:',out/'report.json',flush=True)

if __name__=='__main__':
    main()
