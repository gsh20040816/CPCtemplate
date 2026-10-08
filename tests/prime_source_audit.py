#!/usr/bin/env python3
"""Compile all three kuangbin prime fragments; preserve original global main."""
import argparse
import ast
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
from audit_copy_context import candidate, extract_components
from usage_examples import records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    mode = 'sanitizer' if args.sanitize else 'normal'
    output = ROOT / 'build/prime-source-audit' / mode
    output.mkdir(parents=True, exist_ok=True)
    fixture = ROOT / 'tests/fixtures/prime_sources'
    paths = [ROOT / 'tests/prime_source_audit.py', ROOT / 'tests/prime_distance_application.py',
             ROOT / 'src/compact/number_theory.hpp', ROOT / 'src/compact/segmented_sieve.hpp',
             ROOT / 'verify/poj/2689.compact.cpp', *sorted(fixture.glob('*.cpp'))]
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    snapshot = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    flags = ['-std=c++20', '-O1' if args.sanitize else '-O2']
    if args.sanitize:
        flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
               UBSAN_OPTIONS='halt_on_error=1')

    def compile_run(name, code, data='', extra=()):
        source = output / (name + '.cpp')
        exe = output / name
        source.write_text(code)
        subprocess.run([CXX, *flags, *extra, str(source), '-o', str(exe)], check=True)
        run = subprocess.run([str(exe)], input=data, text=True, capture_output=True,
                             timeout=90, env=env)
        assert run.returncode == 0, (name, run.stderr)
        assert not run.stderr, (name, run.stderr)
        return run.stdout

    components = {r['symbol']: r for r in extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))}
    prelude = '#include <bits/stdc++.h>\nusing namespace std;\n'
    source_headers = '\n'.join('namespace ' + name + ' {\n#include "' + str(fixture / file) + '"\n}'
                               for name, file in [('table', 'table.cpp'), ('list_source', 'list.cpp')])
    # Trial division is independent of both source sieves and the linear sieve.
    checks = r'''
bool trial(int n)
{
    if (n < 2) return false;
    for (int d = 2; d <= n / d; d++)
        if (n % d == 0) return false;
    return true;
}

int main()
{
    for (int repeat = 0; repeat < 2; repeat++)
    {
        table::init();
        list_source::getPrime();
        LinearSieve sieve(table::MAXN - 1);
        vector<int> expected;
        for (int x = 0; x < table::MAXN; x++)
        {
            bool prime = trial(x);
            if (table::notprime[x] == prime) return 1;
            if ((x >= 2 && sieve.lp[x] == x) != prime) return 2;
            if (prime) expected.push_back(x);
        }
        if (sieve.prime != expected) return 3;
        int count = upper_bound(expected.begin(), expected.end(), list_source::MAXN) - expected.begin();
        if (list_source::prime[0] != count) return 4;
        for (int i = 1; i <= count; i++)
            if (list_source::prime[i] != expected[i - 1]) return 5;
    }
    for (int n : {0, 1, 2, 3, 4, 97, 10000})
    {
        LinearSieve sieve(n);
        vector<int> expected;
        for (int x = 0; x <= n; x++)
        {
            if ((x >= 2 && sieve.lp[x] == x) != trial(x)) return 6;
            if (trial(x)) expected.push_back(x);
        }
        if (sieve.prime != expected) return 7;
    }
    cout << "table/list PASS\n";
    return 0;
}
'''
    header = '#include "' + str(ROOT / 'src/compact/number_theory.hpp') + '"\n'
    for name, code, extra in [('header', header, ()), ('ndebug', header, ('-DNDEBUG',)),
                              ('copied', components['LinearSieve']['code'], ())]:
        assert compile_run('table-' + name, prelude + code + '\n' + source_headers + checks,
                           extra=extra) == 'table/list PASS\n'

    # Reuse only the independent oracle function definitions, not the old runner.
    tree = ast.parse((ROOT / 'tests/prime_distance_application.py').read_text())
    oracle = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)], type_ignores=[])
    scope = {}
    exec(compile(oracle, '<prime-distance-oracle>', 'exec'), scope)
    cases = [(2, 17), (14, 17), (1, 2), (1, 3), (3, 13), (24, 28),
             (2147483646, 2147483647), (2146483647, 2147483647),
             (1, 1000001), (999900, 1000100)]
    rng = random.Random(2689)
    for _ in range(200):
        l = rng.randrange(1, 2147480000)
        cases.append((l, l + rng.randrange(1, 1000)))
    expected = ''.join(scope['answer'](l, r) + '\n' for l, r in cases)
    data = ''.join(f'{l} {r}\n' for l, r in cases)
    original = prelude + (fixture / 'distance.cpp').read_text()
    assert compile_run('original-distance', original, data) == expected
    row = next(r for r in records() if r['driver'] == 'verify/poj/2689.compact.cpp')
    driver = (ROOT / row['driver']).read_text().replace('../../src/compact/', str(ROOT / 'src/compact') + '/')
    bundle = output / 'expanded.cpp'
    subprocess.run([sys.executable, str(ROOT / 'tools/bundle.py'), row['driver'], str(bundle)], cwd=ROOT, check=True)
    copied = candidate(row, row['requires'], components)['program']
    programs = [('header', driver, ()), ('ndebug', driver, ('-DNDEBUG',)),
                ('expanded', bundle.read_text(), ()), ('copied', copied, ())]
    for name, code, extra in programs:
        assert compile_run('distance-' + name, code, data, extra) == expected
    assert snapshot == {str(p.relative_to(ROOT)): digest(p) for p in paths}
    report = dict(mode=mode, compiler=CXX, flags=flags, source_sha256=snapshot,
                  table_domain=[0, 1000009], table_repetitions=2,
                  table_forms=['header', 'ndebug', 'copied'],
                  list_domain=[0, 10000], distance_cases=len(cases),
                  distance_forms=['original-global-main', 'header', 'ndebug', 'expanded', 'copied'],
                  oracle='trial division for full tables; deterministic 32-bit Miller-Rabin for interval outputs',
                  online_verdict=None, passed=True)
    (ROOT / 'verification' / ('prime-source-' + mode + '.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
