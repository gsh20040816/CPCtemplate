#!/usr/bin/env python3
"""Finite exact checks for the row-expansion proof, not a theorem or OJ proof."""
from itertools import combinations, permutations, product
from pathlib import Path
import hashlib
import json
import os
import random
import re


def determinant(a):
    n = len(a)
    answer = 0
    for p in permutations(range(n)):
        term = (-1) ** sum(p[i] > p[j] for i in range(n) for j in range(i + 1, n))
        for i in range(n):
            term *= a[i][p[i]]
        answer += term
    return answer


def reduced(n, edges, root, kind):
    a = [[0] * n for _ in range(n)]
    for u, v, w in edges:
        if kind == 2:
            u, v = v, u
        a[u][u] += w
        a[u][v] -= w
        if kind == 0:
            a[v][v] += w
            a[v][u] -= w
    return [[a[i][j] for j in range(n) if j != root] for i in range(n) if i != root]


def enumerate_trees(n, edges, root, kind):
    total = 0
    for chosen in combinations(edges, n - 1):
        graph = [[] for _ in range(n)]
        degree = [0] * n
        weight = 1
        for u, v, w in chosen:
            if kind == 1:
                u, v = v, u  # Traverse inward arcs in reverse from root.
            graph[u].append(v)
            degree[v] += 1
            if kind == 0:
                graph[v].append(u)
            weight *= w
        seen = {root}
        todo = [root]
        for u in todo:
            for v in graph[u]:
                if v not in seen:
                    seen.add(v)
                    todo.append(v)
        if len(seen) == n and (kind == 0 or degree == [int(i != root) for i in range(n)]):
            total += weight
    return total


def main():
    if not __debug__ or os.environ.get('PYTHONOPTIMIZE') not in (None, '', '0'):
        raise SystemExit('Validation requires assertions')
    root = Path(__file__).resolve().parents[1]
    fixture = root / 'tests/fixtures/matrix-tree-knowledge'
    manifest = json.loads((fixture / 'manifest.json').read_text())
    for i, digest in enumerate(manifest['original_sections_sha256']):
        assert hashlib.sha256((fixture / f'original-{i}.tex').read_bytes()).hexdigest() == digest
    text = (root / 'docs/knowledge-matrix-tree.tex').read_text()
    candidate = re.split(r'(?=\\section\{)', text)[1:]
    assert len(candidate) == 2
    for i, amendments in enumerate(manifest['explicit_line_amendments']):
        lines = (fixture / f'original-{i}.tex').read_text().splitlines(keepends=True)
        for amendment in reversed(amendments):
            a, b = amendment['start_line_zero_based'], amendment['end_line_exclusive']
            assert ''.join(lines[a:b]) == amendment['original']
            lines[a:b] = amendment['replacement'].splitlines(keepends=True)
        assert ''.join(lines) == candidate[i], ('unlisted migration change', i)
    mapping = json.loads((root / 'docs/knowledge-taxonomy.json').read_text())
    rows = [x for x in mapping['entries'] if x['label'] in manifest['labels']]
    assert [x['label'] for x in rows] == manifest['labels']
    assert all(x['path'] == 'graph/matrix-tree.md' for x in rows)
    for target in ['compact-MatrixTree', 'compact-MatrixTreeMod', 'compact-determinant_mod', 'usage-example-76']:
        assert r'\ref{' + target + '}' in text and r'\pageref{' + target + '}' in text
    for fragment in ['每个非根点恰选一条出边', '有向环', '三角矩阵', '没有除法', 'type=1', 'type=0', '297619886', '297620263']:
        assert fragment in text
    # Every functional edge choice, including loops and every root, through n=5.
    functional = 0
    for n in range(1, 6):
        for r in range(n):
            vertices = [i for i in range(n) if i != r]
            for parents in product(range(n), repeat=n - 1):
                parent = dict(zip(vertices, parents))
                good = True
                for start in vertices:
                    seen = set()
                    u = start
                    while u != r and u not in seen:
                        seen.add(u)
                        u = parent[u]
                    good &= u == r
                edges = [(u, v, 1) for u, v in parent.items()]
                assert determinant(reduced(n, edges, r, 1)) == int(good)
                functional += 1
    # Integer permutation determinant versus independent n-1-edge subset oracle.
    rng = random.Random(617800)
    graphs = [(1, [(0, 0, -(1 << 63))]),
              (2, [(0, 1, 3), (0, 1, -3), (1, 1, 7)]),
              (3, [(0, 1, 2), (1, 2, 3), (2, 0, 5)])]
    for _ in range(300):
        n = rng.randrange(1, 6)
        graphs.append((n, [(rng.randrange(n), rng.randrange(n), rng.choice([-3, -1, 0, 1, 4, (1 << 63) - 1])) for _ in range(rng.randrange(9))]))
    comparisons = 0
    mods = [1, 2, 4, 6, 8, 9, 12, 998244353, (1 << 63) - 1]
    for n, edges in graphs:
        for r in range(n):
            for kind in range(3):
                answer = enumerate_trees(n, edges, r, kind)
                matrix = reduced(n, edges, r, kind)
                assert determinant(matrix) == answer
                for mod in mods:
                    assert determinant([[v % mod for v in row] for row in matrix]) % mod == answer % mod
                comparisons += 1
    print(f'Matrix Tree knowledge: {functional} exact functional choices; {len(graphs)} weighted multigraphs; {comparisons} root/direction comparisons and {len(mods)} moduli PASS')


if __name__ == '__main__':
    main()
