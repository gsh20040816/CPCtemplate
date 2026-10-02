#!/usr/bin/env python3
"""Independent finite-state mathematics and actual recurrence-pipeline verification.

Fixtures and reports default to fresh build directories. One mode per invocation;
ASan/UBSan retains default PIE/quarantine, with only LSan disabled.
"""
from pathlib import Path
from itertools import permutations, product
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
SELF=Path(__file__).resolve()
sys.path.insert(0,str(ROOT/'tests'))
from compiler_config import CXX
sys.path.insert(0,str(ROOT/"tools"))
from usage_examples import expand

def mul(a,b,p=None):
    r=[[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
    return r if p is None else [[x%p for x in row] for row in r]
def characteristic(a):
    d=len(a); ans=[0]*(d+1)
    for perm in permutations(range(d)):
        poly=[(-1)**sum(perm[i]>perm[j] for i in range(d) for j in range(i+1,d))]
        for i,j in enumerate(perm):
            q=[0]*(len(poly)+1)
            for k,x in enumerate(poly):
                q[k]-=a[i][j]*x
                if i==j:q[k+1]+=x
            poly=q
        ans=[x+y for x,y in zip(ans,poly)]
    assert ans[-1]==1
    return ans

def ch_check(a,chi):
    d=len(a); r=[[0]*d for _ in range(d)]
    for c in reversed(chi):
        r=mul(r,a)
        for i in range(d):r[i][i]+=c
    assert all(x==0 for row in r for x in row)

def sequence(a,v,u,count):
    out=[]
    for _ in range(count):
        out.append(sum(x*y for x,y in zip(u,v)))
        v=[sum(x*y for x,y in zip(row,v)) for row in a]
    return out

def nth(a,v,u,n,p):
    a=[[x%p for x in row] for row in a]; v=[[x%p] for x in v]
    while n:
        if n&1:v=mul(a,v,p)
        a=mul(a,a,p); n>>=1
    return sum(x*y[0] for x,y in zip(u,v))%p

def walk_enum(a,s,t,n):
    # Enumerate vertex paths, independently of matrix-vector multiplication.
    if n==0:return int(s==t)
    paths=[(s,)]
    for _ in range(n):
        paths=[path+(j,) for path in paths for j in range(len(a)) if a[j][path[-1]]]
    return sum(path[-1]==t for path in paths)

def generate_cases(out):
    model=[[1,0,1],[1,1,0],[0,1,0]]
    strings=[sum('101' not in ''.join(bits) for bits in product('01',repeat=n)) for n in range(13)]
    assert strings==sequence(model,[1,0,0],[1,1,1],13)
    assert characteristic(model)==[-1,1,-2,1]
    cases=[]; graph_counts={}; enumerated_walks=0
    for d in range(1,4):
        graph_counts[d]=2**(d*d)
        for mask,bits in enumerate(product(range(2),repeat=d*d)):
            a=[list(bits[i*d:(i+1)*d]) for i in range(d)]
            chi=characteristic(a);ch_check(a,chi)
            for s in range(d):
                for t in range(d):
                    v=[int(i==s) for i in range(d)];u=[int(i==t) for i in range(d)]
                    seq=sequence(a,v,u,21)
                    for n in range(5):
                        assert seq[n]==walk_enum(a,s,t,n);enumerated_walks+=1
                    c=[-x for x in reversed(chi[:-1])]
                    for n in range(d,21):assert seq[n]==sum(c[j]*seq[n-j-1] for j in range(d))
                    cases.append((f"graph_d{d}_mask{mask}_s{s}_t{t}",a,v,u,seq,c))
    named={
      'avoid101':(model,[1,0,0],[1,1,1]),
      'nilpotent_impulse':([[0,0,0],[1,0,0],[0,1,0]],[1,0,0],[0,0,1]),
      'zero_output':(model,[1,0,0],[0,0,0]),
      'jordan':([[1,1,0],[0,1,1],[0,0,1]],[0,0,1],[1,0,0]),
      'unreachable':([[1,0,0],[0,2,0],[0,0,3]],[1,0,0],[1,1,1]),
      'scalar_order1':([[2,0,0],[0,2,0],[0,0,2]],[1,1,1],[1,0,0])}
    for name,(a,v,u) in named.items():
        chi=characteristic(a);ch_check(a,chi)
        cases.append((name,a,v,u,sequence(a,v,u,21),[-x for x in reversed(chi[:-1])]))
    primes=[2,3,5,998244353]; composites=[4,6,8,9,12,1000]
    queries=[21,64,10**18,2**64-1]
    with (out/'cases.txt').open('w') as f:
        f.write(str(len(cases)*(len(primes)+len(composites)))+'\n')
        for name,a,v,u,seq,c in cases:
            for p in primes+composites:
                row=[name,len(a),p,int(p in primes),*map(lambda x:x%p,c),*map(lambda x:x%p,seq)]
                row += [nth(a,v,u,n,p) for n in queries]
                f.write(' '.join(map(str,row))+'\n')
    path=sequence([[0,0],[1,0]],[1,0],[0,1],8)
    cycle=sequence([[0,1],[1,0]],[1,0],[0,1],8)
    assert path[:3]==cycle[:3]==[0,1,0] and (path[3],cycle[3])==(0,1)
    assert characteristic([[1,0],[0,2]])==[2,-3,1]
    assert sequence([[1,0],[0,2]],[1,0],[1,0],13)==[1]*13
    return dict(binary_strings_enumerated=8191, binary_string_counts_0_to_12=strings,
                graphs_by_dimension=graph_counts,total_graphs=sum(graph_counts.values()),
                graph_endpoint_cases=4674,direct_path_checks_lengths_0_to_4=enumerated_walks,
                matrix_cases_including_named=len(cases),modulus_cases=len(cases)*10,
                queries_per_case=25,prime_moduli=primes,known_recurrence_composite_moduli=composites,
                remote_queries=queries,documented_path=path,documented_cycle=cycle,
                scalar_witness="diag(1,2), first-coordinate projection; valid over F2",
                named_sequences={name:sequence(a,v,u,13) for name,(a,v,u) in named.items()})


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def options(prefix):
    if not __debug__:
        raise RuntimeError('Python -O is unsupported: assertions are required')
    parser=argparse.ArgumentParser(description=__doc__)
    default='sanitizer' if os.environ.get('SANITIZE')=='1' or os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    parser.add_argument('--mode',choices=['normal','sanitizer'],default=default)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    (ROOT/'build').mkdir(exist_ok=True)
    args.out=Path(tempfile.mkdtemp(prefix=prefix+'-',dir=ROOT/'build'))
    args.report=args.report.resolve() if args.report else args.out/'report.json'
    return args


def run_bound(args, prepare):
    """Bind source/compiler before any derivation; always retain a failure report."""
    started=time.monotonic()
    cpp=ROOT/'tests/state_recurrence_usage.cpp'
    dependencies=set()
    expand(cpp.read_text(),cpp.parent,dependencies)
    sources={SELF,ROOT/'tests/state_recurrence_snippet.py',cpp,
             ROOT/'docs/knowledge-state-recurrence.tex',ROOT/'tests/compiler_config.py',
             ROOT/'tools/usage_examples.py',*dependencies}
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    def snapshot():
        return {str(p.relative_to(ROOT)):file_sha(p) for p in sorted(sources)}
    before=snapshot();compiler_hash=file_sha(compiler)
    frontend_name=subprocess.check_output([str(compiler),'-print-prog-name=cc1plus'],text=True).strip()
    frontend=Path(shutil.which(frontend_name) or frontend_name).resolve()
    frontend_hash=file_sha(frontend)
    flags=['-std=c++20','-Wall','-Wextra','-Werror']+(['-O2'] if args.mode=='normal' else
          ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])
    env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
             UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    env.pop('LSAN_OPTIONS',None)
    report=dict(passed=False,mode=args.mode,started_at=datetime.now(timezone.utc).isoformat(),
                source_sha256_before=before,compiler=str(compiler),compiler_sha256_before=compiler_hash,
                compiler_version=subprocess.check_output([str(compiler),'--version'],text=True),
                compiler_frontend=str(frontend),compiler_frontend_sha256_before=frontend_hash,
                toolchain_scope='Resolved compiler driver and cc1plus only; not full toolchain',
                flags=flags,platform=platform.platform(),build_directory=str(args.out.relative_to(ROOT)),
                pie='compiler default; no override',quarantine='ASan default; no override',
                sanitizer_options={k:env[k] for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')},
                scope='Local mathematical and interface checks only; no OJ, CI, full-suite, or LSan claim')
    failure=None
    try:
        program,fixture,expected,evidence=prepare(args.out)
        report['evidence']=evidence
        generated=args.out/'program.cpp';generated.write_text(program)
        binary=args.out/'program'
        report['program_sha256']=file_sha(generated)
        report['fixture_sha256']=file_sha(fixture)
        command=[str(compiler),*flags,'-I',str(cpp.parent),str(generated),'-o',str(binary)]
        report['compile_command']=command
        compiled=subprocess.run(command,capture_output=True,text=True,timeout=180)
        report['compile']=dict(exit_code=compiled.returncode,stdout=compiled.stdout,stderr=compiled.stderr)
        assert compiled.returncode==0,'C++ compilation failed'
        report['binary_sha256']=file_sha(binary)
        with fixture.open() as data:
            ran=subprocess.run([str(binary)],stdin=data,text=True,capture_output=True,env=env,timeout=600)
        report['run']=dict(exit_code=ran.returncode,stdout=ran.stdout,stderr=ran.stderr,expected_stdout=expected)
        assert ran.returncode==0 and not ran.stderr and ran.stdout==expected,'C++ output differs or sanitizer failed'
        assert file_sha(generated)==report['program_sha256'],'Generated C++ changed'
        assert file_sha(binary)==report['binary_sha256'],'Executable changed'
        assert file_sha(fixture)==report['fixture_sha256'],'Fixture changed'
        report['passed']=True
    except BaseException as error:
        failure=error;report['error']=repr(error)
    finally:
        report['source_sha256_after']=snapshot()
        report['compiler_sha256_after']=file_sha(compiler)
        report['compiler_frontend_sha256_after']=file_sha(frontend)
        if (report['source_sha256_after']!=before or report['compiler_sha256_after']!=compiler_hash
                or report['compiler_frontend_sha256_after']!=frontend_hash):
            report['passed']=False
            failure=RuntimeError('Bound source/compiler changed during verification')
            report['error']=repr(failure)
        report['seconds']=round(time.monotonic()-started,6)
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2)+'\n')
    if failure:raise failure
    print(f"{args.mode}: PASS in {report['seconds']:.3f}s; report {args.report}")


def prepare_pipeline(out):
    evidence=generate_cases(out)
    expected='PASS cases=46800 recurrence_nth=1638000 BM-derived=468000 BostanMori=234000\n'
    return (ROOT/'tests/state_recurrence_usage.cpp').read_text(),out/'cases.txt',expected,evidence


def main():
    run_bound(options('state-recurrence'),prepare_pipeline)


if __name__=='__main__':
    main()
