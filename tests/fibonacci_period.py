#!/usr/bin/env python3
"""Independent sequential and matrix oracles, exact minimality certificates, copy forms."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from usage_examples import records
from audit_copy_context import extract_components,candidate

def stepping(m):
    a,b=0,1 % m
    for k in range(1,6*m+1):
        a,b=b,(a+b)%m
        if (a,b)==(0,1 % m):
            return k
    raise AssertionError(m)

def matrix(k,m):
    def mul(a,b):
        return tuple(sum(a[2*i+t]*b[2*t+j] for t in range(2))%m for i in range(2) for j in range(2))
    a=(1,1,1,0)
    r=(1,0,0,1)
    while k:
        if k&1:
            r=mul(r,a)
        a=mul(a,a)
        k//=2
    return r[1]%m,r[0]%m

def factors(numbers):
    executable=shutil.which('gfactor') or shutil.which('factor')
    assert executable,'GNU factor required for independent period certificates'
    p=subprocess.run([executable],input='\n'.join(map(str,numbers))+'\n',text=True,capture_output=True,check=True,timeout=180)
    result={}
    for line in p.stdout.splitlines():
        n,tail=line.split(':')
        fs=list(map(int,tail.split()))
        assert math.prod(fs)==int(n)
        # These period factors are at most 64 bit; trial division suffices for
        # small factors, deterministic Miller-Rabin verifies larger GNU results.
        for q in fs:
            assert is_prime(q)
        result[int(n)]=set(fs)
    assert set(result)==set(numbers)
    return result

def is_prime(n):
    if n<2:
        return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n%p==0:
            return n==p
    d=n-1
    s=0
    while d%2==0:
        d//=2
        s+=1
    assert n<2**64
    for a in (2,325,9375,28178,450775,9780504,1795265022):
        if a%n==0:
            continue
        x=pow(a,d,n)
        if x in (1,n-1):
            continue
        for _ in range(s-1):
            x=x*x%n
            if x==n-1:
                break
        else:
            return False
    return True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--sanitize',action='store_true')
    args=parser.parse_args()
    mode='sanitizer' if args.sanitize else 'normal'
    out=ROOT/'build/fibonacci-period'/mode
    out.mkdir(parents=True,exist_ok=True)
    sha=lambda data:hashlib.sha256(data).hexdigest()
    paths=[str(p.relative_to(ROOT)) for base in ('src/compact','tests/fixtures/fibonacci_period_sources') for p in (ROOT/base).glob('*') if p.is_file()]
    paths+=['tests/fibonacci_period.py','docs/catalog.json','docs/template-dependencies.json','docs/usage-examples.json','tools/usage_examples.py','tools/audit_copy_context.py']
    rows=[r for r in records() if r['symbol']=='FibonacciPeriod']
    paths += [r['driver'] for r in rows]
    snapshot={p:sha((ROOT/p).read_bytes()) for p in paths}
    flags=['-std=c++20','-O1' if args.sanitize else '-O2']
    if args.sanitize:
        flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
    env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'}
    def compile_program(source,exe,extra=()):
        proc=subprocess.run([CXX,*flags,*extra,str(source),'-o',str(exe)],text=True,capture_output=True)
        assert proc.returncode==0,proc.stderr
    def run(exe,data):
        proc=subprocess.run([str(exe)],input=data,text=True,capture_output=True,timeout=180,env=env)
        assert proc.returncode==0,proc.stderr
        return proc.stdout
    primes=[p for p in range(2,46341) if is_prime(p)]
    powers=[]
    for p in primes:
        q=p*p
        while q<=2**31-1:
            powers.append(q)
            q*=p
    small=list(range(1,5001))
    rng=random.Random(20261008)
    source_moduli=sorted(set(small+powers+[2**31-1,2**31-2,10**9+7,10**9+9]+[rng.randrange(1,2**31) for _ in range(150)]))
    bounds=[2**64-1,2**64-59,2**63-1,2**63+1,2*5**27,4294967291*4294967279]
    bounds += [2**i for i in range(1,64)]+[5**i for i in range(1,28)]
    moduli=sorted(set(source_moduli+bounds+[rng.randrange(1,2**64) for _ in range(100)]))
    data=str(len(moduli))+'\n'+'\n'.join(map(str,moduli))+'\n'
    baseline=out/'baseline'
    compile_program(ROOT/'verify/api/fibonacci_period.compact.cpp',baseline)
    answers=list(map(int,run(baseline,data).split()))
    assert len(answers)==len(moduli)
    expected=dict(zip(moduli,answers))
    factor_map=factors(sorted(set(answers)))
    for m,t in expected.items():
        assert 1<=t<=6*m and matrix(t,m)==(0,1%m),(m,t)
        assert all(matrix(t//q,m)!=(0,1%m) for q in factor_map[t]),(m,t)
    for m in small:
        assert expected[m]==stepping(m),(m,expected[m])
    for i in range(1,64):
        assert expected[2**i]==3*2**(i-1)
    for i in range(1,28):
        assert expected[5**i]==4*5**i
    assert expected[2*5**27]==89406967163085937500
    # Arbitrary 128-bit indices and residues independently checked by matrices.
    fib_cases=[(rng.getrandbits(128),rng.randrange(1,2**64)) for _ in range(1000)]
    fib_cases += [(k,m) for k in (0,1,2,2**127,2**128-1) for m in (1,2,5,2**64-1,2**64-59)]
    components={r['symbol']:r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    prelude='#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'+'\n'.join(components[s]['code'] for s in rows[0]['requires'])
    harness='''
int main()
{
    unsigned long long high, low, m;
    while (cin >> high >> low >> m)
    {
        auto k = (__uint128_t(high) << 64) | low;
        auto [a, b] = FibonacciPeriod::fib(k, m);
        cout << a << ' ' << b << '\\n';
    }
}
'''
    fibdata=''.join(f'{k>>64} {k%(2**64)} {m}\n' for k,m in fib_cases)
    fibexpected=[matrix(k,m) for k,m in fib_cases]
    for suffix,extra in (('',[]),('-ndebug',['-DNDEBUG'])):
        src=out/('fib'+suffix+'.cpp');src.write_text(prelude+harness)
        exe=src.with_suffix('');compile_program(src,exe,extra)
        assert [tuple(map(int,line.split())) for line in run(exe,fibdata).splitlines()]==fibexpected
    # Preserve the actual malformed source: headers alone must not repair it.
    raw=ROOT/'tests/fixtures/fibonacci_period_sources/kuangbin.raw.cpp'
    p=subprocess.run([CXX,'-std=c++20','-include','bits/stdc++.h','-fsyntax-only',str(raw)],capture_output=True,text=True)
    assert p.returncode!=0
    (out/'raw-source-compile.log').write_text(p.stderr)
    src=ROOT/'tests/fixtures/fibonacci_period_sources/kuangbin.compat.cpp'
    exe=out/'kuangbin';compile_program(src,exe)
    source_data=str(len(source_moduli))+'\n'+'\n'.join(map(str,source_moduli))+'\n'
    source_output=''.join(f'Case #{i}: {expected[m]}\n' for i,m in enumerate(source_moduli,1))
    assert run(exe,source_data)==source_output
    formal_moduli=[2,3,5,10,706150]+[rng.randrange(2,706151) for _ in range(35)]
    formal=[(str(m)+'\n',str(stepping(m))+'\n') for m in formal_moduli]
    programs=[]
    for row in rows:
        for form in ('header','ndebug','expanded','copied'):
            exe=out/(row['id']+'-'+form)
            source=ROOT/row['driver']
            program=row['program'] if form=='expanded' else candidate(row,row['requires'],components)['program']
            if form in ('expanded','copied'):
                source=exe.with_suffix('.cpp');source.write_text(program)
            compile_program(source,exe,['-DNDEBUG'] if form=='ndebug' else [])
            cases=formal if row['id']=='example-335' else [(data,''.join(str(t)+'\n' for t in answers))] if row['id']=='example-336' else [(source_data,source_output)]
            for inp,want in cases:
                assert run(exe,inp)==want,(row['id'],form)
            programs.append(dict(id=row['id'],form=form,cases=len(formal) if row['id']=='example-335' else len(moduli) if row['id']=='example-336' else len(source_moduli),program_sha256=row['program_sha256'] if form=='expanded' else sha(source.read_bytes())))
    mutants=[]
    if not args.sanitize:
        alterations=[('unminimized','while (t % q == 0 && is_period(t / q, p))','while (false)'),('single-zero','fib(k, m) == make_pair(0ULL, 1 % m)','fib(k, m).first == 0'),('truncated','return answer;','return ull(answer);')]
        driver=candidate(rows[1],rows[1]['requires'],components)['program']
        for name,before,after in alterations:
            assert before in driver
            source=out/(name+'.cpp');source.write_text(driver.replace(before,after))
            exe=source.with_suffix('');compile_program(source,exe)
            assert run(exe,data)!=''.join(str(t)+'\n' for t in answers),name
            mutants.append(name)
        source=out/'overflow.cpp'
        old='u128(Mod64::mul(a, a, m)) + Mod64::mul(b, b, m)'
        assert old in prelude
        source.write_text(prelude.replace(old,'u128(a) * a + u128(b) * b')+harness)
        exe=source.with_suffix('');compile_program(source,exe)
        assert [tuple(map(int,line.split())) for line in run(exe,fibdata).splitlines()]!=fibexpected
        mutants.append('unreduced-129-bit-sum')
    assert all(sha((ROOT/p).read_bytes())==h for p,h in snapshot.items())
    report=dict(mode=mode,moduli=len(moduli),small_bruteforce=len(small),prime_powers_in_source_int_range=len(powers),source_cases=len(source_moduli),fib_cases=len(fib_cases),programs=programs,mutants=mutants,snapshot=snapshot,certificates='Positive period and failure after division by every prime divisor; arbitrary-precision 2x2 matrices and GNU factor.',online_ac=False)
    (ROOT/f'verification/fibonacci-period-{mode}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('snapshot','programs')},ensure_ascii=False),flush=True)
if __name__=='__main__':
    main()
