"""Audit the old WIDA floating max-flow. Integer instantiation is separate."""
import hashlib, os, random, subprocess, sys
from collections import deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = (root / 'tests/fixtures/wida_flow6b/main.cpp').read_bytes()
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '0c820e9e44641bc6b80950037bd10b0fb9dd6a21'
text = blob.decode().replace('\r\n', '\n')
assert 'double res = 0;' in text and 'ans += dfs(s, t, 1E100);' in text
assert 'return f;' in text and 'return res;' in text

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
        return 0.0
    total = 0.0
    while True:
        parent = [-1] * n
        q = deque([s])
        parent[s] = -2
        found = False
        while q and not found:
            u = q.popleft()
            for i, (v, c, _) in enumerate(g[u]):
                if c > 1e-12 and parent[v] == -1:
                    parent[v] = (u, i)
                    if v == t:
                        found = True
                        break
                    q.append(v)
        if not found:
            return total
        v = t
        cap = 1e300
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

rng = random.Random(7)
cases = [
    (1, [], 0, 0),
    (2, [(0, 1, 0.0)], 0, 1),
    (2, [(0, 1, 5.0), (0, 1, 7.0)], 0, 1),
    (3, [(0, 1, 0.1), (1, 2, 0.2), (0, 2, 0.05)], 0, 2),
    (3, [(0, 0, 4.0), (0, 1, 1.5)], 0, 1),
]
for _ in range(30):
    n = rng.randrange(1, 7)
    edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(0, 11) / 2) for _k in range(rng.randrange(0, 10))]
    cases.append((n, edges, rng.randrange(n), rng.randrange(n)))

lines = [str(len(cases))]
for n, edges, s, t in cases:
    lines.append(f'{n} {len(edges)} {s} {t}')
    lines += [f'{u} {v} {c:.17g}' for u, v, c in edges]
payload = '\n'.join(lines) + '\n'
out = root / 'build/wida-flow6b'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_flow6b.cpp'
report = []
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe), 'double'], input=payload, text=True, capture_output=True, env=env, timeout=60, check=True)
    assert got.stderr == ''
    rows = got.stdout.splitlines()
    assert len(rows) == len(cases)
    worst = 0.0
    for row, (n, edges, s, t) in zip(rows, cases):
        original = float(row)
        expect = ek(n, edges, s, t)
        err = abs(original - expect)
        worst = max(worst, err)
        assert err <= 1e-9 * max(1.0, abs(expect))
    report.append(dict(mode=mode, cases=len(cases), worst_abs=worst))
    print(mode, 'worst', worst, flush=True)

ub = out / 'int-ub'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'int'], text=True, capture_output=True, env=env, timeout=30)
report.append(dict(mode='int-limit', returncode=bad.returncode, stderr=bad.stderr.strip().splitlines()[-1] if bad.stderr else '', stdout=bad.stdout.strip()))
print('int', bad.returncode, bad.stdout.strip(), bad.stderr.strip().splitlines()[-1] if bad.stderr else '', flush=True)
assert bad.returncode == 0 and bad.stdout.strip() == '3' and bad.stderr == ''

import json
(root / 'verification/wida-flow6b.json').write_text(json.dumps(dict(
    scope='Floating Dinic. dfs accumulates in double and maxFlow passes 1E100. Tested double graphs match Edmonds-Karp exactly. Flow<int> happened to return the edge capacity under UBSan without a diagnostic; that does not define the 1E100 conversion. No online AC.',
    blob='0c820e9e44641bc6b80950037bd10b0fb9dd6a21', runs=report), indent=2) + '\n')
