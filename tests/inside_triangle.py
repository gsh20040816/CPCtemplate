#!/usr/bin/env python3
"""Independent triangle half-plane oracle for Chengdu 2025 I."""
import functools
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from usage_examples import records
from compiler_config import CXX


def sha(data):
    return hashlib.sha256(data).hexdigest()


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def hull(points):
    points = sorted(set(points))
    lower, upper = [], []
    for a in points:
        while len(lower) > 1 and cross(lower[-2], lower[-1], a) <= 0:
            lower.pop()
        lower.append(a)
    for a in points[::-1]:
        while len(upper) > 1 and cross(upper[-2], upper[-1], a) <= 0:
            upper.pop()
        upper.append(a)
    return lower[:-1] + upper[:-1]


def strictly_inside(p, x):
    return all(cross(p[i], p[(i + 1) % len(p)], x) > 0 for i in range(len(p)))


def brute(p, q):
    return sum(all(cross(p[u], p[v], x) >= 0 for x in q
                   for u, v in [(a, b), (b, c), (c, a)])
               for a, b, c in itertools.combinations(range(len(p)), 3))


def encode(cases):
    assert 1 <= len(cases) <= 1000
    assert sum(len(p) for p, q, _ in cases) <= 500000
    assert sum(len(q) for p, q, _ in cases) <= 500000
    assert all(3 <= len(poly) <= 300000 and all(abs(v) <= 10**9 for point in poly for v in point) for p, q, _ in cases for poly in [p, q])
    text = [str(len(cases))]
    for p, q, _ in cases:
        for poly in [p, q]:
            text.append(str(len(poly)))
            text.extend(f'{x} {y}' for x, y in poly)
    return ('\n'.join(text) + '\n').encode()


def lattice_polygon():
    quarter = []
    y = 2
    while len(quarter) < 75000:
        for x in range(1, y):
            if math.gcd(x, y) == 1:
                quarter.extend([(x, y), (y, x)])
                if len(quarter) == 75000:
                    break
        y += 1
    def cmp(a, b):
        z = a[0] * b[1] - a[1] * b[0]
        return (z < 0) - (z > 0)
    quarter.sort(key=functools.cmp_to_key(cmp))
    edges = quarter + [(-y, x) for x, y in quarter] + [(-x, -y) for x, y in quarter] + [(y, -x) for x, y in quarter]
    p, x, y = [], 0, 0
    for dx, dy in edges:
        p.append((x, y))
        x += dx
        y += dy
    assert (x, y) == (0, 0)
    cx, cy = p[len(p) // 2]
    p = [(2 * x - cx, 2 * y - cy) for x, y in p]
    n = len(p)
    assert n == 300000
    assert all(p[i + n // 2] == (-p[i][0], -p[i][1]) for i in range(n // 2))
    assert all(cross(p[i], p[(i + 1) % n], p[(i + 2) % n]) > 0 for i in range(n))
    assert all(cross(p[i], p[(i + 1) % n], (0, 0)) > 0 for i in range(n))
    # Edges are sorted around one turn, distinct primitive directions; local
    # strict turns plus this construction give a simple strictly convex polygon.
    return p


def datasets():
    small = []
    def add(p, q):
        assert len(p) >= 3 and len(q) >= 3
        for poly in [p, q]:
            assert len(set(poly)) == len(poly)
            assert all(cross(poly[i], poly[(i + 1) % len(poly)], poly[j]) > 0
                       for i in range(len(poly)) for j in range(len(poly))
                       if j not in (i, (i + 1) % len(poly)))
            assert all(abs(v) <= 10**9 for point in poly for v in point)
        assert all(strictly_inside(p, x) for x in q)
        small.append((p, q, brute(p, q)))
    outer = [(-4, -4), (4, -4), (4, 4), (-4, 4)]
    add(outer, [(-2, -2), (2, -2), (0, 0)])
    add(outer, [(-1, -1), (1, -1), (1, 1), (-1, 1)])
    assert [x[2] for x in small] == [2, 0]
    add([(x * 250000000, y * 250000000) for x, y in outer],
        [(-500000000, -500000000), (500000000, -500000000), (0, 0)])
    for p in [outer, [(-4, -3), (4, -3), (0, 5)], [(-4, -1), (-1, -4), (4, -2), (3, 4), (-3, 4)]]:
        inside = [x for x in itertools.product(range(-2, 3), repeat=2) if strictly_inside(p, x)]
        for triangle in itertools.combinations(inside, 3):
            q = hull(triangle)
            if len(q) == 3:
                add(p, q)
    exhaustive_count = len(small)
    rng = random.Random(106161)
    for _ in range(1000):
        p = hull([(rng.randrange(-30, 31), rng.randrange(-30, 31)) for _ in range(rng.randrange(5, 22))])
        candidates = [(rng.randrange(-29, 30), rng.randrange(-29, 30)) for _ in range(120)]
        q = hull([x for x in candidates if strictly_inside(p, x)][:rng.randrange(3, 12)])
        if len(p) >= 3 and len(q) >= 3:
            add(p, q)
    for p, q, want in small[::max(1, len(small) // 100)]:
        a, b = len(p) // 2, len(q) - 1
        small.append((p[a:] + p[:a], q[b:] + q[:b], want))
        transform = lambda poly: [(3 * x + y + 1000000, x + 2 * y - 1000000) for x, y in poly]
        pp, qq = transform(p), transform(q)
        assert brute(pp, qq) == want
        small.append((pp, qq, want))
    batches = []
    for i in range(0, len(small), 1000):
        batch = small[i:i + 1000]
        batches.append((f'small-{i // 1000}', encode(batch), [x[2] for x in batch]))
    fixture = ROOT / 'tests/fixtures/inside-triangle'
    batches.insert(0, ('official', (fixture / 'official.in').read_bytes(), list(map(int, (fixture / 'official.out').read_bytes().split()))))
    reset = [([(-10, -10), (10, -10), (0, 10)], [(-1, -1), (1, -1), (0, 1)], 1)] * 1000
    batches.append(('1000-reset', encode(reset), [1] * 1000))
    r = lattice_polygon()
    p = [(10 * x, 10 * y) for x, y in r]
    q = [(-1, -1), (1, -1), (0, 1)]
    assert strictly_inside(q, (0, 0))
    n, h = len(p), len(p) // 2
    assert all(cross(p[i], p[(i + h - 1) % n], v) > 0 for i in range(n) for v in q)
    answer = n * (h - 1) * (h - 2) // 6
    assert answer == 1124977500100000
    for rotation in [0, 12345, n - 1]:
        pp = p[rotation:] + p[:rotation]
        batches.append((f'maximum-n-rotation-{rotation}', encode([(pp, q, answer)]), [answer]))
    big = [(-1000000000, -1000000000), (1000000000, -1000000000), (0, 1000000000)]
    assert all(strictly_inside(big, x) for x in r)
    batches.append(('maximum-m', encode([(big, r, 1)]), [1]))
    q = [(9 * x, 9 * y) for x, y in r]
    area2 = sum(q[i][0] * q[(i + 1) % n][1] - q[i][1] * q[(i + 1) % n][0] for i in range(n))
    width = max(x for x, y in p) - min(x for x, y in p)
    height = max(y for x, y in p) - min(y for x, y in p)
    assert area2 > width * height
    assert max(abs(v) for poly in [p, q] for point in poly for v in point) <= 10**9
    batches.append(('maximum-joint-area-zero', encode([(p, q, 0)]), [0]))
    return batches, dict(small_nested_pairs=len(small),exhaustive_prefix_pairs=exhaustive_count,large_vertex_count=n,large_positive_answer=answer,joint_inner_area2=area2,outer_bbox_double_triangle_bound=width*height)


def main():
    if not __debug__:
        raise RuntimeError('Python checks must stay enabled')
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='inside-triangle-' + mode + '-', dir=ROOT / 'build'))
    before = snapshot(ROOT)
    batches, counts = datasets()
    for label, inp, expected in batches:
        (out / (label + '.in')).write_bytes(inp)
        (out / (label + '.expected')).write_text('\n'.join(map(str, expected)) + '\n')
    row = next(r for r in records() if r['id'] == 'example-242')
    inventory = json.loads((ROOT / 'docs/template-problems.json').read_text())
    candidates = next(r['candidate_drivers'] for r in inventory['algorithms'] if r['symbol'] == 'convex_tangents_i64')
    assert any(r['driver'] == row['driver'] and r['url'] == row['url'] for r in candidates)
    components = {r['symbol']:r['code'] for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    core = '\n'.join(components[x] for x in ['IntegerPlane', 'convex_tangents_i64'])
    prelude = '#include <bits/stdc++.h>\nusing namespace std;\n'
    copied = prelude + core + '\n' + row['snippet']
    flags = ['-std=c++20', '-Wall', '-Wextra'] + (['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    report = dict(mode=mode, source_before_sha256=before, compiler=str(compiler), compiler_sha256=sha(compiler.read_bytes()), flags=flags, counts=counts,programs=[],mutants=[])
    def compile(name, text, nd=False):
        cpp, exe = out/(name+'.cpp'), out/name
        cpp.write_text(text)
        cmd = [CXX, *flags, *(['-DNDEBUG'] if nd else []), str(cpp), '-o', str(exe)]
        subprocess.run(cmd, check=True, capture_output=True)
        return exe, dict(name=name, compile_command=cmd, source_sha256=sha(cpp.read_bytes()), binary_sha256=sha(exe.read_bytes()))
    for form, text in [('driver','#include "'+str(ROOT/row['driver'])+'"\n'),('bundle',row['program']),('minimal-copy',copied)]:
        for nd in [False, True]:
            exe, entry = compile(form+('-ndebug' if nd else '-assert'),text,nd)
            entry['runs'] = []
            for label, inp, expected in batches:
                run = subprocess.run([str(exe)],input=inp,capture_output=True,env=env,timeout=180)
                assert run.returncode==0 and not run.stderr,(form,label,run.returncode,run.stderr[-1000:])
                assert list(map(int,run.stdout.split()))==expected,(form,label,run.stdout[:1000],expected[:10])
                (out/(entry['name']+'-'+label+'.out')).write_bytes(run.stdout)
                entry['runs'].append(dict(case=label,input_sha256=sha(inp),expected_sha256=sha((out/(label+'.expected')).read_bytes()),output_sha256=sha(run.stdout),passed=True))
            report['programs'].append(entry)
    # Include the entire independently-enumerated small suite to reject all
    # semantic mutations without treating crashes/diagnostics as oracle proof.
    mutation_batches = [(label, inp, expected) for label, inp, expected in batches if label=='official' or label.startswith('small-')]
    mutations = [('strict-contact','q[k]) >= 0','q[k]) > 0'),('wrong-divisor','ans / 3','ans / 2'),('drop-last-c','* (g - 1);','* g;'),('skip-equal-b','f[h] < g','f[h] <= g'),('skip-equal-c','f[g] < a + n','f[g] <= a + n')]
    for name, old, new in mutations:
        assert copied.count(old)==1,name
        exe,entry=compile(name,copied.replace(old,new),True)
        entry['runs']=[];rejected=False
        for label,inp,expected in mutation_batches:
            run=subprocess.run([str(exe)],input=inp,capture_output=True,env=env,timeout=180)
            assert run.returncode==0 and not run.stderr,(name,label,run.returncode,run.stderr[-1000:])
            mismatch=list(map(int,run.stdout.split()))!=expected
            (out/(name+'-'+label+'.out')).write_bytes(run.stdout)
            entry['runs'].append(dict(case=label,input_sha256=sha(inp),output_sha256=sha(run.stdout),oracle_rejected=mismatch))
            if mismatch:rejected=True;break
        assert rejected,name
        report['mutants'].append(entry)
    report.update(source_after_sha256=snapshot(ROOT),passed=True,scope='Formal Chengdu I application under published valid-input contract; six driver/bundle/copy forms, independent exact triangle oracle, maximum geometry certificates. Local checks, not online AC or time-limit ranking; no LeakSanitizer.')
    assert report['source_before_sha256']==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Inside Triangle',mode,counts,'PASS:',out/'report.json')


if __name__=='__main__':main()
