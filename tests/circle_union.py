"""Independent 70-digit vertical arrangement integration; no arc-cover sweep."""
from pathlib import Path
from itertools import combinations
import random, subprocess, json, hashlib, time
import mpmath as mp
mp.mp.dps=70
root=Path(__file__).resolve().parents[1]
build=root/'build/circle-union';build.mkdir(exist_ok=True)
def area(circles):
    a=[tuple(mp.mpf(str(v)) for v in c) for c in circles if c[2]>0]
    if not a:return mp.mpf(0)
    ox,oy,_=a[0]
    a=[(x-ox,y-oy,r) for x,y,r in a]
    events=[]
    for x,y,r in a:events.extend([x-r,x+r])
    for (x,y,r),(u,v,s) in combinations(a,2):
        dx=u-x;dy=v-y;q=dx*dx+dy*dy
        if not q or q>(r+s)**2 or q<(r-s)**2:continue
        k=(q+r*r-s*s)/(2*q)
        h=mp.sqrt(max(mp.mpf(0),r*r/q-k*k))
        events.extend([x+k*dx-h*dy,x+k*dx+h*dy])
    events=sorted(set(events));answer=mp.mpf(0)
    def cap(c,l,u):
        x,y,r=c
        def f(v):
            t=max(-r,min(r,v-x))
            return (t*mp.sqrt(max(mp.mpf(0),r*r-t*t))+r*r*mp.asin(t/r))/2
        return f(u)-f(l)
    for l,u in zip(events,events[1:]):
        if u-l<mp.mpf('1e-55'):continue
        mid=(l+u)/2;intervals=[]
        for i,(x,y,r) in enumerate(a):
            if abs(mid-x)>=r:continue
            h=mp.sqrt(r*r-(mid-x)**2)
            intervals.append((y-h,y+h,i))
        intervals.sort()
        groups=[]
        for low,high,i in intervals:
            if not groups or low>groups[-1][0]:groups.append([high,i,i])
            elif high>groups[-1][0]:groups[-1][0]=high;groups[-1][2]=i
        for _,bottom,top in groups:
            answer+=(a[top][1]-a[bottom][1])*(u-l)+cap(a[top],l,u)+cap(a[bottom],l,u)
    return answer

cases=[];expected=[]
def add(a,value=None):
    cases.append(a);expected.append(area(a) if value is None else mp.mpf(value))
add([]);add([(0,0,0)]);add([(7,-3,2)]);add([(0,0,2)]*7)
add([(0,0,5),(0,0,2),(3,0,2),(0,0,0)])
add([(0,0,1),(2,0,1)]);add([(0,0,1),(0,2,1)])
add([(0,0,1),(1,0,1)]);add([(0,0,1),(-1,0,1)])
# Hole in the union; full coverage of one boundary by several circles.
add([(0,0,5),(8,0,5),(8,8,5),(0,8,5)])
add([(0,0,1),(1,0,1),(-1,0,1),(0,1,1),(0,-1,1)])
for d in ['1.9999999999','2.0000000001','0.0000000001']:
    add([(0,0,1),(d,0,1)])
for d in ['0.9999999999','1.0000000001']:
    add([(0,0,2),(d,0,1)])
# Exhaustive triples from a small catalog, including equal/concentric circles.
catalog=[(0,0,0),(0,0,1),(0,0,2),(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(2,0,1),(1,1,1)]
for c in combinations(range(len(catalog)+2),3):
    ids=[c[0],c[1]-1,c[2]-2]
    add([catalog[i] for i in ids])
rng=random.Random(8073)
for k in range(180):
    a=[(rng.randint(-15,15),rng.randint(-15,15),rng.randint(0,12)) for _ in range(rng.randint(1,8))]
    value=area(a);add(a,value)
    if k<30:
        add(list(reversed(a)),value)
        add([(-y,x,r) for x,y,r in a],value)
        add([(x+10**12,y-10**12,r) for x,y,r in a],value)
        add([(x*3,y*3,r*3) for x,y,r in a],value*9)
        # Two far-separated copies with intersections within each component.
        add(a+[(x+10**12,y+10**12,r) for x,y,r in a],value*2)
# Known analytic stress cases, n=1000.
add([(i*3,0,1) for i in range(1000)],1000*mp.pi)
add([(0,0,1)]*1000,mp.pi)
add([(0,0,r) for r in range(1,1001)],10**6*mp.pi)
chain_value=1000*mp.pi-999*(2*mp.pi/3-mp.sqrt(3)/2)
add([(i,0,1) for i in range(1000)],chain_value)
# In a chain, non-neighbors only touch; adjacent lens overlaps have disjoint interiors.
text=str(len(cases))+'\n'+''.join(str(len(a))+'\n'+''.join(' '.join(map(str,c))+'\n' for c in a) for a in cases)
source=(root/'src/compact/circle_union.hpp').read_text()
plane=(root/'src/compact/real_plane.hpp').read_text().replace('#pragma once\n','')
body=source.split('// BEGIN circle_union_area\n')[1].split('// END circle_union_area')[0]
driver=(root/'tests/circle_union.cpp').read_text().split('\n',1)[1]
(build/'copied.cpp').write_text(plane+'\n'+body+driver)
reports={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
    for form in ['header','ndebug','copied']:
        src=build/'copied.cpp' if form=='copied' else root/'tests/circle_union.cpp'
        exe=build/f'{mode}-{form}'
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
        start=time.monotonic();out=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,timeout=60)
        assert not out.stderr,out.stderr
        lines=out.stdout.splitlines();assert len(lines)==len(cases)
        worst=0
        for k,(line,truth) in enumerate(zip(lines,expected)):
            v=mp.mpf(line);assert mp.isfinite(v)
            err=abs(v-truth)/(1+abs(truth));worst=max(worst,float(err))
            assert err<mp.mpf('1e-10'),(k,line,str(truth),str(err),cases[k])
        reports[f'{mode}-{form}']={'status':'pass','cases':len(cases),'max_scaled_error':worst,'seconds':round(time.monotonic()-start,3)}
        print(mode,form,len(cases),worst,'PASS',flush=True)
(root/'verification/circle-union-local.json').write_text(json.dumps({'status':'pass','oracle':'70-digit independent vertical decomposition at all circle extrema and pair intersection abscissas; analytic antiderivative of vertical envelopes; four analytic n=1000 stress cases','cases':len(cases),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'forms':reports},indent=2)+'\n')
(build/'cases.json').write_text(json.dumps({'cases':cases,'expected':[str(v) for v in expected]},indent=2)+'\n')
