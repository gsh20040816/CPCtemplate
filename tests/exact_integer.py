#!/usr/bin/env python3
"""Independent permutation/subset oracles for exact determinants and trees."""
import argparse
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]

def determinant(a):
    n = len(a)
    ans = 0
    for p in it.permutations(range(n)):
        term = (-1) ** sum(p[i] > p[j] for i in range(n) for j in range(i + 1, n))
        for i in range(n):
            term *= a[i][p[i]]
        ans += term
    return ans


def trees(n, edges, root, kind):
    ans = 0
    for selected in it.combinations(edges, n - 1):
        adj = [[] for _ in range(n)]
        degree = [0] * n
        weight = 1
        for u, v, w in selected:
            weight *= w
            if kind == 2:
                u, v = v, u
            if kind:
                degree[u] += 1
                adj[v].append(u)
            else:
                adj[u].append(v)
                adj[v].append(u)
        if kind and degree != [int(i != root) for i in range(n)]:
            continue
        seen = {root}
        queue = [root]
        for u in queue:
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        if len(seen) == n:
            ans += weight
    return ans


def corpus():
    rng = random.Random(20261008)
    matrices = []
    for n in range(4):
        for flat in it.product((-1, 0, 1), repeat=n * n):
            a = [list(flat[i*n:(i+1)*n]) for i in range(n)]
            matrices.append((a, determinant(a)))
    for n in range(4, 8):
        for _ in range(30):
            a = [[rng.randrange(-9, 10) for _ in range(n)] for _ in range(n)]
            matrices.append((a, determinant(a)))
    for n in (2, 5, 12):
        xs = [10**20 + 7*i for i in range(n)]
        a = [[x**j for j in range(n)] for x in xs]
        value = 1
        for i in range(n):
            for j in range(i+1, n):
                value *= xs[j] - xs[i]
        matrices.append(([row[:] for row in a], value))
        a[0], a[-1] = a[-1], a[0]
        matrices.append(([row[:] for row in a], -value))
    graphs = []
    simple = []
    for n in range(1, 6):
        pairs = list(it.combinations(range(n), 2))
        for mask in range(1 << len(pairs)):
            edges = [(u, v, 1) for j, (u, v) in enumerate(pairs) if mask >> j & 1]
            expected = trees(n, edges, 0, 0)
            simple.append((n, edges, expected))
            for root in range(n):
                graphs.append((n, edges, root, 0, expected))
    for n in range(1, 4):
        pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
        for mask in range(1 << len(pairs)):
            edges = [(u, v, 1) for j, (u, v) in enumerate(pairs) if mask >> j & 1]
            for root in range(n):
                for kind in (1, 2):
                    graphs.append((n, edges, root, kind, trees(n, edges, root, kind)))
    for _ in range(240):
        n = rng.randrange(1, 6)
        edges = [(rng.randrange(n), rng.randrange(n), rng.choice((-10**35, -3, -1, 0, 1, 5, 10**40))) for _ in range(rng.randrange(10))]
        for root in range(n):
            for kind in range(3):
                graphs.append((n, edges, root, kind, trees(n, edges, root, kind)))
    for n in (10, 25):
        w = 10**30 + 1
        edges = [(u, v, w) for u in range(n) for v in range(u+1, n)]
        graphs.append((n, edges, n-1, 0, n**(n-2) * w**(n-1)))
    # Connected theta graph: path lengths 1,71,138; exactly 10007 trees.
    edges = [(0, 1, 1)]
    nxt = 2
    for length in (71, 138):
        path = [0] + list(range(nxt, nxt + length - 1)) + [1]
        nxt += length - 1
        edges.extend((u, v, 1) for u, v in zip(path, path[1:]))
    graphs.append((209, edges, 0, 0, 10007))
    return matrices, graphs, simple


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    mode = 'sanitizer' if args.sanitize else 'normal'
    out = ROOT / 'build/exact-integer' / mode
    out.mkdir(parents=True, exist_ok=True)
    matrices, graphs, simple = corpus()
    datasets = {
        'determinant_exact': (str(len(matrices))+'\n'+''.join(str(len(a))+'\n'+''.join(' '.join(map(str,row))+'\n' for row in a) for a, _ in matrices), [x for _, x in matrices]),
        'matrix_tree_exact': (str(len(graphs))+'\n'+''.join(f'{n} {len(e)} {r} {k}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in e) for n,e,r,k,_ in graphs), [x[-1] for x in graphs]),
    }
    # Duplicate/reverse/loop input must retain Boolean adjacency source semantics.
    source_cases = [(n, [(u+1,v+1) for u,v,_ in e], x) for n,e,x in simple]
    source_cases += [(n, [(u+1,v+1) for u,v,_ in e] + [(v+1,u+1) for u,v,_ in e] + [(u+1,u+1) for u in range(n)], x) for n,e,x in simple]
    datasets['kuangbin_tree_count'] = (str(len(source_cases))+'\n'+''.join(f'{n} {len(e)}\n'+''.join(f'{u} {v}\n' for u,v in e) for n,e,_ in source_cases), [x[-1] for x in source_cases])
    sys.path.insert(0, str(ROOT / 'tools'))
    from usage_examples import records
    from audit_copy_context import candidate, extract_components
    rows = {Path(r['driver']).name.split('.')[0]: r for r in records() if r['id'] in ('example-329', 'example-330', 'example-331')}
    components = {r['symbol']: r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    results = []
    flags = ['-std=c++17', '-O1' if args.sanitize else '-O2', '-I/opt/homebrew/include']
    if args.sanitize:
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
    paths = [ROOT/'src/compact/determinant_exact.hpp', ROOT/'src/compact/matrix_tree_exact.hpp', Path(__file__)]
    paths += [ROOT/f'verify/api/{name}.compact.cpp' for name in datasets]
    paths += [ROOT/'tools/usage_examples.py', ROOT/'tools/audit_copy_context.py', ROOT/'docs/usage-examples.json']
    paths += list((ROOT/'tests/fixtures/exact_integer_sources').glob('*.inc'))
    sha = lambda b: hashlib.sha256(b).hexdigest()
    snapshot = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in paths}
    for name, (data, expected) in datasets.items():
        for form in ('header', 'ndebug', 'expanded', 'copied'):
            exe = out / (name + '-' + form)
            source = ROOT/f'verify/api/{name}.compact.cpp'
            if form in ('expanded', 'copied'):
                source = exe.with_suffix('.cpp')
                row = rows[name]
                program = row['program'] if form == 'expanded' else candidate(row, row['requires'], components)['program']
                source.write_text(program)
            command = [CXX, *flags, *(['-DNDEBUG'] if form == 'ndebug' else []), str(source), '-o', str(exe)]
            subprocess.run(command, check=True, capture_output=True)
            start = time.monotonic()
            run = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env={**os.environ, 'ASAN_OPTIONS':'detect_leaks=0'}, timeout=180)
            assert run.returncode == 0, run.stderr
            actual = [int(x) for x in run.stdout.split()]
            assert actual == expected, (name, next((i for i,(x,y) in enumerate(zip(actual,expected)) if x != y), 'length'), run.stderr)
            results.append(dict(name=name, form=form, cases=len(expected), input_sha256=sha(data.encode()), output_sha256=sha(run.stdout.encode()), source_sha256=sha(source.read_bytes()), binary_sha256=sha(exe.read_bytes()), command=command, seconds=round(time.monotonic()-start, 3)))
            print(name, form, len(expected), 'passed', flush=True)
    def execute(name, program, data):
        source = out / (name + '.cpp')
        source.write_text(program)
        exe = source.with_suffix('')
        command = [CXX, *flags, str(source), '-o', str(exe)]
        subprocess.run(command, check=True, capture_output=True)
        run = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env={**os.environ, 'ASAN_OPTIONS':'detect_leaks=0'}, timeout=180)
        assert run.returncode == 0, (name, run.stderr)
        return dict(name=name, source_sha256=sha(program.encode()), input_sha256=sha(data.encode()), output=run.stdout, binary_sha256=sha(exe.read_bytes()), command=command)
    prefix = '#include <bits/stdc++.h>\nusing namespace std;\n'
    original = (ROOT/'tests/fixtures/exact_integer_sources/floating.inc').read_text()
    source_results = [execute('source-floating', prefix + original, datasets['kuangbin_tree_count'][0])]
    assert list(map(int,source_results[0]['output'].split())) == datasets['kuangbin_tree_count'][1]
    k25 = '1\n25 300\n'+''.join(f'{u+1} {v+1}\n' for u in range(25) for v in range(u+1,25))
    big = execute('source-floating-k25', prefix + original, k25)
    big['exact_expected'] = str(25**23)
    assert int(big['output']) != 25**23
    source_results.append(big)
    lines = (ROOT/'tests/fixtures/exact_integer_sources/modular.inc').read_text().splitlines()
    wrapped = prefix + '\n'.join(lines[:42]) + '\nint g[330][330];\nint main() { int t; cin >> t; while(t--) { int n,m; cin >> n >> m; memset(g,0,sizeof(g)); while(m--) {int u,v; cin>>u>>v; --u; --v; g[u][v]=g[v][u]=1;}\n' + '\n'.join(lines[43:]) + '\n}}\n'
    mod = execute('source-modular', wrapped, datasets['kuangbin_tree_count'][0])
    assert list(map(int,mod['output'].split())) == [x%10007 if x%10007 else -1 for x in datasets['kuangbin_tree_count'][1]]
    source_results.append(mod)
    n,e,_,_,expected = graphs[-1]
    theta = f'1\n{n} {len(e)}\n'+''.join(f'{u+1} {v+1}\n' for u,v,_ in e)
    mod = execute('source-modular-theta', wrapped, theta)
    assert int(mod['output']) == -1 and expected == 10007
    mod['exact_expected'] = expected
    mod['correct_residue'] = 0
    source_results.append(mod)
    mutations = [
        ('swap-sign', 'determinant_exact', 'sign = -sign;', 'sign = sign;'),
        ('denominator', 'determinant_exact', 'value / prev', 'value'),
        ('early-zero', 'determinant_exact', 'Z value = a[i][j]', 'a[i][k] = 0; Z value = a[i][j]'),
        ('orientation', 'matrix_tree_exact', 'kind == Kind::away_from_root', 'kind == Kind::toward_root'),
        ('duplicate-source', 'kuangbin_tree_count', 'set<pair<int, int>> seen;', 'multiset<pair<int, int>> seen;'),
    ]
    mutant_results = []
    for label, name, old, new in mutations:
        program = rows[name]['program']
        assert old in program, (label,old)
        result = execute('mutant-'+label, program.replace(old,new,1), datasets[name][0])
        actual = list(map(int,result['output'].split()))
        assert actual != datasets[name][1], label
        result['first_mismatch'] = next(i for i,(x,y) in enumerate(zip(actual,datasets[name][1])) if x!=y)
        result.pop('output')
        mutant_results.append(result)
    for r in source_results:
        r['output_sha256'] = sha(r['output'].encode())
        if len(r['output']) > 100:
            r['output_lines'] = len(r.pop('output').splitlines())
    assert snapshot == {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in paths}
    receipt = dict(mode=mode, seed=20261008, snapshot=snapshot, results=results, source_results=source_results, mutants=mutant_results, online_ac=False)
    (ROOT/f'verification/exact-integer-{mode}.json').write_text(json.dumps(receipt, indent=2)+'\n')

if __name__ == '__main__':
    main()
