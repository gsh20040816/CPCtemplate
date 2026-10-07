"""Pinned kuangbin Simpson source: analytic oracles and a sampling alias."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import tempfile
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot


def main():
    if not __debug__:
        raise RuntimeError('Oracle requires assertions')
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='simpson-source-' + mode + '-', dir=ROOT / 'build'))
    rng = random.Random(2152026)
    cases = []
    for degree in range(6):
        for _ in range(20):
            a = Fraction(rng.randrange(-8, 8), 4)
            b = a + Fraction(rng.randrange(1, 13), 4)
            c = [rng.randrange(-5, 6) for _ in range(degree + 1)]
            exact = sum((v * (b ** (i + 1) - a ** (i + 1)) / (i + 1)
                         for i, v in enumerate(c)), Fraction(0))
            cases.append(dict(kind=0, a=float(a), b=float(b), eps=1e-10,
                              coef=c, exact=str(exact)))
    for kind in (1, 2, 3):
        for a, b in [(-3, 2), (0, 1), (1, 0), (-1, 1), (2, 2), (-8, 8)]:
            exact = {1: math.atan(b) - math.atan(a),
                     2: math.exp(b) - math.exp(a),
                     3: math.cos(a) - math.cos(b)}[kind]
            cases.append(dict(kind=kind, a=a, b=b, eps=1e-10, coef=[0], exact=repr(exact)))
    # Quartic correction is exact in real arithmetic, even at the loose root tolerance.
    cases.append(dict(kind=0, a=0, b=1, eps=0.001, coef=[0, 0, 0, 0, 1],
                      exact='1/5', name='quartic-correction'))
    # Exact rational polynomial integral, independent of either quadrature.
    p = [Fraction(1)]
    for i in range(5):
        q = [Fraction(0)] * (len(p) + 1)
        for j, x in enumerate(p):
            q[j] -= x * Fraction(i, 4)
            q[j + 1] += x
        p = q
    sq = [Fraction(0)] * (2 * len(p) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(p):
            sq[i + j] += x * y
    alias = sum((v / (i + 1) for i, v in enumerate(sq)), Fraction(0))
    assert alias > Fraction(1, 10 ** 12)
    cases.append(dict(kind=4, a=0, b=1, eps=1e-12, coef=[0],
                      exact=str(alias), name='sampling-alias'))
    data = ''.join(' '.join(map(str, [t['kind'], t['a'], t['b'], t['eps'],
                                   len(t['coef']) - 1, *t['coef']])) + '\n' for t in cases)
    sha = lambda b: hashlib.sha256(b).hexdigest()
    flags = ['-std=c++20', '-Wall', '-Wextra'] + (['-O1', '-g', '-fsanitize=address,undefined',
             '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    report = dict(mode=mode, source_before_sha256=before, programs=[], mutants=[],
                  cases=cases, input_sha256=sha(data.encode()), alias_integral=str(alias),
                  scope='Pinned source comparison only, no online AC or rigorous quadrature error guarantee.')
    probe = (ROOT / 'tests/simpson_source_probe.cpp').read_text()
    fixture = (ROOT / 'tests/fixtures/simpson_sources/kuangbin.inc').read_text()
    text = probe.replace('#include "../src/compact/adaptive_simpson.hpp"',
                         '#include "' + str(ROOT / 'src/compact/adaptive_simpson.hpp') + '"')
    text = text.replace('#include "fixtures/simpson_sources/kuangbin.inc"', fixture)

    def compile_run(name, source, ndebug=False, input_data=data):
        cpp, exe = out / (name + '.cpp'), out / name
        cpp.write_text(source)
        command = [CXX, *flags, *(['-DNDEBUG'] if ndebug else []), str(cpp), '-o', str(exe)]
        p = subprocess.run(command, capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        run = subprocess.run([str(exe)], input=input_data, capture_output=True, text=True, env=env, timeout=120)
        assert run.returncode == 0 and not run.stderr, (name, run.returncode, run.stderr)
        return run.stdout, dict(name=name, command=command, source_sha256=sha(source.encode()),
                              binary_sha256=sha(exe.read_bytes()), compiler_stderr=p.stderr,
                              output_sha256=sha(run.stdout.encode()))

    for ndebug in (False, True):
        output, entry = compile_run('ndebug' if ndebug else 'assert', text, ndebug)
        rows = output.splitlines()
        assert len(rows) == len(cases)
        max_error = [0.0, 0.0]
        for t, line in zip(cases, rows):
            old, old_calls, now, err, met, evaluations, calls = line.split()
            old, now, err = map(float, (old, now, err))
            old_calls, met, evaluations, calls = map(int, (old_calls, met, evaluations, calls))
            assert met == 1 and evaluations == calls and 0 <= err <= t['eps']
            if t.get('name') == 'sampling-alias':
                assert old == now == err == 0 and old_calls == 9 and calls == 5
                continue
            exact = float(Fraction(t['exact']))
            for j, value in enumerate((old, now)):
                error = abs(value - exact)
                max_error[j] = max(max_error[j], error)
                tolerance = 8 * t['eps'] + 5e-13 * (1 + abs(exact))
                if t.get('name') == 'quartic-correction':
                    tolerance = 1e-14
                    assert old_calls == 9 and calls == 5
                assert math.isfinite(value) and error <= tolerance, (t, line, exact)
            if t['a'] == t['b']:
                assert old_calls == 9 and calls == 0 and old == now == 0
        entry.update(datasets=len(cases), maximum_absolute_error=max_error,
                     alias_source_calls=9, alias_cached_calls=5, zero_length_source_calls=9,
                     zero_length_cached_calls=0)
        report['programs'].append(entry)
        print(entry['name'], len(cases), 'PASS', flush=True)
    anchor = 'return L + R + (L + R - A)/15.0;'
    assert text.count(anchor) == 1
    mutant = text.replace(anchor, 'return L + R - (L + R - A)/15.0;')
    output, entry = compile_run('wrong-source-correction', mutant,
                               input_data='0 0 1 0.001 4 0 0 0 0 1\n')
    assert abs(float(output.split()[0]) - 0.2) > 1e-5
    entry['rejected_by'] = 'quartic exact antiderivative, answer mismatch'
    report['mutants'].append(entry)
    after = snapshot(ROOT)
    assert before == after
    report.update(source_after_sha256=after, passed=True)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out / 'report.json', flush=True)


if __name__ == '__main__':
    main()
