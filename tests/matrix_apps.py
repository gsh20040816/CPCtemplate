"""Full protocols checked against edge/parent enumeration, not elimination."""
from pathlib import Path
import hashlib
import itertools
import json
import math
import os
import random
import subprocess
import time
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/matrix-apps'
OUT.mkdir(parents=True, exist_ok=True)
rng = random.Random(43364455)
cases = {'P4336': [], 'P4455': []}


def companies(n, groups):
    answer = 0
    for choice in itertools.product(*groups):
        adj = [[] for _ in range(n)]
        for u, v in choice:
            adj[u].append(v)
            adj[v].append(u)
        reached = set()

        def dfs(u):
            if u in reached:
                return
            reached.add(u)
            for v in adj[u]:
                dfs(v)

        dfs(0)
        answer += len(reached) == n
    data = str(n) + '\n'
    for group in groups:
        data += str(len(group)) + '\n'
        data += ''.join(f'{u+1} {v+1}\n' for u, v in group)
    cases['P4336'].append((data, answer % 1000000007))


def followers(n, edges):
    friends = [set() for _ in range(n)]
    for u, v in edges:
        if u != v:
            friends[u].add(v)
    answer = 0
    for parents in itertools.product(*friends[1:]):
        parent = (0,) + parents
        good = True
        for u in range(1, n):
            visited = set()
            while u != 0 and u not in visited:
                visited.add(u)
                u = parent[u]
            if u != 0:
                good = False
                break
        answer += good
    data = f'{n} {len(edges)}\n'
    data += ''.join(f'{u+1} {v+1}\n' for u, v in edges)
    cases['P4455'].append((data, answer % 10007))


companies(2, [[]])
companies(2, [[(0, 1)]])
companies(3, [[(0, 1)], [(0, 1)]])
companies(3, [[(0, 1), (1, 2)], [(0, 1), (1, 2)]])
for _ in range(200):
    n = rng.randrange(2, 7)
    edges = list(itertools.combinations(range(n), 2))
    groups = [rng.sample(edges, rng.randrange(min(5, len(edges)) + 1))
              for _ in range(n - 1)]
    companies(n, groups)
for n in range(2, 7):
    companies(n, [list(itertools.combinations(range(n), 2))] * (n - 1))
for n in range(1, 5):
    edges = [(u, v) for u in range(n) for v in range(n) if u != v]
    for mask in range(1 << len(edges)):
        followers(n, [e for i, e in enumerate(edges) if mask >> i & 1])
for _ in range(100):
    n = rng.randrange(2, 7)
    edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(15)]
    followers(n, edges)

large = {}
n = 17
group = list(itertools.combinations(range(n), 2))
data = str(n) + '\n' + (str(len(group)) + '\n' + ''.join(
    f'{u+1} {v+1}\n' for u, v in group)) * (n - 1)
large['P4336'] = [(data, pow(n, n-2, 1000000007) * math.factorial(n-1) % 1000000007)]
large['P4336'].append((str(n) + '\n0\n' + (str(len(group)) + '\n' + ''.join(
    f'{u+1} {v+1}\n' for u, v in group)) * (n - 2), 0))
n = 250
edges = [(u, v) for u in range(n) for v in range(n) if u != v]
large['P4455'] = [(f'{n} {len(edges)}\n' + ''.join(
    f'{u+1} {v+1}\n' for u, v in edges), pow(n, n-2, 10007))]

env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
           UBSAN_OPTIONS='halt_on_error=1')
results = {}
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    for problem in cases:
        src = ROOT / f'verify/luogu/{problem}.compact.cpp'
        exe = OUT / f'{problem}-{mode}'
        subprocess.run([CXX, *flags, str(src), '-o', str(exe)], check=True)
        times = []
        for i, (data, expected) in enumerate(cases[problem] + large[problem]):
            start = time.monotonic()
            r = subprocess.run([str(exe)], input=data, text=True, capture_output=True,
                               check=True, env=env, timeout=180)
            elapsed = time.monotonic() - start
            assert not r.stderr, r.stderr
            assert r.stdout.split() == [str(expected)], (problem, i, expected, r.stdout)
            if i >= len(cases[problem]):
                times.append(elapsed)
        results[f'{problem}-{mode}'] = {'small_cases': len(cases[problem]),
                                      'large_cases': len(large[problem]),
                                      'large_seconds': times}
        print(problem, mode, results[f'{problem}-{mode}'], flush=True)
paths = ['tests/matrix_apps.py', 'src/compact/matrix_tree.hpp', 'src/compact/det_prime.hpp',
         'src/compact/number_theory.hpp', 'verify/luogu/P4336.compact.cpp',
         'verify/luogu/P4455.compact.cpp']
report = {'status': 'pass', 'results': results,
          'scope': 'Local full protocols, exhaustive digraphs through n=4, independent company/parent enumeration and maximum-size Cayley identities. No online verdict or ranking.',
          'hashes': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}}
(ROOT / 'verification/matrix-apps.json').write_text(json.dumps(report, indent=2) + '\n')
