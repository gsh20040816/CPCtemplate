"""AOJ D/E/H/I complete programs; 80-digit independent geometric oracles.
Run with build/tools-env/bin/python (mpmath); CPC_SANITIZE=1 enables sanitizers.
"""
from compiler_config import CXX
from pathlib import Path
import hashlib
import json
import math
import os
import random
import subprocess
import mpmath as mp

mp.mp.dps = 80
root = Path(__file__).resolve().parents[1]
mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
exe = {}
for letter in 'DEHI':
    exe[letter] = root / f'build/circle-{letter}-{mode}'
    subprocess.run([CXX, '-std=c++20', *flags, str(root / f'verify/aoj/CGL_7_{letter}.compact.cpp'), '-o', str(exe[letter])], check=True)
counts = dict.fromkeys('DEHI', 0)
worst = dict.fromkeys('DEHI', mp.mpf(0))


def validate(output, expected, tolerance):
    got = [mp.mpf(x) for x in output.split()]
    assert len(got) == len(expected)
    assert all(mp.isfinite(x) for x in got)
    error = max(abs(x - y) for x, y in zip(got, expected))
    assert error < tolerance, (output, expected, error)
    return error


def run(letter, data, expected):
    p = subprocess.run([str(exe[letter])], input=data, text=True, capture_output=True, check=True, timeout=30)
    assert not p.stderr, p.stderr
    tolerance = mp.mpf('1e-5' if letter == 'H' else '1e-6')
    worst[letter] = max(worst[letter], validate(p.stdout, expected, tolerance))
    counts[letter] += len(expected) // 4 if letter == 'D' else 1


def ordered(points):
    return [v for p in sorted(points) for v in p]


def line_reference(a, b, o, r):
    x, y = b[0] - a[0], b[1] - a[1]
    u, v = a[0] - o[0], a[1] - o[1]
    aa, bb, cc = x*x + y*y, 2*(x*u+y*v), u*u+v*v-r*r
    d = bb*bb-4*aa*cc
    if aa == 0 or d < 0:
        return None
    ts = [(-bb + sign*mp.sqrt(d))/(2*aa) for sign in [-1, 1]]
    return ordered([(a[0]+t*x, a[1]+t*y) for t in ts])


def circle_reference(a, r, b, s):
    x, y = b[0]-a[0], b[1]-a[1]
    q = x*x+y*y
    if not q or not (r-s)**2 <= q <= (r+s)**2:
        return None
    d = mp.sqrt(q)
    t = (mp.mpf(q)+r*r-s*s)/(2*d)
    h = mp.sqrt(max(0, r*r-t*t))
    return ordered([(a[0]+t*x/d-sign*h*y/d, a[1]+t*y/d+sign*h*x/d) for sign in [-1, 1]])


def lens(a, r, b, s):
    d = mp.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)
    if d >= r+s:
        return mp.mpf(0)
    if d <= abs(r-s):
        return mp.pi*min(r,s)**2
    x = mp.acos((d*d+r*r-s*s)/(2*d*r))
    y = mp.acos((d*d+s*s-r*r)/(2*d*s))
    return r*r*(x-mp.sin(2*x)/2)+s*s*(y-mp.sin(2*y)/2)


def polygon_reference(p, radius):
    # Integrate vertical slices analytically. Split at vertices and all edge/disk
    # crossings; each clipped slice boundary is one affine edge or a semicircle.
    r = mp.mpf(radius)
    xs = [-r, r]
    edges = []
    for a, b in zip(p, p[1:]+p[:1]):
        if -r < a[0] < r:
            xs.append(mp.mpf(a[0]))
        if a[0] == b[0]:
            continue
        slope = mp.mpf(b[1]-a[1])/(b[0]-a[0])
        intercept = a[1]-slope*a[0]
        edges.append((min(a[0], b[0]), max(a[0], b[0]), slope, intercept))
        aa, bb, cc = 1+slope*slope, 2*slope*intercept, intercept*intercept-r*r
        disc = bb*bb-4*aa*cc
        if disc >= 0:
            for sign in [-1, 1]:
                x = (-bb+sign*mp.sqrt(disc))/(2*aa)
                if max(-r, min(a[0], b[0])) < x < min(r, max(a[0], b[0])):
                    xs.append(x)
    xs = sorted(set(xs))
    def arc(x):
        return (x*mp.sqrt(max(0,r*r-x*x))+r*r*mp.asin(x/r))/2
    total = mp.mpf(0)
    for left, right in zip(xs, xs[1:]):
        mid = (left+right)/2
        y = mp.sqrt(max(0,r*r-mid*mid))
        active = sorted([(m*mid+c,m,c) for lo,hi,m,c in edges if lo < mid < hi])
        assert len(active)%2 == 0
        def affine(edge):
            _, m, c = edge
            return m*(right*right-left*left)/2+c*(right-left)
        for low, high in zip(active[::2],active[1::2]):
            if min(high[0],y) <= max(low[0],-y):
                continue
            top = arc(right)-arc(left) if high[0] > y else affine(high)
            bottom = -arc(right)+arc(left) if low[0] < -y else affine(low)
            total += top-bottom
    return total


rng = random.Random(2026092909)
coord = lambda: rng.randrange(-10000,10001)
for o,r in [((-7717,-10000),9758),((0,0),10000),((2,1),1),((9999,-9999),9999)]:
    lines = [((-10000,-367),(-5909,-108)), ((-5909,-108),(-10000,-367))] if r == 9758 else []
    while len(lines) < 1000:
        a,b = (coord(),coord()),(coord(),coord())
        # Include guaranteed diameters even when a small disk is unlikely to be hit.
        if len(lines)%3 == 0:
            a = o
        if line_reference(a,b,o,r) is not None:
            lines.append((a,b))
    data = f'{o[0]} {o[1]} {r}\n{len(lines)}\n'
    data += ''.join(f'{a[0]} {a[1]} {b[0]} {b[1]}\n' for a,b in lines)
    expected = sum((line_reference(a,b,o,r) for a,b in lines),[])
    run('D', data, expected)
run('D','2 1 1\n2\n0 1 4 1\n3 0 3 3\n',[1,1,3,1,3,1,3,1])

fixtures = [((0,0),2,(2,0),2),((0,0),2,(0,3),1),((0,0),10000,(1,0),9999),
            ((-9999,0),10000,(9999,1),9999),((0,0),10000,(1,1),9999),
            ((-10000,0),10000,(10000,0),10000),((0,0),1,(0,0),1),
            ((1,0),1,(0,0),3),((0,0),1,(2,0),2)]
for _ in range(700):
    fixtures.append(((coord(),coord()),rng.randrange(1,10001),(coord(),coord()),rng.randrange(1,10001)))
for a,r,b,s in fixtures:
    for a,r,b,s in [(a,r,b,s),(b,s,a,r)]:
        data = f'{a[0]} {a[1]} {r}\n{b[0]} {b[1]} {s}\n'
        ref = circle_reference(a,r,b,s)
        if ref is not None:
            run('E',data,ref)
        run('I',data,[lens(a,r,b,s)])

polygons = [([(1,1),(4,1),(5,5)],5), ([(0,0),(-3,-6),(1,-3),(5,-4)],5),
            ([(-100,-100),(100,-100),(100,100),(-100,100)],100),
            ([(0,-100),(100,-100),(100,100),(0,100)],100),
            ([(0,0),(100,0),(100,100),(0,100)],100),
            ([(-90,-90),(90,-90),(90,90),(30,90),(30,-20),(-30,-20),(-30,90),(-90,90)],75),
            ([(-100,1),(100,1),(100,100),(-100,100)],1)]
for it in range(90):
    n = 100 if it%10 == 0 else rng.randrange(3,31)
    p=[]
    for i in range(n):
        angle=2*math.pi*i/n
        r = rng.randrange(40,100)
        p.append((round(r*math.cos(angle)),round(r*math.sin(angle))))
    assert len(set(p)) == n
    polygons.append((p,rng.randrange(1,101)))
for p,r in polygons:
    expected = polygon_reference(p,r)
    data = f'{len(p)} {r}\n'+''.join(f'{x} {y}\n' for x,y in p)
    run('H',data,[expected])
# Analytic anchors also audit the independent vertical-slice oracle.
assert abs(polygon_reference(polygons[2][0],100)-10000*mp.pi) < mp.mpf('1e-60')
assert abs(polygon_reference(polygons[3][0],100)-5000*mp.pi) < mp.mpf('1e-60')
assert abs(polygon_reference(polygons[4][0],100)-2500*mp.pi) < mp.mpf('1e-60')
for output, expected in [('1 0 -1 0',[-1,0,1,0]),('0 2',[0,2,0,2]),
                         ('nan',[0]),('inf',[0]),('1.000002',[1])]:
    try:
        validate(output,expected,mp.mpf('1e-6'))
    except (AssertionError,ValueError):
        pass
    else:
        raise AssertionError('Negative control accepted')
proof = {'mode':mode,'cases':counts,'maximum_absolute_errors':{k:str(v) for k,v in worst.items()},
         'oracle':'80-digit mpmath; parametric quadratic, distance/projection, lens segments, analytic vertical slices',
         'negative_controls':5,'scope':'Local complete AOJ drivers, no online submission or AC',
         'sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),*[root/f'verify/aoj/CGL_7_{x}.compact.cpp' for x in 'DEHI']]}}
(root/f'verification/circle-applications-{mode}.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof,indent=2))
