"""Exact small-system classification vs pinned kuangbin real elimination."""
from fractions import Fraction
from pathlib import Path
from collections import Counter
import hashlib
import itertools
import json
import os
import subprocess
import sys
import tempfile
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot


def exact(matrix, n):
    a = [[Fraction(x) for x in row] for row in matrix]
    m = len(a)
    pivots = []
    for col in range(n):
        row = len(pivots)
        p = next((i for i in range(row, m) if a[i][col]), None)
        if p is None:
            continue
        a[row], a[p] = a[p], a[row]
        scale = a[row][col]
        a[row] = [v / scale for v in a[row]]
        for i in range(m):
            if i != row:
                scale = a[i][col]
                a[i] = [u - scale * v for u, v in zip(a[i], a[row])]
        pivots.append(col)
    rank = len(pivots)
    if any(not any(row[:n]) and row[n] for row in a):
        return False, rank, [], []
    particular = [Fraction(0)] * n
    for i, col in enumerate(pivots):
        particular[col] = a[i][n]
    kernel = []
    for col in range(n):
        if col not in pivots:
            v = [Fraction(0)] * n
            v[col] = 1
            for i, p in enumerate(pivots):
                v[p] = -a[i][col]
            kernel.append(v)
    return True, rank, particular, kernel


def main():
    if not __debug__:
        raise RuntimeError('Oracle requires assertions')
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='gauss-real-source-' + mode + '-', dir=ROOT / 'build'))
    cases = []
    for m in (1, 2):
        for n in (1, 2):
            for values in itertools.product((-1, 0, 1), repeat=m * (n + 1)):
                a = [list(values[i * (n + 1):(i + 1) * (n + 1)]) for i in range(m)]
                cases.append(dict(n=n, matrix=a, name='exhaustive'))
    cases.extend([dict(n=2, matrix=[[1, 1, 2], [2, 2, 4]], name='consistent-singular'),
                  dict(n=1, matrix=[[1, 0], [1, 1]], name='contradictory-extra-row'),
                  dict(n=2, matrix=[[0, 1, 1]], name='first-column-free'),
                  dict(n=1, matrix=[['1e-10', '1e-10']], name='absolute-threshold')])
    data = ''.join(f"{len(t['matrix'])} {t['n']}\n" +
                   '\n'.join(' '.join(map(str, row)) for row in t['matrix']) + '\n' for t in cases)
    sha = lambda b: hashlib.sha256(b).hexdigest()
    flags = ['-std=c++20', '-Wall', '-Wextra'] + (['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    probe = (ROOT / 'tests/gauss_real_source_probe.cpp').read_text()
    fixture = (ROOT / 'tests/fixtures/gauss_real_sources/kuangbin.inc').read_text()
    text = probe.replace('#include "../src/compact/gauss_real.hpp"', '#include "' + str(ROOT / 'src/compact/gauss_real.hpp') + '"')
    text = text.replace('#include "fixtures/gauss_real_sources/kuangbin.inc"', fixture)
    report = dict(mode=mode, source_before_sha256=before, datasets=len(cases),
                  input_sha256=sha(data.encode()), programs=[], mutants=[],
                  scope='Pinned source return-contract audit. Exact small rational oracles do not certify arbitrary floating-point rank or OJ AC.')

    def compile_run(name, source, ndebug=False, input_data=data):
        cpp, exe = out / (name + '.cpp'), out / name
        cpp.write_text(source)
        command = [CXX, *flags, *(['-DNDEBUG'] if ndebug else []), str(cpp), '-o', str(exe)]
        p = subprocess.run(command, capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        run = subprocess.run([str(exe)], input=input_data, capture_output=True, text=True, env=env, timeout=60)
        assert run.returncode == 0 and not run.stderr, (name, run.returncode, run.stderr)
        return run.stdout, dict(name=name, command=command, source_sha256=sha(source.encode()),
                               binary_sha256=sha(exe.read_bytes()), output_sha256=sha(run.stdout.encode()), compiler_stderr=p.stderr)

    for ndebug in (False, True):
        got, entry = compile_run('ndebug' if ndebug else 'assert', text, ndebug)
        lines = got.splitlines()
        assert len(lines) == len(cases)
        mismatches = Counter()
        examples = []
        unique_square = 0
        for t, line in zip(cases, lines):
            n, matrix = t['n'], t['matrix']
            consistent, rank, particular, kernel = exact(matrix, n)
            fields = line.split()
            old = int(fields[0])
            old_x = list(map(Fraction, fields[1:n + 1]))
            now, nrank, nkernel = map(int, fields[n + 1:n + 4])
            values = list(map(Fraction, fields[n + 4:]))
            assert now == consistent and nrank == rank and nkernel == len(kernel), (t, line)
            wanted = particular + [v for row in kernel for v in row]
            assert len(values) == len(wanted)
            assert all(abs(u - v) <= Fraction(1, 10 ** 12) for u, v in zip(values, wanted)), (t, line)
            if t['name'] == 'exhaustive' and len(matrix) == n and rank == n:
                unique_square += 1
                assert old == 1 and all(abs(u - v) <= Fraction(1, 10 ** 12) for u, v in zip(old_x, particular)), (t, line)
            if old != consistent:
                mismatches['false_negative' if consistent else 'false_positive'] += 1
            if t['name'] != 'exhaustive':
                expected_old = 1 if t['name'] == 'contradictory-extra-row' else 0
                assert old == expected_old and old != consistent
                examples.append(dict(**t, original_status=old, exact_consistent=consistent, exact_rank=rank,
                                     current_consistent=bool(now), current_rank=nrank))
        assert unique_square == 438 and mismatches['false_positive'] and mismatches['false_negative']
        entry.update(unique_nonsingular_square_cases=unique_square,
                     source_status_mismatches=dict(mismatches), counterexamples=examples)
        report['programs'].append(entry)
        print(entry['name'], len(cases), unique_square, dict(mismatches), 'PASS', flush=True)
    anchor = 'x[k]/=a[k][col];'
    assert text.count(anchor) == 1
    got, entry = compile_run('omit-rhs-normalization', text.replace(anchor, ''), input_data='1 1\n-1 1\n')
    assert int(got.split()[0]) == 1 and Fraction(got.split()[1]) != -1
    entry['rejected_by'] = 'exact scalar solution, answer mismatch'
    report['mutants'].append(entry)
    after = snapshot(ROOT)
    assert before == after
    report.update(source_after_sha256=after, passed=True)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out / 'report.json', flush=True)


if __name__ == '__main__':
    main()
