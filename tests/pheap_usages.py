"""Printed PBDS drivers against a sorted multiset and Floyd-Warshall."""
from pathlib import Path
import argparse
import bisect
import hashlib
import itertools
import json
import random
import subprocess
import sys
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sanitizer', action='store_true')
    args = ap.parse_args()
    mode = 'sanitizer' if args.sanitizer else 'normal'
    work = ROOT / 'build' / ('pheap-usage-' + mode)
    work.mkdir(parents=True, exist_ok=True)
    rows = {r['id']: r for r in records()}
    exes = {}
    for name in ['example-189', 'example-190']:
        source = work / (name + '.cpp')
        source.write_text(rows[name]['program'])
        flags = ['-O1', '-g', '-fsanitize=address,undefined'] if args.sanitizer else ['-O2']
        exe = work / name
        subprocess.run([CXX, '-std=c++20', *flags, str(source), '-o', str(exe)], check=True)
        exes[name] = exe
    counts = {}
    inputs = hashlib.sha256()
    outputs = hashlib.sha256()

    def execute(name, data, group):
        p = subprocess.run([str(exes[name])], input=data, text=True, capture_output=True,
                           check=True, timeout=60)
        assert not p.stderr, p.stderr
        counts[group] = counts.get(group, 0) + 1
        inputs.update(data.encode())
        outputs.update(p.stdout.encode())
        return p.stdout

    def heap(initial, ops, group):
        ref = sorted(initial)
        expected = []
        for op in ops:
            if op[0] == 0:
                bisect.insort(ref, op[1])
            else:
                if not ref:
                    return
                expected.append(ref.pop(0 if op[0] == 1 else -1))
        data = f'{len(initial)} {len(ops)}\n' + ' '.join(map(str, initial)) + '\n'
        data += ''.join(' '.join(map(str, op)) + '\n' for op in ops)
        got = execute('example-189', data, group)
        assert got == ''.join(str(x) + '\n' for x in expected)

    kinds = [(0, -1), (0, 0), (0, 1), (1,), (2,)]
    for n in range(1, 5):
        for ops in itertools.product(kinds, repeat=n):
            heap([], ops, 'all_legal_empty_start_traces_length_1_to_4')
    rng = random.Random(20260930)
    for case in range(300):
        initial = [rng.choice([-10**9, 10**9, 0, rng.randrange(-30, 31)]) for _ in range(rng.randrange(31))]
        size = len(initial)
        ops = []
        for _ in range(500):
            op = rng.randrange(3) if size else 0
            if op == 0:
                ops.append((0, rng.choice([-10**9, 10**9, 0, rng.randrange(-30, 31)])))
                size += 1
            else:
                ops.append((op,))
                size -= 1
        heap(initial, ops, 'random_duplicate_and_extreme_value_traces')
    heap([0] * 500000, [(1 + i % 2,) for i in range(500000)], 'maximum_size_all_equal_alternating_delete')

    def graph(n, edges, s, t, group):
        inf = 10**30
        d = [[0 if u == v else inf for v in range(n)] for u in range(n)]
        for (u, v), w in edges.items():
            d[u][v] = w
        for k in range(n):
            for u in range(n):
                for v in range(n):
                    d[u][v] = min(d[u][v], d[u][k] + d[k][v])
        data = f'{n} {len(edges)} {s} {t}\n' + ''.join(f'{u} {v} {w}\n' for (u, v), w in edges.items())
        output = execute('example-190', data, group)
        lines = output.splitlines()
        if d[s][t] == inf:
            assert lines == ['-1']
            return
        cost, length = map(int, lines[0].split())
        assert cost == d[s][t] and len(lines) == length + 1
        current = s
        seen = {s}
        total = 0
        for line in lines[1:]:
            u, v = map(int, line.split())
            assert u == current and (u, v) in edges and v not in seen
            total += edges[u, v]
            current = v
            seen.add(v)
        assert current == t and total == cost

    for state in itertools.product([None, 0, 1], repeat=6):
        pairs = [(u, v) for u in range(3) for v in range(3) if u != v]
        edges = {pair: w for pair, w in zip(pairs, state) if w is not None}
        if edges:
            graph(3, edges, 0, 2, 'all_three_vertex_zero_one_graphs')
    for trial in range(200):
        n = rng.randrange(2, 22)
        s, t = rng.sample(range(n), 2)
        density = [0, .1, .4, 1][trial % 4]
        edges = {(u, v): rng.choice([0, 1, 10**9, rng.randrange(100)])
                 for u in range(n) for v in range(n) if u != v and rng.random() < density}
        if not edges:
            edges[t, s] = 0
        graph(n, edges, s, t, 'random_floyd_and_path_certificates')
    report = dict(mode=mode, counts=counts, invocations=sum(counts.values()),
                  program_sha256={k: rows[k]['program_sha256'] for k in exes},
                  input_sha256=inputs.hexdigest(), output_sha256=outputs.hexdigest(),
                  oracle='Sorted Python multiset; Floyd-Warshall and independent path certificates',
                  scope='Independent local driver tests; distinct from official checker and online AC')
    (ROOT / 'verification' / ('pheap-usages-' + mode + '.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
