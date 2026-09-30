"""Synthetic mixed-Euler composition: independent existence and walk certificates.

Run directly for normal and ASan/UBSan tests. Import check_output(data, stdout)
for small printed-usage cases; importing this module does not compile or run tests.
"""
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations_with_replacement, product
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import random
import subprocess
import time



ROOT = Path(__file__).resolve().parents[1]
DRIVER = 'docs/usage-drivers/mixed-euler-demo.cpp'
SOURCES = [DRIVER, 'src/compact/mixed_euler.hpp',
           'src/compact/directed_euler.hpp', 'src/compact/flow.hpp',
           'tests/mixed_euler_demo.py', 'tests/compiler_config.py', 'tools/bundle.py']


def case(mode, n, edges=(), start=0, finish=0):
    return mode, n, tuple(edges), start, finish


def encode(cases):
    lines = [str(len(cases))]
    for mode, n, edges, start, finish in cases:
        lines.append(f'{mode} {n} {len(edges)} {start} {finish}')
        lines.extend(f'{u} {v} {kind}' for u, v, kind in edges)
    return '\n'.join(lines) + '\n'


def decode(data):
    words = iter(data.split())
    count = int(next(words))
    assert 1 <= count <= 10000
    cases = []
    for _ in range(count):
        mode = next(words)
        n, m, start, finish = (int(next(words)) for _ in range(4))
        assert mode in ('A', 'C', 'P') and 1 <= n <= 200 and 0 <= m <= 800
        assert (1 <= start <= n and 1 <= finish <= n) if mode == 'P' else start == finish == 0
        edges = [tuple(int(next(words)) for _ in range(3)) for _ in range(m)]
        assert all(1 <= u <= n and 1 <= v <= n and kind in (0, 1)
                   for u, v, kind in edges)
        cases.append(case(mode, n, edges, start, finish))
    assert next(words, None) is None, 'Trailing input tokens'
    return cases


def existence(spec):
    """Enumerate flexible orientations; use weak connectivity and degree theorem.

    This does not call a flow solver or construct a Hierholzer walk. Deliberately
    reject large flexible instances so a central checker cannot explode silently.
    """
    mode, n, edges, start, finish = spec
    flexible = sum(kind == 0 for u, v, kind in edges)
    assert flexible <= 12, 'Use independently justified expectations for scale cases'
    if not edges:
        return mode != 'P' or start == finish
    adjacency = [[] for _ in range(n + 1)]
    for u, v, _ in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    seen = {edges[0][0]}
    queue = list(seen)
    for u in queue:
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    if any(adjacency[u] and u not in seen for u in range(1, n + 1)):
        return False
    if mode == 'P' and (start not in seen or finish not in seen):
        return False
    target = [0] * (n + 1)
    if mode == 'P':
        target[start] += 1
        target[finish] -= 1
    for flips in product((False, True), repeat=flexible):
        choices = iter(flips)
        balance = [0] * (n + 1)
        for u, v, kind in edges:
            if kind == 0 and next(choices):
                u, v = v, u
            balance[u] += 1
            balance[v] -= 1
        if mode == 'A':
            nonzero = sorted(value for value in balance if value)
            if nonzero in ([], [-1, 1]):
                return True
        elif balance == target:
            return True
    return False


def check_cases(cases, stdout, expected):
    """Accept any feasible orientation/walk, with every original edge exactly once."""
    assert len(cases) == len(expected)
    lines = stdout.splitlines()
    pos = 0
    successes = 0
    for index, (spec, possible) in enumerate(zip(cases, expected)):
        mode, n, edges, start, finish = spec
        assert pos < len(lines), ('Missing verdict', index)
        verdict = lines[pos].split()
        pos += 1
        assert verdict == (['YES'] if possible else ['NO']), (index, spec, verdict, possible)
        if not possible:
            continue
        assert pos + 1 < len(lines), ('Missing certificate', index)
        vertex_line, edge_line = lines[pos].split(), lines[pos + 1].split()
        pos += 2
        assert vertex_line[:1] == ['VERTICES'] and edge_line[:1] == ['EDGES']
        assert len(vertex_line) >= 2 and len(edge_line) >= 2
        vertices = list(map(int, vertex_line[2:]))
        ids = list(map(int, edge_line[2:]))
        m = len(edges)
        assert int(vertex_line[1]) == len(vertices) == m + 1
        assert int(edge_line[1]) == len(ids) == m
        assert all(1 <= u <= n for u in vertices), (index, vertices)
        assert sorted(ids) == list(range(1, m + 1)), ('Missing/repeated original edge', index, ids)
        for a, b, edge_id in zip(vertices, vertices[1:], ids):
            u, v, kind = edges[edge_id - 1]
            assert (a, b) == (u, v) or (kind == 0 and (a, b) == (v, u)), (
                'Fixed edge reversed or edge-ID/walk mismatch', index, edge_id, (a, b), (u, v, kind))
        if mode == 'C':
            assert vertices[0] == vertices[-1], ('Circuit is open', index)
        elif mode == 'P':
            assert (vertices[0], vertices[-1]) == (start, finish), ('Wrong endpoints', index)
        if not edges:
            assert vertices == [start if mode == 'P' else 1], ('Empty-walk convention', index)
        successes += 1
    assert pos == len(lines), ('Trailing output', lines[pos:])
    return successes


def check_output(data, stdout):
    """Small, independent certificate checker for central printed-usage checks."""
    cases = decode(data)
    return check_cases(cases, stdout, [existence(spec) for spec in cases])


def all_modes(n, edges):
    result = [case('C', n, edges), case('A', n, edges)]
    result.extend(case('P', n, edges, s, t)
                  for s in range(1, n + 1) for t in range(1, n + 1))
    return result


def build_groups():
    # Every multiset of at most four edges on two labelled vertices, including
    # both stored orders of flexible edges, all fixed directions and all loops.
    options = list(product(range(1, 3), range(1, 3), range(2)))
    exhaustive = []
    for m in range(5):
        for edges in combinations_with_replacement(options, m):
            exhaustive.extend(all_modes(2, edges))
    assert len(exhaustive) == 495 * 6

    rng = random.Random(2061637)
    randomized = []
    for _ in range(240):
        n = rng.randint(1, 6)
        edges = [(rng.randint(1, n), rng.randint(1, n), rng.randrange(2))
                 for _ in range(rng.randrange(9))]
        randomized.extend(all_modes(n, edges))

    boundary = []
    for n, edges in [
        (1, []), (3, []),
        (3, [(1, 2, 1)]), (3, [(2, 1, 1)]),
        (4, [(1, 2, 0), (2, 3, 1), (3, 4, 0)]),
        (4, [(1, 2, 1), (2, 1, 1), (3, 4, 0), (3, 4, 0)]),
        (4, [(2, 3, 1), (2, 3, 0)]),
        (3, [(3, 3, 0), (3, 3, 1)]),
        (3, [(1, 1, 1), (3, 3, 0)]),
        (4, [(1, 2, 0), (1, 3, 0), (1, 4, 0)]),
    ]:
        boundary.extend(all_modes(n, edges))

    scale, scale_expected = [], []

    def add(spec, possible):
        scale.append(spec)
        scale_expected.append(possible)

    # Reversing every flexible edge gives a connected balanced orientation.
    chain = [(u, u + 1, kind) for u in range(1, 200) for kind in (1, 0)]
    add(case('C', 200, chain), True)
    add(case('P', 200, chain, 137, 137), True)
    # Add one fixed edge to the balanced witness to obtain an open trail.
    open_chain = chain + [(200, 1, 1)]
    add(case('A', 200, open_chain), True)
    add(case('P', 200, open_chain, 200, 1), True)
    # Only 200 -> 1 is possible here, so the any-endpoints API needs both tries.
    descending = [(u, u - 1, 1) for u in range(200, 1, -1)]
    add(case('A', 200, descending), True)
    add(case('P', 200, descending, 200, 1), True)
    add(case('P', 200, descending, 1, 200), False)
    cycle = [(u, u % 200 + 1, 1) for u in range(1, 201)] * 4
    add(case('C', 200, cycle), True)
    add(case('P', 200, cycle, 137, 137), True)
    add(case('A', 200, [(2, 199, 0)] * 799), True)
    add(case('C', 200, [(2, 199, 0)] * 800), True)
    add(case('P', 200, [(2, 199, 0)] * 800, 1, 1), False)
    add(case('A', 200, [(1, 2, 1)] * 800), False)
    add(case('C', 200, [(1, 1, 1)] * 400 + [(200, 200, 0)] * 400), False)
    add(case('P', 200, [(200, 200, 0)] * 800, 200, 200), True)
    add(case('C', 200, [(200, 200, 1)] * 800), True)
    add(case('A', 200), True)
    add(case('P', 200, (), 200, 200), True)
    add(case('P', 200, (), 1, 200), False)

    # Multiple successes and failures in one process, including the T bound.
    reset_base = [case('A', 3, [(2, 1, 1)]), case('C', 3, [(2, 1, 1)]),
                  case('P', 3, (), 3, 3), case('P', 3, (), 3, 1)]
    reset = reset_base * 2500
    return [
        ('exhaustive', exhaustive, [existence(spec) for spec in exhaustive]),
        ('randomized', randomized, [existence(spec) for spec in randomized]),
        ('boundary', boundary, [existence(spec) for spec in boundary]),
        ('scale', scale, scale_expected),
        ('reset', reset, [True, False, True, False] * 2500),
    ]


def checker_selftest():
    # Accept both valid orientations; reject falsely unique-output checkers.
    data = encode([case('A', 2, [(1, 2, 0)])])
    check_output(data, 'YES\nVERTICES 2 1 2\nEDGES 1 1\n')
    check_output(data, 'YES\nVERTICES 2 2 1\nEDGES 1 1\n')
    bad = [
        (data, 'NO\n'),
        (data, 'YES\nVERTICES 2 1 2\nEDGES 1 0\n'),
        (data, 'YES\nVERTICES 2 1 3\nEDGES 1 1\n'),
        (data, 'YES\nVERTICES 1 1\nEDGES 1 1\n'),
        (data, 'YES\nVERTICES 2 1 2\nEDGES 1 1\nNO\n'),
        (encode([case('A', 2, [(1, 2, 1)])]),
         'YES\nVERTICES 2 2 1\nEDGES 1 1\n'),
        (encode([case('P', 2, [(1, 2, 0)], 1, 2)]),
         'YES\nVERTICES 2 2 1\nEDGES 1 1\n'),
        (encode([case('C', 2, [(1, 2, 0), (1, 2, 0)])]),
         'YES\nVERTICES 3 1 2 1\nEDGES 2 1 1\n'),
        (encode([case('P', 3, (), 3, 3)]),
         'YES\nVERTICES 1 1\nEDGES 0\n'),
    ]
    for input_data, output in bad:
        try:
            check_output(input_data, output)
        except (AssertionError, ValueError):
            continue
        raise AssertionError(('Checker accepted a corrupted certificate', input_data, output))
    return len(bad)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes():
    return {path: sha256(ROOT / path) for path in SOURCES}


def main():
    from compiler_config import CXX
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('normal', 'sanitizer', 'both'), default='both')
    args = parser.parse_args()
    modes = ('normal', 'sanitizer') if args.mode == 'both' else (args.mode,)
    before = source_hashes()
    rejected = checker_selftest()
    groups = build_groups()
    compiler_version = subprocess.check_output([CXX, '--version'], text=True).splitlines()[0]
    for mode in modes:
        work = ROOT / 'build' / 'mixed-euler-demo' / mode
        work.mkdir(parents=True, exist_ok=True)
        bundle, exe = work / 'mixed-euler-demo.cpp', work / 'mixed-euler-demo'
        bundle_cmd = ['python3', 'tools/bundle.py', DRIVER, str(bundle)]
        subprocess.run(bundle_cmd, cwd=ROOT, check=True)
        flags = ['-O2'] if mode == 'normal' else [
            '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        compile_cmd = [CXX, '-std=c++20', *flags, str(bundle), '-o', str(exe)]
        subprocess.run(compile_cmd, cwd=ROOT, check=True)
        env = dict(os.environ)
        env['ASAN_OPTIONS'] = 'detect_leaks=0:halt_on_error=1'
        env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
        results = []
        for name, cases, expected in groups:
            data = encode(cases)
            assert decode(data) == cases
            start = time.monotonic()
            run = subprocess.run([str(exe)], input=data, text=True, capture_output=True,
                                 timeout=60, env=env, check=True)
            assert not run.stderr, run.stderr
            successes = check_cases(cases, run.stdout, expected)
            (work / (name + '.in')).write_text(data)
            (work / (name + '.out')).write_text(run.stdout)
            results.append(dict(group=name, cases=len(cases), successes=successes,
                                elapsed_seconds=round(time.monotonic() - start, 6),
                                input_sha256=hashlib.sha256(data.encode()).hexdigest(),
                                output_sha256=hashlib.sha256(run.stdout.encode()).hexdigest()))
        assert source_hashes() == before, 'Sources changed during testing; rerun'
        report = dict(
            mode=mode, passed=True, timestamp_utc=datetime.now(timezone.utc).isoformat(),
            compiler=compiler_version, platform=platform.platform(),
            bundle_command=bundle_cmd, compile_command=compile_cmd,
            source_sha256=before, bundle_sha256=sha256(bundle),
            executable_sha256=sha256(exe), groups=results,
            total_cases=sum(item['cases'] for item in results),
            mode_counts=dict(Counter(spec[0] for _, cases, _ in groups for spec in cases)),
            checker_corruptions_rejected=rejected,
            sanitizer_options={key: env[key] for key in ('ASAN_OPTIONS', 'UBSAN_OPTIONS')},
            scope='Local bounded synthetic API driver only. Independent exhaustive orientation '
                  'and weak-connectivity/degree oracle on small graphs; explicit witnesses or '
                  'obstructions at n<=200, m<=800. Full walk and original edge-ID certificates. '
                  'No OJ submission, online AC, global lexicographic minimum, or full-suite claim. '
                  'LeakSanitizer disabled; recursive implementations unchanged.')
        (work / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(f'Mixed Euler API demo {mode}: {report["total_cases"]} cases PASS; '
              f'report {work.relative_to(ROOT)}/report.json')


if __name__ == '__main__':
    main()
