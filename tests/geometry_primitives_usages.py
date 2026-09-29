"""Exact-rational independent oracles for five complete AOJ geometry drivers."""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
import hashlib
import itertools
import json
import random
import subprocess
import sys

from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def projection(p, a, b):
    v = sub(b, a)
    if v == (0, 0):
        return tuple(map(F, a))
    t = F(dot(sub(p, a), v), dot(v, v))
    return tuple(x + t * y for x, y in zip(a, v))


def crossing(a, b, c, d):
    """Solve for the two segment parameters, rather than orientation signs."""
    u, v, w = sub(b, a), sub(d, c), sub(c, a)
    det = cross(u, v)
    if det:
        t, s = F(cross(w, v), det), F(cross(w, u), det)
        if 0 <= t <= 1 and 0 <= s <= 1:
            return tuple(F(x) + t * y for x, y in zip(a, u))
        return None
    if u == (0, 0):
        if v == (0, 0):
            return a if a == c else None
        k = 0 if v[0] else 1
        s = F(a[k] - c[k], v[k])
        return a if 0 <= s <= 1 and all(F(c[i]) + s * v[i] == a[i] for i in range(2)) else None
    if cross(u, w):
        return None
    k = 0 if u[0] else 1
    lo, hi = sorted((F(c[k] - a[k], u[k]), F(d[k] - a[k], u[k])))
    return a if max(lo, 0) <= min(hi, 1) else None


def point_distance2(p, a, b):
    v, w = sub(b, a), sub(p, a)
    length = dot(v, v)
    if not length or dot(w, v) <= 0:
        return F(dot(w, w))
    if dot(w, v) >= length:
        return F(dot(sub(p, b), sub(p, b)))
    # Squared triangle height, without constructing the projection point.
    return F(cross(v, w) ** 2, length)


def distance2(a, b, c, d):
    if crossing(a, b, c, d) is not None:
        return F(0)
    return min(point_distance2(a, c, d), point_distance2(b, c, d),
               point_distance2(c, a, b), point_distance2(d, a, b))


def area(p):
    """Integrate horizontal interior widths; independent of shoelace summation."""
    heights = sorted({y for x, y in p})
    ans = F(0)
    for lo, hi in zip(heights, heights[1:]):
        mid = F(lo + hi, 2)
        xs = []
        for a, b in zip(p, p[1:] + p[:1]):
            if min(a[1], b[1]) < mid < max(a[1], b[1]):
                xs.append(F(a[0]) + (mid - a[1]) * F(b[0] - a[0], b[1] - a[1]))
        xs.sort()
        assert len(xs) % 2 == 0
        ans += sum((r - l) * (hi - lo) for l, r in zip(xs[::2], xs[1::2]))
    return ans


def decimal(x):
    x = F(x)
    return Decimal(x.numerator) / Decimal(x.denominator)


def row(points):
    return ' '.join(str(x) for p in points for x in p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sanitizer', action='store_true')
    args = ap.parse_args()
    mode = 'sanitizer' if args.sanitizer else 'normal'
    out = ROOT / 'build' / ('geometry-primitives-' + mode)
    out.mkdir(parents=True, exist_ok=True)
    info = {x['id']: x for x in records()}
    flags = ['-O1', '-g', '-fsanitize=address,undefined'] if args.sanitizer else ['-O2']
    reports = {}
    for i in range(180, 185):
        r = info[f'example-{i}']
        src = out / f'{i}.cpp'
        src.write_text(r['program'])
        subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(out / str(i))], check=True)
        reports[str(i)] = dict(driver=r['driver'], program_sha256=r['program_sha256'],
                               invocations=0, queries=0, max_absolute_error='0')

    def run(i, data, expected, queries=None):
        p = subprocess.run([str(out / str(i))], input=data, text=True,
                           capture_output=True, check=True, timeout=30)
        assert not p.stderr, p.stderr
        actual = p.stdout.split()
        assert len(actual) == len(expected), (i, p.stdout, expected)
        err = Decimal(0)
        for a, b in zip(actual, expected):
            value = Decimal(a)
            assert value.is_finite(), (i, a)
            delta = abs(value - b)
            assert delta < Decimal('1e-8'), (i, data, a, str(b), str(delta))
            err = max(err, delta)
        r = reports[str(i)]
        r['invocations'] += 1
        r['queries'] += queries if queries is not None else len(expected)
        r['max_absolute_error'] = str(max(Decimal(r['max_absolute_error']), err))
        if i == 184:
            assert p.stdout.endswith('.0\n') or p.stdout.endswith('.5\n'), p.stdout

    rng = random.Random(20260930)
    pts = list(itertools.product(range(-1, 2), repeat=2))
    segments = [(a, b) for a in pts for b in pts if a != b]
    quadruples = [a + b for a in segments for b in segments]
    for _ in range(3000):
        p = tuple((rng.randint(-10000, 10000), rng.randint(-10000, 10000)) for _ in range(4))
        if p[0] != p[1] and p[2] != p[3]:
            quadruples.append(p)
    # Small nonzero determinants and large direction magnitudes; shared endpoint.
    for k in range(9990, 10001):
        a, b, c, d = (-k + 1, -k + 2), (k, k), (-k + 1, -k + 2), (k - 1, k - 1)
        for first in [(a, b), (b, a)]:
            for second in [(c, d), (d, c)]:
                quadruples.extend([first + second, second + first])
    for start in range(0, len(quadruples), 1000):
        batch = quadruples[start:start + 1000]
        data = str(len(batch)) + '\n' + '\n'.join(map(row, batch)) + '\n'
        expected = []
        for a, b, c, d in batch:
            u, v = sub(b, a), sub(d, c)
            expected.append(Decimal(2 if cross(u, v) == 0 else 1 if dot(u, v) == 0 else 0))
        run(180, data, expected)
        run(182, data, [decimal(distance2(*p)).sqrt() for p in batch])
        valid = [p for p in batch if cross(sub(p[1], p[0]), sub(p[3], p[2])) and crossing(*p) is not None]
        if valid:
            run(183, str(len(valid)) + '\n' + '\n'.join(map(row, valid)) + '\n',
                [decimal(x) for p in valid for x in crossing(*p)], len(valid))

    # Degenerate input is an explicit extension, not part of the AOJ constraints.
    degenerate = [p for p in itertools.product(pts, repeat=4) if p[0] == p[1] or p[2] == p[3]]
    for start in range(0, len(degenerate), 1000):
        batch = degenerate[start:start + 1000]
        run(182, str(len(batch)) + '\n' + '\n'.join(map(row, batch)) + '\n',
            [decimal(distance2(*p)).sqrt() for p in batch])
    reports['182']['extension_queries'] = len(degenerate)

    lines = segments + [((rng.randint(-10000, 10000), rng.randint(-10000, 10000)),
                          (rng.randint(-10000, 10000), rng.randint(-10000, 10000))) for _ in range(200)]
    lines += [((-10000, -10000), (10000, 9999)), ((10000, -10000), (-10000, 10000))]
    for a, b in lines:
        queries = pts + [(-10000, -10000), (10000, 10000)]
        queries += [(rng.randint(-10000, 10000), rng.randint(-10000, 10000)) for _ in range(989)]
        run(181, row((a, b)) + '\n1000\n' + '\n'.join(map(row, [(p,) for p in queries])) + '\n',
            [decimal(x) for p in queries for x in projection(p, a, b)], len(queries))
    run(181, '3 7 3 7\n2\n-10000 10000\n3 7\n', list(map(Decimal, [3, 7, 3, 7])), 2)
    reports['181']['extension_queries'] = 2

    polygons = [[(0, 0), (2, 2), (-1, 1)], [(0, 0), (1, 1), (1, 2), (0, 2)],
                [(0, 0), (3, 0), (3, 1), (1, 1), (1, 3), (0, 3)],
                [(-10000, -10000), (10000, -10000), (10000, 10000), (-10000, 10000)]]
    for _ in range(250):
        n = rng.randint(2, 50)
        xs = sorted(rng.sample(range(-10000, 10001), n))
        lower = [(x, -rng.randint(1, 10000)) for x in xs]
        upper = [(x, rng.randint(1, 10000)) for x in reversed(xs)]
        polygons.append(lower + upper)
    polygons.append([(x, -1 - (x % 3)) for x in range(50)] + [(x, 1 + x % 4) for x in reversed(range(50))])
    for p in polygons:
        expected = decimal(area(p))
        for a in [p, list(reversed(p))]:
            run(184, str(len(a)) + '\n' + '\n'.join(row((v,)) for v in a) + '\n', [expected])
    reports['184']['clockwise_extension_invocations'] = len(polygons)

    report = dict(scope='Local exact-rational driver oracles only; not online AC. AOJ range plus separately counted degenerate/clockwise extensions.',
                  mode=mode, compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0], flags=flags,
                  test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), results=reports)
    path = ROOT / 'verification' / f'geometry-primitives-usages-{mode}.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    with localcontext() as ctx:
        ctx.prec = 70
        main()
