"""Exact supporting planes and signed origin moments, independent of vertex masses."""
from pathlib import Path
from itertools import combinations, product
from fractions import Fraction
import random, math, subprocess, hashlib, json, time
root = Path(__file__).resolve().parents[1]
build = root / 'build/hull3d-metrics'
build.mkdir(exist_ok=True)
# Reuse only the independently written geometric oracle primitives, not its test runner.
exec((root / 'tests/hull3d.py').read_text().split('cases=[];expected=[]')[0])
build = root / 'build/hull3d-metrics'

def truth(points):
    p = sorted(set(points))
    dim = oracle(points)[0]
    if dim < 3:
        return dim, int(dim == 2), None
    planes = {}
    for a, b, c in combinations(p, 3):
        v = normal(a, b, c)
        if not any(v):
            continue
        d = dot(v, a)
        signs = [dot(v, q) - d for q in p]
        if min(signs) < 0 < max(signs):
            continue
        if min(signs) >= 0:
            v, d = tuple(-x for x in v), -d
        g = math.gcd(*v, d)
        key = tuple(x // g for x in v) + (d // g,)
        planes[key] = [i for i, q in enumerate(p) if dot(v, q) == d]
    volume = 0
    moments = [0, 0, 0]
    for key, ids in planes.items():
        ring = plane_hull(p, ids, key[:3])
        if dot(normal(*(p[i] for i in ring[:3])), key[:3]) < 0:
            ring.reverse()
        for i in range(1, len(ring) - 1):
            a, b, c = (p[j] for j in (ring[0], ring[i], ring[i + 1]))
            v = orient((0, 0, 0), a, b, c)
            volume += v
            for k in range(3):
                moments[k] += v * (a[k] + b[k] + c[k])
    center = tuple(Fraction(x, 4 * volume) for x in moments)
    radius = min(float(d - dot(v, center)) / math.sqrt(dot(v, v))
                 for *v, d in planes)
    return dim, len(planes), (center, radius, set(planes))

rng = random.Random(4273)
cases = [[], [(1, 2, 3)] * 4, [(i, 2*i, -i) for i in range(-3, 4)]]
cube = list(product([0, 1], repeat=3))
for mask in range(256):
    cases.append([p for i, p in enumerate(cube) if mask >> i & 1])
for k in range(150):
    p = [tuple(rng.randrange(-8, 9) for _ in range(3)) for _ in range(rng.randrange(4, 13))]
    cases.append(p)
    if k < 30:
        cases.append(p + p[:4])
        cases.append([(x+999999990, y-999999990, z+999999990) for x, y, z in p])
        cases.append([(x*100000000, y*100000000, z*100000000) for x, y, z in p])
# Unimodular, extremely thin tetrahedra; determinant exactly 1.
for a in [10, 10000, 999999999]:
    cases.append([(0,0,0), (a,1,0), (a-1,1,0), (a,0,1)])
    cases.append([(-a,-a,-a), (a,a-1,a), (a-1,a-2,a), (0,0,1-a)])
cases += [list(product([-10**9, 10**9], repeat=3)),
          [(-10**9,-10**9,0),(10**9,-10**9,0),(-10**9,10**9,0),(10**9,10**9,0),(0,0,1)],
          list(product(range(3),repeat=3)), [(0,0,0),(1,0,0),(0,1,0),(0,0,1)]]
expected = [truth(p) for p in cases]
text = ''.join(str(len(p))+'\n'+''.join(' '.join(map(str,q))+'\n' for q in p) for p in cases)
(build/'cases.txt').write_text(text)
header = root/'src/compact/hull3d_metrics.hpp'
body = '#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'
for name, path in [('Hull3D','hull3d.hpp'),('Hull3DMetrics','hull3d_metrics.hpp')]:
    body += (root/'src/compact'/path).read_text().split('// BEGIN '+name+'\n')[1].split('// END '+name)[0]
(build/'copied.cpp').write_text(body+(root/'tests/hull3d_metrics.cpp').read_text().split('\n',1)[1])
(build/'4273.cpp').write_text(body+(root/'verify/hdu/4273.compact.cpp').read_text().split('\n',1)[1])

def check(output):
    lines = iter(output.splitlines())
    for case, (points, (dim, count, expected_value)) in enumerate(zip(cases, expected)):
        row = next(lines).split()
        assert tuple(map(int,row[:3])) == (dim,count,int(dim==3)), (case,row,dim,count)
        if dim == 3:
            center, radius, plane_keys = expected_value
            for got, want in zip(map(float,row[3:6]),center):
                assert abs(got-float(want)) < 2e-6, (case,'center',got,want)
            got = float(row[6])
            assert abs(got-radius) <= radius*2e-13, (case,'radius',got,radius)
        seen = set()
        for _ in range(count):
            row = next(lines).split()
            a,b,c = [tuple(map(int,row[k:k+3])) for k in (0,3,6)]
            v = normal(a,b,c)
            d = dot(v,a)
            g = math.gcd(*v,d)
            key = tuple(x//g for x in v)+(d//g,)
            seen.add(key)
            want = abs(dot(v,(123,-456,789))-d)/math.sqrt(dot(v,v))
            assert math.isclose(float(row[9]),want,rel_tol=2e-14,abs_tol=1e-14)
        if dim == 3:
            assert seen == plane_keys, (case,seen,plane_keys)
    assert next(lines,None) is None

reports = {}
for mode, flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
    for form in ['header','ndebug','copied']:
        src = build/'copied.cpp' if form=='copied' else root/'tests/hull3d_metrics.cpp'
        exe = build/f'{mode}-{form}'
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
        start = time.monotonic()
        result = subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,timeout=60)
        assert not result.stderr,result.stderr
        check(result.stdout)
        reports[mode+'-'+form] = {'cases':len(cases),'seconds':round(time.monotonic()-start,3)}
        print(mode,form,len(cases),'PASS',flush=True)
(root/'verification/hull3d-metrics-local.json').write_text(json.dumps({
    'status':'pass','source_sha256':hashlib.sha256(header.read_bytes()).hexdigest(),
    'oracle':'Exact supporting-plane enumeration and Fraction signed origin first moments; thin integer tetrahedra, all cube subsets, translations and scaling',
    'forms':reports},indent=2)+'\n')
