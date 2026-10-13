"""Audit both general-matching snippets in the old WIDA blossom file."""
import hashlib, os, random, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-blossom.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_blossom'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '0b1d98571f5b3578d31fc0745eef3d51fa0a5d6b'
text = blob.decode().replace('\r\n', '\n')
mark = text.index('/**   一般图最大匹配（Graph 带花树算法）【久远】')
special, old = text[:mark], text[mark:]
assert special.count('struct Graph') == 1 and old.count('struct Graph') == 1
assert 'for (int u = 0; u < m; ++u)' in special
assert 'greedy();' in old
out = root / 'build/wida-blossom'
out.mkdir(parents=True, exist_ok=True)
(out / 'special.cpp').write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + special + r'''
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, e;
    cin >> n >> m >> e;
    Graph g(n);
    vector<pair<int,int>> edges;
    for (int i = 0; i < e; i++) {
        int u, v; cin >> u >> v;
        if (u != v) g.addEdge(u, v);
        edges.push_back({u, v});
    }
    auto match = g.findMatching(m, vector<pair<int,int>>{});
    int sz = 0;
    for (int i = 0; i < n; i++) if (match[i] != -1 && match[i] > i) sz++;
    cout << sz;
    for (int x : match) cout << ' ' << x;
    cout << '\n';
}
''')
(out / 'old.cpp').write_text('#include <bits/stdc++.h>\nusing namespace std;\n#include "../../src/compact/blossom.hpp"\n' + old.replace('struct Graph', 'struct OldGraph', 1).replace('Graph(int n)', 'OldGraph(int n)', 1) + r'''
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int cases; cin >> cases;
    while (cases--) {
        int n, e; cin >> n >> e;
        OldGraph g(n);
        Blossom b(n);
        for (int i = 0; i < e; i++) {
            int u, v; cin >> u >> v;
            g.addEdge(u, v);
            b.add(u, v);
        }
        auto match = g.findMatching();
        int sz = 0;
        for (int i = 0; i < n; i++) if (match[i] != -1 && match[i] > i) sz++;
        cout << sz << ' ' << b.solve();
        for (int x : match) cout << ' ' << x;
        cout << '\n';
    }
}
''')

def maximum(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        if u != v and v not in adj[u]:
            adj[u].append(v)
            adj[v].append(u)
    best = 0
    def rec(u, used):
        nonlocal best
        if u == n:
            best = max(best, used.bit_count() // 2)
            return
        rec(u + 1, used)
        if used >> u & 1:
            return
        for v in adj[u]:
            if v > u and not (used >> v & 1):
                rec(u + 1, used | (1 << u) | (1 << v))
    rec(0, 0)
    return best

def valid(n, edges, match):
    ok = {(min(u, v), max(u, v)) for u, v in edges if u != v}
    size = 0
    for i, j in enumerate(match):
        if j == -1:
            continue
        if match[j] != i or (min(i, j), max(i, j)) not in ok:
            return None
        if j > i:
            size += 1
    return size

rng = random.Random(4)
old_cases = [ (1, []), (2, [(0, 1)]), (3, [(0, 1), (1, 2), (2, 0)]), (4, [(0, 1), (1, 2), (2, 3)]) ]
for n in range(1, 9):
    for _ in range(6):
        edges = []
        for _k in range(rng.randrange(0, n + 2)):
            u, v = rng.randrange(n), rng.randrange(n)
            if u != v:
                edges.append((u, v))
        old_cases.append((n, edges))
old_cases.append((1, [(0, 0)]))
special_cases = [
    (3, 1, [(1, 2)]),
    (4, 2, [(2, 3), (0, 1)]),
    (3, 3, [(0, 1), (1, 2), (2, 0)]),
]
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    old_exe = out / ('old-' + mode)
    spec_exe = out / ('spec-' + mode)
    subprocess.run([CXX, '-std=c++20', *flags, str(out / 'old.cpp'), '-o', str(old_exe)], check=True)
    subprocess.run([CXX, '-std=c++20', *flags, str(out / 'special.cpp'), '-o', str(spec_exe)], check=True)
    lines = [str(len(old_cases))]
    for n, edges in old_cases:
        lines.append(f'{n} {len(edges)}')
        lines += [f'{u} {v}' for u, v in edges]
    got = subprocess.run([str(old_exe)], input='\n'.join(lines) + '\n', text=True, capture_output=True, env=env, timeout=60, check=True)
    assert got.stderr == ''
    for row, (n, edges) in zip(got.stdout.splitlines(), old_cases):
        parts = list(map(int, row.split()))
        sz, library = parts[:2]
        match = parts[2:]
        if any(u == v for u, v in edges):
            assert match[0] == 0 and library == 0 and sz == 0
            continue
        assert valid(n, edges, match) == sz
        assert sz == maximum(n, edges) == library
    for n, m, edges in special_cases:
        payload = f'{n} {m} {len(edges)}\n' + '\n'.join(f'{u} {v}' for u, v in edges) + '\n'
        got = subprocess.run([str(spec_exe)], input=payload, text=True, capture_output=True, env=env, timeout=30, check=True)
        assert got.stderr == ''
        parts = list(map(int, got.stdout.split()))
        sz, match = parts[0], parts[1:]
        assert valid(n, edges, match) == sz
        if all(u >= m and v >= m for u, v in edges if u != v):
            assert sz == 0 and maximum(n, edges) == 1
    report.append(dict(mode=mode, old_cases=len(old_cases)))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-blossom.json').write_text(json.dumps(dict(
    scope='The file contains two Graph types and does not compile as one unit. The older findMatching matches Blossom and exhaustive maximum cardinality, ignoring self-loops. findMatching(m, empty) leaves an edge wholly inside [m, n) unmatched. No online AC.',
    blob='0b1d98571f5b3578d31fc0745eef3d51fa0a5d6b', runs=report), indent=2) + '\n')
