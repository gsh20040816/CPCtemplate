"""Official CGL_4_C protocol, exact implicit-line oracle; centroid demo protocol."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D
import subprocess,random,json,sys
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from usage_examples import expand
# Load only the exact reference definitions, not the production-test execution.
source=(root/'tests/polygon_tools.py').read_text()
# Functions share a common globals mapping for hull/cross dependencies.
g={'F':F};exec(source[source.index('def cross'):source.index('rng=random.Random')],g)
hull=g['hull'];cut=g['cut'];rng=random.Random(40419)
def area(p):
 return abs(sum((F(a[0])*b[1]-F(a[1])*b[0] for a,b in zip(p,p[1:]+p[:1])),F(0)))/2
cases=[([(1,1),(4,1),(4,3),(1,3)],[((2,0),(2,4)),((2,4),(2,0))])]
for it in range(180):
 p=hull([(rng.randint(-10000,10000),rng.randint(-10000,10000)) for _ in range(rng.randint(3,100))])
 queries=[]
 for j in range(40):
  a=(rng.randint(-10000,10000),rng.randint(-10000,10000));b=(rng.randint(-10000,10000),rng.randint(-10000,10000))
  if a!=b:queries.append((a,b))
 queries += list(zip(p,p[1:]+p[:1]))[:20]
 cases.append((p,queries))
# Exactly 100 distinct weakly convex boundary points, 100 queries.
p=[(-10000+i*800,-10000) for i in range(25)]+[(10000,-10000+i*800) for i in range(25)]+[(10000-i*800,10000) for i in range(25)]+[(-10000,10000-i*800) for i in range(25)]
cases.append((p,[((-10000,y),(10000,y)) for y in range(-10000,10000,200)]))
prepared=[]
for p,qs in cases:
 text=str(len(p))+'\n'+''.join(f'{x} {y}\n' for x,y in p)+str(len(qs))+'\n'+''.join(f'{a[0]} {a[1]} {b[0]} {b[1]}\n' for a,b in qs)
 prepared.append((text,[area(cut(p,a,b)) for a,b in qs]))
out=root/'build/polygon-tools';report={}
for name,path in [('cut','verify/aoj/CGL_4_C.compact.cpp'),('centroid','docs/usage-drivers/polygon-centroid-demo.cpp')]:
 f=root/path;cpp=out/(name+'-driver.cpp');cpp.write_text(expand(f.read_text(),f.parent,set()))
 for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
  exe=out/(name+'-driver-'+mode);subprocess.run([CXX,'-std=c++20',*flags,str(cpp),'-o',str(exe)],check=True)
  worst=D(0)
  if name=='cut':
   for text,expected in prepared:
    r=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,timeout=10);assert not r.stderr
    values=list(map(D,r.stdout.split()));assert len(values)==len(expected)
    for actual,v in zip(values,expected):
     err=abs(actual-D(v.numerator)/D(v.denominator));worst=max(worst,err);assert err<D('0.000001'),(err,text)
  else:
   for text,expected in [('3\n0 0\n6 0\n0 3\n',[2,1]),('6\n0 0\n4 0\n4 1\n1 1\n1 3\n0 3\n',[1.5,1]),('3\n0 0\n1 1\n2 2\n',None),('0\n',None)]:
    r=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,timeout=10);assert not r.stderr
    if expected is None:assert r.stdout.strip()=='Undefined'
    else:assert all(abs(a-b)<1e-9 for a,b in zip(map(float,r.stdout.split()),expected)),r.stdout
  report[name+'-'+mode]={'status':'pass','max_absolute_area_error':str(worst)}
report.update({'cut_protocol_cases':len(cases),'cut_queries':sum(len(q) for p,q in cases),'centroid_demo_cases':4,'online':'not submitted; AOJ sign-in has no saved account'})
(root/'verification/polygon-tools-driver.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
