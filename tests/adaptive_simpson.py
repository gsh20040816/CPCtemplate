#!/usr/bin/env python3
"""Analytic references, resource semantics and explicit estimator alias limits."""
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import mpmath as mp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from usage_examples import records
from compiler_config import CXX


def digest(b):
    return hashlib.sha256(b).hexdigest()


def main():
    if not __debug__:
        raise RuntimeError('Analytic checks require Python assertions')
    mp.mp.dps = 100
    before = snapshot(ROOT)
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='adaptive-simpson-'+mode+'-',dir=ROOT/'build'))
    cases=[]
    def add(name,kind=0,a='0',b='1',eps='1e-10',depth=20,limit=100000,c=(1,),met=True,count=None):
        cases.append(dict(name=name,kind=kind,a=str(a),b=str(b),eps=str(eps),depth=depth,limit=limit,c=list(c),met=met,count=count))
    rng=random.Random(20261003)
    for degree in range(6):
        for k in range(20):
            a=rng.randrange(-8,8)/4;b=a+rng.randrange(1,13)/4
            add(f'polynomial-{degree}-{k}',a=a,b=b,c=[rng.randrange(-5,6) for _ in range(degree+1)])
    for kind in range(1,5):
        for a,b in [(-3,2),(0,1),(1,0),(-1,1),(2,2),(-8,8)]:
            add(f'analytic-{kind}-{a}-{b}',kind,a,b)
    add('cancellation',a=-1,b=1,c=(1,10000000000),eps='1e-8')
    add('shifted-constant',a=1000000,b=1000001,c=(3,),count=5)
    add('narrow',a=0,b='1e-12',eps='1e-30',c=(0,0,0,0,1),count=5)
    add('root-quartic-accepted',eps='0.001',depth=0,limit=5,c=(0,0,0,0,1),count=5)
    add('root-quartic-depth-stop',eps='1e-6',depth=0,limit=5,c=(0,0,0,0,1),met=False,count=5)
    add('sampling-alias',kind=5,eps='1e-12',count=5)
    for limit in range(11):
        add(f'empty-budget-{limit}',a=2,b=2,limit=limit,count=0)
        add(f'quartic-budget-{limit}',eps='1e-20',limit=limit,c=(0,0,0,0,1),met=False,count=0 if limit<3 else limit-(limit%2==0))
    for depth in (0,1,2,3):
        add(f'depth-{depth}',eps='1e-30',depth=depth,c=(0,0,0,0,1),met=False,count=3+2*((1<<(depth+1))-1))
    for kind,count in [(6,3),(7,5),(8,3),(9,3),(10,3),(11,0),(12,0),(13,5)]:
        add(f'stop-{kind}',kind,a=1 if kind in (9,10) else 0,b=2 if kind in (9,10) else 1,c=(0,0,0,0,1) if kind==13 else (1,),met=False,count=count)
    for name,kw in [('eps-zero',dict(eps=0)),('negative-depth',dict(depth=-1)),('large-depth',dict(depth=61)),('negative-limit',dict(limit=-1))]:
        add(name,met=False,count=0,**kw)
    add('parent-sum-overflow',kind=14,a=0,b=16,depth=1,limit=9,met=False,count=9)
    add('rounded-subnormal-parent-budget',kind=15,a=0,b=12,depth=1,limit=9,met=False,count=9)
    # Repeated calls must not retain budget or samples from a prior invocation.
    add('repeat-rational',kind=1)
    data=str(len(cases))+'\n'
    for t in cases:
        data+=' '.join(map(str,[t['kind'],t['a'],t['b'],t['eps'],t['depth'],t['limit'],len(t['c'])-1,*t['c']]))+'\n'
    (out/'cases.in').write_text(data)
    (out/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
    # Exact polynomial expansion supplies a nonzero analytic alias certificate.
    p=[Fraction(1)]
    for i in range(5):
        q=[Fraction(0)]*(len(p)+1)
        for j,x in enumerate(p):q[j]-=x*Fraction(i,4);q[j+1]+=x
        p=q
    sq=[Fraction(0)]*(2*len(p)-1)
    for i,x in enumerate(p):
        for j,y in enumerate(p):sq[i+j]+=x*y
    alias=sum((v/Fraction(i+1) for i,v in enumerate(sq)),Fraction(0))
    assert alias>Fraction(1,10**12)
    component=next(x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text())) if x['symbol']=='AdaptiveSimpson')
    probe=(ROOT/'tests/adaptive_simpson_probe.cpp').read_text()
    minimal='#include <algorithm>\n#include <cmath>\n#include <iomanip>\n#include <iostream>\n#include <limits>\n#include <numeric>\n#include <set>\n#include <utility>\n#include <vector>\nusing namespace std;\n'
    copied=minimal+component+'\n'+'\n'.join(probe.splitlines()[1:])
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=digest(compiler.read_bytes()),flags=flags,input_sha256=digest(data.encode()),alias_integral=str(alias),reference='100-digit mpmath analytic antiderivatives; exact Fraction sampling-alias integral',environment={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')},programs=[],mutants=[])
    def check(output):
        lines=output.decode().splitlines();assert len(lines)==len(cases)
        max_error=mp.mpf(0)
        for t,line in zip(cases,lines):
            fields=line.split();assert len(fields)==9
            met=int(fields[0]);value,error=map(mp.mpf,fields[1:3]);evaluations,calls,unique=map(int,fields[3:6]);a,b,eps=map(mp.mpf,fields[6:])
            assert met in (0,1) and bool(met)==t['met'],(t,line)
            assert evaluations==calls and 0<=evaluations<=max(0,t['limit'])
            if t['count'] is not None:assert evaluations==t['count'],(t,line)
            if t['kind'] not in (9,10):assert unique==calls,(t,line)
            if met:
                assert mp.isfinite(value) and mp.isfinite(error) and 0<=error<=eps*(1+mp.mpf('1e-18'))
            if t['name']=='sampling-alias':
                assert value==error==0 and met==1
                continue
            if not met:
                if t['kind']==14:
                    assert value==0 and mp.isinf(error)
                if t['kind']==15:
                    assert abs(value/eps-mp.mpf(224)/3)<mp.mpf('1e-17')
                    assert abs(error/eps-mp.mpf(4)/3)<mp.mpf('1e-18') and error>eps
                if t['name'].startswith('quartic-budget-'):
                    assert mp.isinf(error)
                    if t['limit'] < 3:
                        assert mp.isnan(value)
                    else:
                        cuts={3:[0,1],5:[0,Fraction(1,2),1],
                              7:[0,Fraction(1,4),Fraction(1,2),1],
                              9:[0,Fraction(1,8),Fraction(1,4),Fraction(1,2),1]}
                        points=cuts[t['count']]
                        expected=sum((r-l)*(l**4+4*((l+r)/2)**4+r**4)/6
                                     for l,r in zip(map(Fraction,points),map(Fraction,points[1:])))
                        exact=mp.mpf(expected.numerator)/expected.denominator
                        assert abs(value-exact)<mp.mpf('1e-17'),(t,line,str(exact))
                if t['name']=='root-quartic-depth-stop':
                    assert abs(value-mp.mpf(1)/5)<mp.mpf('1e-17')
                    assert abs(error-mp.mpf(1)/1920)<mp.mpf('1e-18')
                continue
            kind=t['kind']
            if kind==1:expected=mp.atan(b)-mp.atan(a)
            elif kind==2:expected=mp.exp(b)-mp.exp(a)
            elif kind==3:expected=mp.cos(a)-mp.cos(b)
            elif kind==4:expected=mp.sqrt(mp.pi)/2*(mp.erf(b)-mp.erf(a))
            else:expected=sum(mp.mpf(v)*(b**(i+1)-a**(i+1))/(i+1) for i,v in enumerate(t['c']))
            diff=abs(value-expected);max_error=max(max_error,diff)
            assert diff<=8*eps+mp.mpf('5e-15')*(1+abs(expected)),(t,line,str(expected),str(diff))
        return str(max_error)
    for form,text in [('header','#include "'+str(ROOT/'tests/adaptive_simpson_probe.cpp')+'"\n'),('copied',copied)]:
        for ndebug in (False,True):
            name=form+('-ndebug' if ndebug else '-assert');cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(text)
            subprocess.run([CXX,*flags,*(['-DNDEBUG'] if ndebug else []),str(cpp),'-o',str(exe)],check=True,capture_output=True)
            run=subprocess.run([str(exe)],input=data.encode(),capture_output=True,env=env,timeout=90)
            assert run.returncode==0 and not run.stderr,(name,run.stderr)
            max_error=check(run.stdout);(out/(name+'.out')).write_bytes(run.stdout)
            thrown=subprocess.run([str(exe),'throw'],capture_output=True,env=env,timeout=10);assert thrown.returncode==0 and thrown.stdout==b'7\n' and not thrown.stderr
            report['programs'].append(dict(name=name,source_sha256=digest(cpp.read_bytes()),binary_sha256=digest(exe.read_bytes()),output_sha256=digest(run.stdout),cases=len(cases),maximum_analytic_absolute_error=max_error,exception_propagation=True))
    # Deliberately broken implementations must fail the same actual-output oracle.
    mutations=[('wrong-correction','sum + delta / 15','sum - delta / 15'),('ignore-depth','if (!left || tol / 2 == 0)','if (tol / 2 == 0)'),('unbounded-budget','used > limit - 2','false'),('wrong-reversal','if (reverse) answer.value = -answer.value;','if (reverse) answer.value = answer.value;'),('rounded-parent-budget','p.met && q.met && error <= tol','p.met && q.met')]
    for name,old,new in mutations:
        assert copied.count(old)==1
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(copied.replace(old,new))
        subprocess.run([CXX,*flags,str(cpp),'-o',str(exe)],check=True,capture_output=True)
        run=subprocess.run([str(exe)],input=data.encode(),capture_output=True,env=env,timeout=90)
        assert run.returncode==0 and not run.stderr
        try:check(run.stdout)
        except AssertionError:pass
        else:raise AssertionError('Surviving mutant: '+name)
        (out/(name+'.out')).write_bytes(run.stdout)
        report['mutants'].append(dict(name=name,source_sha256=digest(cpp.read_bytes()),binary_sha256=digest(exe.read_bytes()),output_sha256=digest(run.stdout),rejected=True))
    row=next(r for r in records() if r['id']=='example-235')
    uses=[('direct','#include "'+str(ROOT/row['driver'])+'"\n'),
          ('expanded',row['program']),('copied',minimal+component+'\n'+row['snippet'])]
    inputs=[('0 1 1e-10 20 100000\n',True),('1 0 1e-10 20 100000\n',True),
            ('2 2 1e-10 0 0\n',True),('0 1 1e-15 0 3\n',False),
            ('-100 100 1e-8 30 200000\n',True)]
    for _ in range(20):
        a,b=[rng.randrange(-1000,1001)/10 for _ in range(2)]
        inputs.append((f'{a} {b} 1e-9 30 200000\n',True))
    report['uses']=[]
    for form,text in uses:
        cpp,exe=out/('usage-'+form+'.cpp'),out/('usage-'+form);cpp.write_text(text)
        subprocess.run([CXX,*flags,str(cpp),'-o',str(exe)],check=True,capture_output=True)
        entry=dict(form=form,source_sha256=digest(cpp.read_bytes()),binary_sha256=digest(exe.read_bytes()),cases=[])
        for i,(inp,success) in enumerate(inputs):
            run=subprocess.run([str(exe)],input=inp.encode(),capture_output=True,env=env,timeout=30)
            assert run.returncode==0 and not run.stderr
            if success:
                a,b,eps=map(mp.mpf,inp.split()[:3]);expected=mp.atan(b)-mp.atan(a)
                assert abs(mp.mpf(run.stdout.decode())-expected)<=8*eps+mp.mpf('1e-15')
            else:assert run.stdout==b'FAILED\n'
            (out/f'usage-{form}-{i}.in').write_text(inp)
            (out/f'usage-{form}-{i}.out').write_bytes(run.stdout)
            entry['cases'].append(dict(input_sha256=digest(inp.encode()),output_sha256=digest(run.stdout),success=success))
        for inp in (b'',b'101 0 1e-5 20 100\n',b'0 1 0 20 100\n',b'0 1 1e-5 61 100\n',b'0 1 1e-5 20 200001\n'):
            run=subprocess.run([str(exe)],input=inp,capture_output=True,env=env,timeout=10)
            assert run.returncode==1 and not run.stdout and not run.stderr
        entry['invalid_cases']=5
        report['uses'].append(entry)
    report.update(source_after_sha256=snapshot(ROOT),passed=True,scope='Bounded local analytic and resource-contract checks; explicit smooth alias demonstrates non-certification. No universal accuracy, full-suite, OJ or LSan claim.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Adaptive Simpson {mode}: {len(cases)} cases x four core forms PASS; {out.relative_to(ROOT)}/report.json')


if __name__=='__main__':main()
