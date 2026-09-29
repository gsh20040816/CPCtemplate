"""Complete graph applications, independently checked by subsets and parent choices."""
from compiler_config import CXX
from usage_checkers import check_output
from pathlib import Path
import itertools
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
mode = 'san' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-std=c++20', '-O2'] if mode == 'normal' else ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
exe = {}
for problem in ['P2762', 'P4716', 'P5632']:
    source = root / f'build/cut-{problem}-{mode}.cpp'
    exe[problem] = source.with_suffix('')
    subprocess.run(['python3', str(root / 'tools/bundle.py'), str(root / f'verify/luogu/{problem}.compact.cpp'), str(source)], check=True)
    subprocess.run([CXX, *flags, str(source), '-o', str(exe[problem])], check=True)


def run(problem, data):
    p = subprocess.run([str(exe[problem])], input=data, text=True, capture_output=True, check=True, timeout=120)
    assert not p.stderr, p.stderr
    return p.stdout


def project_best(profit, needs, cost):
    best = 0
    for mask in range(1 << len(profit)):
        chosen = [i for i in range(len(profit)) if mask >> i & 1]
        tools = {j for i in chosen for j in needs[i]}
        best = max(best, sum(profit[i] for i in chosen) - sum(cost[j] for j in tools))
    return best


count = 0

def project(profit, needs, cost, known=None):
    global count
    best = project_best(profit, needs, cost) if known is None else known
    # A second small oracle enumerates both selections, without inferring tools.
    if len(profit) + len(cost) <= 8:
        brute = 0
        for a in range(1 << len(profit)):
            for b in range(1 << len(cost)):
                if all(not(a >> i & 1) or all(b >> j & 1 for j in ns) for i, ns in enumerate(needs)):
                    value = sum(p for i, p in enumerate(profit) if a >> i & 1) - sum(c for j, c in enumerate(cost) if b >> j & 1)
                    brute = max(brute, value)
        assert brute == best
    sep = '\r\n' if count % 2 else '\n'
    lines = [f'{len(profit)} {len(cost)}']
    for p, ns in zip(profit, needs):
        lines.append(str(p) + ''.join(f'\t{j+1} ' for j in ns) + '  ')
    lines.append(' '.join(map(str, cost)))
    data = sep.join(lines) + sep
    expected = {'project_plan': (profit, needs, cost, best)}
    check_output('P2762', mode, data, run('P2762', data), expected)
    count += 1


for values in itertools.product([1, 3], repeat=4):
    for mask in range(16):
        project(values[:2], [[j for j in range(2) if mask >> (2*i+j) & 1] for i in range(2)], values[2:])
rng = random.Random(2026092906)
for _ in range(400):
    m, n = rng.randrange(1, 9), rng.randrange(1, 8)
    project([rng.randrange(1, 100) for _ in range(m)], [[j for j in range(n) if rng.randrange(2)] for _ in range(m)], [rng.randrange(1, 100) for _ in range(n)])
big = (1 << 31) - 1
project([big] * 50, [[] for _ in range(50)], [big] * 50, 50 * big)
project([big] * 50, [list(range(50)) for _ in range(50)], [big] * 50, 0)
project([big] * 50, [[0] for _ in range(50)], [big] * 50, 49 * big)
project([100+i for i in range(50)], [[i] for i in range(50)], [100 if i%2 else 200 for i in range(50)], sum(i for i in range(50) if i%2))
# Reject malformed, duplicate, infeasible and nonoptimal certificates.
expected = {'project_plan': ([9, 2], [[0], [1]], [3, 4], 6)}
for bad in ['1\n\n6\n', '1 1\n1\n6\n', '1\n1\n7\n', '\n\n0\n', '3\n1\n6\n', '1\n1\n6\nextra\n']:
    try:
        check_output('negative-control', mode, '', bad, expected)
    except (AssertionError, ValueError):
        pass
    else:
        raise AssertionError(('accepted bad certificate', bad))
print(f'P2762 PASS: {count} independent optimum and selection certificates; exhaustive 2x2 models, CRLF/LF, empty lines, 50x50 and 64-bit totals; 6 negative controls rejected', flush=True)


def arb_best(n, root, edges):
    options = [[e for e in edges if e[1] == v and e[0] != v] for v in range(n) if v != root]
    best = None
    for picked in itertools.product(*options):
        children = [[] for _ in range(n)]
        for u, v, w in picked:
            children[u].append(v)
        seen = {root}
        queue = [root]
        for u in queue:
            for v in children[u]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        if len(seen) == n:
            value = sum(e[2] for e in picked)
            best = value if best is None else min(best, value)
    return -1 if best is None else best


arb_count = 0

def arb(n, r, edges, known=None):
    global arb_count
    best = arb_best(n, r, edges) if known is None else known
    data = f'{n} {len(edges)} {r+1}\n' + ''.join(f'{u+1} {v+1} {w}\n' for u, v, w in edges)
    assert run('P4716', data).split() == [str(best)]
    arb_count += 1


for _ in range(350):
    n = rng.randrange(1, 7)
    e = [(rng.randrange(n), rng.randrange(n), rng.randrange(1, 8)) for _ in range(rng.randrange(1, 13))]
    arb(n, rng.randrange(n), e)
# Positive costs still create cycles after selecting minimum incoming edges.
for shift in [0, 37, 99]:
    n = 100
    e = [(0, 1, 99), (0, n-1, 6), (1, 0, 1)]
    for i in range(1, n-1):
        e += [(i, i+1, 1), (i+1, i, 1)]
    e += [(i % n, (i*17+13) % n, 10**6) for i in range(10000-len(e))]
    e = [((u+shift)%n, (v+shift)%n, w) for u, v, w in e]
    arb(n, shift, e, 104)
arb(100, 17, [(u, v, 10**6) for u in range(100) for v in range(100)], 99*10**6)
arb(100, 99, [(u, v, 1) for u in range(99) for v in range(99)], -1)
print(f'P4716 PASS: {arb_count} full inputs; independent incoming-edge choices and root reachability; 100-vertex/10000-edge nested cycles, arbitrary roots, unreachable and maximum weights', flush=True)


def cut_best(n, e):
    return min(sum(w for u, v, w in e if (mask >> u & 1) != (mask >> v & 1)) for mask in range(1, (1<<n)-1, 2))


cut_count = 0

def cut(n, e, known=None):
    global cut_count
    best = cut_best(n, e) if known is None else known
    data = f'{n} {len(e)}\n' + ''.join(f'{u+1} {v+1} {w}\n' for u, v, w in e)
    assert run('P5632', data).split() == [str(best)]
    cut_count += 1


for n in range(2, 5):
    pairs = list(itertools.combinations(range(n), 2))
    for values in itertools.product(range(3), repeat=len(pairs)):
        e = [(u, v, w) for (u, v), w in zip(pairs, values) if w]
        seen = {0}
        for _ in range(n):
            for u, v, _ in e:
                if u in seen or v in seen:
                    seen.update([u, v])
        if len(seen) == n:
            cut(n, e)
for _ in range(240):
    n = rng.randrange(2, 10)
    e = [(rng.randrange(v), v, rng.randrange(1, 1000)) for v in range(1, n)]
    used = {tuple(sorted((u, v))) for u, v, _ in e}
    for u, v in itertools.combinations(range(n), 2):
        if (u, v) not in used and rng.randrange(2):
            e.append((u, v, rng.randrange(1, 1000)))
    cut(n, e)
cut(600, [(u, v, 1) for u, v in itertools.combinations(range(600), 2)], 599)
cut(600, [(v-1, v, 1+v%997) for v in range(1, 600)], 2)
cut(600, [(0, v, 1000+v) for v in range(1, 600)], 1001)
e = [(u, v, 1) for group in [range(300), range(300, 600)] for u, v in itertools.combinations(group, 2)]
cut(600, e+[(299, 300, 1)], 1)
cut(2, [(0, 1, 10**9)], 10**9)
print(f'P5632 PASS: {cut_count} official-scope full inputs; all connected ternary-weight graphs through 4 vertices and independent cut enumeration; 600-vertex dense/chain/star/bridge families', flush=True)
# Extra adapter behavior outside the connected, positive, nontrivial task.
cut(1, [(0, 0, 7)], 0)
cut(3, [(0, 1, 8)], 0)
cut(2, [(0, 1, 3), (1, 0, 7), (0, 0, 500)], 10)
print('P5632 extensions PASS: singleton convention, disconnected graph, parallel/reversed edges and ignored loops', flush=True)
