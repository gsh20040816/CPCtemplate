#!/usr/bin/env python3
"""Full119-line source audit; Horner oracle is independent of both convolutions."""
import argparse,hashlib,itertools,json,os,random,subprocess,sys
from pathlib import Path
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from usage_examples import records
from audit_copy_context import candidate,extract_components
MOD=1000003


def evaluate(a,x):
    value=0
    for v in reversed(a):value=(value*x+v)%MOD
    return value


def oracle(case):
    a,b,c,d=case
    return [evaluate(a,(b*pow(c,2*k,MOD)+d)%MOD) for k in range(len(a))]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sanitize',action='store_true');args=ap.parse_args()
    mode='sanitizer' if args.sanitize else 'normal';out=ROOT/'build/shift-geometric'/mode;out.mkdir(parents=True,exist_ok=True)
    row=next(r for r in records() if r['id']=='example-347');sha=lambda b:hashlib.sha256(b).hexdigest()
    paths=['src/compact/convolution_mod.hpp','src/compact/ntt_convolution.hpp','src/compact/number_theory.hpp',row['driver'],'tests/shift_geometric.py','tests/fixtures/shift_geometric_sources/kuangbin.cpp','docs/catalog.json','docs/usage-examples.json','tools/usage_examples.py','tools/audit_copy_context.py']
    snapshot={p:sha((ROOT/p).read_bytes()) for p in paths}
    cases=[]
    for n in range(1,5):
        for a in itertools.product((0,1,MOD-1),repeat=n):
            for b,c,d in itertools.product((0,1,2),(0,1,2,MOD-1),(0,1,MOD-1)):
                case=(list(a),b,c,d);cases.append((case,oracle(case)))
    rng=random.Random(20261010)
    for _ in range(180):
        case=([rng.randrange(-2**31,2**31) for _ in range(rng.randrange(1,55))],*[rng.randrange(-2**31,2**31) for _ in range(3)])
        cases.append((case,oracle(case)))
    # n around powers of two, with sparse coefficients evaluated independently.
    for n in (65535,65536,65537,100000,100009,100010):
        a=[0]*n
        for i in (0,1,n//2,n-1):a[i]=rng.randrange(MOD)
        b,c,d=17,23,41
        want=[sum(a[i]*pow((b*pow(c,2*k,MOD)+d)%MOD,i,MOD) for i in (0,1,n//2,n-1))%MOD for k in range(n)]
        cases.append(((a,b,c,d),want))
    for c in (0,1,MOD-1):
        a=[rng.randrange(MOD) for _ in range(100010)];b,d=5,7
        first=evaluate(a,b+d);rest=evaluate(a,d) if c==0 else first
        cases.append(((a,b,c,d),[first]+[rest]*(len(a)-1)))
    source=[]
    for n in (1,2,3,7,31,50):
        for c in (1,2,MOD-1):
            case=([rng.randrange(MOD) for _ in range(n)],rng.randrange(MOD),c,rng.randrange(MOD))
            source.append((case,oracle(case)))
    source += [cases[-9],cases[-4],cases[-2],cases[-1]]
    # source[-4] and source[-3] are sparse maximum-sized boundary cases; c is nonzero.
    assert all(case[2]!=0 and 1<=len(case[0])<=100010 for case,_ in source)
    flags=['-std=c++20','-O1' if args.sanitize else '-O2']
    if args.sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
    env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1'}
    def compile(src,exe,extra=()):
        p=subprocess.run([CXX,*flags,*extra,str(src),'-o',str(exe)],text=True,capture_output=True);assert p.returncode==0,p.stderr
    def encode(batch):
        return ''.join(f'{len(a)} {b} {c} {d}\n'+' '.join(map(str,a))+'\n' for (a,b,c,d),_ in batch)
    def check(exe,batch):
        p=subprocess.run([str(exe)],input=encode(batch),text=True,capture_output=True,timeout=300,env=env)
        assert p.returncode==0,p.stderr
        got=list(map(int,p.stdout.split()));want=[v for _,answer in batch for v in answer]
        assert got==want,(exe,len(got),len(want),next(((i,x,y) for i,(x,y) in enumerate(zip(got,want)) if x!=y),None))
    original=(ROOT/'tests/fixtures/shift_geometric_sources/kuangbin.cpp').read_text()
    old='return (x*y - (long long)(x/(long double)z*y+1e-3)*z+z)%z;'
    assert original.count(old)==1
    fixed=original.replace(old,'return (__int128)x*y%z;')
    prefix='#include <bits/stdc++.h>\nusing namespace std;\nnamespace original {\n'
    suffix='\n}\nint main()\n{\n    return original::main();\n}\n'
    # Raw source must produce a signed-overflow diagnostic, not be called sanitizer-clean.
    raw=out/'raw.cpp';raw.write_text(prefix+original+suffix);exe=out/'raw';compile(raw,exe,['-fsanitize=undefined','-fno-sanitize-recover=all'])
    p=subprocess.run([str(exe)],input='1 1 1 0\n100\n',text=True,capture_output=True,timeout=90,env=env)
    assert p.returncode!=0 and 'signed integer overflow' in p.stderr,p.stderr
    raw_diagnostic=p.stderr
    src=out/'source-exact-mul.cpp';src.write_text(prefix+fixed+suffix);exe=out/'source-exact-mul';compile(src,exe);check(exe,source)
    print(mode,'source exact-mul',len(source),'PASS',flush=True)
    # c=0 is an explicitly added case: old source computes a different first point.
    zero_case=(([1,2],3,0,4),oracle(([1,2],3,0,4)))
    p=subprocess.run([str(exe)],input=encode([zero_case]),text=True,capture_output=True,timeout=90,env=env)
    assert p.returncode==0 and list(map(int,p.stdout.split()))!=zero_case[1]
    zero_source=list(map(int,p.stdout.split()))
    components={r['symbol']:r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    programs=[]
    for form in ('header','ndebug','expanded','copied'):
        exe=out/form;src=ROOT/row['driver']
        if form in ('expanded','copied'):
            src=exe.with_suffix('.cpp');src.write_text(row['program'] if form=='expanded' else candidate(row,row['requires'],components)['program'])
        compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
        check(exe,[]);check(exe,cases);check(exe,source)
        programs.append(dict(form=form,cases=len(cases),source_cases=len(source),source_sha256=sha(src.read_bytes())))
        print(mode,form,len(cases),'PASS',flush=True)
    mutants=[]
    if not args.sanitize:
        for name,old,new in [('wrong-shift-index','product[n - 1 - j]','product[j]'),('lost-factorial',' * inv[j] * power',' * power'),('wrong-output-index','product[n - 1 + k]','product[k]'),('linear-not-square-step','step = step * step2;','step = step;')]:
            assert old in row['program'];src=out/(name+'.cpp');src.write_text(row['program'].replace(old,new));exe=out/name;compile(src,exe)
            p=subprocess.run([str(exe)],input=encode(cases[:4320]),text=True,capture_output=True,timeout=90)
            assert p.returncode==0,(name,p.stderr)
            assert list(map(int,p.stdout.split()))!=[v for _,answer in cases[:4320] for v in answer],name
            mutants.append(dict(name=name,detected_by_wrong_output=True))
    assert all(sha((ROOT/p).read_bytes())==v for p,v in snapshot.items())
    report=dict(mode=mode,cases=len(cases),source_cases=len(source),programs=programs,mutants=mutants,snapshot=snapshot,usage=row['id'],program_sha256=row['program_sha256'],raw_source_signed_overflow=raw_diagnostic,source_exact_mul_sha256=sha(fixed.encode()),source_repair='Only line30 modular multiplication replaced by exact int128; original raw source fails signed-overflow sanitizer.',zero_extension=dict(case='n=2,b=3,c=0,d=4,a=[1,2]',source_output=zero_source,expected=zero_case[1]),scope='Complete119-line source protocol with disclosed mul repair;Horner oracle and sparse/dense max-size closed forms. Nonzero c source domain;zero and signed-int normalization are new extensions. Official HDU statement/resources and online verdict unverified.')
    (ROOT/f'verification/shift-geometric-{mode}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(mode,'PASS',flush=True)
if __name__=='__main__':main()
