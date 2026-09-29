"""Independent full-driver checks; local evidence, not online AC."""
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
work = root / 'build' / ('connectivity-' + mode)
work.mkdir(parents=True, exist_ok=True)
flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2']
if os.uname().sysname == 'Darwin':
    flags += ['-Wl,-stack_size,0x20000000']
drivers = {'scc': 'verify/library_checker/scc.kosaraju.compact.cpp',
           'cut': 'verify/aoj/GRL_3_A.removal.compact.cpp',
           'rank': 'verify/uva/10765.compact.cpp',
           'orient': 'verify/luogu/CF118E.compact.cpp'}
for name, driver in drivers.items():
    subprocess.run(['python3', 'tools/bundle.py', driver, str(work / (name + '.cpp'))], check=True)
    subprocess.run([CXX, '-std=c++20', *flags, str(work / (name + '.cpp')), '-o', str(work / name)], check=True)
counts = Counter()
def run(name, data):
    p = subprocess.run([str(work / name)], input=data, text=True, capture_output=True, timeout=120, check=True)
    assert not p.stderr, p.stderr
    counts[name] += 1
    return p.stdout

def components(n, edges, removed=-1, skip=-1):
    g = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        if i != skip and u != removed and v != removed:
            g[u].append(v)
            g[v].append(u)
    seen = {removed}
    count = 0
    for u in range(n):
        if u not in seen:
            count += 1
            seen.add(u)
            q = [u]
            for v in q:
                for w in g[v]:
                    if w not in seen:
                        seen.add(w)
                        q.append(w)
    return count

def reaches(n, edges):
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
    seen = {0}
    q = [0]
    for u in q:
        for v in g[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == n

def scc_check(n, edges, text, want=None):
    lines = text.splitlines()
    k = int(lines[0])
    assert len(lines) == k + 1 and 1 <= k <= n
    bel = [-1] * n
    for i, line in enumerate(lines[1:]):
        row = list(map(int, line.split()))
        assert row[0] == len(row) - 1 and row[0] > 0
        for u in row[1:]:
            assert 0 <= u < n and bel[u] == -1
            bel[u] = i
    assert min(bel) >= 0
    assert all(bel[u] <= bel[v] for u, v in edges)
    if want is not None:
        # Compare partitions without assuming arbitrary order of disconnected SCCs.
        mapped = {}
        reverse = {}
        for a, b in zip(bel, want):
            assert mapped.setdefault(a, b) == b and reverse.setdefault(b, a) == a
    else:
        reach = [[u == v for v in range(n)] for u in range(n)]
        for u, v in edges:
            reach[u][v] = True
        for t in range(n):
            for u in range(n):
                if reach[u][t]:
                    for v in range(n):
                        reach[u][v] |= reach[t][v]
        assert all((bel[u] == bel[v]) == (reach[u][v] and reach[v][u]) for u in range(n) for v in range(n))

def orientation_check(n, edges, text, possible):
    values = list(map(int, text.split()))
    if not possible:
        assert values == [0]
        return
    assert len(values) == 2 * len(edges)
    directed = [(values[i] - 1, values[i + 1] - 1) for i in range(0, len(values), 2)]
    assert Counter(tuple(sorted(e)) for e in directed) == Counter(tuple(sorted(e)) for e in edges)
    assert reaches(n, directed) and reaches(n, [(v, u) for u, v in directed])

def data(n, edges, base=0):
    return f'{n} {len(edges)}\n' + ''.join(f'{u + base} {v + base}\n' for u, v in edges)

rng = random.Random(2909161)
# Exhaustive directed three-vertex graphs, including loops and empty graph extension.
for mask in range(1 << 9):
    edges = [(u, v) for u in range(3) for v in range(3) if mask >> (3 * u + v) & 1]
    scc_check(3, edges, run('scc', data(3, edges)))
for _ in range(120):
    n = rng.randrange(1, 18)
    edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randrange(1, 80))]
    scc_check(n, edges, run('scc', data(n, edges)))
n = 500000
for edges, want in [([(u, u + 1) for u in range(n - 1)], list(range(n))),
                    ([(u, (u + 1) % n) for u in range(n)], [0] * n),
                    ([(u, u ^ 1) for u in range(n)], [u // 2 for u in range(n)])]:
    scc_check(n, edges, run('scc', data(n, edges)), want)

small = []
for n in range(1, 5):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        small.append((n, [e for i, e in enumerate(pairs) if mask >> i & 1]))
for _ in range(150):
    n = rng.randrange(1, 12)
    small.append((n, [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randrange(35))]))
rank_inputs = []
rank_answers = []
connected_cut = 0
for n, edges in small:
    before = components(n, edges)
    after = [components(n, edges, u) for u in range(n)]
    expected = ''.join(f'{u}\n' for u in range(n) if after[u] > before)
    assert run('cut', data(n, edges)) == expected
    connected_cut += before == 1
    m = rng.randrange(1, n + 1)
    rank_inputs.append(f'{n} {m}\n' + ''.join(f'{u} {v}\n' for u, v in edges) + '-1 -1\n')
    order = sorted(range(n), key=lambda u: (-after[u], u))[:m]
    rank_answers.append(''.join(f'{u} {after[u]}\n' for u in order) + '\n')
# Official UVA sample and exact blank-line formatting, followed by many test cases.
rank_inputs.insert(0, '8 4\n0 4\n1 2\n2 3\n2 4\n3 5\n3 6\n3 7\n6 7\n-1 -1\n')
rank_answers.insert(0, '2 3\n3 3\n4 2\n0 1\n\n')
n = 10000
rank_inputs.append(f'{n} {n}\n' + ''.join(f'{u} {u + 1}\n' for u in range(n - 1)) + '-1 -1\n')
rank_answers.append(''.join(f'{u} 2\n' for u in range(1, n - 1)) + f'0 1\n{n - 1} 1\n\n')
assert run('rank', ''.join(rank_inputs) + '0 0\n') == ''.join(rank_answers)
assert run('rank', '0 0\n') == ''
n = 100000
for edges, expected in [([(u, u + 1) for u in range(n - 1)], ''.join(f'{u}\n' for u in range(1, n - 1))),
                        ([(0, u) for u in range(1, n)], '0\n'),
                        ([(u, (u + 1) % n) for u in range(n)], '')]:
    assert run('cut', data(n, edges)) == expected

# Strong orientation: independent deletion of every edge establishes feasibility.
orient_cases = 0
for n in range(2, 6):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [e for i, e in enumerate(pairs) if mask >> i & 1]
        if components(n, edges) != 1:
            continue
        possible = all(components(n, edges, skip=i) == 1 for i in range(len(edges)))
        orientation_check(n, edges, run('orient', data(n, edges, 1)), possible)
        orient_cases += 1
# Parallel edges, self loops and disconnected graph are API extensions, not CF constraints.
for n, edges in small:
    if n < 2:
        continue
    possible = components(n, edges) == 1 and all(components(n, edges, skip=i) == 1 for i in range(len(edges)))
    orientation_check(n, edges, run('orient', data(n, edges, 1)), possible)
n = 100000
for edges, possible in [([(u, u + 1) for u in range(n - 1)], False),
                        ([(u, (u + 1) % n) for u in range(n)], True),
                        ([(u, (u + k) % n) for k in [1, 2, 3] for u in range(n)], True)]:
    orientation_check(n, edges, run('orient', data(n, edges, 1)), possible)
negative = 0
for check in [lambda: scc_check(2, [(0, 1)], '2\n1 1\n1 0\n'),
              lambda: scc_check(2, [(0, 1)], '1\n2 0 1\n'),
              lambda: scc_check(2, [(0, 1), (1, 0)], '2\n1 0\n1 1\n'),
              lambda: scc_check(2, [], '2\n1 0\n1 0\n'),
              lambda: orientation_check(3, [(0, 1), (1, 2), (2, 0)], '1 2\n2 3\n1 3\n', True),
              lambda: orientation_check(3, [(0, 1), (1, 2), (2, 0)], '1 2\n2 3\n2 3\n', True),
              lambda: orientation_check(3, [(0, 1), (1, 2), (2, 0)], '0\n', True)]:
    try:
        check()
    except AssertionError:
        negative += 1
    else:
        raise AssertionError('Negative output accepted')
paths = list(drivers.values()) + ['src/compact/graph.hpp', 'src/compact/biconnected_core.hpp', 'src/compact/vertex_removal.hpp', 'src/compact/edge_components.hpp', 'tests/connectivity_usages.py']
report = dict(mode=mode, invocations=dict(counts), removal_small_cases=len(small), removal_connected_cases=connected_cut,
              rank_cases=len(rank_inputs), orientation_exhaustive_connected_simple=orient_cases, negative_controls=negative,
              scope='Independent full-driver reachability/removal certificates, exact UVA formatting and recursive maximum-depth graphs. Extensions beyond official input constraints are included separately. Local only; no online AC.',
              sha256={p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths})
Path(f'verification/connectivity-usages-{mode}.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
