#!/usr/bin/env python3
import hashlib,itertools,json,os,random,subprocess
from decimal import Decimal,localcontext
from pathlib import Path
from compiler_config import CXX
root=Path(__file__).resolve().parents[1];out=root/'build/incircle';out.mkdir(parents=True,exist_ok=True)
rng=random.Random(7002)
cases=[]
for p in [((0,0),(4,0),(0,3)), ((0,0),(-4,1),(-4,-1)), ((-10000,-10000),(10000,9999),(9999,9998)), ((0,0),(1,1),(2,2)),((3,4),(3,4),(3,4))]:
 cases.extend(itertools.permutations(p))
for _ in range(5000):
 cases.append(tuple((rng.randrange(-10000,10001),rng.randrange(-10000,10001)) for i in range(3)))
for e in [-60,-20,20,60]:
 s=Decimal(2)**e
 cases.extend([((0,0),(s*4,0),(0,s*3)),((s,s),(s*5,s),(s,s*4))])
def oracle(p):
 with localcontext() as ctx:
  ctx.prec=90
  a,b,c=[tuple(Decimal(x) for x in q) for q in p]
  # Solve the intersection of two inward unit-offset edge lines:
  # n1 dot (o-a) = r, n2 dot(o-b) = r, n3 dot(o-c) = r.
  det=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
  if not det:return None
  sign=1 if det>0 else -1
  rows=[]
  for s,t in [(a,b),(b,c),(c,a)]:
   dx=t[0]-s[0];dy=t[1]-s[1];length=(dx*dx+dy*dy).sqrt()
   nx=-dy/length*sign;ny=dx/length*sign
   rows.append([nx,ny,Decimal(-1),nx*s[0]+ny*s[1]])
  for i in range(3):
   j=max(range(i,3),key=lambda j:abs(rows[j][i]));rows[i],rows[j]=rows[j],rows[i]
   v=rows[i][i];rows[i]=[x/v for x in rows[i]]
   for j in range(3):
    if i!=j:
     v=rows[j][i];rows[j]=[x-v*y for x,y in zip(rows[j],rows[i])]
  return [rows[i][3] for i in range(3)]
wants=[oracle(p) for p in cases]
data=''.join(' '.join(str(x) for q in p for x in q)+'\n' for p in cases)
harness='''#include "../../src/compact/triangle_incircle.hpp"
int main()
{
 RealPlane::Point a,b,c;
 while(cin>>a.x>>a.y>>b.x>>b.y>>c.x>>c.y)
 {
  auto r=triangle_incircle(a,b,c);
  if(!r) cout<<"none\\n";
  else cout<<setprecision(21)<<r->o.x<<' '<<r->o.y<<' '<<r->r<<'\\n';
 }
}
'''
(out/'test.cpp').write_text(harness)
real=(root/'src/compact/real_plane.hpp').read_text();core=(root/'src/compact/triangle_incircle.hpp').read_text().split('// BEGIN triangle_incircle')[1].split('// END')[0]
(out/'copied.cpp').write_text(harness.replace('#include "../../src/compact/triangle_incircle.hpp"',real+'\n'+core))
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
result={}
for mode in ['normal','sanitizer']:
 flags=['-std=c++20','-O2']+(['-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else [])
 for form in ['header','ndebug','copied']:
  exe=out/(mode+'-'+form);src=out/('copied.cpp' if form=='copied' else 'test.cpp')
  subprocess.run([CXX,*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
  r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,env=env,check=True)
  lines=r.stdout.splitlines();assert len(lines)==len(cases)
  error=Decimal(0)
  for p,w,line in zip(cases,wants,lines):
   if w is None:assert line=='none',(p,line);continue
   got=list(map(Decimal,line.split()));assert len(got)==3
   for x,y in zip(got,w):
    tol=Decimal('5e-11')*max(Decimal(1),abs(y))
    assert x.is_finite() and abs(x-y)<tol,(p,w,got)
   if all(abs(Decimal(x))<=10000 and Decimal(x)==int(Decimal(x)) for q in p for x in q):
    error=max(error,*[abs(x-y) for x,y in zip(got,w)])
  result[mode+'-'+form]=dict(cases=len(cases),max_integer_absolute_error=str(error))
 # Formal one-triangle driver (first 60 nondegenerate integer inputs).
 exe=out/('driver-'+mode)
 subprocess.run([CXX,*flags,str(root/'verify/aoj/CGL_7_B.compact.cpp'),'-o',str(exe)],check=True)
 count=0
 for p,w in zip(cases,wants):
  if w is None:continue
  text=' '.join(str(x) for q in p for x in q)+'\n'
  r=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,env=env)
  got=list(map(Decimal,r.stdout.split()));assert len(got)==3
  assert all(abs(x-y)<Decimal('0.000001') for x,y in zip(got,w))
  count+=1
  if count==60:break
 result['driver-'+mode]=count
# Complete fixed kuangbin geometry source, only the incircle constructor exercised.
original = out/'original-probe.cpp'
original.write_text('''#include "../circle-coverage/original.cpp"
int main() {
 Point a,b,c;
 while(cin>>a.x>>a.y>>b.x>>b.y>>c.x>>c.y) {
  circle q(a,b,c,true);
  cout<<setprecision(17)<<q.p.x<<" "<<q.p.y<<" "<<q.r<<"\\n";
 }
}
''')
valid=[(p,w) for p,w in zip(cases,wants) if w is not None and all(abs(Decimal(x))<=10000 and Decimal(x)==int(Decimal(x)) for q in p for x in q)]
source_data=''.join(' '.join(str(x) for q in p for x in q)+'\n' for p,w in valid)
for mode in ['normal','sanitizer']:
 exe=out/('original-'+mode)
 flags=['-std=c++17','-O2']+(['-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else [])
 subprocess.run([CXX,*flags,str(original),'-o',str(exe)],check=True)
 r=subprocess.run([str(exe)],input=source_data,text=True,capture_output=True,env=env,check=True)
 lines=r.stdout.splitlines();assert len(lines)==len(valid)
 maxerr=Decimal(0)
 failures=[]
 for (p,w),line in zip(valid,lines):
  got=list(map(Decimal,line.split()));assert len(got)==3
  assert all(x.is_finite() for x in got)
  err=max(abs(x-y) for x,y in zip(got,w));maxerr=max(maxerr,err)
  if err>=Decimal('1e-6'):
   failures.append(dict(points=[[str(x) for x in q] for q in p],error=str(err)))
 assert maxerr>Decimal('0.001'), 'known skinny-triangle precision regression not reproduced'
 result['source-'+mode]=dict(cases=len(valid),max_absolute_error=str(maxerr),outside_1e6_tolerance=failures)
report=dict(status='pass',results=result,oracle='90-digit Decimal intersection of three inward unit-offset lines; independent of weighted-center implementation',source_sha256=hashlib.sha256((root/'src/compact/triangle_incircle.hpp').read_bytes()).hexdigest(),source_geometry_sha256=hashlib.sha256((root/'build/circle-coverage/original.cpp').read_bytes()).hexdigest(),scope='All permutations, AOJ integer bounds, collinear/repeated, powers-of-two scale; finite tests are not an exact real-predicate guarantee; online pending')
(root/'verification/triangle-incircle.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
