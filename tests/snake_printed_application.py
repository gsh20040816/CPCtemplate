#!/usr/bin/env python3
"""Check example-215's exact registered program and independently bundled driver.

Small cases use literal whole-body command BFS, not a release-time graph.
Large cases use integer closed forms; the induced-path case really wraps uint64.
Default receipts/artifacts go below build/. Pass --report-dir verification to
publish receipts. SANITIZE=1 or CPC_SANITIZE=1 selects sanitizer unless --mode
is explicit. Sanitizer runs disable LSan only, retaining default ASan quarantine.
"""
import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
MOD = 1 << 64


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    return sha(Path(path).read_bytes())


def adjacent(u, v, m):
    return abs(u // m - v // m) + abs(u % m - v % m) == 1


def encode(n, m, body, grid):
    # Validate independently of the C++ parser, including body order and bounds.
    assert 1 <= n <= 3000 and 1 <= m <= 3000
    assert 1 <= len(body) <= min(n * m, 100000)
    assert len(grid) == n and all(len(row) == m and set(row) <= {'.', '#'} for row in grid)
    assert len(set(body)) == len(body)
    assert all(0 <= u < n * m and grid[u // m][u % m] == '.' for u in body)
    assert all(adjacent(u, v, m) for u, v in zip(body, body[1:]))
    return (f'{n} {m} {len(body)}\n' + ''.join(f'{u // m + 1} {u % m + 1}\n' for u in body)
            + '\n'.join(grid) + '\n').encode()


def literal_bfs(n, m, body, grid):
    body = tuple(body)
    queue = deque([(body, 0)])
    seen = {body}
    first = {}
    while queue:
        state, commands = queue.popleft()
        first.setdefault(state[0], commands)
        successors = []
        if len(state) > 1:  # S removes exactly one tail segment; the head stays.
            successors.append(state[:-1])
        x, y = divmod(state[0], m)
        for a, b in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= a < n and 0 <= b < m and grid[a][b] == '.':
                v = a * m + b
                # Current tail vacates simultaneously, even for a length-two swap.
                if v not in state[:-1]:
                    successors.append((v,) + state[:-1])
        for successor in successors:
            if successor not in seen:
                seen.add(successor)
                queue.append((successor, commands + 1))
    return sum(d * d for d in first.values()) % MOD


def square_sum(t):
    return t * (t + 1) * (2 * t + 1) // 6


def rectangle(n, m):
    return (m * square_sum(n - 1) + n * square_sum(m - 1)
            + 2 * (n * (n - 1) // 2) * (m * (m - 1) // 2)) % MOD


def cases():
    samples = [
        (2, 2, [0, 1, 3, 2], ['..', '..'], 14),
        (4, 5, [14, 13, 12, 11, 16], ['.....'] * 4, 293),
        (5, 5, [1, 0, 5], ['.....', '.###.', '.#.#.', '.###.', '.....'], 407),
    ]
    for i, (n, m, body, grid, want) in enumerate(samples, 1):
        assert literal_bfs(n, m, body, grid) == want
        yield f'official-sample-{i}', encode(n, m, body, grid), want, 'official sample + literal whole-body BFS'
    for n, m in ((2, 3), (3, 2)):
        count = 0
        for mask in range(1, 1 << (n * m)):
            grid = [''.join('.' if mask >> (r * m + c) & 1 else '#' for c in range(m)) for r in range(n)]
            def extend(body):
                nonlocal count
                count += 1
                yield (f'exhaustive-{n}x{m}-mask{mask}-body' + '_'.join(map(str, body)),
                       encode(n, m, body, grid), literal_bfs(n, m, body, grid), 'literal whole-body BFS')
                for v in range(n * m):
                    if mask >> v & 1 and v not in body and adjacent(body[-1], v, m):
                        yield from extend(body + [v])
            for head in range(n * m):
                if mask >> head & 1:
                    yield from extend([head])
        assert count == 744, (n, m, count)
    for name, n, m, body, grid in [
        ('isolated-head-unreachable-free-cell', 1, 3, [0], ['.#.']),
        ('single-cell', 1, 1, [0], ['.']),
        ('length-two-tail-swap', 1, 2, [0, 1], ['..']),
        ('length-two-tail-swap-transposed', 2, 1, [0, 1], ['.', '.']),
        ('full-corridor', 1, 8, list(range(8)), ['.' * 8]),
        ('full-corridor-transposed', 8, 1, list(range(8)), ['.'] * 8),
    ]:
        yield name, encode(n, m, body, grid), literal_bfs(n, m, body, grid), 'literal whole-body BFS'
    k = 3000
    want = square_sum(2 * k - 3) - square_sum(k - 2)
    yield 'full-3000-corridor', encode(1, k, list(range(k)), ['.' * k]), want, 'path distances j+k-2 for j>=1'
    n = m = 3000
    yield 'maximum-open-grid', encode(n, m, [0], ['.' * m] * n), rectangle(n, m), 'rectangular Manhattan-distance squared sum'
    yield 'maximum-barrier-grid', encode(n, m, [0], ['.' * 1499 + '#' + '.' * 1500] * n), rectangle(n, 1499), 'reachable 3000x1499 rectangular Manhattan-distance squared sum'
    grid = []
    body = []
    k = 100000
    for r in range(n):
        if r % 2 == 0:
            grid.append('.' * m)
            if len(body) < k:
                columns = range(m) if (r // 2) % 2 == 0 else range(m - 1, -1, -1)
                for c in columns:
                    if len(body) == k:
                        break
                    body.append(r * m + c)
        elif r < n - 1:
            c = m - 1 if (r // 2) % 2 == 0 else 0
            grid.append('#' * c + '.' + '#' * (m - c - 1))
            if len(body) < k:
                body.append(r * m + c)
        else:
            grid.append('#' * m)
    length = sum(row.count('.') for row in grid)
    assert length == 4501499 and len(body) == 100000
    exact = square_sum(k + length - 3) - square_sum(k - 2)
    assert exact == 32476676257872893237 and exact > MOD
    assert exact % MOD == 14029932184163341621
    yield ('maximum-induced-path-uint64-overflow', encode(n, m, body, grid), exact % MOD,
           f'induced path L={length}, k={k}; exact integer sum of squares [{k-1},{k+length-3}]={exact}')


def save(path, report):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, indent=2) + '\n')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default_mode = 'sanitizer' if any(os.getenv(v) == '1' for v in ('SANITIZE', 'CPC_SANITIZE')) else 'both'
    parser.add_argument('--mode', choices=['normal', 'sanitizer', 'both'], default=default_mode)
    parser.add_argument('--report-dir', type=Path, default=ROOT / 'build/snake-printed')
    args = parser.parse_args()
    work = ROOT / 'build/snake-printed'
    work.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('usage_examples', ROOT / 'tools/usage_examples.py')
    usage = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(usage)
    row, = [r for r in usage.records() if r['id'] == 'example-215']
    assert row['symbol'] == 'release_bfs' and row['kind'] == 'application'
    printed = work / 'example-215.printed.cpp'
    printed.write_text(row['program'])
    standalone = work / '8236.standalone.cpp'
    subprocess.run([sys.executable, str(ROOT / 'tools/bundle.py'), str(ROOT / row['driver']), str(standalone)], check=True)
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    compiler_version = subprocess.check_output([str(compiler), '--version'], text=True)
    sources = [Path(__file__).resolve(), ROOT / row['driver'], ROOT / 'src/compact/release_bfs.hpp',
               ROOT / 'tools/usage_examples.py', ROOT / 'tools/bundle.py', ROOT / 'docs/usage-examples.json']
    modes = ['normal', 'sanitizer'] if args.mode == 'both' else [args.mode]
    for mode in modes:
        began = time.monotonic()
        report_path = args.report_dir / f'snake-printed-{mode}.json'
        report = dict(status='running', example_id=row['id'], mode=mode,
                      started_utc=datetime.now(timezone.utc).isoformat(),
                      claim='Local application verification only; no new online AC claim',
                      compiler=dict(path=str(compiler), sha256=file_sha(compiler), version=compiler_version),
                      source_sha256={str(p.relative_to(ROOT)): file_sha(p) for p in sources},
                      registered_program_sha256=row['program_sha256'], programs=[])
        save(report_path, report)
        try:
            for form, source in [('registered_printed', printed), ('standalone_driver', standalone)]:
                flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
                binary = work / f'{form}.{mode}'
                command = [str(compiler), '-std=c++20', *flags, str(source), '-o', str(binary)]
                program = dict(form=form, source_sha256=file_sha(source), compile_command=command, status='compiling', cases=[])
                report['programs'].append(program)
                start = time.monotonic()
                cp = subprocess.run(command, capture_output=True, text=True)
                program['compile'] = dict(returncode=cp.returncode, stdout=cp.stdout, stderr=cp.stderr, wall_seconds=time.monotonic()-start)
                assert cp.returncode == 0, f'Compilation failed: {form}/{mode}: {cp.stderr}'
                program['binary_sha256'] = file_sha(binary)
                environment = os.environ.copy()
                if mode == 'sanitizer':
                    environment['ASAN_OPTIONS'] = 'detect_leaks=0'
                    environment['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
                    program['sanitizer_environment'] = {v: environment[v] for v in ('ASAN_OPTIONS', 'UBSAN_OPTIONS')}
                    program['asan_quarantine'] = 'runtime defaults (no quarantine override)'
                program['status'] = 'running'
                for name, data, expected, oracle in cases():
                    expected_bytes = f'{expected}\n'.encode()
                    result = dict(name=name, input_bytes=len(data), input_sha256=sha(data), expected=expected,
                                  expected_sha256=sha(expected_bytes), oracle=oracle, status='running')
                    program['cases'].append(result)
                    start = time.monotonic()
                    try:
                        run = subprocess.run([str(binary)], input=data, capture_output=True, env=environment, timeout=180)
                        result.update(returncode=run.returncode, actual=run.stdout.decode(errors='replace'),
                                      actual_sha256=sha(run.stdout), stderr=run.stderr.decode(errors='replace'))
                        assert run.returncode == 0 and run.stdout == expected_bytes and not run.stderr, (form, mode, name, result)
                        result['status'] = 'passed'
                    except BaseException as error:
                        result.update(status='failed', error=repr(error))
                        raise
                    finally:
                        result['wall_seconds'] = time.monotonic() - start
                    if len(program['cases']) % 100 == 0:
                        save(report_path, report)
                program.update(status='passed', case_count=len(program['cases']))
                print(f'{form}/{mode}: {len(program["cases"])} cases PASS', flush=True)
                save(report_path, report)
            report['status'] = 'passed'
        except BaseException as error:
            report.update(status='failed', error=repr(error))
            raise
        finally:
            report['wall_seconds'] = time.monotonic() - began
            report['finished_utc'] = datetime.now(timezone.utc).isoformat()
            save(report_path, report)
        print(f'Receipt: {report_path}', flush=True)


if __name__ == '__main__':
    main()
