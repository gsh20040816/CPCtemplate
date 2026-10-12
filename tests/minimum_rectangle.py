"""Independent rational edge enumeration, including returned rectangle witnesses."""
from pathlib import Path
from fractions import Fraction as F
import random,json,subprocess,hashlib,math,time
from decimal import Decimal as D,getcontext
from compiler_config import CXX
getcontext().prec=60
root=Path(__file__).resolve().parents[1];b=root/'build/minimum-rectangle';b.mkdir(exist_ok=True)
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def hull(p):
 p=sorted(set(p))
 if len(p)<2:return p
 def chain(a):
  q=[]
  for v in a:
   while len(q)>1 and cross(q[-2],q[-1],v)<=0:q.pop()
   q.append(v)
  return q
 return chain(p)[:-1]+chain(p[::-1])[:-1]
def oracle(p):
 if len(p)<3:return F(0)
 areas=[]
 for a,b in zip(p,p[1:]+p[:1]):
  x=b[0]-a[0];y=b[1]-a[1]
  dot=[x*(q[0]-a[0])+y*(q[1]-a[1]) for q in p]
  height=[x*(q[1]-a[1])-y*(q[0]-a[0]) for q in p]
  areas.append(F((max(dot)-min(dot))*(max(height)-min(height)),x*x+y*y))
 return min(areas)
rng=random.Random(3187780);cases=[];truth=[]
def add(p,v=None):
 cases.append(p);truth.append(oracle(p) if v is None else v)
grid=[(i,j) for i in range(-1,2) for j in range(-1,2)]
for mask in range(512):add(hull([p for i,p in enumerate(grid) if mask>>i&1]))
for it in range(1800):
 h=hull([(rng.randint(-1000000,1000000),rng.randint(-1000000,1000000)) for _ in range(rng.randint(3,35))]);add(h)
 if it<100:
  k=rng.randrange(len(h));add(h[k:]+h[:k]);add([(-y,x) for x,y in h]);add([(x+10**12,y-10**12) for x,y in h]);add([(x*3,y*3) for x,y in h])
  add([(str(D(x)/D(1024)),str(D(y)/D(1024))) for x,y in h],oracle(h)/1024**2)
  add([(str(D(x)/D(10**12)),str(D(y)/D(10**12))) for x,y in h],oracle(h)/10**24)
# Thin hulls, long parallel supports and negative coordinates.
for k in [1,2,10,1000000,10**12]:
 add(hull([(0,0),(k,1),(k+1,1),(1,0)]))
 add(hull([(0,0),(k,1),(2*k,3),(k,2)]))
n=50000
add([(math.cos(2*math.pi*i/n),math.sin(2*math.pi*i/n)) for i in range(n)],4*math.cos(math.pi/n)**2)
text=str(len(cases))+'\n'+''.join(str(len(p))+'\n'+''.join(f'{x} {y}\n' for x,y in p) for p in cases)
source=(root/'src/compact/minimum_rectangle.hpp').read_text();plane=(root/'src/compact/real_plane.hpp').read_text().replace('#pragma once\n','');body=source.split('// BEGIN minimum_rectangle\n')[1].split('// END minimum_rectangle')[0];driver=(root/'tests/minimum_rectangle.cpp').read_text().split('\n',1)[1]
(b/'copied.cpp').write_text(plane+'\n'+body+driver)
def dec(v):return D(v.numerator)/D(v.denominator) if isinstance(v,F) else D(str(v))
def validate(p,line,expected):
 v=list(map(D,line.split()));assert len(v)==9 and all(x.is_finite() for x in v)
 area=v[0];q=list(zip(v[1::2],v[2::2]));expected=dec(expected)
 assert abs(area-expected)/max(D('1e-100'),abs(expected))<D('1e-9'),(area,expected,p[:10])
 if len(p)<3:return
 p=[(D(str(x)),D(str(y))) for x,y in p];span=max(max(x for x,y in p)-min(x for x,y in p),max(y for x,y in p)-min(y for x,y in p));tol=D('1e-7')*span*span
 e=[(q[(i+1)%4][0]-q[i][0],q[(i+1)%4][1]-q[i][1]) for i in range(4)]
 for i in range(4):
  assert min(cross(q[i],q[(i+1)%4],v) for v in p)>=-tol
  assert abs(e[i][0]*e[(i+1)%4][0]+e[i][1]*e[(i+1)%4][1])<=tol
 assert abs(cross(q[0],q[1],q[2])-area)<=tol
 assert all(abs(e[0][j]+e[2][j])<=D('1e-6')*span and abs(e[1][j]+e[3][j])<=D('1e-6')*span for j in range(2))
report={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 for form in ['header','ndebug','copied']:
  src=b/'copied.cpp' if form=='copied' else root/'tests/minimum_rectangle.cpp';exe=b/(mode+'-'+form)
  subprocess.run([CXX,'-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
  t=time.monotonic();r=subprocess.run([str(exe)],input=text,text=True,capture_output=True,timeout=25,check=True);elapsed=time.monotonic()-t
  assert not r.stderr,r.stderr
  lines=r.stdout.splitlines();assert len(lines)==len(cases)
  for p,line,v in zip(cases,lines,truth):validate(p,line,v)
  report[mode+'-'+form]=dict(status='pass',cases=len(cases),runtime_seconds=elapsed)
  print(mode,form,len(cases),elapsed,'PASS',flush=True)
(root/'verification/minimum-rectangle-local.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.encode()).hexdigest(),oracle='exact Fraction scan of all points for each hull edge; rectangle containment, orthogonality, area and CCW checks; 50000-vertex regular polygon',forms=report),indent=2)+'\n')
(b/'cases.json').write_text(json.dumps(dict(cases=cases[:-1],truth=[str(v) for v in truth[:-1]])))
