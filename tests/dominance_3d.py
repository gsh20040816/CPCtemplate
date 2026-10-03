#!/usr/bin/env python3
"""Static weak dominance: direct comparisons, exact ties, copies and large formulas."""
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


def sha(data):return hashlib.sha256(data).hexdigest()


def oracle(p):
    return [sum(j!=i and all(u<=v for u,v in zip(q,x)) for j,q in enumerate(p)) for i,x in enumerate(p)]


def main():
    if not __debug__:raise RuntimeError('Independent result checks require Python assertions')
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='dominance-3d-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT);rng=random.Random(20261004);cases=[]
    def add(name,p,expected=None,reference='quadratic direct coordinate comparisons'):
        p=list(p);expected=oracle(p) if expected is None else list(expected)
        assert len(p)==len(expected)
        cases.append(dict(name=name,p=p,expected=expected,reference=reference))
    cube=list(itertools.product(range(2),repeat=3))
    for n in range(7):
        for k,ids in enumerate(itertools.combinations_with_replacement(range(8),n)):
            p=[cube[i] for i in ids];add(f'cube-{n}-{k}',p)
            if n>1:rng.shuffle(p);add(f'shuffle-{n}-{k}',p)
    lo,hi=-(1<<63),(1<<63)-1
    add('signed64-corners',itertools.product([lo,hi],repeat=3))
    add('uneven-groups',[(1,1,1)]*2+[(1,2,1),(2,1,2),(2,2,2)])
    for axis in range(3):
        for k in range(10):
            p=[tuple(0 if j==axis else rng.randrange(-5,6) for j in range(3)) for _ in range(40)]
            add(f'fixed-axis-{axis}-{k}',p)
    for k in range(400):
        n=rng.randrange(51)
        values=[lo,lo+1,-1,0,1,hi-1,hi] if k%3==0 else list(range(-7,8))
        p=[tuple(rng.choice(values) for _ in range(3)) for _ in range(n)]
        expected=oracle(p);add(f'random-{k}',p,expected)
        if k<60:
            for axes in itertools.permutations(range(3)):
                add(f'axes-{k}-{axes}',[tuple(x[a] for a in axes) for x in p],expected,'axis-permutation invariance from direct oracle')
            perm=list(range(n));rng.shuffle(perm)
            add(f'permutation-{k}',[p[i] for i in perm],[expected[i] for i in perm],'input permutation of direct oracle')
            maps=[{x:i*3-100 for i,x in enumerate(sorted({q[a] for q in p}))} for a in range(3)]
            add(f'relabel-{k}',[tuple(maps[a][q[a]] for a in range(3)) for q in p],expected,'strictly increasing rank relabeling of direct oracle')
            add(f'triple-{k}',[x for x in p for _ in range(3)],[3*(x+1)-1 for x in expected for _ in range(3)],'replication identity q*(count+1)-1')
    n=100000
    add('large-chain',((i,i,i) for i in range(n)),range(n),'monotone chain rank')
    add('large-antichain',((i,n-i,0) for i in range(n)),[0]*n,'opposing first/second coordinates')
    add('large-identical',[(lo,hi,lo)]*n,[n-1]*n,'all other occurrences')
    p=list(itertools.product(range(40),range(50),range(50)))
    add('large-grid',p,[(x+1)*(y+1)*(z+1)-1 for x,y,z in p],'Cartesian prefix volume minus self')
    p=list(itertools.product(range(20),range(50),range(50)))
    add('large-duplicate-grid',[x for x in p for _ in range(2)],[2*(x+1)*(y+1)*(z+1)-1 for x,y,z in p for _ in range(2)],'twice Cartesian prefix volume minus self')
    add('large-fullwidth-chain',((lo+i*180000000000000,hi,lo+i*180000000000000) for i in range(n)),range(n),'fullwidth signed64 monotone chain with fixed coordinate')
    def encode(items):
        return (str(len(items))+'\n'+''.join(str(len(t['p']))+'\n'+''.join(f'{x} {y} {z}\n' for x,y,z in t['p']) for t in items)).encode()
    data=encode(cases);(out/'cases.in').write_bytes(data)
    (out/'expected.json').write_text(json.dumps([{k:v for k,v in t.items() if k!='p'} for t in cases],separators=(',',':'))+'\n')
    components={x['symbol']:x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    prelude='#include <algorithm>\n#include <array>\n#include <cassert>\n#include <climits>\n#include <iostream>\n#include <numeric>\n#include <vector>\nusing namespace std;\n'
    core=components['Fenwick']+'\n'+components['Dominance3D']
    probe=(ROOT/'tests/dominance_3d_probe.cpp').read_text();copied=prelude+core+'\n'+'\n'.join(probe.splitlines()[1:])
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),flags=flags,input_sha256=sha(data),expected_sha256=sha((out/'expected.json').read_bytes()),environment={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')},programs=[],mutants=[])
    def check(output,items):
        lines=iter(output.decode().splitlines())
        for t in items:
            assert list(map(int,next(lines).split()))==[len(t['p']),1,1]
            got=list(map(int,next(lines).split()));assert got==t['expected'],t['name']
        assert next(lines,None) is None
    for form,text in [('header','#include "'+str(ROOT/'tests/dominance_3d_probe.cpp')+'"\n'),('copied',copied)]:
        for ndebug in (False,True):
            name=form+('-ndebug' if ndebug else '-assert');cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(text)
            cmd=[CXX,*flags,*(['-DNDEBUG'] if ndebug else []),str(cpp),'-o',str(exe)];subprocess.run(cmd,check=True,capture_output=True)
            run=subprocess.run([str(exe)],input=data,capture_output=True,env=env,timeout=600);assert run.returncode==0 and not run.stderr,(name,run.returncode,run.stderr[-1000:]);check(run.stdout,cases)
            (out/(name+'.out')).write_bytes(run.stdout)
            report['programs'].append(dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),output_sha256=sha(run.stdout),cases=len(cases),large_cases=6,repeat_and_interleaved_calls=True))
    small=cases[:100]+[t for t in cases if t['name'] in ['signed64-corners','uneven-groups'] or t['name'].startswith('random-')][:100]
    negative=encode(small);(out/'mutations.in').write_bytes(negative)
    mutations=[('strict-y','a[i].y <= a[j].y','a[i].y < a[j].y'),('strict-z','bit.sum(a[j].z)','bit.sum(a[j].z - 1)'),('unit-insert','bit.add(a[i].z, a[i].w)','bit.add(a[i].z, 1)'),('missing-self-exclusion','+ w[group[i]] - 1','+ w[group[i]]'),('no-rollback','bit.add(a[t].z, -a[t].w)','(void) a[t].z'),('sort-x-only','return p[i] < p[j];','return p[i][0] < p[j][0];'),('wrong-original-index','cnt[group[i]]','cnt[0]')]
    mutations += [('balanced-unit-weights','bit.add(a[i].z, a[i].w)','bit.add(a[i].z, 1)'),('wrong-scatter','ans[i] = cnt','ans[order[i]] = cnt')]
    for name,old,new in mutations:
        assert copied.count(old)==1,(name,copied.count(old))
        changed=copied.replace(old,new)
        if name=='balanced-unit-weights':
            assert changed.count('bit.add(a[t].z, -a[t].w)')==1
            changed=changed.replace('bit.add(a[t].z, -a[t].w)','bit.add(a[t].z, -1)')
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(changed);cmd=[CXX,*flags,'-DNDEBUG',str(cpp),'-o',str(exe)];subprocess.run(cmd,check=True,capture_output=True)
        run=subprocess.run([str(exe)],input=negative,capture_output=True,env=env,timeout=60);assert run.returncode==0 and not run.stderr,(name,run.stderr[-1000:])
        rejected=False
        try:check(run.stdout,small)
        except (AssertionError,ValueError,StopIteration):rejected=True
        assert rejected,name
        (out/(name+'.out')).write_bytes(run.stdout);report['mutants'].append(dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),output_sha256=sha(run.stdout),independent_checker_rejected=True))
    report.update(source_after_sha256=snapshot(ROOT),passed=True,scope='Static unweighted weak dominance; full signed64/empty API extensions; independent comparisons and closed forms, not online AC, weighted/strict/dynamic CDQ, full suite or LSan.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(f'Dominance3D {mode}: {len(cases)} cases x four forms PASS; {out.relative_to(ROOT)}/report.json')


if __name__=='__main__':main()
