"""Version branching and function-graph drivers against independent state oracles."""
from compiler_config import CXX
from pathlib import Path
from collections import Counter
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
work = root / 'build' / ('version-function-' + mode)
work.mkdir(parents=True, exist_ok=True)
flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2']
drivers = {'jump': 'verify/cses/1750.compact.cpp', 'steps': 'verify/cses/1160.compact.cpp',
           'visits': 'verify/luogu/P2921.compact.cpp', 'versions': 'verify/luogu/SP11470.compact.cpp',
           'cards': 'verify/qoj/8240.compact.cpp'}
for name, driver in drivers.items():
    subprocess.run(['python3', 'tools/bundle.py', driver, str(work / (name + '.cpp'))], check=True)
    subprocess.run([CXX, '-std=c++20', *flags, str(work / (name + '.cpp')), '-o', str(work / name)], check=True)
counts = Counter()
seconds = Counter()
def run(name, data, expected):
    start = time.monotonic()
    p = subprocess.run([str(work / name)], input=data, text=True, capture_output=True, timeout=180, check=True)
    seconds[name] += time.monotonic() - start
    assert not p.stderr, p.stderr
    assert p.stdout.split() == list(map(str, expected)), (name, data[:1000], p.stdout[:1000], str(expected)[:1000])
    counts[name] += 1

rng = random.Random(114701750)
def graph_input(to, queries=None):
    data = str(len(to)) if queries is None else f'{len(to)} {len(queries)}'
    data += '\n' + ' '.join(str(v+1) for v in to) + '\n'
    if queries is not None:
        data += ''.join(f'{u} {v}\n' for u, v in queries)
    return data

def graph_check(to):
    jumps, answers, steps, distances, visits = [], [], [], [], []
    for start in range(len(to)):
        seen, path = {}, []
        u = start
        while u not in seen:
            seen[u] = len(path)
            path.append(u)
            u = to[u]
        tail, length = seen[u], len(path)-seen[u]
        visits.append(len(path))
        for k in list(range(2*len(to)+1)) + [10**9, 2**63, 2**64-1]:
            jumps.append((start+1, k))
            answers.append(path[k if k < len(path) else tail+(k-tail)%length]+1)
        for v in range(len(to)):
            steps.append((start+1, v+1))
            distances.append(seen.get(v, -1))
    run('jump', graph_input(to, jumps), answers)
    run('steps', graph_input(to, steps), distances)
    run('visits', graph_input(to), visits)

exhaustive = 0
for n in range(1, 5):
    for to in itertools.product(range(n), repeat=n):
        graph_check(to)
        exhaustive += 1
for _ in range(100):
    n = rng.randint(1, 50)
    graph_check([rng.randrange(n) for _ in range(n)])
for name in ['jump', 'steps', 'visits']:
    n = 100000 if name == 'visits' else 200000
    entry = n//3
    to = list(range(1, n)) + [entry]
    if name == 'visits':
        run(name, graph_input(to), [n-u if u < entry else n-entry for u in range(n)])
    else:
        queries, expected = [], []
        for _ in range(200000):
            u = rng.randrange(n)
            if name == 'jump':
                k = rng.choice([0, 1, 10**9, 2**64-1, rng.randrange(10**9+1)])
                queries.append((u+1, k))
                expected.append((u+k if u+k < n else entry+(u+k-entry)%(n-entry))+1)
            else:
                v = rng.randrange(n)
                queries.append((u+1, v+1))
                expected.append(v-u if v >= u else n-u+v-entry if v >= entry else -1)
        run(name, graph_input(to, queries), expected)

# Full independent arrays are keyed by the problem's logical time, overwritten after B.
def version_case(n, m):
    initial = [rng.randint(-10**9, 10**9) for _ in range(n)]
    states = {0: initial[:]}
    t = 0
    ops, expected = [], []
    for _ in range(m):
        op = rng.choice(['C', 'C', 'Q', 'H', 'B'])
        if op == 'B':
            t = rng.randint(0, t)
            ops.append(f'B {t}')
            continue
        l, r = sorted([rng.randrange(n), rng.randrange(n)])
        if op == 'C':
            d = rng.randint(-10000, 10000)
            a = states[t][:]
            for p in range(l, r+1):
                a[p] += d
            t += 1
            states[t] = a
            ops.append(f'C {l+1} {r+1} {d}')
        else:
            h = rng.randint(0, t) if op == 'H' else t
            ops.append(f'{op} {l+1} {r+1}' + (f' {h}' if op == 'H' else ''))
            expected.append(sum(states[h][l:r+1]))
    return f'{n} {m}\n' + ' '.join(map(str, initial)) + '\n' + '\n'.join(ops) + '\n', expected
for _ in range(300):
    data, expected = version_case(rng.randint(1, 30), rng.randint(1, 200))
    run('versions', data, expected)
# EOF multi-case reset, independent n/values/version space for each case.
a, x = version_case(1, 150)
b, y = version_case(17, 100)
run('versions', a+b, x+y)
n = m = 100000
initial = [10**9 if i % 2 else -10**9 for i in range(n)]
pre = [0]
for v in initial:
    pre.append(pre[-1]+v)
delta, t, ops, expected = {0: 0}, 0, [], []
for i in range(m):
    if i % 7 < 3:
        d = 10000 if i % 2 else -10000
        value = delta[t]+d
        t += 1
        delta[t] = value
        ops.append(f'C 1 {n} {d}')
    elif i % 7 == 3:
        t = rng.randint(0, t)
        ops.append(f'B {t}')
    else:
        l, r = sorted([rng.randint(1, n), rng.randint(1, n)])
        h = rng.randint(0, t)
        ops.append(f'H {l} {r} {h}')
        expected.append(pre[r]-pre[l-1]+(r-l+1)*delta[h])
run('versions', f'{n} {m}\n'+' '.join(map(str, initial))+'\n'+'\n'.join(ops)+'\n', expected)
# Many distinct partial paths force vector expansion; final/history queries retain old roots.
ops = [f'C {i} {i} 10000' for i in range(1, m-1)]
ops += [f'Q 1 {n}', f'H 1 {n} {m//2}']
run('versions', f'{n} {m}\n'+'1000000000 '*n+'\n'+'\n'.join(ops)+'\n', [10**9*n+10000*(m-2), 10**9*n+10000*(m//2)])

def remaining(a, l, r):
    pile = []
    for x in a[l-1:r]:
        if x in pile:
            del pile[pile.index(x):]
        else:
            pile.append(x)
    return len(pile)

def cards(a, queries, formula=None):
    expected, lines, last = [], [f'{len(a)} {len(queries)}', ' '.join(map(str, a))], 0
    for l, r in queries:
        lines.append(f'{l^last} {r^last}')
        last = remaining(a, l, r) if formula is None else formula(l, r)
        expected.append(last)
    run('cards', '\n'.join(lines)+'\n', expected)
card_exhaustive = 0
for n in range(1, 8):
    for a in itertools.product(range(1, min(n, 2)+1), repeat=n):
        queries = [(l, r) for l in range(1, n+1) for r in range(l, n+1)]
        rng.shuffle(queries)
        cards(a, queries)
        card_exhaustive += 1
for _ in range(100):
    n = rng.randint(1, 70)
    a = [rng.randint(1, n) for _ in range(n)]
    queries = [tuple(sorted([rng.randint(1, n), rng.randint(1, n)])) for _ in range(100)]
    cards(a, queries)
n = q = 300000
queries = [tuple(sorted([rng.randint(1, n), rng.randint(1, n)])) for _ in range(q)]
for period in [1, 1000, n]:
    cards([i % period+1 for i in range(n)], queries, lambda l, r: (r-l+1) % (period+1))
a = [rng.randint(1, n//2) for _ in range(n)]
queries = []
for _ in range(q):
    l = rng.randint(1, n)
    queries.append((l, min(n, l+rng.randrange(25))))
cards(a, queries)
report = dict(mode=mode, counts=dict(counts), seconds=dict(seconds), exhaustive_functions_up_to_4=exhaustive,
              exhaustive_binary_card_arrays_up_to_7=card_exhaustive,
              scope='Local complete programs. First-visit functional walks, full version snapshots with overwrites, literal card removal with XOR queries, statement maxima. Jump tests additionally include full unsigned64 range; this is beyond CSES constraints and not an online AC claim.',
              programs={name:dict(driver=driver,bundle_sha256=hashlib.sha256((work/(name+'.cpp')).read_bytes()).hexdigest()) for name,driver in drivers.items()})
(root/'verification'/('version-function-usages-'+mode+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
