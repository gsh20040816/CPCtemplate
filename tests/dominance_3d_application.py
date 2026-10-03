#!/usr/bin/env python3
"""P3810 exact histogram programs on valid formal-domain inputs."""
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from usage_examples import records
from compiler_config import CXX
from dominance_3d import oracle


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    if not __debug__:raise RuntimeError('Exact output checks require assertions')
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='dominance-application-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT);cases=[];rng=random.Random(20261004)
    def add(name,p,counts=None,reference='quadratic direct coordinate comparisons'):
        p=list(p);n=len(p);assert 1<=n<=100000 and all(1<=c<=200000 for q in p for c in q)
        counts=oracle(p) if counts is None else list(counts);assert len(counts)==n
        hist=[0]*n
        for c in counts:assert 0<=c<n;hist[c]+=1
        data=(f'{n} 200000\n'+''.join(f'{x} {y} {z}\n' for x,y,z in p)).encode()
        (out/(name+'.in')).write_bytes(data)
        cases.append(dict(name=name,data=data,n=n,expected=hist,reference=reference))
    add('constructed-five',[(1,1,1)]*2+[(1,2,1),(2,1,2),(2,2,2)])
    add('single-boundary',[(200000,200000,200000)])
    add('identical-boundary',[(200000,200000,200000)]*9)
    add('same-x',[(1,i+1,30-i) for i in range(30)])
    add('same-y',[(i+1,1,i+1) for i in range(30)])
    add('same-z',[(i+1,30-i,1) for i in range(30)])
    for k in range(60):add(f'random-{k}',[tuple(rng.randrange(1,21) for _ in range(3)) for _ in range(rng.randrange(1,51))])
    n=100000
    add('max-chain',((i+1,i+1,i+1) for i in range(n)),range(n),'monotone chain rank')
    add('max-antichain',((i+1,n-i,200000) for i in range(n)),[0]*n,'opposing coordinates')
    add('max-identical',[(200000,200000,200000)]*n,[n-1]*n,'all others')
    p=list(itertools.product(range(1,41),range(1,51),range(1,51)))
    add('max-grid',p,[x*y*z-1 for x,y,z in p],'Cartesian prefix volume minus self')
    p=list(itertools.product(range(1,21),range(1,51),range(1,51)))
    add('max-duplicate-grid',[q for q in p for _ in range(2)],[2*x*y*z-1 for x,y,z in p for _ in range(2)],'duplicated Cartesian prefix volume minus self')
    expected=json.dumps([{k:v for k,v in t.items() if k!='data'} for t in cases],separators=(',',':')).encode();(out/'expected.json').write_bytes(expected)
    row=next(r for r in records() if r['id']=='example-237')
    components={x['symbol']:x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    copied='#include <algorithm>\n#include <array>\n#include <cassert>\n#include <climits>\n#include <iostream>\n#include <numeric>\n#include <vector>\nusing namespace std;\n'+components['Fenwick']+'\n'+components['Dominance3D']+'\n'+row['snippet']
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),flags=flags,environment={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')},expected_sha256=sha(expected),inputs=[dict(name=t['name'],sha256=sha(t['data']),n=t['n'],reference=t['reference']) for t in cases],programs=[])
    for name,text in [('direct','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('copied',copied)]:
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(text);cmd=[CXX,*flags,str(cpp),'-o',str(exe)];subprocess.run(cmd,check=True,capture_output=True)
        entry=dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),runs=[])
        for t in cases:
            run=subprocess.run([str(exe)],input=t['data'],capture_output=True,env=env,timeout=90);assert run.returncode==0 and not run.stderr,(name,t['name'],run.stderr[-1000:])
            got=list(map(int,run.stdout.split()));assert len(got)==t['n'] and sum(got)==t['n'] and got==t['expected'],(name,t['name'])
            (out/(name+'-'+t['name']+'.out')).write_bytes(run.stdout);entry['runs'].append(dict(case=t['name'],output_sha256=sha(run.stdout),passed=True))
        report['programs'].append(entry)
    report.update(source_after_sha256=snapshot(ROOT),passed=True,scope='All inputs satisfy official P3810 numerical domain, independently checked locally. Constructed examples are not official samples. No official checker/hidden data, online AC, ranking, full-suite or LSan claim.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(f'P3810 {mode}: {len(cases)} inputs x three program forms PASS; {out.relative_to(ROOT)}/report.json')


if __name__=='__main__':main()
