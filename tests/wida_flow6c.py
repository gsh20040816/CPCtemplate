"""Audit WIDA MaxFlow flow, restored edges, and the post-flow source cut."""
import hashlib, os, random, subprocess, sys
from collections import deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = (root / 'tests/fixtures/wida_flow6c/main.cpp').read_bytes()
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'a51f7e70858f6002bbe4bedb8f8c6e5f8aefd66b'
text = blob.decode().replace('\r\n', '\n')
assert 'std::vector<bool> minCut()' in text and 'x.flow = e[i + 1].cap' in text

def ek(n, edges, s, t):
    g = [[] for _ in range(n)]
    def add(u, v, c):
        if u == v or c == 0:
            return
        g[u].append([v, c, len(g[v])])
        g[v].append([u, 0, len(g[u]) - 1])
    for u, v, c in edges:
        add(u, v, c)
    if s == t:
        return 0, [True] + [False] * (n - 1) if n else []
    total = 0
    while True:
        parent = [-1] * n
        parent[s] = -2
        q = deque([s])
        found = False
        while q and not found:
            u = q.popleft()
            for i, (v, c, _) in enumerate(g[u]):
                if c and parent[v] == -1:
                    parent[v] = (u, i)
                    if v == t:
                        found = True
                        break
                    q.append(v)
        if not found:
            side = [False] * n
            q = deque([s])
            side[s] = True
            while q:
                u = q.popleft()
                for v, c, _ in g[u]:
                    if c and not side[v]:
                        side[v] = True
                        q.append(v)
            return total, side
        v = t
        cap = 10**30
        while v != s:
            u, i = parent[v]
            cap = min(cap, g[u][i][1])
            v = u
        v = t
        while v != s:
            u, i = parent[v]
            g[u][i][1] -= cap
            rev = g[u][i][2]
            g[v][rev][1] += cap
            v = u
        total += cap

rng = random.Random(8)
cases = [
    (1, [], 0, 0, 1),
    (2, [(0, 1, 0)], 0, 1, 0),
    (2, [(0, 1, 5), (0, 1, 7)], 0, 1, 0),
    (3, [(0, 1, 3), (1, 2, 4), (0, 2, 1), (2, 1, 5)], 0, 2, 0),
    (3, [(0, 0, 9), (0, 1, 2)], 0, 1, 0),
]
for _ in range(25):
    n = rng.randrange(1, 7)
    edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(0, 12)) for _k in range(rng.randrange(0, 10))]
    cases.append((n, edges, rng.randrange(n), rng.randrange(n), 0))

lines = [str(len(cases))]
for n, edges, s, t, pre in cases:
    lines.append(f'{n} {len(edges)} {s} {t} {pre}')
    lines += [f'{u} {v} {c}' for u, v, c in edges]
payload = '\n'.join(lines) + '\n'
out = root / 'build/wida-flow6c'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_flow6c.cpp'
report = []
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], input=payload, text=True, capture_output=True, env=env, timeout=60, check=True)
    assert got.stderr == ''
    checks = 0
    for row, (n, edges, s, t, pre) in zip(got.stdout.splitlines(), cases):
        parts = list(map(int, row.split()))
        flow, library, before = parts[:3]
        cut = parts[3:3 + n]
        rest = parts[3 + n:]
        count = rest[0]
        rec = rest[1:]
        expect, _side = ek(n, edges, s, t)
        assert flow == expect
        if s != t:
            assert library == flow and cut[s] == 1 and cut[t] == 0
        else:
            assert library == -1 and flow == 0 and cut[s] == 1
        if pre:
            assert before == 1
        assert count == len(edges)
        parsed = []
        for i in range(count):
            parsed.append(tuple(rec[i * 4:(i + 1) * 4]))
        assert parsed == [(u, v, c, parsed[i][3]) for i, (u, v, c) in enumerate(edges)]
        sent = sum(f for u, v, c, f in parsed if u == s and v != s) - sum(f for u, v, c, f in parsed if v == s and u != s)
        if s != t:
            assert sent == flow
        for u, v, c, f in parsed:
            assert 0 <= f <= c
            if cut[u] and not cut[v]:
                assert f == c
        leaving = sum(c for u, v, c, f in parsed if cut[u] and not cut[v])
        assert leaving == flow
        checks += 1
    report.append(dict(mode=mode, cases=len(cases), checks=checks))
    print(mode, checks, 'checks PASS', flush=True)

import json
(root / 'verification/wida-flow6c.json').write_text(json.dumps(dict(
    scope='0-based MaxFlow. Flow matches Edmonds-Karp and 1-based Dinic when s!=t. edges() restores original endpoints, capacity and flow. minCut after flow is the residual source side. Before any BFS, h is zero so minCut is all true. No online AC.',
    blob='a51f7e70858f6002bbe4bedb8f8c6e5f8aefd66b', runs=report), indent=2) + '\n')
