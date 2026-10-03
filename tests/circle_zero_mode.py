"""Bounded integral-input proofs for the actual floating no-tolerance APIs."""
import argparse, hashlib, itertools, json, os, random, re, resource, subprocess, sys, tempfile
from decimal import Decimal as D, localcontext
from pathlib import Path
if not __debug__:
    raise RuntimeError("Run this test without Python optimization")
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot
from usage_examples import records
from audit_copy_context import extract_components


def line_reference(a, b, o, r):
    # Quadratic in the parameter of A+t(B-A), not the core's perpendicular foot.
    v = [b[i]-a[i] for i in range(2)]
    w = [a[i]-o[i] for i in range(2)]
    aa = sum(x*x for x in v)
    if not aa:
        return 4, []
    bb = 2*sum(x*y for x,y in zip(v,w)); cc = sum(x*x for x in w)-r*r
    dd = bb*bb-4*aa*cc
    if dd < 0:
        return 0, []
    roots = [(-D(bb)-D(dd).sqrt())/(2*aa)]
    if dd:
        roots.append((-D(bb)+D(dd).sqrt())/(2*aa))
    return len(roots), sorted(tuple(D(a[i])+t*v[i] for i in range(2)) for t in roots)


def circle_reference(a, r, b, s):
    # Classify by center-distance inequalities; intersect the radical axis via
    # coordinate elimination, rather than the core's midpoint/discriminant formula.
    x,y = b[0]-a[0], b[1]-a[1]; q=x*x+y*y
    if not q:
        return (0, []) if r != s else (3, []) if r else (1, [tuple(map(D,a))])
    if q > (r+s)**2 or q < (r-s)**2:
        return 0, []
    u,v,z=2*x,2*y,q+r*r-s*s
    swapped = not v
    if swapped:
        u,v=v,u
    aa=v*v+u*u; bb=-2*z*u; cc=z*z-r*r*v*v
    dd=bb*bb-4*aa*cc
    assert dd >= 0
    roots=[(-D(bb)-D(dd).sqrt())/(2*aa)]
    if dd:
        roots.append((-D(bb)+D(dd).sqrt())/(2*aa))
    points=[]
    for first in roots:
        p=[first,(D(z)-u*first)/v]
        if swapped:
            p.reverse()
        points.append(tuple(D(a[i])+p[i] for i in range(2)))
    return len(points),sorted(points)


def fixture_cases():
    lines=[((9797,396),(9574,5913),(0,0),9805),
           ((9797,-5314),(9178,10000),(0,-5710),9805)]
    circles=[((0,0),10000,(9999,1),1)]
    points=list(itertools.product(range(-1,2),repeat=2))
    lines += [(a,b,o,r) for a in points for b in points for o in [(0,0),(1,-1)] for r in range(3)]
    circles += [(a,r,b,s) for a in points for b in points for r in range(3) for s in range(3)]
    rng=random.Random(20261003)
    for _ in range(3000):
        point=lambda:tuple(rng.randint(-10000,10000) for _ in range(2))
        lines.append((point(),point(),point(),rng.randint(0,10000)))
        circles.append((point(),rng.randint(0,10000),point(),rng.randint(0,10000)))
    # Near external/internal tangency, exact tangency and extreme translated values.
    for r in [1,2,9999,10000]:
        for d in [-1,0,1]:
            circles.extend([((-1,0),r,(r+d-1,0),1),((-1,0),r,(r+d-1,1),1)])
    circles.extend([((0,0),10000,(1,0),10000), ((0,0),10000,(1,0),9999),
                    ((-10000,0),10000,(10000,0),10000), ((-10000,-10000),10000,(10000,10000),10000)])
    lines.append(((10000,10000),(9999,10000),(10000,10000),10000))
    lines.extend([((-10000,-10000),(10000,10000),(10000,-10000),10000),
                  ((-10000,0),(10000,0),(0,10000),10000),
                  ((0,-10000),(0,10000),(0,0),10000)])
    for a,b,o,r in list(lines[:2]):
        for flip in [-1,1]:
            for swap in [False,True]:
                f=lambda p: (flip*p[1],p[0]) if swap else (flip*p[0],p[1])
                lines.extend([(f(a),f(b),f(o),r),(f(b),f(a),f(o),r)])
    for a,r,b,s in list(circles[:1]):
        for flip in [-1,1]:
            for swap in [False,True]:
                f=lambda p: (flip*p[1],p[0]) if swap else (flip*p[0],p[1])
                circles.extend([(f(a),r,f(b),s),(f(b),s,f(a),r)])
    assert all(abs(z)<=10000 for a,b,o,r in lines for p in (a,b,o) for z in p)
    assert all(abs(z)<=10000 for a,r,b,s in circles for p in (a,b) for z in p)
    return lines,circles


def check_points(values, points, tolerance):
    want=[c for p in points for c in p]
    assert len(values)==len(want) and all(x.is_finite() for x in values)
    assert list(zip(values[::2],values[1::2]))==sorted(zip(values[::2],values[1::2]))
    error=max([D(0)]+[abs(x-y) for x,y in zip(values,want)])
    assert error<tolerance,error
    return error


def check_result(line, kind, points):
    fields=line.split()
    assert len(fields)>=2 and list(map(int,fields[:2]))==[kind,len(points)]
    return check_points(list(map(D,fields[2:])),points,D('1e-10'))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sanitizer',action='store_true');args=ap.parse_args()
    san=args.sanitizer or os.environ.get('SANITIZE')=='1' or os.environ.get('CPC_SANITIZE')=='1'
    mode='sanitizer' if san else 'normal'
    before=snapshot(ROOT);out=Path(tempfile.mkdtemp(prefix='circle-zero-'+mode+'-',dir=ROOT/'build'))
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    compiler=Path(subprocess.check_output(['which',CXX],text=True).strip()).resolve()
    frontend=Path(subprocess.check_output([CXX,'-print-prog-name=cc1plus'],text=True).strip()).resolve()
    compiler_before,frontend_before=sha(compiler),sha(frontend)
    checks=[]
    def no_core():
        _,hard=resource.getrlimit(resource.RLIMIT_CORE)
        resource.setrlimit(resource.RLIMIT_CORE,(0,hard))
    def run(cmd, data=None, expected=0, diagnostic=None):
        p=subprocess.run(cmd,input=data,text=True,capture_output=True,cwd=ROOT,timeout=180,preexec_fn=no_core)
        n=len(checks);so=out/f'{n}.stdout';se=out/f'{n}.stderr';so.write_text(p.stdout);se.write_text(p.stderr)
        checks.append(dict(command=list(map(str,cmd)),returncode=p.returncode,input_sha256=hashlib.sha256((data or '').encode()).hexdigest(),stdout=str(so.relative_to(ROOT)),stdout_sha256=sha(so),stderr=str(se.relative_to(ROOT)),stderr_sha256=sha(se)))
        if data is not None:
            stdin=out/f'{n}.stdin';stdin.write_text(data)
            checks[-1]['stdin']=str(stdin.relative_to(ROOT))
        assert p.returncode==expected,(cmd,p.returncode,p.stderr[:1500])
        if diagnostic is not None:
            assert diagnostic in p.stderr,p.stderr
        if data is not None and expected==0:
            assert not p.stderr,p.stderr
        return p.stdout
    flags=['-std=c++20','-fno-fast-math']+(['-O1','-g','-fsanitize=address,undefined'] if san else ['-O2'])
    platform_source=out/'platform.cpp'
    platform_source.write_text('#include <iostream>\n#include <limits>\n#include <cfenv>\nint main(){std::cout<<std::numeric_limits<long double>::radix<<" "<<std::numeric_limits<long double>::digits<<" "<<fegetround()<<" "<<FE_TONEAREST<<"\\n";}\n')
    run([CXX,*flags,str(platform_source),'-o',str(out/'platform')])
    platform=list(map(int,run([str(out/'platform')],'').split()))
    assert platform[0]==2 and platform[1]>=64 and platform[2]==platform[3]
    components={x['symbol']:x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    prelude='#include <algorithm>\n#include <cassert>\n#include <cfenv>\n#include <cmath>\n#include <iomanip>\n#include <iostream>\n#include <limits>\n#include <tuple>\n#include <vector>\nusing namespace std;\n'
    body=(ROOT/'tests/circle_zero_probe.cpp').read_text();body=body[body.index('int main()'):]
    minimal=prelude+'\n'.join(components[x] for x in ['RealPlane','line_projection','line_circle_intersections','circle_intersections'])+'\n'+body
    sources={'core':(ROOT/'tests/circle_zero_probe.cpp').read_text(),'minimal':minimal}
    sources['core']=sources['core'].replace('../src/',str(ROOT/'src')+'/')
    # Prove positive-epsilon source paths were preserved, not just a handful of outputs.
    for name in ['line_circle_intersections','circle_intersections']:
        new=(ROOT/f'src/compact/{name}.hpp').read_text()
        old=(ROOT/f'tests/fixtures/circle-zero-default/{name}.hpp').read_text()
        begin=new.index('    if (eps == 0)'); end=new.index('    R '+('len' if name.startswith('line') else 'd')+' = G::norm(v);',begin)
        assert (new[:begin]+new[end:]).replace('assert(eps >= 0);','assert(eps > 0);')==old
    lines,circles=fixture_cases()
    rows=[];expected=[]
    with localcontext() as context:
        context.prec=100
        for a,b,o,r in lines:
            rows.append('L 0 '+' '.join(map(str,(*a,*b,*o,r))));expected.append(line_reference(a,b,o,r))
        for a,r,b,s in circles:
            rows.append('C 0 '+' '.join(map(str,(*a,r,*b,s))));expected.append(circle_reference(a,r,b,s))
        data='\n'.join(rows)+'\n'
        errors={};binaries={}
        for name,text in sources.items():
            src=out/(name+'.cpp');src.write_text(text);exe=out/name
            run([CXX,*flags,'-pedantic-errors',str(src),'-o',str(exe)])
            result=run([str(exe)],data).splitlines();assert len(result)==len(expected)
            error=D(0)
            for actual,(kind,points) in zip(result,expected):
                error=max(error,check_result(actual,kind,points))
            assert error<D('1e-10'),error
            errors[name]=str(error);binaries[name]=dict(source=str(src.relative_to(ROOT)),binary=str(exe.relative_to(ROOT)),source_sha256=sha(src),binary_sha256=sha(exe))
            default=run([str(exe)],'L 1e-12 9797 396 9574 5913 0 0 9805\nC 1e-12 0 0 10000 9999 1 1\n')
            assert all(s.split()[:2]==['1','1'] for s in default.splitlines())
            run([str(exe)],'L -1 0 0 1 0 0 0 1\n',expected=-6)
            run([str(exe)],'C -1 0 0 1 1 0 1\n',expected=-6)
        # Exercise complete programs in direct, registered-expanded, and real minimal contexts.
        infos={r['id']:r for r in records()};program_reports={}
        for number,letter in [(229,'D'),(230,'E')]:
            row=infos[f'example-{number}'];driver=ROOT/row['driver']
            forms={'direct':driver.read_text().replace('../../src/',str(ROOT/'src')+'/'),'expanded':row['program'],
                   'copied':prelude+'\n'.join(components[x] for x in row['requires'])+'\n'+row['snippet']}
            samples=[]
            if letter=='D':
                valid=[(x,y) for x,y in zip(lines,expected[:len(lines)]) if y[0] in [1,2] and x[3]>=1]
                for (a,b,o,r),ref in valid[:130]+valid[-25:]:
                    samples.append((' '.join(map(str,(*o,r)))+'\n1\n'+' '.join(map(str,(*a,*b)))+'\n',[ref]))
                # Actual maximum q with a fixed circle and guaranteed secants/tangents.
                queries=[((-10000,y),(10000,y)) for y in range(-500,500)]
                samples.append(('0 0 10000\n1000\n'+'\n'.join(' '.join(map(str,(*a,*b))) for a,b in queries)+'\n',[line_reference(a,b,(0,0),10000) for a,b in queries]))
            else:
                valid=[(x,y) for x,y in zip(circles,expected[len(lines):]) if y[0] in [1,2] and x[0]!=x[2] and x[1]>=1 and x[3]>=1]
                for (a,r,b,s),ref in valid[:130]+valid[-25:]:samples.append((' '.join(map(str,(*a,r,*b,s)))+'\n',[ref]))
            for name,text in forms.items():
                src=out/f'{number}-{name}.cpp';src.write_text(text);exe=src.with_suffix('')
                run([CXX,*flags,str(src),'-o',str(exe)])
                error=D(0)
                for inp,refs in samples:
                    got=run([str(exe)],inp).splitlines();assert len(got)==len(refs)
                    for line,(_,points) in zip(got,refs):
                        if len(points)==1:points=points*2
                        vals=list(map(D,line.split()));want=[c for p in points for c in p]
                        error=max(error,check_points(vals,points,D('1e-9')))
                assert error<D('1e-9'),error
                program_reports[f'{number}-{name}']=dict(inputs=len(samples),queries=sum(len(r) for _,r in samples),max_absolute_error=str(error),source=str(src.relative_to(ROOT)),binary=str(exe.relative_to(ROOT)),source_sha256=sha(src),binary_sha256=sha(exe))
    rejected=0
    points=[(D(0),D(0)),(D(1),D(0))]
    for values in [[D(0)], [D('NaN'),D(0),D(1),D(0)], [D('Infinity'),D(0),D(1),D(0)],
                   [D('0.00001'),D(0),D(1),D(0)], [D(1),D(0),D(0),D(0)]]:
        try:
            check_points(values,points,D('1e-9'))
        except AssertionError:
            rejected+=1
        else:
            raise AssertionError('Bad numeric certificate accepted')
    assert rejected==5
    for bad in ['1 2 0 0 1 0','2 1 0 0','2 2 0 0','2 2 1 0 0 0']:
        try:
            check_result(bad,2,points)
        except AssertionError:
            rejected+=1
        else:
            raise AssertionError('Bad kind/count/order accepted')
    try:
        check_points([D(0),D(0)],[(D(0),D(0))]*2,D('1e-9'))
    except AssertionError:
        rejected+=1
    else:
        raise AssertionError('Missing tangent duplication accepted')
    assert rejected==10
    for number in [229,230]:
        row=infos[f'example-{number}']
        src=out/f'{number}-expanded.cpp'
        run([CXX,'-std=c++20','-ffast-math','-fsyntax-only',str(src)],expected=1,diagnostic='This example requires normal floating arithmetic')
        # Compile a 53-bit long-double ABI probe only on this GNU x86 target;
        # it must fail the actual driver's static_assert and is never executed.
        machine=subprocess.check_output([CXX,'-dumpmachine'],text=True).strip()
        if machine.startswith(('x86_64','i686')):
            run([CXX,'-std=c++20','-mlong-double-64','-fsyntax-only',str(src)],expected=1,diagnostic='static assertion failed')
        text=row['program'].replace('int main()','int example_main()')
        end=text.rfind('}')
        text=text[:end]+'    return 0;\n'+text[end:]
        text+='\nint main() { fesetround(FE_DOWNWARD); return example_main(); }\n'
        src=out/f'{number}-rounding.cpp';src.write_text(text);exe=src.with_suffix('')
        run([CXX,*flags,str(src),'-o',str(exe)])
        run([str(exe)],'',expected=1)
    # Independent binary53 negative control; no claim of testing another platform ABI.
    q=234901757;z=150276382
    assert 9805**2*q-z*z==1 and float(9805)**2*float(q)-float(z)*float(z)==0
    compiler=Path(subprocess.check_output(['which',CXX],text=True).strip()).resolve()
    frontend=Path(subprocess.check_output([CXX,'-print-prog-name=cc1plus'],text=True).strip()).resolve()
    after=snapshot(ROOT);assert before==after
    assert compiler_before==sha(compiler) and frontend_before==sha(frontend)
    report=dict(mode=mode,passed=True,source_before_sha256=before,source_after_sha256=after,compiler=str(compiler),compiler_sha256=sha(compiler),frontend=str(frontend),frontend_sha256=sha(frontend),compiler_version=subprocess.check_output([CXX,'--version'],text=True).strip(),flags=flags,platform=dict(radix=platform[0],digits=platform[1],rounding=platform[2],FE_TONEAREST=platform[3]),line_cases=len(lines),circle_cases=len(circles),numeric_negative_controls=rejected,core_max_absolute_error=errors,core_artifacts=binaries,complete_programs=program_reports,commands=checks,scope='Actual floating eps=0 APIs on coordinates bounded by 10000 and integer radii 0..10000, including point/degenerate extensions beyond AOJ. Complete AOJ forms use positive radii and promised intersections; 100-digit independent quadratic/coordinate elimination references. Defaults source-preserved and old counterexamples retained. Not arbitrary-real robustness, online AC, other-platform or LeakSanitizer certification.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(f'Circle zero {mode}: {len(lines)} line + {len(circles)} circle cases, six full program forms PASS; report {out.relative_to(ROOT)}/report.json',flush=True)

if __name__=='__main__':main()
