"""Independent supporting-plane enumeration, facet planar hulls, mesh checks."""
from pathlib import Path
from itertools import combinations,product
import random,math,json,hashlib,subprocess,time
root=Path(__file__).resolve().parents[1];build=root/'build/hull3d';build.mkdir(exist_ok=True)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def normal(a,b,c):return cross(sub(b,a),sub(c,a))
def orient(a,b,c,d):return dot(normal(a,b,c),sub(d,a))
def plane_hull(points,ids,axis):
    drop=next(i for i,v in enumerate(axis) if v)
    proj=lambda i:tuple(v for j,v in enumerate(points[i]) if j!=drop)
    order=sorted(ids,key=proj)
    def turn(a,b,c):
        x,y=proj(a);u,v=proj(b);s,t=proj(c)
        return (u-x)*(t-y)-(v-y)*(s-x)
    def chain(order):
        out=[]
        for v in order:
            while len(out)>1 and turn(out[-2],out[-1],v)<=0:out.pop()
            out.append(v)
        return out
    return chain(order)[:-1]+chain(order[::-1])[:-1]
def oracle(input):
    p=sorted(set(input));n=len(p)
    if n<2:return n-1,0.0,0
    triple=next((t for t in combinations(range(n),3) if any(normal(*(p[i] for i in t)))),None)
    if triple is None:return 1,0.0,0
    v=normal(*(p[i] for i in triple))
    if all(orient(*(p[i] for i in triple),q)==0 for q in p):
        h=plane_hull(p,range(n),v)
        area=sum(math.sqrt(dot(w,w))/2 for i in range(1,len(h)-1) if (w:=normal(p[h[0]],p[h[i]],p[h[i+1]])))
        return 2,area,0
    planes={}
    for i,j,k in combinations(range(n),3):
        v=normal(p[i],p[j],p[k])
        if not any(v):continue
        d=dot(v,p[i]);s=[dot(v,q)-d for q in p]
        if min(s)<0<max(s):continue
        if min(s)>=0:v=tuple(-x for x in v);d=-d
        g=math.gcd(*v,d);key=tuple(x//g for x in v)+(d//g,)
        planes[key]=[i for i,q in enumerate(p) if dot(v,q)==d]
    area=0;volume6=0
    for key,ids in planes.items():
        v=key[:3];h=plane_hull(p,ids,v)
        if dot(normal(p[h[0]],p[h[1]],p[h[2]]),v)<0:h.reverse()
        for i in range(1,len(h)-1):
            a,b,c=(p[j] for j in (h[0],h[i],h[i+1]));w=normal(a,b,c)
            area+=math.sqrt(dot(w,w))/2
            volume6+=orient(p[0],a,b,c)
    return 3,area,volume6
cases=[];expected=[]
def add(p,value=None):cases.append(p);expected.append(oracle(p) if value is None else value)
add([]);add([(0,0,0)]*4);add([(i,i*2,-i) for i in range(-4,5)])
add([(x,y,0) for x,y in product(range(4),repeat=2)])
add([(x,y,2*x-3*y+7) for x,y in product(range(4),repeat=2)])
# All subsets of cube corners, exercises lower dimensions and coplanar faces.
cube=list(product([0,1],repeat=3))
for mask in range(256):add([v for i,v in enumerate(cube) if mask>>i&1])
rng=random.Random(4724)
for k in range(180):
    p=[tuple(rng.randrange(-4,5) for _ in range(3)) for _ in range(rng.randrange(4,13))]
    truth=oracle(p);add(p,truth)
    if k<30:
        add(p[::-1],truth)
        add(p+p[:3],truth)
        add([(x+999999990,y-999999990,z+999999990) for x,y,z in p],truth)
        add([(x*100000000,y*100000000,z*100000000) for x,y,z in p],(truth[0],truth[1]*10**16,truth[2]*10**24))
# Many coplanar faces/edges and an extension beyond a coplanar face.
add(list(product(range(3),repeat=3)))
add(cube+[(2,0,0),(2,1,0),(2,0,1),(2,1,1)])
add([(-10**9,-10**9,0),(10**9,-10**9,0),(-10**9,10**9,0),(10**9,10**9,0),(0,0,1)])
# 2000 points, mostly boundary grid, known cube hull.
p=[(x,y,z) for x,y,z in product(range(13),repeat=3) if 0 in (x,y,z) or 12 in (x,y,z)]
p=(p*3)[:2000];add(p,(3,864,10368))
text=str(len(cases))+'\n'+''.join(str(len(p))+'\n'+''.join(' '.join(map(str,v))+'\n' for v in p) for p in cases)
source=(root/'src/compact/hull3d.hpp').read_text()
body=source.split('// BEGIN Hull3D\n')[1].split('// END Hull3D')[0]
driver=(root/'tests/hull3d.cpp').read_text().split('\n',1)[1]
(build/'copied.cpp').write_text('#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'+body+driver)
reports={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
    for form in ['header','ndebug','copied']:
        src=build/'copied.cpp' if form=='copied' else root/'tests/hull3d.cpp';exe=build/f'{mode}-{form}'
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
        start=time.monotonic();result=subprocess.run([str(exe)],input=text,text=True,capture_output=True,timeout=90,check=True)
        assert not result.stderr,result.stderr
        lines=iter(result.stdout.splitlines())
        for case,(input,truth) in enumerate(zip(cases,expected)):
            for kind in ['integer','real']:
                row=next(lines).split();dim=int(row[0]);area=float(row[1]);vol=float(row[2]);n=int(row[3]);fcount=int(row[4])
                ids=list(map(int,next(lines).split()));assert len(ids)==n
                p=[input[i] for i in ids];assert p==sorted(set(input))
                assert all(i==input.index(input[i]) for i in ids)
                faces=[tuple(map(int,next(lines).split())) for _ in range(fcount)]
                b=list(map(int,next(lines).split()));assert b[0]==len(b)-1
                assert dim==truth[0],(case,kind,dim,truth)
                assert abs(area-truth[1])<=1e-9*(1+truth[1]),(case,kind,area,truth)
                assert abs(vol-truth[2])<=1e-9*(1+truth[2]),(case,kind,vol,truth)
                for f in faces:
                    assert len(set(f))==3 and all(0<=i<n for i in f)
                    assert any(normal(*(p[i] for i in f)))
                    if dim==3:assert all(orient(*(p[i] for i in f),q)<=0 for q in p),(case,kind,f)
                if dim==3:
                    edges={};vertices=set()
                    for f in faces:
                        vertices.update(f)
                        for i in range(3):
                            e=(f[i],f[(i+1)%3]);edges[e]=edges.get(e,0)+1
                    assert all(v==1 and edges.get((e[1],e[0]))==1 for e,v in edges.items()),(case,kind,'manifold')
                    assert len(vertices)-len(edges)//2+len(faces)==2,(case,kind,'Euler')
        assert next(lines,None) is None
        reports[f'{mode}-{form}']={'status':'pass','cases_per_numeric_type':len(cases),'seconds':round(time.monotonic()-start,3)}
        print(mode,form,len(cases),'both types PASS',flush=True)
(root/'verification/hull3d-local.json').write_text(json.dumps({'status':'pass','oracle':'Independent exact supporting-plane enumeration with planar hull facets; full mesh orientation, reverse-edge pairing and Euler checks','cases_per_numeric_type':len(cases),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'forms':reports},indent=2)+'\n')
