"""Independent complete-driver feasibility/certificate tests for LOJ 115."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import random
import subprocess
import sys

from compiler_config import CXX
from usage_checkers import check_output
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records


def feasible(n, edges):
    # Enumerate reachable balance vectors, never run a second flow algorithm.
    states = {(0,) * n}
    for u, v, lo, hi in edges:
        nxt = set()
        for state in states:
            for f in range(lo, hi + 1):
                b = list(state)
                b[u - 1] -= f
                b[v - 1] += f
                nxt.add(tuple(b))
        states = nxt
    return (0,) * n in states


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sanitizer', action='store_true')
    args = ap.parse_args()
    mode = 'sanitizer' if args.sanitizer else 'normal'
    out = ROOT / 'build' / ('circulation-' + mode)
    out.mkdir(parents=True, exist_ok=True)
    record = next(x for x in records() if x['id'] == 'example-185')
    source = out / '115.cpp'
    source.write_text(record['program'])
    flags = ['-O1', '-g', '-fsanitize=address,undefined'] if args.sanitizer else ['-O2']
    if sys.platform == 'darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    subprocess.run([CXX, '-std=c++20', *flags, str(source), '-o', str(out / '115')], check=True)
    counts = {}

    def run(n, edges, group, want=None):
        if want is None:
            want = feasible(n, edges)
        data = f'{n} {len(edges)}\n' + ''.join(' '.join(map(str, e)) + '\n' for e in edges)
        p = subprocess.run([str(out / '115')], input=data, text=True, capture_output=True, check=True, timeout=30)
        assert not p.stderr, p.stderr
        check_output('example-185', mode, data, p.stdout, {'circulation': want})
        counts[group] = counts.get(group, 0) + 1

    edge_types = [(u, v, lo, hi) for u in (1, 2) for v in (1, 2)
                  for lo, hi in [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2)]]
    for m in [1, 2]:
        for edges in itertools.product(edge_types, repeat=m):
            run(2, edges, 'two_vertex_ordered_multigraphs')
    pairs = [(u, v) for u in range(1, 4) for v in range(1, 4) if u != v]
    for states in itertools.product(range(3), repeat=6):
        edges = [(u, v, int(s == 2), 1) for (u, v), s in zip(pairs, states) if s]
        if edges:
            run(3, edges, 'three_vertex_directed_graphs')
    rng = random.Random(11520260930)
    for _ in range(400):
        n = rng.randint(1, 5)
        edges = []
        for i in range(rng.randint(1, 8)):
            u, v, lo = rng.randint(1, n), rng.randint(1, n), rng.randint(0, 2)
            edges.append((u, v, lo, rng.randint(lo, 2)))
        run(n, edges, 'random_small')
    for n in [1, 2, 200]:
        run(n, [], 'empty_graph_extension', True)

    # Valid maximum-size networks with known explicit feasible circulation.
    edges = []
    for _ in range(3400):
        a, b, c = rng.sample(range(1, 201), 3)
        f = rng.randint(0, 2999)
        for u, v in [(a, b), (b, c), (c, a)]:
            edges.append((u, v, rng.randint(0, f), rng.randint(f, 2999)))
    run(200, edges, 'maximum_legal_feasible', True)
    run(200, [(1, 2, 1, 1)] + [(2, 2, 2999, 2999)] * 10199, 'maximum_legal_infeasible', False)
    # Force the super-source flow through a 200-vertex recursive path.
    edges = [(200, 1, 2999, 2999)] + [(i, i + 1, 0, 2999) for i in range(1, 200)]
    edges += [(1, 1, 0, 2999)] * 10000
    run(200, edges, 'maximum_legal_recursive_path', True)
    # Values exceeding 32 bits, and a long path, are separately marked extensions.
    cap = 3_000_000_000_000_000_000
    run(200, [(200, 1, cap, cap)] + [(i, i + 1, 0, cap) for i in range(1, 200)], 'int64_extension', True)
    n = 50000
    run(n, [(n, 1, 7, 7)] + [(i, i + 1, 0, 7) for i in range(1, n)], 'deep_recursion_extension', True)

    # Certificate checker negative controls: conservation, bounds, count and verdict.
    data = '2 2\n1 2 1 3\n2 1 1 3\n'
    for bad in ['NO\n', 'YES\n2\n1\n', 'YES\n0\n0\n', 'YES\n1\n', 'YES\n1 1\n1\n']:
        try:
            check_output('example-185', mode, data, bad, {'circulation': True})
        except AssertionError:
            pass
        else:
            raise AssertionError('Bad circulation certificate accepted: ' + bad)
    report = dict(scope='Local complete-driver feasibility enumeration and certificate verification; not online AC.', mode=mode,
                  driver=record['driver'], program_sha256=record['program_sha256'],
                  test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  certificate_checker_sha256=hashlib.sha256((ROOT / 'tests/usage_checkers.py').read_bytes()).hexdigest(),
                  compiler=subprocess.check_output([CXX,'--version'],text=True).splitlines()[0], flags=flags,
                  cases=counts, negative_controls=5)
    (ROOT / f'verification/circulation-usages-{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
