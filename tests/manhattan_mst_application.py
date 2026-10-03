#!/usr/bin/env python3
"""Full LC-format programs; optional pinned generators/checker, never online AC."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import time

from manhattan_mst import prim, tree_check
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot
from usage_examples import records
from audit_copy_context import extract_components


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse_input(data):
    values=list(map(int,data.split()));n=values[0]
    assert 1<=n<=200000 and len(values)==1+2*n
    points=list(zip(values[1::2],values[2::2]))
    assert all(0<=x<=1000000000 and 0<=y<=1000000000 for x,y in points)
    return points


def parse_output(data,points,expected):
    values=list(map(int,data.split()));n=len(points)
    assert len(values)==1+2*(n-1)
    tree_check(points,list(zip(values[1::2],values[2::2])),values[0],expected)


def main():
    if not __debug__:raise RuntimeError('Certificate checks require assertions')
    ap=argparse.ArgumentParser();ap.add_argument('--upstream-checkout',type=Path);args=ap.parse_args()
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='manhattan-application-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT);cases=[];rng=random.Random(20261003)
    def add(name,points,expected=None,source='local independent generation'):
        points=list(points)
        if expected is None:expected=prim(points)
        data=(str(len(points))+'\n'+''.join(f'{x} {y}\n' for x,y in points)).encode()
        parse_input(data);path=out/(name+'.in');path.write_bytes(data)
        cases.append(dict(name=name,path=path,expected=expected,source=source))
    sample=(ROOT/'tests/fixtures/manhattan-mst/sample.in').read_bytes();add('official-sample',parse_input(sample),source='pinned upstream sample bytes')
    add('single',[(1000000000,1000000000)])
    add('closed-boundary',[(0,0),(2,0),(1,1)])
    add('same-sum',[(i,20-i) for i in range(21)])
    for k in range(60):
        n=rng.randrange(1,41);points=[(rng.randrange(31),rng.randrange(31)) for _ in range(n)]
        add(f'random-small-{k}',points)
    n=200000
    add('max-horizontal',((i,0) for i in range(n)),n-1)
    add('max-antidiagonal',((i,1000000000-i) for i in range(n)),2*(n-1))
    add('max-identical',[(1000000000,1000000000)]*n,0)
    add('max-unit-grid',((i%400,i//400) for i in range(n)),n-1)
    add('max-two-clusters',[(0,0)]*(n//2)+[(1000000000,1000000000)]*(n//2),2000000000)
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),cases=[],programs=[])
    verifier=checker=reference=None;up_hash={}
    if args.upstream_checkout:
        up=args.upstream_checkout.resolve();commit='e64660561a995c357cdc61ddee1bde68b80528db'
        assert subprocess.check_output(['git','-C',str(up),'rev-parse','HEAD'],text=True).strip()==commit
        assert not subprocess.check_output(['git','-C',str(up),'status','--porcelain'],text=True).strip()
        task=up/'geo/manhattanmst'
        assert sample==(task/'gen/example_00.in').read_bytes(), 'pinned sample differs'
        files=list(task.rglob('*'))+list((up/'common').rglob('*'))
        up_hash={str(p):sha(p.read_bytes()) for p in files if p.is_file()}
        def compile_ref(path,name):
            exe=out/name;subprocess.run([CXX,'-std=c++20','-O2','-I'+str(up/'common'),str(path),'-o',str(exe)],check=True,capture_output=True);return exe
        verifier=compile_ref(task/'verifier.cpp','official-verifier')
        checker=compile_ref(task/'checker.cpp','official-checker')
        reference=compile_ref(task/'sol/correct.cpp','official-fenwick-reference')
        for family in ['small','random','max_random','many_cluster','enclosed']:
            exe=compile_ref(task/'gen'/f'{family}.cpp','generator-'+family)
            for seed in range(3):
                name=f'upstream-{family}-{seed}';path=out/(name+'.in')
                run=subprocess.run([str(exe),str(seed)],capture_output=True,timeout=30,check=True);assert not run.stderr;path.write_bytes(run.stdout)
                points=parse_input(run.stdout)
                answer=subprocess.run([str(reference)],input=run.stdout,capture_output=True,timeout=30,check=True);assert not answer.stderr
                expected=int(answer.stdout.split()[0]);parse_output(answer.stdout,points,expected)
                if len(points)<=50:assert expected==prim(points)
                (out/(name+'.reference.out')).write_bytes(answer.stdout)
                cases.append(dict(name=name,path=path,expected=expected,source=f'locked official {family}.cpp; explicit local seed{seed}, not canonical judge data'))
        report['upstream']=dict(commit=commit,source_sha256=up_hash,local_seeds=[0,1,2],reference_sanitized=False,binaries={p.name:sha(p.read_bytes()) for p in [verifier,checker,reference,*out.glob('generator-*')]})
    for t in cases:
        data=t['path'].read_bytes();points=parse_input(data)
        if verifier:
            valid=subprocess.run([str(verifier)],input=data,capture_output=True,timeout=30);assert valid.returncode==0,(t['name'],valid.stderr)
            answer=out/(t['name']+'.reference.out')
            if not answer.exists():
                ref=subprocess.run([str(reference)],input=data,capture_output=True,timeout=30,check=True);assert not ref.stderr;parse_output(ref.stdout,points,t['expected']);answer.write_bytes(ref.stdout)
        entry=dict(name=t['name'],n=len(points),input_sha256=sha(data),expected=str(t['expected']),source=t['source'])
        if reference:
            entry['reference_output_sha256']=sha((out/(t['name']+'.reference.out')).read_bytes())
            entry['official_verifier_returncode']=0
        report['cases'].append(entry)
    row=next(r for r in records() if r['id']=='example-236')
    components={x['symbol']:x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    copied='#include <algorithm>\n#include <cassert>\n#include <climits>\n#include <iostream>\n#include <map>\n#include <numeric>\n#include <tuple>\n#include <utility>\n#include <vector>\nusing namespace std;\n'+components['dsu']+'\n'+components['ManhattanMST']+'\n'+row['snippet']
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    report['flags']=flags;report['environment']={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')}
    for form,text in [('direct','#include "'+str(ROOT/row['driver'])+'"\n'),('expanded',row['program']),('copied',copied)]:
        cpp,exe=out/(form+'.cpp'),out/form;cpp.write_text(text)
        subprocess.run([CXX,*flags,str(cpp),'-o',str(exe)],check=True,capture_output=True)
        entry=dict(form=form,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),runs=[])
        for t in cases:
            data=t['path'].read_bytes();start=time.monotonic();run=subprocess.run([str(exe)],input=data,capture_output=True,env=env,timeout=90);seconds=time.monotonic()-start
            assert run.returncode==0 and not run.stderr,(form,t['name'],run.returncode,run.stderr[-1000:])
            parse_output(run.stdout,parse_input(data),t['expected'])
            output=out/(form+'-'+t['name']+'.out');output.write_bytes(run.stdout)
            check_record={}
            if checker:
                checked=subprocess.run([str(checker),str(t['path']),str(output),str(out/(t['name']+'.reference.out'))],capture_output=True,timeout=30)
                assert checked.returncode==0,(form,t['name'],checked.stderr)
                check_bytes=checked.stdout+checked.stderr
                (out/(form+'-'+t['name']+'.checker.txt')).write_bytes(check_bytes)
                check_record=dict(checker_returncode=checked.returncode,checker_output_sha256=sha(check_bytes))
            entry['runs'].append(dict(case=t['name'],returncode=run.returncode,output_sha256=sha(run.stdout),wall_seconds=seconds,official_checker_used=bool(checker),**check_record))
        report['programs'].append(entry)
    if up_hash:assert all(sha(Path(p).read_bytes())==h for p,h in up_hash.items())
    report.update(source_after_sha256=snapshot(ROOT),passed=True,scope='Full local programs and tree certificates. Optional upstream generators use explicit local seeds and an ordinary official Fenwick reference/checker; not online AC, judge ranking, canonical hidden data or LSan certification.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Manhattan application {mode}: {len(cases)} inputs x three forms PASS; {out.relative_to(ROOT)}/report.json')


if __name__=='__main__':main()
