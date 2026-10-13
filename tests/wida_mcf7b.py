"""Audit the newer WIDA min-cost flow, including its unsafe boundaries."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = (root / 'tests/fixtures/wida_mcf7b/main.cpp').read_bytes()
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '7d59e03ce2f94fe2990de3f44e360acdf737250c'
text = blob.decode().replace('\r\n', '\n')
assert 'e.emplace_back(v, cap, cost);' in text
assert 'e.emplace_back(u, 0, -cost);' in text
assert 'T aug = std::numeric_limits<int>::max();' in text

def mcmf(n, edges, s, t):
    g = [[] for _ in range(n)]
    def add(u, v, cap, cost):
        g[u].append([v, cap, cost, len(g[v])])
        g[v].append([u, 0, -cost, len(g[u]) - 1])
    for e in edges:
        add(*e)
    flow = cost = 0
    while True:
        dist = [10**18] * n
        dist[s] = 0
        parent = [-1] * n
        for _ in range(n - 1):
            changed = False
            for u in range(n):
                if dist[u] >= 10**18:
                    continue
                for i, (v, cap, w, _) in enumerate(g[u]):
                    if cap and dist[v] > dist[u] + w:
                        dist[v] = dist[u] + w
                        parent[v] = (u, i)
                        changed = True
            if not changed:
                break
        if dist[t] >= 10**18:
            return flow, cost
        v = t
        aug = 10**18
        while v != s:
            u, i = parent[v]
            aug = min(aug, g[u][i][1])
            v = u
        v = t
        while v != s:
            u, i = parent[v]
            g[u][i][1] -= aug
            rev = g[u][i][3]
            g[v][rev][1] += aug
            v = u
        flow += aug
        cost += aug * dist[t]

cases = [
    (2, [(0, 1, 5, 3)], 0, 1),
    (2, [(0, 1, 5, -4)], 0, 1),
    (3, [(0, 1, 3, 1), (1, 2, 2, 4), (0, 2, 2, 10)], 0, 2),
    (3, [(0, 1, 2, 5), (0, 2, 2, 1), (2, 1, 2, -3)], 0, 1),
    (3, [(0, 0, 9, 1), (0, 1, 4, 2)], 0, 1),
]
lines = [str(len(cases))]
for n, edges, s, t in cases:
    lines.append(f'{n} {len(edges)} {s} {t}')
    lines += [f'{u} {v} {cap} {cost}' for u, v, cap, cost in edges]
payload = '\n'.join(lines) + '\n'
out = root / 'build/wida-mcf7b'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_mcf7b.cpp'
report = []
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe), 'cases'], input=payload, text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    for row, (n, edges, s, t) in zip(got.stdout.splitlines(), cases):
        parts = list(map(int, row.split()))
        assert parts[:2] == list(mcmf(n, edges, s, t))
        count = parts[2]
        rec = parts[3:]
        assert count == len(edges)
        for i, (u, v, cap, cost) in enumerate(edges):
            frm, to, got_cap, got_cost, flow = rec[i * 5:(i + 1) * 5]
            assert (frm, to, got_cap, got_cost) == (u, v, cap, cost)
            assert 0 <= flow <= cap
    report.append(dict(mode=mode, cases=len(cases)))
    print(mode, 'PASS', flush=True)

exe = out / 'normal'
wide = subprocess.run([str(exe), 'wide'], text=True, capture_output=True, env=env, timeout=30, check=True)
assert wide.stdout == '3000000000 3000000000\n'
report.append(dict(wide=wide.stdout.strip()))

ub = out / 'overflow'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'overflow'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
report.append(dict(overflow=bad.stderr.strip().splitlines()[-1]))

timed_out = False
try:
    subprocess.run([str(exe), 'same'], text=True, capture_output=True, env=env, timeout=2, check=False)
except subprocess.TimeoutExpired:
    timed_out = True
assert timed_out
report.append(dict(same_source_sink='timed out'))
print('boundaries PASS', flush=True)

import json
(root / 'verification/wida-mcf7b.json').write_text(json.dumps(dict(
    scope='Normal edge orientation. Tested min-cost max-flow values match Bellman-Ford. Augmentation is capped by INT_MAX per round. s==t does not return. Unreachable potentials overflow. No online AC.',
    blob='7d59e03ce2f94fe2990de3f44e360acdf737250c', runs=report), indent=2) + '\n')
