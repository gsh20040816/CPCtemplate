"""Audit the old WIDA integer Dinic against Edmonds-Karp and the library."""
import hashlib, os, random, subprocess, sys
from collections import deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = (root / 'tests/fixtures/wida_flow6a/main.cpp').read_bytes()
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'c02700f9bec81ff3c4184ee16f11bdbd977bc379'
text = blob.decode().replace('\r\n', '\n')
assert 'if (v == t)' in text and 'return true;' in text
assert 'std::numeric_limits<T>::max()' in text

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
        return 0
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
            return total
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

rng = random.Random(6)
cases = []
cases.append((1, [], 0, 0, 0))
cases.append((2, [(0, 1, 0)], 0, 1, 0))
cases.append((2, [(0, 1, 5), (0, 1, 7)], 0, 1, 0))
cases.append((3, [(0, 1, 3), (1, 2, 4), (0, 2, 1), (2, 1, 5)], 0, 2, 0))
cases.append((3, [(0, 0, 9), (0, 1, 2), (1, 1, 4)], 0, 1, 1))
for _ in range(40):
    n = rng.randrange(1, 8)
    edges = []
    for _k in range(rng.randrange(0, 14)):
        edges.append((rng.randrange(n), rng.randrange(n), rng.randrange(0, 20)))
    s, t = rng.randrange(n), rng.randrange(n)
    cases.append((n, edges, s, t, rng.randrange(2)))

lines = [str(len(cases))]
for n, edges, s, t, kind in cases:
    lines.append(f'{n} {len(edges)} {s} {t} {kind}')
    lines += [f'{u} {v} {c}' for u, v, c in edges]
payload = '\n'.join(lines) + '\n'
out = root / 'build/wida-flow6a'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_flow6a.cpp'
report = []
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], input=payload, text=True, capture_output=True, env=env, timeout=60, check=True)
    assert got.stderr == ''
    rows = got.stdout.splitlines()
    assert len(rows) == len(cases)
    checks = 0
    for row, (n, edges, s, t, kind) in zip(rows, cases):
        original, library = map(int, row.split())
        expect = ek(n, edges, s, t)
        assert original == expect
        if s == t:
            assert library == -1 and original == 0
        else:
            assert library == original
        checks += 1
    report.append(dict(mode=mode, cases=len(cases), checks=checks))
    print(mode, checks, 'checks PASS', flush=True)

import json
(root / 'verification/wida-flow6a.json').write_text(json.dumps(dict(
    scope='0-based integer Dinic. BFS returns when the sink is first reached. Edmonds-Karp and, when s!=t, the 1-based library Dinic agree. Self-loops add no source-sink flow. No online AC.',
    blob='c02700f9bec81ff3c4184ee16f11bdbd977bc379', runs=report), indent=2) + '\n')
