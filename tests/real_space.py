#!/usr/bin/env python3
"""Rational projection/intersection oracles, quaternion rotations and source diagnostics."""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from audit_copy_context import candidate, extract_components
from usage_examples import records, expand


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def mul(a, k):
    return tuple(x * k for x in a)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def norm(a):
    return math.sqrt(dot(a, a))


def quaternion(a, b):
    w, x, y, z = a
    v, i, j, k = b
    return (w*v-x*i-y*j-z*k, w*i+x*v+y*k-z*j,
            w*j-x*k+y*v+z*i, w*k+x*j-y*i+z*v)


def near(a, b):
    return math.isfinite(float(a)) and abs(float(a)-float(b)) <= 3e-9 * max(1, abs(float(a)), abs(float(b)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    mode = 'sanitizer' if args.sanitize else 'normal'
    out = ROOT / 'build/real-space' / mode
    out.mkdir(parents=True, exist_ok=True)
    paths = [ROOT / p for p in ['src/compact/real_space.hpp', 'src/compact/line3.hpp', 'src/compact/plane3.hpp',
             'tests/real_space.cpp', 'tests/real_space.py', 'tests/fixtures/real_space_sources/kuangbin.cpp',
             'docs/catalog.json', 'docs/usage-examples.json', 'tools/audit_copy_context.py', 'tools/usage_examples.py']]
    rows = [r for r in records() if r['id'] in ['example-348', 'example-349', 'example-350', 'example-351']]
    paths += [ROOT / r['driver'] for r in rows]
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    snapshot = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    flags = ['-std=c++20', '-O1' if args.sanitize else '-O2']
    if args.sanitize:
        flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')

    def compile_program(name, code, extra=()):
        src = out / (name + '.cpp')
        src.write_text(code)
        exe = out / name
        p = subprocess.run([CXX, *flags, *extra, str(src), '-o', str(exe)], capture_output=True, text=True)
        (out / (name + '.compile.log')).write_text(p.stderr)
        assert p.returncode == 0, p.stderr
        return exe

    def run(exe, data=''):
        p = subprocess.run([str(exe)], input=data, capture_output=True, text=True, timeout=120, env=env)
        assert p.returncode == 0 and not p.stderr, (exe, p.stderr)
        return p.stdout

    components = {r['symbol']: r for r in extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))}
    body = (ROOT / 'tests/real_space.cpp').read_text()
    body = body.replace('#include "../src/compact/plane3.hpp"', '#include "' + str(ROOT / 'src/compact/plane3.hpp') + '"')
    body = body.replace('"fixtures/real_space_sources/kuangbin.cpp"', '"' + str(ROOT / 'tests/fixtures/real_space_sources/kuangbin.cpp') + '"')
    core = '#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n' + '\n'.join(components[n]['code'] for n in ['RealSpace', 'Line3', 'Plane3'])
    copied_body = body.replace('#include "' + str(ROOT / 'src/compact/plane3.hpp') + '"', core)
    core_results = {}
    for name, code, extra in [('header', body, ()), ('ndebug', body, ('-DNDEBUG',)), ('copied', copied_body, ())]:
        core_results[name] = run(compile_program('core-' + name, code, extra)).strip()

    rng = random.Random(7302026)
    def point():
        return tuple(rng.randrange(-10, 11) for _ in range(3))
    def nonzero():
        p = point()
        while p == (0, 0, 0):
            p = point()
        return p
    batches = {}
    vectors = [((0, 0, 0), (0, 0, 0)), ((1, 0, 0), (-1, 0, 0))]
    vectors += [(point(), point()) for _ in range(2000)]
    data = ''.join(' '.join(map(str, (*a, *b))) + '\n' for a, b in vectors)
    want = []
    for a, b in vectors:
        angle = math.atan2(norm(cross(a, b)), dot(a, b)) if norm(a)*norm(b) else -1
        want.extend([dot(a, b), *cross(a, b), norm(a), norm(b), angle])
    batches['example-348'] = (data, want, len(vectors))
    lines = [((0, 0, 0), (2, 0, 0), q, math.pi/2) for q in [(1, 0, 0), (-1, 0, 0), (3, 0, 0), (1, 1, 0)]]
    lines += [((1, 2, 3), (1, 2, 3), (1, 2, 5), 0)]
    lines += [(point(), point(), point(), rng.randrange(-300, 301)/100) for _ in range(2000)]
    data = ''.join(' '.join(map(str, (*a, *b, *q, rad))) + '\n' for a, b, q, rad in lines)
    want = []
    for a, b, q, rad in lines:
        d, v = sub(b, a), sub(q, a)
        t = F(dot(v, d), dot(d, d)) if dot(d, d) else F(0)
        p = add(a, mul(d, t))
        s = add(a, mul(d, min(1, max(0, t))))
        distance = norm(sub(q, p))
        ds = norm(sub(q, s))
        want.extend([*p, *s, distance, ds, int(ds <= 1e-10)])
        if norm(d):
            u = mul(d, math.sin(rad/2)/norm(d))
            quat = (math.cos(rad/2), *u)
            conjugate = (quat[0], *mul(u, -1))
            rotated = quaternion(quaternion(quat, (0, *v)), conjugate)[1:]
            want.extend(add(a, rotated))
        else:
            want.extend(['no', 'axis'])
    batches['example-349'] = (data, want, len(lines))
    planes = []
    for _ in range(2000):
        planes.append((nonzero(), rng.randrange(-20, 21), point(), point(), point()))
    planes += [((1, 0, 0), 2, (1, 2, 3), (x, 0, 0), (x, y, 0)) for x in [0, 2] for y in [0, 1]]
    data = ''.join(' '.join(map(str, (*n, h, *q, *a, *b))) + '\n' for n, h, q, a, b in planes)
    want = []
    for n, h, q, a, b in planes:
        value = dot(n, q)-h
        foot = sub(q, mul(n, F(value, dot(n, n))))
        want.extend([value/norm(n), *foot])
        d = sub(b, a)
        off, den = h-dot(n, a), dot(n, d)
        kind = 1 if den else (-1 if off == 0 and norm(d) else 1 if off == 0 else 0)
        want.append(kind)
        if kind == 1:
            want.extend(add(a, mul(d, F(off, den))) if den else a)
    batches['example-350'] = (data, want, len(planes))
    pairs = [(nonzero(), rng.randrange(-20, 21), nonzero(), rng.randrange(-20, 21)) for _ in range(2000)]
    pairs += [((1, 0, 0), 1, (0, 1, 0), 2), ((1, 0, 0), 1, (-2, 0, 0), -2), ((1, 0, 0), 1, (2, 0, 0), 3)]
    data = ''.join(' '.join(map(str, (*a, h, *b, k))) + '\n' for a, h, b, k in pairs)
    batches['example-351'] = (data, None, len(pairs))
    evidence = {}
    for row in rows:
        data, want, count = batches[row['id']]
        header = (ROOT / row['driver']).read_text().replace('../../src/compact/', str(ROOT / 'src/compact') + '/')
        copied = candidate(row, row['requires'], components)['program']
        expanded = row['program']
        for form, code, extra in [('header', header, ()), ('ndebug', header, ('-DNDEBUG',)), ('expanded', expanded, ()), ('copied', copied, ())]:
            tokens = run(compile_program(row['id'] + '-' + form, code, extra), data).split()
            if want is not None:
                assert len(tokens) == len(want), (row['id'], len(tokens), len(want))
                for i, (got, expected) in enumerate(zip(tokens, want)):
                    assert got == expected if isinstance(expected, str) else near(float(got), expected), (row['id'], form, i, got, expected)
            else:
                it = iter(tokens)
                for a, h, b, k in pairs:
                    angle, kind = float(next(it)), int(next(it))
                    d = cross(a, b)
                    assert near(angle, math.atan2(norm(d), dot(a, b)))
                    if norm(d):
                        assert kind == 1
                        p = tuple(float(next(it)) for _ in range(3))
                        u = tuple(float(next(it)) for _ in range(3))
                        assert near(dot(a, p), h) and near(dot(b, p), k), (a, h, b, k, p)
                        assert near(norm(u), 1) and near(dot(a, u), 0) and near(dot(b, u), 0)
                    else:
                        i = next(i for i in range(3) if a[i])
                        assert kind == (-1 if a[i]*k == b[i]*h else 0)
                assert list(it) == []
        evidence[row['id']] = dict(program_sha256=row['program_sha256'], copied_program_sha256=hashlib.sha256(copied.encode()).hexdigest(), cases=count, forms=['header', 'ndebug', 'expanded', 'copied'])
    mutants = []
    if not args.sanitize:
        mutations = [('unclamped-segment', 'clamp(dot(q - p, u), R(0), len)', 'dot(q - p, u)'),
                     ('reverse-rotation', 'cross(u, v) * s', 'cross(u, v) * (-s)'),
                     ('unnormalized-plane', 'n(unit(normal))', 'n(normal)'),
                     ('wrong-plane-intersection-sign', 'Point q = p + v *', 'Point q = p - v *')]
        for name, old, new in mutations:
            assert copied_body.count(old) == 1
            exe = compile_program('mutant-' + name, copied_body.replace(old, new))
            p = subprocess.run([str(exe)], capture_output=True, text=True, timeout=120, env=env)
            assert p.returncode != 0 and 'real-space check failed' in p.stderr, (name, p.returncode, p.stderr)
            mutants.append(name)
    assert snapshot == {str(p.relative_to(ROOT)): digest(p) for p in paths}
    report = dict(mode=mode, compiler=CXX, flags=flags, source_sha256=snapshot, core=core_results,
                  usages=evidence, mutants_detected=mutants, passed=True,
                  scope='Finite, well-conditioned rational fixtures plus explicit tolerance boundary cases; numerical validation, not universal exact topology or online AC.')
    (ROOT / 'verification' / ('real-space-' + mode + '.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
