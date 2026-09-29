"""Independent exact ray parity and hull intersection; full geometry drivers."""
from compiler_config import CXX
from pathlib import Path
from itertools import combinations
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
mode = 'san' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-std=c++20', '-O2'] if mode == 'normal' else ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
rng = random.Random(20260929)


def compile(source, name, bundle=True):
    exe = root / f'build/{name}-{mode}'
    if bundle:
        dest = exe.with_suffix('.cpp')
        subprocess.run(['python3', str(root/'tools/bundle.py'), str(root/source), str(dest)], check=True)
    else:
        dest = root/source
    subprocess.run([CXX, *flags, str(dest), '-o', str(exe)], check=True)
    return exe


def run(exe, data):
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=60)
    assert not p.stderr, p.stderr
    return p.stdout.split()


def points(p):
    return ''.join(f'{x} {y}\n' for x, y in p)


def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def on(a, b, q):
    return cross(a,b,q)==0 and all(min(a[k],b[k])<=q[k]<=max(a[k],b[k]) for k in (0,1))


def inside(p, q):
    if not p: return 0
    edges = list(zip(p, p[1:]+p[:1]))
    if any(on(a,b,q) for a,b in edges): return 1
    # Choose an oblique ray through no polygon vertex. Its far endpoint is
    # outside the bounding box. Count proper segment crossings, not winding.
    s = 1
    while any(v[1]-q[1] == s*(v[0]-q[0]) for v in p): s += 1
    reach = max(abs(v[0]-q[0]) for v in p)+1
    far = (q[0]+reach, q[1]+s*reach)
    hits = sum(cross(q,far,a)*cross(q,far,b)<0 and cross(a,b,q)*cross(a,b,far)<0 for a,b in edges)
    return 2 if hits%2 else 0


def hull(p):
    # Gift wrapping, independent of the library's monotone chain.
    p = sorted(set(p))
    if len(p)<2: return p
    h, i = [], 0
    while not h or i:
        h.append(p[i])
        j = (i+1)%len(p)
        for k in range(len(p)):
            c = cross(p[i],p[j],p[k])
            d = lambda t: sum((p[t][a]-p[i][a])**2 for a in (0,1))
            if c<0 or c==0 and d(k)>d(j): j=k
        i=j
    return h


probe = compile('tests/polygon_probe.cpp', 'polygon-probe', False)
aoj = compile('verify/aoj/CGL_3_C.compact.cpp', 'polygon-aoj')
war = compile('verify/luogu/P4557.compact.cpp', 'polygon-war')
closest = compile('verify/library_checker/closest_pair.compact.cpp', 'closest-driver')
squared = compile('verify/luogu/P7883.compact.cpp', 'closest-squared')
core, wants = [], []


def add(p, qs, convex=0):
    core.append(f'{len(p)} {len(qs)} {convex}\n'+points(p)+points(qs))
    for q in qs:
        v = str(inside(p,q))
        wants.extend([v, v] if convex==1 else [v])


# Exhaustive subsets include empty/single-point/segment hulls, all cyclic starts.
grid = [(x,y) for x in range(-1,2) for y in range(-1,2)]
queries = [(x,y) for x in range(-2,3) for y in range(-2,3)]
for mask in range(512):
    h = hull([p for i,p in enumerate(grid) if mask>>i&1])
    for shift in range(max(1,len(h))): add(h[shift:]+h[:shift],queries,1)

# Simple nonconvex x-monotone boundaries; test both orientations and vertices.
shapes = [[(0,0),(6,0),(6,6),(4,6),(4,2),(2,2),(2,6),(0,6)]]
for _ in range(160):
    xs = sorted(rng.sample(range(-12,13),rng.randrange(3,12)))
    lo = [(x,-rng.randrange(1,9)) for x in xs]
    hi = [(x,rng.randrange(1,9)) for x in xs[::-1]]
    shapes.append(lo+hi)
for p in shapes:
    qs = p+[(rng.randrange(-14,15),rng.randrange(-10,11)) for _ in range(80)]
    qs += [(a[0]+b[0],a[1]+b[1]) for a,b in zip(p,p[1:]+p[:1])]
    for rev in [False,True]:
        poly = p[::-1] if rev else p
        add(poly,qs)
        # AOJ input is counterclockwise; the core separately accepts both.
        if not rev:
            inp=f'{len(poly)}\n'+points(poly)+f'{len(qs)}\n'+points(qs)
            assert run(aoj,inp)==[str(inside(poly,q)) for q in qs]
    scale=10**10
    add([(x*scale+123,y*scale-456) for x,y in p],[(x*scale+123,y*scale-456) for x,y in qs])
assert run(probe,str(len(core))+'\n'+''.join(core)) == wants
sample='4\n0 0\n3 1\n2 3\n0 3\n3\n2 1\n0 2\n3 2\n'
assert run(aoj,sample)==['2','1','0']
# AOJ maximum n and q, with allowed collinear boundary vertices.
p=[(x,0) for x in range(49)]+[(48,48)]+[(x,48) for x in range(47,-1,-1)]+[(0,24),(0,12)]
assert len(p)==100
qs=[(rng.randrange(-2,51),rng.randrange(-2,51)) for _ in range(1000)]
assert run(aoj,'100\n'+points(p)+'1000\n'+points(qs))==[str(inside(p,q)) for q in qs]
# 100001 strict hull vertices; O(n) per query would make this unusable.
h=[(x,x*x) for x in range(-50000,50001)]
qs=h+[(x,x*x-1) for x in range(-50000,50001)]+[(x,x*x+1) for x in range(-49999,50000)]
expected=['1']*len(h)+['0']*len(h)+['2']*99999
assert run(probe,'1\n'+f'{len(h)} {len(qs)} 2\n'+points(h)+points(qs))==expected
print('Polygon containment: all 512 grid subset hulls/cyclic starts, 161 simple boundaries including concave cases in both orientations and translated trillion-scale inputs, AOJ sample/max shape and 100001-vertex/300001-query convex search PASS',flush=True)


def intersect(a,b):
    if any(inside(a,p) for p in b) or any(inside(b,p) for p in a): return True
    for u,v in zip(a,a[1:]+a[:1]):
        for x,y in zip(b,b[1:]+b[:1]):
            if cross(u,v,x)*cross(u,v,y)<0 and cross(x,y,u)*cross(x,y,v)<0: return True
    return False


# Compare translated hull intersection directly, without constructing differences.
for case in range(180):
    pool=rng.sample([(x,y) for x in range(-9,10) for y in range(-9,10)],40)
    a,b=pool[:20],pool[20:]
    ha,hb=hull(a),hull(b)
    assert len(ha)>=3 and len(hb)>=3
    qs=[(rng.randrange(-40,41),rng.randrange(-40,41)) for _ in range(60)]
    qs += [(x-u,y-v) for x,y in ha for u,v in hb]
    expected=[str(int(intersect(ha,[(x+dx,y+dy) for x,y in hb]))) for dx,dy in qs]
    data=f'{len(a)} {len(b)} {len(qs)}\n'+points(a)+points(b)+points(qs)
    assert run(war,data)==expected,(case,qs)
# Maximum original input size, 100000 distinct points in each rectangle.
a=[(2*x,2*y) for x in range(500) for y in range(200)]
b=[(x+10001,y+10001) for x,y in a]
qs=[(-10001+dx,-10001+dy) for dx,dy in [(0,0),(998,398),(999,0),(0,399),(-998,-398)]]
qs=(qs*20000)
assert run(war,'100000 100000 100000\n'+points(a)+points(b)+points(qs))==['1','1','0','0','1']*20000
print('Minkowski difference full P4557 driver: 180 independent translated-hull intersection cases including boundary differences, 100000+100000 distinct points and 100000 queries PASS',flush=True)


def cp(cases, known=None):
    out=list(map(int,run(closest,str(len(cases))+'\n'+''.join(str(len(p))+'\n'+points(p) for p in cases))))
    assert len(out)==2*len(cases)
    for t,p in enumerate(cases):
        i,j=out[2*t:2*t+2]
        assert 0<=i<len(p) and 0<=j<len(p) and i!=j
        dist=lambda a,b:sum((a[k]-b[k])**2 for k in (0,1))
        best=known[t] if known is not None else min(dist(a,b) for a,b in combinations(p,2))
        assert dist(p[i],p[j])==best


cases=[]
for t in range(1600):
    bound=20 if t%2 else 10**9
    cases.append([(rng.randint(-bound,bound),rng.randint(-bound,bound)) for _ in range(rng.randrange(2,36))])
cp(cases)
cp([[(0,0)]*500000],[0])
cp([[(1000000000,-1000000000+3*i) for i in range(500000)]],[9])
cp([[(-10**9,-10**9),(10**9,10**9)]]*100000,[8*10**18]*100000)
print('Closest-pair complete driver: 1600 Python integer pair-enumeration cases, 500000 duplicates/collinear points, 100000-case reset and extreme coordinates PASS',flush=True)

for _ in range(200):
    p = rng.sample([(x,y) for x in range(-10,11) for y in range(-10,11)],rng.randrange(2,40))
    want = min(sum((a[k]-b[k])**2 for k in (0,1)) for a,b in combinations(p,2))
    assert run(squared,str(len(p))+'\n'+points(p))==[str(want)]
p=[(-10000000,-10000000),(10000000,10000000)]
assert run(squared,'2\n'+points(p))==['800000000000000']
p=[(10000000,-10000000+3*i) for i in range(400000)]
assert run(squared,'400000\n'+points(p))==['9']
print('Existing P7883 full driver: 200 unique-point pair-enumeration inputs, 400000-point maximum and 8e14 squared-distance boundary PASS',flush=True)
