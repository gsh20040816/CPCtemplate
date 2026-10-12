from pathlib import Path
from fractions import Fraction as F
import random,subprocess,json,time,hashlib
from compiler_config import CXX
b=Path('build/minimum-rectangle');rng=random.Random(3187)
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def hull(p):
 p=sorted(set(p))
 def chain(p):
  q=[]
  for v in p:
   while len(q)>1 and cross(q[-2],q[-1],v)<=0:q.pop()
   q.append(v)
  return q
 return chain(p)[:-1]+chain(p[::-1])[:-1]
def oracle(p):
 h=hull(p);best=None
 for a,b in zip(h,h[1:]+h[:1]):
  dx=b[0]-a[0];dy=b[1]-a[1];ds=[dx*(x-a[0])+dy*(y-a[1]) for x,y in h];hs=[dx*(y-a[1])-dy*(x-a[0]) for x,y in h]
  v=F((max(ds)-min(ds))*(max(hs)-min(hs)),(dx*dx+dy*dy)*10**10)
  best=v if best is None else min(best,v)
 return best
cases=[[(100000,300000),(100000,400000),(200000,100000),(300000,0),(300000,600000),(600000,300000)]]
for i in range(220):
 p=[(rng.randrange(1000001),rng.randrange(1000001)) for _ in range(rng.randrange(3,60))]
 if oracle(p)>=F(1,10):cases.append(p)
cases+=[[(0,0),(1000000,0),(1000000,1000000),(0,1000000)]+[(rng.randrange(1000001),rng.randrange(1000001)) for _ in range(49996)]]
report={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
 exe=b/('driver-'+mode);subprocess.run([CXX,'-std=c++20',*flags,'verification/submitted/P3187.compact.cpp','-o',str(exe)],check=True)
 worst=0;durations=[]
 for p in cases:
  text=str(len(p))+'\n'+''.join(f'{x/100000:.5f} {y/100000:.5f}\n' for x,y in p)
  t=time.monotonic();r=subprocess.run([str(exe)],input=text,text=True,capture_output=True,timeout=5,check=True);durations.append(time.monotonic()-t);assert not r.stderr
  out=list(map(float,r.stdout.split()));assert len(out)==9
  v=oracle(p);err=abs(out[0]-float(v))/max(1,float(v));worst=max(worst,err);assert err<1e-8
  q=list(zip(out[1::2],out[2::2]));edges=[(q[(i+1)%4][0]-q[i][0],q[(i+1)%4][1]-q[i][1]) for i in range(4)]
  for i in range(4):
   assert min(cross(q[i],q[(i+1)%4],(x/100000,y/100000)) for x,y in p)>-1e-7
   assert abs(edges[i][0]*edges[(i+1)%4][0]+edges[i][1]*edges[(i+1)%4][1])<1e-7
  assert abs(cross(q[0],q[1],q[2])-out[0])<1e-7
 report[mode]=dict(cases=len(cases),worst_area_error=worst,large_case_seconds=durations[-1],status='pass')
 print(mode,len(cases),worst,'PASS',flush=True)
Path('verification/minimum-rectangle-driver.json').write_text(json.dumps(report,indent=2)+'\n')
