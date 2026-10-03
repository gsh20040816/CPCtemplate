"""Check migrated modular conditions by exact enumeration and actual APIs."""
import argparse, hashlib, json, math, os, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path
if not __debug__:
    raise RuntimeError('Run this test without Python optimization')
from compiler_config import CXX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sanitizer',action='store_true');args=ap.parse_args()
    san=args.sanitizer or os.environ.get('SANITIZE')=='1' or os.environ.get('CPC_SANITIZE')=='1'
    mode='sanitizer' if san else 'normal'
    before=snapshot(ROOT);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    fixture=ROOT/'tests/fixtures/modular-knowledge';meta=json.loads((fixture/'manifest.json').read_text())
    old=(fixture/'original.tex').read_text();assert sha(fixture/'original.tex')==meta['original_sha256']
    expected=old
    for change in meta['prefix_changes']:
        assert expected.count(change['old'])==1;expected=expected.replace(change['old'],change['new'])
    actual=(ROOT/'docs/knowledge-modular-conditions.tex').read_text()
    assert actual.split(meta['extension_marker'],1)[0]==expected
    mathtext=(ROOT/'docs/mathematics.tex').read_text()
    assert mathtext.count(r'\input{knowledge-modular-conditions.tex}')==1 and r'\section{模运算的适用条件}' not in mathtext
    mapping=json.loads((ROOT/'docs/knowledge-taxonomy.json').read_text())
    row=[r for r in mapping['entries'] if r['label']=='knowledge-modular-conditions'];assert len(row)==1 and row[0]['path']=='math/number-theory/mod-arithmetic.md'
    for target in ['compact-mod_inverse','compact-linear_congruence','compact-ModInt','compact-Binomial','compact-euler_power']:
        assert r'\ref{'+target+'}' in actual and r'\pageref{'+target+'}' in actual
    assert '一次逆元快速幂' not in (ROOT/'docs/knowledge-combinatorics.tex').read_text()
    inputs=[];answers=[];counts=Counter()
    def add(op, values, answer):
        inputs.append(op+' '+' '.join(map(str,values)));answers.append(' '.join(map(str,answer)));counts[op]+=1
    for m in range(1,31):
        for a in range(-m,m+1):
            inv=[x for x in range(m) if a*x%m==1%m]
            assert len(inv)<=1;add('I',[a,m],[inv[0] if inv else -1])
            for b in range(-m,m+1):
                roots=[x for x in range(m) if (a*x+b)%m==0]
                if not roots:
                    assert b%math.gcd(a,m);answer=[-1,-1]
                else:
                    period=m//len(roots)
                    assert roots==list(range(roots[0],m,period))
                    assert len(roots)==math.gcd(a,m) and b%len(roots)==0
                    answer=[roots[0],period]
                add('C',[a,b,m],answer)
        for a in [-(1<<63),(1<<63)-1]:
            for b in [-(1<<63),-1,0,(1<<63)-1]:
                roots=[x for x in range(m) if (a*x+b)%m==0]
                add('C',[a,b,m],[-1,-1] if not roots else [roots[0],m//len(roots)])
    for m in range(1,11):
        for n in range(1,11):
            period=math.lcm(m,n)
            for r in range(m):
                for a in range(n):
                    roots=[x for x in range(period) if x%m==r and x%n==a]
                    assert len(roots)<=1 and bool(roots)==((a-r)%math.gcd(m,n)==0)
                    add('R',[r-m,m,a-n,n],[-1] if not roots else [roots[0],period])
    for m in range(1,41):
        phi=sum(math.gcd(x,m)==1 for x in range(1,m+1))
        for a in range(0,2*m+1):
            power=1%m
            for b in range(0,2*phi+2):
                e=b if b<phi else b%phi+phi
                # Independent repeated multiplication, not the reduction under test.
                assert pow(a,e,m)==power
                add('E',[a,('000' if b%3==0 else '')+str(b),m,phi],[power])
                power=power*a%m
        for a in [0,2,(1<<64)-1]:
            b='000'+'9'*101
            add('E',[a,b,m,phi],[pow(a,int(b),m)])
    for p in [2,3,5,7,11]:
        # Pascal recurrence, no factorial division or Lucas digits in the oracle.
        row=[1]
        for n in range(61):
            for k in range(n+3):add('L',[p,n,k],[row[k]%p if k<=n else 0])
            row=[1]+[row[i-1]+row[i] for i in range(1,len(row))]+[1]
    quotient_checks=0
    for m in range(1,31):
        for d in range(1,21):
            for q in range(-100,101):
                x=d*q;r=x%(m*d)
                assert r%d==0 and r//d==q%m;quotient_checks+=1
    assert (6%4)//2 != (6//2)%4
    assert math.factorial(2)%6==2 and math.gcd(math.factorial(2),6)>1
    assert pow(2,4,8)!=pow(2,4%4,8) and pow(2,1,8)!=pow(2,1+4,8)
    assert math.comb(4,2)%4==2 and math.comb(0,2)==0 # naive base-4 digit formula fails
    out=Path(tempfile.mkdtemp(prefix='modular-knowledge-'+mode+'-',dir=ROOT/'build'))
    data='\n'.join(inputs)+'\n';want='\n'.join(answers)+'\n'
    (out/'input.txt').write_text(data);(out/'expected.txt').write_text(want)
    compiler=Path(subprocess.check_output(['which',CXX],text=True).strip()).resolve()
    frontend=Path(subprocess.check_output([CXX,'-print-prog-name=cc1plus'],text=True).strip()).resolve()
    hashes={'compiler':sha(compiler),'frontend':sha(frontend)}
    flags=['-std=c++20']+(['-O1','-g','-fsanitize=address,undefined'] if san else ['-O2'])
    exe=out/'probe';cmd=[CXX,*flags,str(ROOT/'tests/modular_knowledge_probe.cpp'),'-o',str(exe)]
    build=subprocess.run(cmd,text=True,capture_output=True);(out/'compile.stdout').write_text(build.stdout);(out/'compile.stderr').write_text(build.stderr);assert build.returncode==0,build.stderr
    run=subprocess.run([str(exe)],input=data,text=True,capture_output=True,timeout=180)
    (out/'actual.txt').write_text(run.stdout);(out/'stderr.txt').write_text(run.stderr)
    assert run.returncode==0 and not run.stderr,run.stderr
    assert run.stdout.splitlines()==answers,'API answer differs from independent enumeration'
    assert snapshot(ROOT)==before and hashes['compiler']==sha(compiler) and hashes['frontend']==sha(frontend)
    report=dict(mode=mode,passed=True,source_before_sha256=before,source_after_sha256=snapshot(ROOT),counts=dict(counts),quotient_checks=quotient_checks,compiler=str(compiler),compiler_sha256=hashes['compiler'],frontend=str(frontend),frontend_sha256=hashes['frontend'],compile_command=cmd,compile_returncode=build.returncode,run_returncode=run.returncode,artifacts={str(p.relative_to(ROOT)):sha(p) for p in out.iterdir() if p.is_file()},scope='Knowledge conditions, migration prefix and actual existing APIs; exhaustive small inverse/congruence/CRT, repeated multiplication Euler oracle, exact Pascal Lucas oracle, integer quotient identities. No new algorithm, online AC or full-suite/LeakSanitizer claim.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Modular knowledge {mode}: {dict(counts)}, {quotient_checks} integer quotient identities PASS; report {out.relative_to(ROOT)}/report.json',flush=True)

if __name__=='__main__':main()
