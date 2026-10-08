#!/usr/bin/env python3
"""Exact CRT convolution against direct signed products, not another transform."""
import argparse,hashlib,json,os,random,subprocess,sys
from pathlib import Path
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from usage_examples import records
from audit_copy_context import candidate,extract_components

def oracle(a,b,mod):
    if not a or not b:return []
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]=(c[i+j]+x*y)%mod
    return c

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sanitize',action='store_true');args=ap.parse_args()
    mode='sanitizer' if args.sanitize else 'normal';out=ROOT/'build/convolution-mod'/mode;out.mkdir(parents=True,exist_ok=True)
    sha=lambda b:hashlib.sha256(b).hexdigest()
    rows=[r for r in records() if r['symbol']=='convolution_mod']
    paths=['src/compact/convolution_mod.hpp','src/compact/ntt_convolution.hpp','src/compact/number_theory.hpp','tests/convolution_mod.cpp','tests/convolution_mod.py','docs/catalog.json','docs/usage-examples.json','tools/usage_examples.py','tools/audit_copy_context.py']+[r['driver'] for r in rows]
    snapshot={p:sha((ROOT/p).read_bytes()) for p in paths}
    flags=['-std=c++20','-O1' if args.sanitize else '-O2']
    if args.sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
    env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1'}
    def compile(src,exe,extra=()):
        p=subprocess.run([CXX,*flags,*extra,str(src),'-o',str(exe)],text=True,capture_output=True);assert p.returncode==0,p.stderr
    def run(exe,data='',timeout=240):
        p=subprocess.run([str(exe)],input=data,text=True,capture_output=True,timeout=timeout,env=env)
        assert p.returncode==0,p.stderr
        return p.stdout
    components={r['symbol']:r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    copied=candidate(rows[0],rows[0]['requires'],components)['program'].split('int main()')[0]
    probe=(ROOT/'tests/convolution_mod.cpp').read_text();core=[]
    for form in ('header','ndebug','copied'):
        exe=out/('core-'+form);src=ROOT/'tests/convolution_mod.cpp'
        if form=='copied':
            src=exe.with_suffix('.cpp');src.write_text(probe.replace('#include "../src/compact/convolution_mod.hpp"',copied))
        compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
        count=int(run(exe));assert count==20103,count
        core.append(dict(form=form,cases=count,source_sha256=sha(src.read_bytes())))
        print(mode,form,count,'PASS',flush=True)
    rng=random.Random(20261008)
    formal=[]
    for _ in range(80):
        a=[rng.randrange(10**9+1) for _ in range(rng.randrange(2,35))];b=[rng.randrange(10**9+1) for _ in range(rng.randrange(2,35))];mod=rng.choice([2,6,1000003,998244353,1000000009])
        formal.append((a,b,mod,oracle(a,b,mod)))
    for mod in [6,1000000009]:
        n=100001;a=[10**9]*n;b=a[:];factor=(10**18)%mod
        formal.append((a,b,mod,[min(k+1,2*n-1-k,n)*factor%mod for k in range(2*n-1)]))
    api=[]
    for _ in range(160):
        a=[rng.randrange(-2**31,2**31) for _ in range(rng.randrange(30))];b=[rng.randrange(-2**31,2**31) for _ in range(rng.randrange(30))];mod=rng.choice([1,2,4,167772161,469762049,1224736769,2**31-1]);api.append((a,b,mod,oracle(a,b,mod)))
    api += [([],[],1,[]),([-2**31],[2**31-1],2**31-1,[0]),([-1]*20,[-1]*20,2**31-1,[min(k+1,39-k,20) for k in range(39)])]
    programs=[]
    for row in rows:
        cases=formal if row['id']=='example-345' else api
        def data(case):
            a,b,mod,_=case;delta=1 if row['id']=='example-345' else 0
            return f'{len(a)-delta} {len(b)-delta} {mod}\n'+' '.join(map(str,a))+'\n'+' '.join(map(str,b))+'\n'
        for form in ('header','ndebug','expanded','copied'):
            exe=out/(row['id']+'-'+form);src=ROOT/row['driver']
            if form in ('expanded','copied'):
                src=exe.with_suffix('.cpp');src.write_text(row['program'] if form=='expanded' else candidate(row,row['requires'],components)['program'])
            compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
            if row['id']=='example-345':
                for case in cases:assert list(map(int,run(exe,data(case)).split()))==case[3]
            else:
                got=run(exe,''.join(map(data,cases))).splitlines();assert len(got)==len(cases)
                assert [list(map(int,line.split())) for line in got]==[c[3] for c in cases]
            programs.append(dict(id=row['id'],form=form,cases=len(cases),program_sha256=row['program_sha256'],source_sha256=sha(src.read_bytes())))
            print(mode,row['id'],form,'PASS',flush=True)
    mutants=[]
    if not args.sanitize:
        core_text=probe.replace('#include "../src/compact/convolution_mod.hpp"',copied)
        for name,old,new in [('signed-representative','x[i] = value % mod;','if (value > (__int128)pq * r / 2) value -= (__int128)pq * r;\n        x[i] = value % mod;'),('two-primes-only','v + (__int128)pq * u','v'),('wrong-crt-inverse','ModInt<r>(pq).inv().v','ModInt<r>(p).inv().v'),('negative-shift','v += mod;','v += mod - 1;')]:
            assert old in core_text
            src=out/(name+'.cpp');src.write_text(core_text.replace(old,new));exe=out/name;compile(src,exe)
            p=subprocess.run([str(exe)],text=True,capture_output=True,timeout=240)
            # The mathematical coefficient bound prevents ever selecting a centered representative.
            if name=='signed-representative':
                assert p.returncode==0,p.stderr
                mutants.append(dict(name=name,detected=False,reason='Equivalent within proven int-modulus and length domain: all coefficients below half CRT product.'))
            else:
                assert p.returncode==1 and 'wrong convolution' in p.stderr,(name,p.returncode,p.stderr)
                mutants.append(dict(name=name,detected=True))
    assert all(sha((ROOT/p).read_bytes())==v for p,v in snapshot.items())
    report=dict(mode=mode,core=core,programs=programs,mutants=mutants,snapshot=snapshot,scope='Direct signed-product modular oracle, exhaustive small arrays,full signed-int extremes,prime/composite/1 targets;closed form stress across powers of two and formal P4245 maximal degrees. Algebraic2^24 capacity bound, not a maximal-memory benchmark;no online AC.')
    (ROOT/f'verification/convolution-mod-{mode}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
