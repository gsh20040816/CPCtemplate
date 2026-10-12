"""Independent exact halfplane intersection and vertical first-moment integrals."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,getcontext
import random,json,subprocess,hashlib
from compiler_config import CXX
getcontext().prec=70
root=Path(__file__).resolve().parents[1];outdir=root/'build/polygon-tools';outdir.mkdir(exist_ok=True)
(outdir/'precision.cpp').write_text('#include <limits>\n#include <iostream>\nint main()\n{\n    std::cout << std::numeric_limits<long double>::digits;\n}\n')
subprocess.run([CXX,'-std=c++20',str(outdir/'precision.cpp'),'-o',str(outdir/'precision')],check=True)
digits=int(subprocess.check_output([str(outdir/'precision')],text=True));epsilon=D(2)**(1-digits)
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def hull(p):
 p=sorted(set(p))
 if len(p)<2:return p
 def chain(p):
  q=[]
  for v in p:
   while len(q)>1 and cross(q[-2],q[-1],v)<=0:q.pop()
   q.append(v)
  return q
 return chain(p)[:-1]+chain(p[::-1])[:-1]
def cut(p,a,b):
 points=[v for v in p if cross(a,b,v)>=0]
 # Intersect the implicit supporting lines by Cramer's rule.
 A=a[1]-b[1];B=b[0]-a[0];C=A*a[0]+B*a[1]
 for u,v in zip(p,p[1:]+p[:1]):
  E=u[1]-v[1];G=v[0]-u[0];H=E*u[0]+G*u[1];det=A*G-B*E
  if not det:continue
  q=(F(C*G-B*H,det),F(A*H-C*E,det))
  if min(u[0],v[0])<=q[0]<=max(u[0],v[0]) and min(u[1],v[1])<=q[1]<=max(u[1],v[1]):points.append(q)
 return hull(points)
def moments(p):
 if len(p)<3:return None
 xs=sorted(set(x for x,y in p));area=mx=my=F(0)
 for l,r in zip(xs,xs[1:]):
  mid=F(l+r,2);ys=[]
  for a,b in zip(p,p[1:]+p[:1]):
   if min(a[0],b[0])<mid<max(a[0],b[0]):
    m=F(b[1]-a[1],b[0]-a[0]);c=a[1]-m*a[0];ys.append((m*mid+c,m,c))
  ys.sort();assert len(ys)%2==0
  for low,high in zip(ys[::2],ys[1::2]):
   m=high[1]-low[1];c=high[2]-low[2]
   area+=m*(r*r-l*l)/2+c*(r-l)
   mx+=m*(r**3-l**3)/3+c*(r*r-l*l)/2
   my+=((high[1]**2-low[1]**2)*(r**3-l**3)/3+(high[1]*high[2]-low[1]*low[2])*(r*r-l*l)+(high[2]**2-low[2]**2)*(r-l))/2
 return None if not area else (mx/area,my/area)
rng=random.Random(692729);cases=[];expected=[]
def addcut(p,a,b):cases.append((0,p,a,b));expected.append(cut(p,a,b))
def addcenter(p):cases.append((1,p,None,None));expected.append(moments(p))
for p in [[],[(0,0)],[(0,0),(3,7)],[(0,0),(1,1),(2,2)],[(0,0),(1,0),(2,0),(2,2),(0,2)]]:
 addcenter(p)
 for a,b in [((0,0),(1,0)),((0,1),(1,1)),((1,-1),(1,3))]:addcut(p,a,b)
for it in range(600):
 p=hull([(rng.randrange(-100,101),rng.randrange(-100,101)) for _ in range(rng.randrange(3,30))])
 a=(rng.randrange(-150,151),rng.randrange(-150,151));b1=(a[0]+rng.randrange(1,100),a[1]+rng.randrange(-99,100))
 addcut(p,a,b1);addcut(p,b1,a);addcut(p[::-1],a,b1)
 if len(p)>2:
  addcut(p,p[0],p[1]);addcut(p,p[1],p[0])
  if it<100:addcut(p,(-200,p[0][1]),(200,p[0][1]))
 addcenter(p)
 if it<100:
  addcenter(p[::-1]);addcenter([(x+10**12,y-10**12) for x,y in p]);addcenter([(F(x,1024),F(y,1024)) for x,y in p]);addcenter([(F(x,10**12),F(y,10**12)) for x,y in p])
for it in range(250):
 w=rng.randrange(2,100);h=rng.randrange(2,100);x=rng.randrange(1,w);y=rng.randrange(1,h)
 p=[(0,0),(w,0),(w,y),(x,y),(x,h),(0,h)]
 addcenter(p);addcenter(p[::-1]);addcenter([(u+10**12,v+10**12) for u,v in p])
for it in range(100):
 p=[(x*(r:=rng.randrange(1,100)),y*r) for x,y in [(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0)]]
 addcenter(p);addcenter(p[::-1])
# One hundred thousand collinear boundary vertices: weak convexity is supported.
n=25000;p=[(i,0) for i in range(n)]+[(n,i) for i in range(n)]+[(n-i,n) for i in range(n)]+[(0,n-i) for i in range(n)]
cases.append((0,p,(n//2,-1),(n//2,n+1)));expected.append([(0,0),(n//2,0),(n//2,n),(0,n)])
cases.append((1,p,None,None));expected.append((F(n,2),F(n,2)))
def dec(x):return D(x.numerator)/D(x.denominator) if isinstance(x,F) else D(str(x))
def token(x):return str(dec(x))
text=str(len(cases))+'\n'+''.join(f'{mode} {len(p)}\n'+''.join(token(x)+' '+token(y)+'\n' for x,y in p)+((' '.join(token(x) for x in (*a,*b))+'\n') if mode==0 else '') for mode,p,a,b in cases)
plane=(root/'src/compact/real_plane.hpp').read_text().replace('#pragma once\n','');parts=[]
for name in ['convex_cut','polygon_centroid']:
 s=(root/f'src/compact/{name}.hpp').read_text();parts.append(s.split(f'// BEGIN {name}\n')[1].split(f'// END {name}')[0])
driver=(root/'tests/polygon_tools.cpp').read_text().split('\n',2)[2];(outdir/'copied.cpp').write_text(plane+'\n'+'\n'.join(parts)+driver)
def validate(case,want,line):
 mode,p,a,b=case;v=line.split();count=int(v[0]);got=list(zip(map(D,v[1::2]),map(D,v[2::2])));assert len(got)==count
 p=[tuple(map(dec,q)) for q in p];span=max([D('1e-30')]+[max(q[j] for q in p)-min(q[j] for q in p) for j in range(2)] if p else [D('1e-30')]);coord=max([D(0)]+[abs(x) for q in p for x in q]);tol=D('1e-9')*span+2*epsilon*coord+D('1e-30')
 if mode==1:
  assert bool(count)==(want is not None),(case,want,got)
  if want is not None:assert max(abs(got[0][i]-dec(want[i])) for i in range(2))<tol,(want,got,tol)
  return
 want=[tuple(map(dec,q)) for q in want]
 assert bool(got)==bool(want),(case,want,got)
 for q in want:assert min(max(abs(x-y) for x,y in zip(q,z)) for z in got)<tol,(case,want,got)
 if not want:return
 def dist2(q,u,v):
  dx=v[0]-u[0];dy=v[1]-u[1];d=dx*dx+dy*dy
  t=max(D(0),min(D(1),((q[0]-u[0])*dx+(q[1]-u[1])*dy)/d)) if d else D(0)
  return (q[0]-u[0]-t*dx)**2+(q[1]-u[1]-t*dy)**2
 for q in got:assert min(dist2(q,u,v) for u,v in zip(want,want[1:]+want[:1]))<tol*tol,(case,want,got)
 def area(poly):return abs(sum(cross(poly[0],u,v) for u,v in zip(poly,poly[1:]+poly[:1]))) if poly else D(0)
 assert abs(area(got)-area(want))<tol*max(span,D('1e-30'))*10,(case,want,got)
report={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 for form in ['header','ndebug','copied']:
  src=outdir/'copied.cpp' if form=='copied' else root/'tests/polygon_tools.cpp';exe=outdir/(mode+'-'+form)
  subprocess.run([CXX,'-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
  r=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,timeout=30);assert not r.stderr
  lines=r.stdout.splitlines();assert len(lines)==len(cases)
  for case,want,line in zip(cases,expected,lines):validate(case,want,line)
  report[mode+'-'+form]=dict(status='pass',cases=len(cases));print(mode,form,len(cases),'PASS',flush=True)
(root/'verification/polygon-tools-local.json').write_text(json.dumps(dict(long_double_digits=digits,coordinate_tolerance='1e-9*span + 2*epsilon*max_abs_coordinate + 1e-30',forms=report,oracles=['Cramer line intersections, retained vertices, exact rational hull','vertical strip area and first moments'],sources={name:hashlib.sha256((root/f'src/compact/{name}.hpp').read_bytes()).hexdigest() for name in ['convex_cut','polygon_centroid']}),indent=2)+'\n')
(outdir/'cases.json').write_text(json.dumps(dict(cases=[c for c in cases if len(c[1])<1000],expected=expected[:-2]),default=str))
