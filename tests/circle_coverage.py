"""70-digit vertical arrangement integral for every exact coverage multiplicity."""
from pathlib import Path
from itertools import combinations,combinations_with_replacement
import random,subprocess,json,hashlib,time,sys
import mpmath as mp
from compiler_config import CXX
mp.mp.dps=70
root=Path(__file__).resolve().parents[1];b=root/'build/circle-coverage';b.mkdir(exist_ok=True)
def areas(circles):
 a=[tuple(mp.mpf(str(v)) for v in c) for c in circles if mp.mpf(str(c[2]))>0]
 ans=[mp.mpf(0)]*(len(circles)+1)
 if not a:return ans
 ox,oy,_=a[0];a=[(x-ox,y-oy,r) for x,y,r in a];events=[]
 for x,y,r in a:events.extend([x-r,x+r])
 for (x,y,r),(u,v,s) in combinations(a,2):
  dx=u-x;dy=v-y;q=dx*dx+dy*dy
  if not q or q>(r+s)**2 or q<(r-s)**2:continue
  k=(q+r*r-s*s)/(2*q);h=mp.sqrt(max(mp.mpf(0),r*r/q-k*k))
  events.extend([x+k*dx-h*dy,x+k*dx+h*dy])
 def cap(c,l,u):
  x,y,r=c
  def f(v):
   t=max(-r,min(r,v-x))
   return (t*mp.sqrt(max(mp.mpf(0),r*r-t*t))+r*r*mp.asin(t/r))/2
  return f(u)-f(l)
 events=sorted(set(events))
 for l,u in zip(events,events[1:]):
  if u-l<mp.mpf('1e-55'):continue
  mid=(l+u)/2;ys=[]
  for i,(x,y,r) in enumerate(a):
   if abs(mid-x)>=r:continue
   h=mp.sqrt(r*r-(mid-x)**2)
   ys.extend([(y-h,1,i,-1),(y+h,-1,i,1)])
  ys.sort();count=0
  for low,high in zip(ys,ys[1:]):
   count+=low[1]
   if count==0 or low[0]==high[0]:continue
   lo,hi=low[2],high[2]
   ans[count]+=(a[hi][1]-a[lo][1])*(u-l)+high[3]*cap(a[hi],l,u)-low[3]*cap(a[lo],l,u)
 return ans
cases=[];expected=[]
def add(c,v=None):
 cases.append(c);expected.append(areas(c) if v is None else v)
add([]);add([(0,0,0)]*5);add([(7,-3,2)]);add([(0,0,2)]*7)
add([(0,0,5),(0,0,2),(3,0,2),(0,0,0)])
add([(0,0,5),(8,0,5),(8,8,5),(0,8,5)])
for d in ['0','0.0000000001','0.9999999999','1','1.0000000001','1.9999999999','2','2.0000000001']:
 add([(0,0,1),(d,0,1)]);add([(0,0,2),(d,0,1)])
catalog=[(0,0,0),(0,0,1),(0,0,2),(1,0,1),(-1,0,1),(0,1,1),(2,0,1)]
for ids in combinations_with_replacement(range(len(catalog)),4):add([catalog[i] for i in ids])
rng=random.Random(71949)
for it in range(130):
 c=[(rng.randint(-8,8),rng.randint(-8,8),rng.randint(0,7)) for _ in range(rng.randint(1,8))]
 if it%3==0:c+=c[:2]
 v=areas(c);add(c,v)
 if it<20:
  add(list(reversed(c)),v)
  add([(-y,x,r) for x,y,r in c],v)
  add([(x+10**12,y-10**12,r) for x,y,r in c],v)
  add([(3*x,3*y,3*r) for x,y,r in c],[x*9 for x in v])
  add(c+[(x+10**12,y+10**12,r) for x,y,r in c],[x*2 for x in v]+[mp.mpf(0)]*len(c))
n=1000
add([(3*i,0,1) for i in range(n)],[mp.mpf(0),n*mp.pi]+[mp.mpf(0)]*(n-1))
add([(0,0,1)]*n,[mp.mpf(0)]*n+[mp.pi])
add([(0,0,i) for i in range(1,n+1)],[mp.mpf(0)]+[mp.pi*(2*(n-k)+1) for k in range(1,n+1)])
lens=2*mp.pi/3-mp.sqrt(3)/2
add([(i,0,1) for i in range(n)],[mp.mpf(0),n*mp.pi-2*(n-1)*lens,(n-1)*lens]+[mp.mpf(0)]*(n-2))
text=str(len(cases))+'\n'+''.join(str(len(c))+'\n'+''.join(' '.join(map(str,q))+'\n' for q in c) for c in cases)
source=(root/'src/compact/circle_coverage.hpp').read_text();plane=(root/'src/compact/real_plane.hpp').read_text().replace('#pragma once\n','')
body=source.split('// BEGIN circle_coverage_area\n')[1].split('// END circle_coverage_area')[0]
driver=(root/'tests/circle_coverage.cpp').read_text().split('\n',1)[1]
(b/'copied.cpp').write_text(plane+'\n'+body+driver)
reports={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 for form in ['header','ndebug','copied']:
  src=b/'copied.cpp' if form=='copied' else root/'tests/circle_coverage.cpp';exe=b/f'{mode}-{form}'
  subprocess.run([CXX,'-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
  p=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,timeout=120)
  assert not p.stderr,p.stderr
  lines=p.stdout.splitlines();assert len(lines)==len(cases);worst=0
  for i,(line,v) in enumerate(zip(lines,expected)):
   got=list(map(mp.mpf,line.split()));assert len(got)==len(v)
   for k,(x,y) in enumerate(zip(got,v)):
    err=abs(x-y)/(1+abs(y));worst=max(worst,float(err));assert mp.isfinite(x) and err<mp.mpf('1e-9'),(i,k,str(x),str(y),cases[i])
   total=sum(mp.pi*mp.mpf(str(c[2]))**2 for c in cases[i])
   assert abs(sum(k*x for k,x in enumerate(got))-total)/(1+total)<mp.mpf('1e-10')
  reports[f'{mode}-{form}']=dict(status='pass',cases=len(cases),max_scaled_error=worst)
  print(mode,form,len(cases),worst,'PASS',flush=True)
(root/'verification/circle-coverage-local.json').write_text(json.dumps(dict(status='pass',oracle='70-digit vertical arrangement, per-level analytic integrals; four1000circle closed forms; weighted area conservation',source_sha256=hashlib.sha256(source.encode()).hexdigest(),forms=reports),indent=2)+'\n')
(b/'cases.json').write_text(json.dumps(dict(cases=cases,expected=[[str(x) for x in v] for v in expected]),indent=2)+'\n')
