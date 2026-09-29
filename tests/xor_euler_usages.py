"""Complete vector drivers: walk-state BFS, exhaustive Euler trails, vector spans."""
from compiler_config import CXX
from pathlib import Path
from collections import Counter, deque
import hashlib
import itertools
import json
import os
import random
import subprocess
import time

root = Path(__file__).resolve().parents[1]
os.chdir(root)
mode = 'sanitizer' if os.getenv('CPC_SANITIZE') == '1' else 'normal'
work = root / 'build' / ('xor-euler-' + mode)
work.mkdir(parents=True, exist_ok=True)
flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2']
if os.uname().sysname == 'Darwin':
    flags += ['-Wl,-stack_size,0x20000000']
drivers = {'walk': 'verify/luogu/P4151.compact.cpp', 'euler': 'verify/luogu/P2731.compact.cpp',
           'intersection': 'verify/library_checker/intersection_intersection.compact.cpp',
           'zassenhaus': 'verify/library_checker/intersection_zassenhaus.compact.cpp'}
for name, driver in drivers.items():
    subprocess.run(['python3', 'tools/bundle.py', driver, str(work / (name + '.cpp'))], check=True)
    subprocess.run([CXX, '-std=c++20', *flags, str(work / (name + '.cpp')), '-o', str(work / name)], check=True)
counts, seconds = Counter(), Counter()
def run(name, data):
    start = time.monotonic()
    p = subprocess.run([str(work / name)], input=data, text=True, capture_output=True, timeout=240, check=True)
    assert not p.stderr, p.stderr
    counts[name] += 1
    seconds[name] += time.monotonic() - start
    return p.stdout

rng = random.Random(41512731)
def walk(n, edges, want=None):
    if want is None:
        g = [[] for _ in range(n)]
        for u, v, w in edges:
            g[u].append((v, w)); g[v].append((u, w))
        seen = {(0, 0)}
        todo = deque(seen)
        while todo:
            u, x = todo.popleft()
            for v, w in g[u]:
                state = (v, x ^ w)
                if state not in seen:
                    seen.add(state); todo.append(state)
        want = max(x for u, x in seen if u == n - 1)
    data = f'{n} {len(edges)}\n' + ''.join(f'{u+1} {v+1} {w}\n' for u, v, w in edges)
    assert run('walk', data).split() == [str(want)]

for weights in itertools.product(range(-1, 3), repeat=3):
    pairs = [(0, 1), (0, 2), (1, 2)]
    edges = [(u, v, w) for (u, v), w in zip(pairs, weights) if w >= 0]
    if len(edges) >= 2:
        walk(3, edges)
for _ in range(300):
    n = rng.randint(1, 9)
    edges = [(i, rng.randrange(i), rng.randrange(32)) for i in range(1, n)]
    edges += [(rng.randrange(n), rng.randrange(n), rng.randrange(32)) for _ in range(rng.randint(1, 20))]
    rng.shuffle(edges)
    walk(n, edges)
# Maxima: deep recursion with all sixty relevant cycle bits, and full 64-bit extension.
n = 50000
edges = [(i-1, i, 0) for i in range(1, n)]
edges += [(0, 0, 1 << i) for i in range(60)]
edges += [(0, n-1, 0)] * (100000-len(edges))
walk(n, edges, (1 << 60)-1)
walk(2, [(0, 1, 1 << 63), (0, 0, (1 << 63)-1)], (1 << 64)-1)

# Enumerate edge identities, minimizing vertex sequences. No Hierholzer in the oracle.
def euler(edges, want=None):
    if want is None:
        vertices = sorted({u for e in edges for u in e})
        best = None
        def search(path, mask):
            nonlocal best
            if best is not None and path > best[:len(path)]:
                return
            if mask == (1 << len(edges))-1:
                if best is None or path < best:
                    best = path[:]
                return
            u = path[-1]
            for i, (a, b) in enumerate(edges):
                if mask >> i & 1 or u not in (a, b):
                    continue
                v = b if u == a else a
                search(path + [v], mask | (1 << i))
        for u in vertices:
            search([u], 0)
        if best is None:
            return
        want = best
    got = list(map(int, run('euler', f'{len(edges)}\n' + ''.join(f'{u} {v}\n' for u, v in edges)).split()))
    assert got == want, (edges, got, want)
    assert Counter(tuple(sorted(e)) for e in edges) == Counter(tuple(sorted(e)) for e in zip(got, got[1:]))

possible = [(u, v) for u in range(1, 4) for v in range(u, 4)]
for mask in range(1, 1 << len(possible)):
    euler([e for i, e in enumerate(possible) if mask >> i & 1])
for mult in itertools.product(range(3), repeat=3):
    edges = [e for e, cnt in zip([(1, 1), (1, 2), (2, 2)], mult) for _ in range(cnt)]
    if edges:
        euler(edges)
for _ in range(250):
    labels = rng.sample(range(1, 501), rng.randint(1, 6))
    path = [rng.choice(labels) for _ in range(rng.randint(2, 9))]
    edges = list(zip(path, path[1:]))
    rng.shuffle(edges)
    euler(edges)
euler([(1, 500)] * 1024, [1 if i % 2 == 0 else 500 for i in range(1025)])
euler([(i, i+1) for i in range(1, 500)] + [(500, 1)] + [(1, 1)] * 524,
      [1] * 525 + list(range(2, 501)) + [1])

def span(v):
    result = {0}
    for x in v:
        result |= {x ^ y for y in list(result)}
    return result

def independent(v):
    pivots = []
    for x in v:
        for p in pivots:
            x = min(x, x ^ p)
        if x:
            pivots.append(x)
    return pivots

def basis_case(cases, expected, limit):
    data = str(len(cases)) + '\n' + ''.join(str(len(a))+' '+ ' '.join(map(str,a))+'\n'+str(len(b))+' '+' '.join(map(str,b))+'\n' for a,b in cases)
    for name in ['intersection', 'zassenhaus']:
        lines = run(name, data).splitlines()
        assert len(lines) == len(cases)
        for line, (a, b), want in zip(lines, cases, expected):
            values = list(map(int, line.split()))
            k, v = values[0], values[1:]
            assert len(v) == k and len(independent(v)) == k
            assert all(0 < x < 1 << limit for x in v)
            if isinstance(want, set):
                assert span(v) == want
            else:
                # Coordinate subspace: dimension and membership uniquely certify it.
                assert k == want.bit_count() and all(x & ~want == 0 for x in v)

# Every subspace of F2^4, generated by closure under adjoining a vector.
spaces = {frozenset({0})}
for x in range(1, 16):
    spaces |= {frozenset(set(s) | {x ^ y for y in s}) for s in list(spaces)}
spaces = sorted(spaces, key=lambda s: (len(s), sorted(s)))
assert len(spaces) == 67
cases, expected = [], []
for a in spaces:
    for b in spaces:
        cases.append((independent(sorted(a)), independent(sorted(b))))
        expected.append(set(a & b))
basis_case(cases, expected, 30)
# Dependent inputs and 64-bit values are extensions beyond the official 30-bit task.
cases, expected = [], []
for _ in range(500):
    shared = rng.getrandbits(64)
    a = [shared, 0, shared] + [rng.getrandbits(64) for _ in range(3)]
    b = [shared, shared] + [rng.getrandbits(64) for _ in range(3)]
    cases.append((a,b)); expected.append(span(a) & span(b))
cases += [([1 << i for i in range(64)], [1 << i for i in range(64)])]
expected += [(1 << 64)-1]
basis_case(cases, expected, 64)
# Maximum official T and 30-dimensional bases; varied coordinate intersections.
cases, expected = [], []
for i in range(100000):
    a = [1 << j for j in range(30) if i % 4 == 0 or (j+i) % 3 == 0]
    b = [1 << j for j in range(30) if i % 5 == 0 or (j+i) % 4 == 0]
    cases.append((a, b)); expected.append(sum(set(a) & set(b)))
basis_case(cases, expected, 30)

report = dict(mode=mode, counts=dict(counts), seconds=dict(seconds),
              basis_cases_per_driver=4489+501+100000, exhaustive_subspaces=67,
              scope='Local full-driver tests: walk-state BFS, exhaustive Euler edge-identity trails, enumerated vector spans and coordinate-subspace certificates. 64-bit and dependent-vector cases explicitly extend the official30-bit independent-input task. No online AC claim.',
              programs={k:dict(driver=v,bundle_sha256=hashlib.sha256((work/(k+'.cpp')).read_bytes()).hexdigest()) for k,v in drivers.items()})
Path(f'verification/xor-euler-usages-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
