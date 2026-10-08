#!/usr/bin/env python3
"""Bounded full-source comparison and independently certified factor grouping."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from audit_copy_context import extract_components


def factors(n):
    result = []
    p = 2
    while p <= n // p:
        count = 0
        while n % p == 0:
            n //= p
            count += 1
        if count:
            result.append((p, count))
        p += 1
    if n > 1:
        result.append((n, 1))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    mode = 'sanitizer' if args.sanitize else 'normal'
    output = ROOT / 'build/factor-source-audit' / mode
    output.mkdir(parents=True, exist_ok=True)
    paths = [ROOT / 'tests/factor_source_audit.py', ROOT / 'tests/fixtures/factor_source/kuangbin.cpp',
             ROOT / 'src/compact/number_theory.hpp', ROOT / 'src/compact/prime64.hpp', ROOT / 'src/compact/mod64.hpp']
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    snapshot = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    prelude = '#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'
    original = 'namespace original {\n#include "' + str(paths[1]) + '"\n}\n'
    flags = ['-std=c++20', '-O1' if args.sanitize else '-O2']
    if args.sanitize:
        flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')

    def compile_program(name, code, extra=()):
        path = output / (name + '.cpp')
        path.write_text(code)
        exe = output / name
        subprocess.run([CXX, *flags, *extra, str(path), '-o', str(exe)], check=True)
        return exe

    def run(exe, data, timeout=90):
        proc = subprocess.run([str(exe)], input=data, text=True, capture_output=True, timeout=timeout, env=env)
        assert proc.returncode == 0 and not proc.stderr, (exe, proc.stderr)
        return proc.stdout

    rng = random.Random(22018)
    cases = list(range(1, 10001))
    cases += [rng.randrange(1, 9973**2) for _ in range(400)]
    cases += [9973**2 - 1, 2**26, 3**16, 5**11, 9967**2, 9967 * 9973]
    expected = ''.join(str(len(fs)) + ''.join(f' {p} {e}' for p, e in fs) + '\n' for fs in map(factors, cases))
    data = ''.join(str(n) + '\n' for n in cases)
    source_main = r'''
int main()
{
    original::getPrime();
    long long n;
    while (cin >> n)
    {
        int count = original::getFactors(n);
        cout << count;
        for (int i = 0; i < count; i++)
            cout << ' ' << original::factor[i][0] << ' ' << original::factor[i][1];
        cout << '\n';
    }
    return 0;
}
'''
    source_exe = compile_program('original', prelude + original + source_main)
    assert run(source_exe, data) == expected
    new_main = r'''
int main()
{
    PollardRho solver;
    unsigned long long n;
    while (cin >> n)
    {
        auto values = solver.factor(n);
        vector<pair<unsigned long long, int>> groups;
        for (auto p : values)
        {
            if (groups.empty() || groups.back().first != p)
                groups.push_back({p, 1});
            else
                groups.back().second++;
        }
        cout << groups.size();
        for (auto [p, e] : groups)
            cout << ' ' << p << ' ' << e;
        cout << '\n';
    }
    return 0;
}
'''
    header = '#include "' + str(ROOT / 'src/compact/number_theory.hpp') + '"\n'
    components = {r['symbol']: r for r in extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))}
    copied = '\n'.join(components[n]['code'] for n in ['Mod64', 'Prime64', 'PollardRho'])
    # These cases test the replacement outside the safely bounded source domain.
    extra_cases = [9973**2, 10007**2, 9973 * 10007, 2**63, 3**40, 5**27, 2**64 - 1]
    known = [[(9973, 2)], [(10007, 2)], [(9973, 1), (10007, 1)], [(2, 63)], [(3, 40)], [(5, 27)],
             [(3, 1), (5, 1), (17, 1), (257, 1), (641, 1), (65537, 1), (6700417, 1)]]
    for n, fs in zip(extra_cases, known):
        product = 1
        for p, e in fs:
            assert factors(p) == [(p, 1)]
            product *= p**e
        assert product == n
    extension_data = ''.join(str(n) + '\n' for n in extra_cases)
    extension_expected = ''.join(str(len(fs)) + ''.join(f' {p} {e}' for p, e in fs) + '\n' for fs in known)
    for name, code, extra in [('header', header, ()), ('ndebug', header, ('-DNDEBUG',)), ('copied', copied, ())]:
        exe = compile_program(name, prelude + code + new_main, extra)
        assert run(exe, data) == expected
        assert run(exe, extension_data) == extension_expected
    # Show the exact erroneous next value without executing an unbounded loop.
    witness = r'''
int main()
{
    original::getPrime();
    int count = original::prime[0];
    cout << count << ' ' << original::prime[count] << ' ' << original::prime[count + 1] << '\n';
    return 0;
}
'''
    assert run(compile_program('boundary-witness', prelude + original + witness), '') == '1229 9973 1\n'
    try:
        proc = subprocess.run([str(source_exe)], input=str(9973**2) + '\n', text=True,
                              capture_output=True, timeout=2, env=env)
    except subprocess.TimeoutExpired:
        diagnostic = 'Original getFactors(9973^2) exceeded 2s; next slot=1 gives a non-decreasing divide-by-one loop (eventually signed exponent overflow).'
    else:
        assert proc.returncode != 0 and 'runtime error' in proc.stderr, (proc.returncode, proc.stdout, proc.stderr)
        diagnostic = proc.stderr
    assert snapshot == {str(p.relative_to(ROOT)): digest(p) for p in paths}
    report = dict(mode=mode, compiler=CXX, flags=flags, source_sha256=snapshot,
                  source_cases=len(cases), source_safe_domain='1 <= n < 9973^2',
                  extension_cases=len(extra_cases), forms=['original', 'header', 'ndebug', 'copied'],
                  diagnostic=diagnostic, oracle='independent trial division and prime/product certificates',
                  online_verdict=None, passed=True)
    (ROOT / 'verification' / ('factor-source-' + mode + '.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
