"""Numerical Gauss: exact small rational oracle and explicit threshold models."""
import argparse, hashlib, json, os, random, resource, subprocess, sys, tempfile, time
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
if not __debug__:
    raise RuntimeError('Run without Python optimization')
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from audit_copy_context import extract_components
from usage_examples import records
from run_provenance import snapshot


def exact(a, n):
    a = [[F(x) for x in v] for v in a]; row = 0; where = [-1]*n
    # Exact arithmetic, no tolerance, scaling, maximum-magnitude selection or truncation.
    for col in range(n):
        p = next((i for i in range(row,len(a)) if a[i][col]),None)
        if p is None: continue
        a[p],a[row] = a[row],a[p]; d = a[row][col]
        a[row] = [x/d for x in a[row]]
        for i in range(len(a)):
            if i != row:
                f = a[i][col]; a[i] = [x-f*y for x,y in zip(a[i],a[row])]
        where[col] = row; row += 1
    if any(all(x == 0 for x in v[:n]) and v[n] for v in a): return False,row,[],[]
    x = [a[where[j]][n] if where[j] >= 0 else F(0) for j in range(n)]; kernel=[]
    for j in range(n):
        if where[j] < 0:
            v=[F(0)]*n;v[j]=1
            for k in range(n):
                if where[k]>=0:v[k]=-a[where[k]][j]
            kernel.append(v)
    return True,row,x,kernel


def dec(x):
    x=F(x)
    return Decimal(x.numerator)/Decimal(x.denominator)


def spelling(x):
    with localcontext() as ctx:
        ctx.prec=500
        return format(dec(x),'f')


def make_cases():
    rng=random.Random(234);cases=[]
    def add(name,a,n,eps=F(1,10**12),expected=None,threshold=False):
        cases.append(dict(name=name,a=a,n=n,eps=eps,expected=exact(a,n) if expected is None else expected,threshold=threshold))
    for m,n in [(0,0),(0,3),(3,0),(1,4),(4,1)]: add('empty-shape',[[0]*(n+1) for _ in range(m)],n)
    add('row-swap',[[0,1,2],[1,0,3]],2)
    add('expectation',[[F(1,2),F(-1,2),1],[F(-1,2),1,1]],2)
    add('underdetermined',[[1,2,3]],2)
    add('contradiction',[[1,1],[1,2]],1)
    for trial in range(200):
        m,n=rng.randrange(1,8),rng.randrange(1,8)
        add('small-integer',[[rng.randrange(-4,5) for _ in range(n+1)] for _ in range(m)],n)
    for trial in range(160):
        m,n=rng.randrange(1,8),rng.randrange(1,8);r=rng.randrange(min(m,n)+1)
        u=[[rng.randrange(-3,4) for _ in range(r)] for _ in range(m)]
        v=[[rng.randrange(-3,4) for _ in range(n)] for _ in range(r)]
        a=[[sum(u[i][k]*v[k][j] for k in range(r)) for j in range(n)] for i in range(m)]
        x=[rng.randrange(-4,5) for _ in range(n)]
        for row in a:row.append(sum(z*y for z,y in zip(row,x)))
        add('planted-rank',a,n)
        if trial%4==0:add('planted-inconsistent',a+[[0]*n+[1]],n)
        if trial%5==0:
            scaled=[]
            for row in a:
                e=rng.randrange(-400,401);s=F(2)**e
                scaled.append([z*s for z in row])
            rng.shuffle(scaled);add('power-two-row-scaling',scaled,n)
    eps=F(1,2**20)
    add('tiny-factor-large-rhs',[[1,0,2**30],[F(1,2**30),1,4]],2,eps)
    add('large-rhs-not-row-scale',[[1,2**80]],1,eps)
    add('tiny-coefficient-normalized',[[F(1,2**400),F(3,2**400)]],1,eps)
    for delta in [eps/2,eps,eps*2]:
        a=[[1,1,2],[1,1+delta,2+delta]]
        # Second row normalization means the available residual pivot is delta/(1+delta).
        if delta<=eps:
            add('threshold-near-dependent',a,2,eps,(True,1,[2,0],[[-1,1]]),True)
        else:add('threshold-separated-dependent',a,2,eps)
    add('early-free-column',[[eps/2,1,0,2],[eps/4,0,1,3]],3,eps,(True,2,[0,2,3],[[1,0,0]]),True)
    for b in [0,eps/2,eps,eps*2,-eps*2]:
        expected=(True,0,[],[]) if abs(b)<=eps else (False,0,[],[])
        add('zero-variable-threshold',[[b]],0,eps,expected,True)
    # Ill-conditioned legal integer-size coefficients, bounded exact zero solution.
    # This is a limitation example, not a proof of robust rank on arbitrary systems.
    a=[[0]*5 for _ in range(4)]
    for i in range(4):
        a[i][i]=1
        if i+1<4:a[i][i+1]=10000
    add('triangular-growth-zero-solution',a,4)
    n=100;x=[i%7-3 for i in range(n)]
    a=[[rng.randrange(-2,3) for _ in range(n)] for _ in range(n)]
    for i,row in enumerate(a):row[i]=1+sum(abs(z) for j,z in enumerate(row) if i!=j);row.append(sum(z*y for z,y in zip(row,x)))
    add('size100-diagonally-dominant',a,n,expected=(True,n,x,[]))
    r=50;a=[];b=[i%7-3 for i in range(r)]
    tail=[[rng.randrange(-2,3) for _ in range(n-r)] for _ in range(r)]
    for i in range(r):a.append([int(i==j) for j in range(r)]+tail[i]+[b[i]])
    a += [[-z for z in row] for row in a]
    kernel=[]
    for j in range(n-r):kernel.append([-tail[i][j] for i in range(r)]+[int(j==k) for k in range(n-r)])
    add('size100-rank50',a,n,expected=(True,r,b+[0]*(n-r),kernel))
    return cases


def input_case(c):
    return f"{len(c['a'])} {c['n']} {spelling(c['eps'])}\n"+'\n'.join(' '.join(spelling(x) for x in v) for v in c['a'])+'\n'


def validate_output(output,cases,batch=True):
    tokens=iter(output.split());worst=Decimal(0)
    with localcontext() as ctx:
        ctx.prec=100
        for c in cases:
            good,rank,x,kernel=c['expected'];n=c['n']
            status=int(next(tokens));assert status in (0,1)
            actual_good=bool(status);actual_rank=int(next(tokens))
            assert (actual_good,actual_rank)==(good,rank),c['name']
            if batch:
                nx=int(next(tokens));nk=int(next(tokens))
                assert nx==(n if good else 0) and nk==len(kernel),c['name']
            else:
                nx=n if good else 0;nk=None
            actual_x=[Decimal(next(tokens)) for _ in range(nx)]
            if not batch:nk=int(next(tokens)) if good else 0
            assert nk==len(kernel),c['name']
            actual_k=[[Decimal(next(tokens)) for _ in range(n)] for _ in range(nk)]
            for actual,want in [(actual_x,x),*zip(actual_k,kernel)]:
                assert len(actual)==len(want)
                for z,y in zip(actual,want):
                    assert z.is_finite(),c['name']
                    error=abs(z-dec(y))/(1+abs(dec(y)))
                    worst=max(worst,error);assert error<Decimal('1e-12'),(c['name'],z,y,error)
            if good and not c['threshold']:
                for vec,rhs in [(actual_x,True),*[(v,False) for v in actual_k]]:
                    for row in c['a']:
                        terms=[dec(z)*y for z,y in zip(row[:n],vec)]
                        b=dec(row[n]) if rhs else Decimal(0)
                        denominator=sum(abs(t) for t in terms)+abs(b)
                        error=abs(sum(terms)-b)/denominator if denominator else Decimal(0)
                        worst=max(worst,error);assert error<Decimal('1e-12'),(c['name'],error)
        assert next(tokens,None) is None
    return str(worst)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sanitizer',action='store_true');args=ap.parse_args()
    san=args.sanitizer or os.environ.get('SANITIZE')=='1' or os.environ.get('CPC_SANITIZE')=='1';mode='sanitizer' if san else 'normal'
    before=snapshot(ROOT);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    (ROOT/'build').mkdir(exist_ok=True);out=Path(tempfile.mkdtemp(prefix='gauss-real-'+mode+'-',dir=ROOT/'build'))
    compiler=Path(subprocess.check_output(['which',CXX],text=True).strip()).resolve();frontend=Path(subprocess.check_output([CXX,'-print-prog-name=cc1plus'],text=True).strip()).resolve();ch,fh=sha(compiler),sha(frontend)
    flags=['-std=c++20']+(['-O1','-g','-fsanitize=address,undefined'] if san else ['-O2']);commands=[]
    def limits():
        _,hard=resource.getrlimit(resource.RLIMIT_CORE);resource.setrlimit(resource.RLIMIT_CORE,(0,hard))
    def run(cmd,data=None,expected=0):
        p=subprocess.run(cmd,input=data,text=True,capture_output=True,cwd=ROOT,preexec_fn=limits,timeout=240);entry=dict(command=list(map(str,cmd)),returncode=p.returncode)
        for name,value in [('stdin',data),('stdout',p.stdout),('stderr',p.stderr)]:
            if value is not None:
                f=out/f'{len(commands)}.{name}';f.write_text(value);entry[name]=str(f.relative_to(ROOT));entry[name+'_sha256']=sha(f)
        commands.append(entry);assert p.returncode==expected,(cmd,p.returncode,p.stderr[:1500])
        if data is not None and expected==0:assert not p.stderr,p.stderr
        return p.stdout
    def artifact(src,exe):return dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),binary=str(exe.relative_to(ROOT)),binary_sha256=sha(exe))
    components={r['symbol']:r['code'] for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    prelude=''.join('#include <'+h+'>\n' for h in ['algorithm','cassert','climits','cmath','iomanip','iostream','limits','string','utility','vector'])+'using namespace std;\n'
    original=(ROOT/'tests/gauss_real_probe.cpp').read_text()
    minimal=prelude+components['GaussReal']+'\nint main'+original.split('int main',1)[1]
    cases=make_cases();inp=str(len(cases))+'\n'+''.join(input_case(c) for c in cases)
    # Preserve exact rational expectations separately from floating output.
    def rational(x):
        if isinstance(x,F):return [x.numerator,x.denominator]
        if isinstance(x,(list,tuple)):return [rational(z) for z in x]
        if isinstance(x,dict):return {k:rational(v) for k,v in x.items()}
        return x
    (out/'exact-cases.json').write_text(json.dumps(rational(cases),indent=2)+'\n')
    core={}
    for name,text in [('header',original.replace('../src/',str(ROOT/'src')+'/')),('copied',minimal)]:
        for ndebug in [False,True]:
            key=name+('-ndebug' if ndebug else '')
            src=out/f'core-{key}.cpp';src.write_text(text);exe=src.with_suffix('')
            run([CXX,*flags,'-pedantic-errors',*(['-DNDEBUG'] if ndebug else []),str(src),'-o',str(exe)])
            stdout=run([str(exe)],inp);error=validate_output(stdout,cases)
            core[key]=dict(**artifact(src,exe),cases=len(cases),maximum_mixed_vector_error_or_componentwise_residual=error)
            if not ndebug:
                for bad in ['bad-eps','bad-n','bad-shape','nan']:
                    run([str(exe),bad],'',expected=-6)
                    assert 'Assertion' in (ROOT/commands[-1]['stderr']).read_text()
    mutations={
      'no-row-swap':('swap(a[p], a[row]);',';','row-swap'),
      'wrong-elimination-sign':('a[i][j] -= f * a[row][j];','a[i][j] += f * a[row][j];','expectation'),
      'omit-rhs-elimination':('for (int j = col + 1; j <= n; j++)\n                    {\n                        a[i][j] -=','for (int j = col + 1; j < n; j++)\n                    {\n                        a[i][j] -=','expectation'),
      'skip-small-factor':('a[i][col] != 0','abs(a[i][col]) > eps','tiny-factor-large-rhs'),
      'retain-skipped-column':('for (int i = row; i < m; i++) a[i][col] = 0;',';','early-free-column')}
    negative={}
    for name,(a,b,witness) in mutations.items():
        assert a in components['GaussReal'];text=minimal.replace(components['GaussReal'],components['GaussReal'].replace(a,b))
        src=out/f'mutant-{name}.cpp';src.write_text(text);exe=src.with_suffix('');run([CXX,*flags,str(src),'-o',str(exe)])
        c=next(c for c in cases if c['name']==witness);data='1\n'+input_case(c)
        if name=='no-row-swap':
            run([str(exe)],data,expected=-6);assert 'isfinite' in (ROOT/commands[-1]['stderr']).read_text();reason='nonfinite assertion'
        else:
            stdout=run([str(exe)],data)
            try:validate_output(stdout,[c])
            except AssertionError:reason='independent result mismatch'
            else:raise AssertionError('Mutation not detected: '+name)
        negative[name]=dict(**artifact(src,exe),witness=witness,reason=reason)
    row=next(r for r in records() if r['id']=='example-233')
    forms={'direct':(ROOT/row['driver']).read_text().replace('../../src/',str(ROOT/'src')+'/'),'expanded':row['program'],'copied':prelude+components['GaussReal']+'\n'+row['snippet']}
    selected=cases[:9]+cases[-14:];programs={}
    for name,text in forms.items():
        src=out/f'program-{name}.cpp';src.write_text(text);exe=src.with_suffix('');run([CXX,*flags,str(src),'-o',str(exe)])
        worst=Decimal(0)
        for c in selected:
            stdout=run([str(exe)],input_case(c));worst=max(worst,Decimal(validate_output(stdout,[c],False)))
        programs[name]=dict(**artifact(src,exe),cases=len(selected),maximum_mixed_vector_error_or_componentwise_residual=str(worst))
    assert snapshot(ROOT)==before and sha(compiler)==ch and sha(frontend)==fh
    report=dict(mode=mode,passed=True,source_before_sha256=before,source_after_sha256=snapshot(ROOT),compiler=str(compiler),compiler_sha256=ch,frontend=str(frontend),frontend_sha256=fh,flags=flags,environment={k:os.environ.get(k) for k in ['CXX','ASAN_OPTIONS','UBSAN_OPTIONS']},core=core,mutations=negative,programs=programs,commands=commands,exact_reference_file=str((out/'exact-cases.json').relative_to(ROOT)),exact_reference_sha256=sha(out/'exact-cases.json'),scope='Bounded local numerical-model verification: exact small rational and structured size100 reference systems, explicit threshold expectations, ordinary and NDEBUG forms, debug invalid-precondition assertions. Not exact-rank/full-domain/P3389/online AC/full-suite/LeakSanitizer certification.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(f'GaussReal {mode}: {len(cases)} systems x four core forms, five rejected mutants, {len(selected)} complete inputs x three API forms PASS; report {out.relative_to(ROOT)}/report.json',flush=True)

if __name__=='__main__':main()
