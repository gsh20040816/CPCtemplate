"""Exact independent vertical decomposition for arbitrary simple polygons."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations, combinations_with_replacement
import random, math, json, subprocess, time, hashlib
root=Path(__file__).resolve().parents[1]
build=root/'build/polygon-union';build.mkdir(exist_ok=True)
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def clean(p):
    q=[]
    for v in p:
        if not q or q[-1]!=v:q.append(v)
    if len(q)>1 and q[0]==q[-1]:q.pop()
    if len(q)<3 or sum(cross((0,0),u,v) for u,v in zip(q,q[1:]+q[:1]))==0:return []
    return q

def area(polygons):
    polygons=[q for p in polygons if (q:=clean(p))]
    edges=[(p[i],p[(i+1)%len(p)]) for p in polygons for i in range(len(p))]
    events={F(v[0]) for p in polygons for v in p}
    for (a,b),(c,d) in combinations(edges,2):
        x=cross(a,b,c);y=cross(a,b,d)
        den=y-x
        if not den:continue
        t=F(cross(c,d,a),den)
        s=F(-x,den)
        if 0<=t<=1 and 0<=s<=1:events.add(F(a[0])+t*(b[0]-a[0]))
    events=sorted(events);ans=F(0)
    def line(a,b):
        slope=F(b[1]-a[1],b[0]-a[0]);return slope,F(a[1])-slope*a[0]
    def value(e,x):return e[0]*x+e[1]
    for l,r in zip(events,events[1:]):
        mid=(l+r)/2;intervals=[]
        for p in polygons:
            cuts=[]
            for a,b in zip(p,p[1:]+p[:1]):
                if min(a[0],b[0])<mid<max(a[0],b[0]):
                    e=line(a,b);cuts.append((value(e,mid),e))
            cuts.sort();assert len(cuts)%2==0
            for i in range(0,len(cuts),2):intervals.append((cuts[i][0],cuts[i+1][0],cuts[i][1],cuts[i+1][1]))
        intervals.sort();groups=[]
        for low,high,lo,hi in intervals:
            if not groups or low>groups[-1][0]:groups.append([high,lo,hi])
            elif high>groups[-1][0]:groups[-1][0]=high;groups[-1][2]=hi
        for _,lo,hi in groups:
            ans+=(value(hi,l)+value(hi,r)-value(lo,l)-value(lo,r))*(r-l)/2
    return ans

def rectangle(x,y,w,h):return [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
cases=[];expected=[]
def add(a,v=None):cases.append(a);expected.append(area(a) if v is None else F(v))
add([]);add([[],[(1,2)],[(0,0),(1,1),(2,2)]])
rects=[rectangle(x,y,w,h) for x,y,w,h in [(0,0,2,2),(1,0,2,2),(2,0,2,2),(0,2,2,2),(1,1,1,1),(0,0,1,1),(0,0,4,4)]]
for ids in combinations_with_replacement(range(len(rects)),3):add([rects[i] for i in ids])
# Four bars form a hole; shared edges of equal/opposite directions.
add([rectangle(0,0,4,1),rectangle(0,3,4,1),rectangle(0,1,1,2),rectangle(3,1,1,2)],12)
L=[(0,0),(4,0),(4,1),(1,1),(1,4),(0,4)]
add([L,list(reversed(L))]);add([L,rectangle(1,1,2,2)])
add([[(0,0),(1,0),(2,0),(2,2),(0,2),(0,0)],rectangle(0,0,1,1)])
add([[(0,0),(0,0),(4,0),(0,4)],[(0,4),(0,0),(4,0)]])
comb=[(-2,-2),(2,-2),(2,2),(1,2),(1,-1),(0,-1),(0,2),(-1,2),(-1,-1),(-2,-1)]
add([comb]);add([comb,list(reversed(comb))])
add([comb,rectangle(-3,0,6,1)])
add([comb,[(x+1,y+1) for x,y in comb]])
# Rational intersections, extreme coordinates, disjoint far components.
add([[(-10**9,-10**9),(10**9,-10**9),(0,10**9)],[(-10**9,10**9),(10**9,10**9),(0,-10**9)]])
add([[(0,0),(7,2),(1,8)],[(0,6),(8,0),(9,8)]])
rng=random.Random(13338)
for k in range(200):
    a=[]
    for _ in range(rng.randint(1,5)):
        if rng.randrange(3)==0:
            x=rng.randrange(-10,11);y=rng.randrange(-10,11)
            p=[(u+x,v+y) for u,v in L]
        else:
            while True:
                p=[(rng.randrange(-10,11),rng.randrange(-10,11)) for _ in range(3)]
                if cross(*p):break
        if rng.randrange(2):p.reverse()
        a.append(p)
    v=area(a);add(a,v)
    if k<25:
        add(list(reversed(a)),v)
        add([[(-y,x) for x,y in p] for p in a],v)
        add([[(x+999999000,y-999999000) for x,y in p] for p in a],v)
        add([[(x*7,y*7) for x,y in p] for p in a],v*49)
        add([[(x*50000000,y*50000000) for x,y in p] for p in a],v*2500000000000000)
        add(a+[[(x+999999000,y+999999000) for x,y in p] for p in a],v*2)
add([[ (i*3,0),(i*3+1,0),(i*3,1)] for i in range(1000)],500)
add([[ (0,0),(2,0),(0,2)]]*1000,2)
add([[ (0,0),(i,0),(0,i)] for i in range(1,1001)],500000)
text=str(len(cases))+'\n'
for a in cases:
    text+=str(len(a))+'\n'
    for p in a:text+=str(len(p))+'\n'+''.join(f'{x} {y}\n' for x,y in p)
source=(root/'src/compact/polygon_union.hpp').read_text()
plane=(root/'src/compact/integer_plane.hpp').read_text().replace('#pragma once\n','')
body=source.split('// BEGIN polygon_union_area\n')[1].split('// END polygon_union_area')[0]
driver=(root/'tests/polygon_union.cpp').read_text().split('\n',1)[1]
(build/'copied.cpp').write_text(plane+'\n'+body+driver)
reports={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
    for form in ['header','ndebug','copied']:
        exe=build/f'{mode}-{form}';src=build/'copied.cpp' if form=='copied' else root/'tests/polygon_union.cpp'
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
        start=time.monotonic();out=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,timeout=120)
        assert not out.stderr,out.stderr
        lines=out.stdout.splitlines();assert len(lines)==len(cases)
        worst=0
        for k,(line,v) in enumerate(zip(lines,expected)):
            observed=F(line);err=abs(observed-v)/(1+abs(v));worst=max(worst,float(err))
            assert err<F(1,10**10),(k,line,v,float(err),cases[k])
        reports[f'{mode}-{form}']={'status':'pass','cases':len(cases),'max_scaled_error':worst,'seconds':round(time.monotonic()-start,3)}
        print(mode,form,len(cases),worst,'PASS',flush=True)
(root/'verification/polygon-union-local.json').write_text(json.dumps({'status':'pass','oracle':'Exact Fraction vertical strip decomposition and linear envelope trapezoids; no boundary coverage sweep; three n=1000 analytic stress cases','cases':len(cases),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'forms':reports},indent=2)+'\n')
(build/'cases.json').write_text(json.dumps({'cases':cases,'expected':[str(v) for v in expected]},indent=2)+'\n')
