"""Small simple-path enumeration / edge-deletion checks, no online AC claim."""
from compiler_config import CXX
from pathlib import Path
from collections import Counter
import hashlib
import itertools
import json
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
os.chdir(root)
mode = 'sanitizer' if os.getenv('CPC_SANITIZE') == '1' else 'normal'
work = root / 'build' / ('forest-' + mode)
work.mkdir(parents=True, exist_ok=True)
flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2']
if os.uname().sysname == 'Darwin':
    flags += ['-Wl,-stack_size,0x20000000']
drivers = {'paths': 'verify/luogu/P4630.compact.cpp',
           'leaves': 'verify/luogu/P2860.forest.compact.cpp',
           'augment': 'verify/luogu/P2860.compact.cpp',
           'interfaces': 'tests/forest_interfaces.cpp'}
for name, driver in drivers.items():
    subprocess.run(['python3', 'tools/bundle.py', driver, str(work / (name + '.cpp'))], check=True)
    subprocess.run([CXX, '-std=c++20', *flags, str(work / (name + '.cpp')), '-o', str(work / name)], check=True)
counts = Counter()
def run(name, data):
    p = subprocess.run([str(work / name)], input=data, text=True, capture_output=True, timeout=120, check=True)
    assert not p.stderr, p.stderr
    counts[name] += 1
    return p.stdout

def data(n, edges):
    return f'{n} {len(edges)}\n' + ''.join(f'{u+1} {v+1}\n' for u, v in edges)

def groups(n, edges, skip=-1):
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        if i != skip:
            adj[u].append(v)
            adj[v].append(u)
    bel = [-1] * n
    k = 0
    for u in range(n):
        if bel[u] != -1:
            continue
        bel[u] = k
        q = [u]
        for v in q:
            for w in adj[v]:
                if bel[w] == -1:
                    bel[w] = k
                    q.append(w)
        k += 1
    return bel, k

def resilient(n, edges):
    return groups(n, edges)[1] == 1 and all(groups(n, edges, i)[1] == 1 for i in range(len(edges)))

def optimum(n, edges):
    # Enumerate multisets of added edges, including parallel edges; no leaf formula.
    possible = list(itertools.combinations(range(n), 2))
    for k in range(n + 1):
        for added in itertools.combinations_with_replacement(possible, k):
            if resilient(n, edges + list(added)):
                return k
    raise AssertionError('no augmentation found')

def triples(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    found = set()
    def visit(path, seen):
        for c in path[1:-1]:
            found.add((path[0], c, path[-1]))
        for v in adj[path[-1]] - seen:
            visit(path + [v], seen | {v})
    for s in range(n):
        visit([s], {s})
    return len(found)

simple = []
for n in range(1, 6):
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        simple.append((n, [e for i, e in enumerate(possible) if mask >> i & 1]))
rng = random.Random(46302860)
random_cases = []
for _ in range(100):
    n = rng.randrange(2, 9)
    edges = [e for e in itertools.combinations(range(n), 2) if rng.randrange(4) == 0]
    random_cases.append((n, edges))
for n, edges in simple + random_cases:
    assert run('paths', data(n, edges)).split() == [str(triples(n, edges))], (n, edges)
n = 100000
large_paths = [(n, [(u-1, u) for u in range(1, n)], n*(n-1)*(n-2)//3),
               (n, [(u, (u+1) % n) for u in range(n)], n*(n-1)*(n-2)),
               (n, [(0, u) for u in range(1, n)], (n-1)*(n-2)),
               (n, [], 0),
               (n, [(u-1, u) for u in range(1, n) if u != n//2], 2*(n//2)*(n//2-1)*(n//2-2)//3)]
# Cycle plus chords stays biconnected; maximum m=200000.
large_paths.append((n, [(u, (u+1) % n) for u in range(n)] + [(u, (u+2) % n) for u in range(n)], n*(n-1)*(n-2)))
for n, edges, expected in large_paths:
    assert run('paths', data(n, edges)).split() == [str(expected)]

extended = [(1, [(0, 0)]), (2, [(0, 1)] * 2)]
for _ in range(100):
    n = rng.randrange(1, 9)
    edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randrange(15))]
    extended.append((n, edges))
interface_cases = simple + random_cases + extended
raw = run('interfaces', str(len(interface_cases)) + '\n' + ''.join(data(n, e) for n, e in interface_cases))
lines = iter(raw.splitlines())
minimal_enumerations = 0
for n, edges in interface_cases:
    before = groups(n, edges)[1]
    bridges = [i for i in range(len(edges)) if groups(n, edges, i)[1] > before]
    want, k = groups(n, [e for i, e in enumerate(edges) if i not in bridges])
    cnt = int(next(lines))
    assert cnt == k
    bel = [int(x)-1 for x in next(lines).split()]
    assert len(bel) == n and set(bel) == set(range(k))
    assert all((bel[u] == bel[v]) == (want[u] == want[v]) for u in range(n) for v in range(n))
    actual = Counter()
    degree = []
    for u in range(k):
        row = list(map(int, next(lines).split()))
        assert len(row) == 1 + 2*row[0]
        degree.append(row[0])
        for j in range(row[0]):
            actual[u, row[2*j+1]-1, row[2*j+2]] += 1
    expected = Counter()
    for i in bridges:
        u, v = edges[i]
        expected[bel[u], bel[v], i] += 1
        expected[bel[v], bel[u], i] += 1
    assert actual == expected
    size = int(next(lines))
    if before != 1:
        assert size == -1
        continue
    added = [tuple(int(x)-1 for x in next(lines).split()) for _ in range(size)]
    assert all(len(e) == 2 and 0 <= e[0] < n and 0 <= e[1] < n and e[0] != e[1] for e in added)
    assert resilient(n, edges + added)
    best = (degree.count(1) + 1)//2
    if n <= 5:
        best = optimum(n, edges)
        minimal_enumerations += 1
    assert size == best
    for driver in ['leaves', 'augment']:
        assert run(driver, data(n, edges)).split() == [str(best)]
assert list(lines) == []
large_bridge = [(5000, [(u-1, u) for u in range(1, 5000)], 1),
                (5000, [(0, u) for u in range(1, 5000)], 2500),
                (5000, [(u, (u+1) % 5000) for u in range(5000)] * 2, 0)]
for n, edges, expected in large_bridge:
    for driver in ['leaves', 'augment']:
        assert run(driver, data(n, edges)).split() == [str(expected)]
report = {'mode': mode, 'counts': dict(counts), 'all_simple_graphs_up_to_5': len(simple),
          'interface_cases': len(interface_cases), 'independent_minimum_enumerations': minimal_enumerations,
          'scope': 'Local simple-path enumeration, bridge IDs and adjacency multiplicities, optimal added-edge multisets and edge-deletion certificates. No online AC.',
          'programs': {name: {'driver': driver, 'bundle_sha256': hashlib.sha256((work/(name+'.cpp')).read_bytes()).hexdigest()} for name, driver in drivers.items()}}
(root / 'verification' / ('forest-usages-' + mode + '.json')).write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
