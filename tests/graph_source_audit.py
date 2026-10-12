"""Attachment 2-SAT and LT source programs against exhaustive independent truth."""
from pathlib import Path
import hashlib
import itertools
import json
import os
import random
import re
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
out = root / 'build/graph-source'
out.mkdir(parents=True, exist_ok=True)
pdf = root / 'build/issue11-reference.pdf'
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == 'b5ce46f7cf542be2d9846d8f01898c8ccd7f4619521036b0b7895206895745f3'
text = (root / 'build/issue11-reference.txt').read_text()
sources = {}
for name, marker, count in [('sat', '2-sat.cpp', 67), ('dom', 'Lengauer–Tarjan.cpp', 89)]:
    section = text.split(marker, 1)[1].split('代码：', 1)[0]
    lines = []
    for line in section.splitlines():
        m = re.match(r'^\s*(\d+)(?:[ \t]+(.*))?$', line)
        if m and int(m[1]) == len(lines) + 1:
            lines.append(m[2] or '')
        if len(lines) == count:
            break
    assert len(lines) == count, (name, len(lines))
    sources[name] = '\n'.join(lines) + '\n'
    (out / (name + '-original.cpp')).write_text(sources[name])

sat_reset = '''
        for (int u = 0; u <= 2 * n; u++) {
            edge[u].clear();
            dfn[u] = low[u] = belong[u] = 0;
            in[u] = false;
        }
        top = cnt = dfs_clock = 0;
'''
dom_reset = '''
        for (int u = 0; u <= n; u++) {
            for (int j = 0; j < 3; j++)
                head[u][j] = 0;
            dfn[u] = rk[u] = father[u] = idom[u] = sdom[u] = 0;
            up[u] = Min[u] = ans[u] = 0;
        }
        total = dfs_clock = 0;
'''
for name, reset in [('sat', sat_reset), ('dom', dom_reset)]:
    code = '#define main original_main\n#include "' + name + '-original.cpp"\n#undef main\n'
    code += 'int main() {\n    int cases;\n    scanf("%d", &cases);\n    while (cases--) {\n        original_main();\n' + reset + '    }\n}\n'
    (out / (name + '-batch.cpp')).write_text(code)

rng = random.Random(214782)
literals = [(u, a) for u in [1, 2] for a in [0, 1]]
clauses = [(u, a, v, b) for (u, a), (v, b) in itertools.combinations_with_replacement(literals, 2)]
sat_cases = [(2, [cl for j, cl in enumerate(clauses) if mask >> j & 1]) for mask in range(1 << len(clauses))]
for _ in range(300):
    n = rng.randrange(1, 10)
    sat_cases.append((n, [(rng.randrange(1, n + 1), rng.randrange(2), rng.randrange(1, n + 1), rng.randrange(2)) for _ in range(rng.randrange(40))]))

def valid(mask, clauses):
    return all(((mask >> (u - 1)) & 1) == a or ((mask >> (v - 1)) & 1) == b for u, a, v, b in clauses)
sat_expected = [any(valid(mask, cls) for mask in range(1 << n)) for n, cls in sat_cases]
sat_data = [str(n) + ' ' + str(len(cls)) + '\n' + ''.join(' '.join(map(str, cl)) + '\n' for cl in cls) for n, cls in sat_cases]

def reachable(n, edges, removed=0):
    seen = {1} if removed != 1 else set()
    while True:
        following = seen | {v for u, v in edges if u in seen and v != removed}
        if following == seen:
            return seen
        seen = following

def dom_truth(n, edges):
    live = reachable(n, edges)
    return [len(live - reachable(n, edges, u)) if u in live else 0 for u in range(1, n + 1)]
dom_cases = []
for n in range(1, 4):
    all_edges = list(itertools.product(range(1, n + 1), repeat=2))
    for mask in range(1 << len(all_edges)):
        dom_cases.append((n, [e for j, e in enumerate(all_edges) if mask >> j & 1]))
for _ in range(300):
    n = rng.randrange(1, 10)
    dom_cases.append((n, [(rng.randrange(1, n + 1), rng.randrange(1, n + 1)) for _ in range(rng.randrange(40))]))
dom_data = [f'{n} {len(edges)}\n' + ''.join(f'{u} {v}\n' for u, v in edges) for n, edges in dom_cases]
dom_expected = [dom_truth(n, edges) for n, edges in dom_cases]
results = {}
failures = {}
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    for name in ['sat', 'dom']:
        exe = out / (name + '-' + mode)
        subprocess.run([CXX, *flags, str(out / (name + '-batch.cpp')), '-o', str(exe)], check=True)
        data = sat_data if name == 'sat' else dom_data
        p = subprocess.run([str(exe)], input=str(len(data)) + '\n' + ''.join(data), text=True, capture_output=True, env=env, timeout=120)
        assert p.returncode == 0 and not p.stderr, p.stderr[:2000]
        tokens = iter(p.stdout.split())
        mismatches = []
        for i in range(len(data)):
            if name == 'sat':
                possible = next(tokens)
                assert possible in ['POSSIBLE', 'IMPOSSIBLE']
                assert (possible == 'POSSIBLE') == sat_expected[i]
                if possible == 'POSSIBLE':
                    n, cls = sat_cases[i]
                    values = [int(next(tokens)) for _ in range(n)]
                    assert all(v in [0, 1] for v in values)
                    assert valid(sum(v << j for j, v in enumerate(values)), cls)
            else:
                n, edges = dom_cases[i]
                got = [int(next(tokens)) for _ in range(n)]
                if got != dom_expected[i]:
                    mismatches.append({'n': n, 'edges': edges, 'got': got, 'expected': dom_expected[i], 'all_reachable': len(reachable(n, edges)) == n})
        assert next(tokens, None) is None
        results[name + '-' + mode] = {'cases': len(data), 'mismatches': len(mismatches)}
        if mismatches:
            assert not any(r['all_reachable'] for r in mismatches)
            failures[mode] = mismatches[:3]
        print(name, mode, results[name + '-' + mode], flush=True)
    for name, problem in [('sat', 'P4782'), ('dom', 'P5180')]:
        exe = out / ('current-' + name + '-' + mode)
        subprocess.run([CXX, *flags, str(root / 'verify/luogu' / (problem + '.compact.cpp')), '-o', str(exe)], check=True)
        data = sat_data if name == 'sat' else dom_data
        for i, inp in enumerate(data):
            p = subprocess.run([str(exe)], input=inp, text=True, capture_output=True, env=env, timeout=30)
            assert p.returncode == 0 and not p.stderr, p.stderr[:2000]
            values = p.stdout.split()
            if name == 'sat':
                assert (values[0] == 'POSSIBLE') == sat_expected[i]
                if sat_expected[i]:
                    n, cls = sat_cases[i]
                    a = list(map(int, values[1:]))
                    assert len(a) == n and all(v in [0, 1] for v in a)
                    assert valid(sum(v << j for j, v in enumerate(a)), cls)
                else:
                    assert values == ['IMPOSSIBLE']
            else:
                assert list(map(int, values)) == dom_expected[i]
        results['current-' + name + '-' + mode] = {'cases': len(data), 'mismatches': 0}
        print('current', name, mode, len(data), 'PASS', flush=True)
report = {'source_pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(), 'source_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k, v in sources.items()}, 'runs': results, 'source_dominator_unreachable_counterexamples': failures, 'scope': 'Original function bodies unchanged; wrapper resets globals between protocols. All assignments independently checked. Dominance oracle removes vertices and computes reachability; no second LT as truth.', 'online': 'No new submission'}
report['all_reachable_dominator_cases'] = sum(len(reachable(n, edges)) == n for n, edges in dom_cases)
report['source_dominator_precondition'] = 'Attachment page 18 explicitly assumes every vertex is reachable from the entry; mismatches are outside that domain.'
report['files'] = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in ['tests/graph_source_audit.py', 'src/compact/graph.hpp', 'src/compact/dominator_tree.hpp', 'verify/luogu/P4782.compact.cpp', 'verify/luogu/P5180.compact.cpp']}
(root / 'verification/graph-source-audit.json').write_text(json.dumps(report, indent=2) + '\n')
