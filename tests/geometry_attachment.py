"""Complete programs: fixed-decimal hull, diameter, rational polygon clipping."""
from compiler_config import CXX
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
import argparse
import math
import os
import random
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--sanitize', action='store_true', default=os.environ.get('CPC_SANITIZE') == '1')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
rng = random.Random(20260929)


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def dist(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def hull(points):
    # Gift wrapping, rather than another monotone-chain implementation.
    p = sorted(set(points))
    if len(p) < 2:
        return p
    out, i = [], 0
    while True:
        out.append(p[i])
        j = (i + 1) % len(p)
        for k in range(len(p)):
            t = cross(p[i], p[j], p[k])
            if t < 0 or (t == 0 and dist(p[i], p[k]) > dist(p[i], p[j])):
                j = k
        i = j
        if i == 0:
            return out


def clipped_area(polygons):
    # Sequential exact clipping; no angle sorting or intersection deque.
    p = [tuple(map(F, v)) for v in polygons[0]]
    for polygon in polygons[1:]:
        for a, b in zip(polygon, polygon[1:] + polygon[:1]):
            q = []
            for u, v in zip(p, p[1:] + p[:1]):
                du, dv = cross(a, b, u), cross(a, b, v)
                if du >= 0:
                    q.append(u)
                if (du < 0 < dv) or (dv < 0 < du):
                    t = du / (du - dv)
                    q.append(tuple(u[i] + (v[i] - u[i]) * t for i in range(2)))
            p = q
    return abs(sum(u[0] * v[1] - u[1] * v[0]
                   for u, v in zip(p, p[1:] + p[:1]))) / 2


def compile_driver(problem):
    mode = 'san' if args.sanitize else 'normal'
    exe = root / f'build/geometry-{problem}-{mode}'
    flags = ['-O2']
    if args.sanitize:
        flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    subprocess.run([CXX, '-std=c++20', *flags,
                    str(root / f'verify/luogu/{problem}.compact.cpp'), '-o', str(exe)], check=True)
    return exe


def run(exe, data):
    result = subprocess.run([str(exe)], input=data, text=True,
                            capture_output=True, check=True, timeout=30)
    assert not result.stderr, result.stderr
    assert len(result.stdout.split()) == 1
    return result.stdout.strip()


def encode(points, decimal=False):
    def number(x):
        if not decimal:
            return str(x)
        # Exercise integer, one/two decimals, explicit plus and negative zero.
        s = f'{abs(x) // 100}.{abs(x) % 100:02d}'
        s = s.rstrip('0').rstrip('.')
        return ('-' if x < 0 else rng.choice(['', '+'])) + s
    return str(len(points)) + '\n' + '\n'.join(
        ' '.join(number(x) for x in p) for p in points) + '\n'


perimeter = compile_driver('P2742')
clouds = [[(0, 0)] * 3, [(0, 0), (3, 4), (6, 8)],
          [(100000000, 99999999), (99999999, 99999998), (0, 0)],
          [(-1, -1), (-1, 1), (1, 1), (1, -1)],
          [(-100000000, -100000000), (-100000000, 100000000),
           (100000000, 100000000), (100000000, -100000000)]]
for _ in range(150):
    clouds.append([(rng.randint(-100000000, 100000000),
                    rng.randint(-100000000, 100000000)) for _ in range(rng.randint(3, 35))])
with localcontext() as ctx:
    ctx.prec = 100
    for points in clouds:
        h = hull(points)
        expected = sum(Decimal(dist(u, v)).sqrt() for u, v in zip(h, h[1:] + h[:1])) / 100
        got = Decimal(run(perimeter, encode(points, True)))
        assert abs(got - expected) <= Decimal('0.00500001'), (points, got, expected)
    points = clouds[4] + [(i * 1000, i % 17) for i in range(99996)]
    assert run(perimeter, encode(points, True)) == '8000000.00'
    assert run(perimeter, '3\n-0.0 +0.00\n.03 .04\n0.06 0.08\n') == '0.20'
print('P2742: 155 independent gift-wrap / 100-digit perimeter cases, signed decimal parsing, '
      '100000 points PASS', flush=True)

diameter = compile_driver('P1452')
for _ in range(150):
    points = list({(rng.randint(-10000, 10000), rng.randint(-10000, 10000))
                   for _ in range(rng.randint(2, 50))})
    expected = max(dist(u, v) for u in points for v in points)
    assert int(run(diameter, encode(points))) == expected
points = [(-10000, -10000), (-10000, 10000), (10000, 10000), (10000, -10000)]
points += [(x, y) for x in range(-9999, 10000) for y in (-10000, 10000)]
points += [(-10000, y) for y in range(-9999, 0)]
points = points[:50000]
assert len(points) == 50000 and len(set(points)) == 50000
assert run(diameter, encode(points)) == '800000000'
print('P1452: 150 arbitrary-integer all-pairs cases and 50000 distinct points PASS', flush=True)

halfplanes = compile_driver('P4196')
square = [(0, 0), (10, 0), (10, 10), (0, 10)]
cases = [[square, square], [square, [(10, 0), (20, 0), (20, 10), (10, 10)]],
         [square, [(10, 10), (20, 10), (20, 20), (10, 20)]],
         [square, [(11, 0), (20, 0), (20, 10), (11, 10)]],
         [square, [(0, 0), (5, 0), (10, 0), (10, 10), (0, 10)]],
         [[(-1000, -1000), (999, 998), (1000, 999)],
          [(-999, -1000), (1000, 1000), (999, 1000)]]]
for _ in range(200):
    polygons = []
    for _ in range(rng.randint(2, 10)):
        while True:
            p = hull([(rng.randint(-1000, 1000), rng.randint(-1000, 1000)) for _ in range(10)])
            if len(p) >= 3:
                break
        start = rng.randrange(len(p))
        polygons.append(p[start:] + p[:start])
    cases.append(polygons)
polygons = []
for j in range(10):
    p = [(round(900 * math.cos(2 * math.pi * (i / 50 + j / 500))),
          round(900 * math.sin(2 * math.pi * (i / 50 + j / 500)))) for i in range(50)]
    assert len(hull(p)) == 50
    polygons.append(p)
cases.append(polygons)
for polygons in cases:
    for p in polygons:
        assert all(cross(p[i - 2], p[i - 1], p[i]) >= 0 for i in range(len(p)))
    data = str(len(polygons)) + '\n' + ''.join(encode(p) for p in polygons)
    expected = clipped_area(polygons)
    got = F(run(halfplanes, data))
    assert abs(got - expected) <= F(500001, 10**9), (polygons, got, expected)
print('P4196: 207 exact Fraction clipping cases, empty/point/segment intersections, '
      'collinear sides and 500 total constraints PASS', flush=True)
