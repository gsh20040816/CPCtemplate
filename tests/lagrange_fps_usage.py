#!/usr/bin/env python3
"""Compile the sole documented Lagrange snippet against unchanged FpsPower.

Small cases use an independent characteristic-zero fixed-point oracle. Large
cases check the existing API mapping against exact binomial coefficient
identities, not brute-force coefficients of a huge implicit series. No new
algorithm coverage or online-judge acceptance is claimed.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
from math import comb, factorial
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from compiler_config import CXX
from lagrange_knowledge import fixed_point, mul

ROOT = Path(__file__).resolve().parents[1]
P = 998244353


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def residue(value):
    value = Fraction(value)
    if value.denominator % P == 0:
        raise ValueError('Nonunit rational denominator')
    return value.numerator % P * pow(value.denominator, -1, P) % P


def validate(n, k, phi):
    if not (1 <= k <= n < P):
        raise ValueError('Documented branch requires 1<=k<=n<p')
    if not (1 <= n - k + 1 <= 1 << 22):
        raise ValueError('Documented branch requires L<=2^22')
    if not phi or phi[0] % P == 0:
        raise ValueError('Documented branch requires Phi(0) a unit')


def make_cases():
    cases = []
    for constant in (1, 2):
        for tail in product((-1, 0, 1, 2), repeat=3):
            phi = [constant, *tail]
            t = fixed_point(phi, 10)
            tk = [1] + [0] * 10
            for k in range(1, 11):
                tk = mul(tk, t, 10)
                for n in range(k, 11):
                    cases.append(('small_integer_fixed_point', n, k,
                                  list(map(residue, phi)), residue(tk[n])))
    phi = [Fraction(1, factorial(j)) for j in range(11)]
    t = fixed_point(phi, 10)
    tk = [1] + [0] * 10
    for k in range(1, 11):
        tk = mul(tk, t, 10)
        for n in range(k, 11):
            cases.append(('small_rational_exp_fixed_point', n, k,
                          list(map(residue, phi)), residue(tk[n])))
    # Exact binomial oracle, with integer division BEFORE modular reduction.
    n, k = 65536, 1
    numerator = k * comb(2 * n, n - k)
    assert numerator % n == 0
    cases.append(('long_truncation_binomial_mapping', n, k, [1, 2, 1], numerator // n % P))
    n, k = P - 1, P - 1 - 64
    numerator = k * comb(2 * n, n - k)
    assert numerator % n == 0
    cases.append(('large_upper_index_small_L_binomial_mapping', n, k, [1, 2, 1], numerator // n % P))
    # Phi=2+t: avoid constructing 2**n; use modular exponentiation.
    r = n - k
    expected = k * pow(n, -1, P) % P * (comb(n, r) % P) % P * pow(2, n - r, P) % P
    cases.append(('large_upper_index_nonone_leading_scale_mapping', n, k, [2, 1], expected))
    for _, n, k, phi, _ in cases:
        validate(n, k, phi)
    return cases


def local_headers(path):
    seen = set()
    def visit(p):
        p = p.resolve()
        if p in seen:
            return
        seen.add(p)
        for name in re.findall(r'^\s*#include\s+"([^"]+)"', p.read_text(), re.M):
            visit(p.parent / name)
    visit(path)
    return seen


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: assertions are required')
    sanitized = os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1'
    mode = 'sanitizer' if sanitized else 'normal'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=ROOT / f'build/lagrange-fps-{mode}.json')
    args = parser.parse_args()
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    doc = ROOT / 'docs/knowledge-lagrange.tex'
    paths = local_headers(ROOT / 'src/compact/fps_power.hpp')
    paths.update((Path(__file__).resolve(), ROOT / 'tests/lagrange_knowledge.py',
                  ROOT / 'tests/compiler_config.py', doc, compiler))
    cc1 = subprocess.run([str(compiler), '-print-prog-name=cc1plus'],
                         check=True, capture_output=True, text=True).stdout.strip()
    if Path(cc1).is_file():
        paths.add(Path(cc1).resolve())
    def bindings():
        return {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): digest(p)
                for p in sorted(paths)}
    before = bindings()
    matches = re.findall(r'\\begin\{lstlisting\}(?:\[[^\]]*\])?(.*?)\\end\{lstlisting\}', doc.read_text(), re.S)
    if len(matches) != 1:
        raise RuntimeError(f'Expected sole exact lstlisting, got {len(matches)}')
    snippet = matches[0]
    # This wrapper only handles input, preconditions, and output. Every actual
    # template operation is copied verbatim from the authored documentation.
    source = '''#include "fps_power.hpp"
#include <iostream>
int main() {
    int n, k, m;
    while (std::cin >> n >> k >> m) {
        FpsPower::Poly phi(m);
        for (auto &value : phi) { long long x; std::cin >> x; value = x; }
        if (!(1 <= k && k <= n && n < 998244353) ||
            n-k+1 > (1 << 22) || phi.empty() || phi[0].v == 0) return 2;
''' + snippet + '''
        std::cout << answer.v << '\\n';
    }
}
'''
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix=f'lagrange-fps-{mode}-', dir=build))
    source_path = directory / 'snippet.cpp'
    source_path.write_text(source)
    exe = directory / 'snippet'
    source_hash = digest(source_path)
    flags = ['-std=c++20', '-O2']
    if sanitized:
        flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    command = [str(compiler), *flags, '-I', str(ROOT / 'src/compact'), str(source_path), '-o', str(exe)]
    subprocess.run(command, check=True, capture_output=True, text=True, timeout=180)
    cases = make_cases()
    invalids = [(0, 0, [1]), (2, 0, [1]), (2, 3, [1]), (P, 1, [1]),
                ((1 << 22) + 1, 1, [1]), (2, 1, [0]), (2, 1, [P])]
    for n, k, phi in invalids:
        try:
            validate(n, k, phi)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid documented-branch input admitted')
    environment = os.environ.copy()
    # Keep the compiler's default PIE behavior and ASan's default quarantine.
    # LSan is intentionally disabled for the managed execution environment.
    options = [s for s in environment.get('ASAN_OPTIONS', '').split(':') if s and
               s.split('=')[0] not in ('detect_leaks', 'quarantine_size_mb', 'thread_local_quarantine_size_kb')]
    environment['ASAN_OPTIONS'] = ':'.join(options + ['detect_leaks=0'])
    environment['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
    data = ''.join(f'{n} {k} {len(phi)}\n' + ' '.join(map(str, phi)) + '\n'
                   for _, n, k, phi, _ in cases)
    run = subprocess.run([str(exe)], input=data, capture_output=True, text=True,
                         env=environment, check=True, timeout=300)
    assert not run.stderr, run.stderr
    actual = list(map(int, run.stdout.split()))
    assert len(actual) == len(cases), (len(actual), len(cases))
    for got, (group, n, k, phi, wanted) in zip(actual, cases):
        assert got == wanted, (group, n, k, phi, got, wanted)
    after = bindings()
    assert before == after, 'Bound source/compiler changed during run'
    assert digest(source_path) == source_hash, 'Generated snippet changed during run'
    version = subprocess.run([str(compiler), '--version'], check=True, capture_output=True, text=True).stdout
    report = {'passed': True, 'mode': mode, 'groups': dict(Counter(c[0] for c in cases)),
              'scope': __doc__, 'precondition_rejections_not_sent_to_cpp': len(invalids),
              'case_count': len(cases), 'compiler_version': version, 'compile_command': command,
              'build_directory': str(directory.relative_to(ROOT)),
              'pie': 'compiler default; no disabling flags', 'asan_quarantine': 'default',
              'leak_sanitizer': 'disabled', 'asan_options': environment['ASAN_OPTIONS'],
              'ubsan_options': environment['UBSAN_OPTIONS'],
              'sources_before': before, 'sources_after': after,
              'snippet_sha256': hashlib.sha256(snippet.encode()).hexdigest(),
              'generated_source_sha256': source_hash, 'input_sha256': hashlib.sha256(data.encode()).hexdigest(),
              'long_cases': [{'group': group, 'n': n, 'k': k, 'L': n-k+1, 'phi': phi, 'expected': wanted}
                             for group, n, k, phi, wanted in cases if 'mapping' in group],
              'stderr': run.stderr}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(f'Lagrange documented FpsPower usage {mode} PASS: {len(cases)} cases; {report["groups"]}')


if __name__ == '__main__':
    main()
