#!/usr/bin/env python3
"""Full-uint64 helper API: independent Python integers and actual copy context."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot
from usage_examples import records
from audit_copy_context import extract_components
from compiler_config import CXX


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if not __debug__:
        raise RuntimeError('Run reference checks without Python optimization')
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='mod64-' + mode + '-', dir=ROOT / 'build'))
    before = snapshot(ROOT)
    row = next(r for r in records() if r['id'] == 'example-234')
    cat = json.loads((ROOT / 'docs/catalog.json').read_text())
    component = next(r for r in extract_components(cat) if r['symbol'] == 'Mod64')
    copy = ('#include <cassert>\n#include <iostream>\nusing namespace std;\n'
            + component['code'] + '\n' + row['snippet'])
    maximum = (1 << 64) - 1
    triples = [(a, b, m) for m in range(1, 25)
               for a in range(25) for b in range(25)]
    special = [0, 1, 2, 3, (1 << 32) - 1, 1 << 32,
               (1 << 63) - 1, 1 << 63, (1 << 63) + 1, maximum - 1, maximum]
    triples += [(a, b, m) for a in special for b in special for m in special if m]
    rng = random.Random(20261003)
    triples += [(rng.getrandbits(64), rng.getrandbits(64),
                 rng.randrange(1, maximum + 1)) for _ in range(20000)]
    # A full-q boundary file, including every one-bit exponent and modulus.
    boundary = [(maximum - i % 2, 1 << (i % 64), 1 << ((i // 64) % 64))
                for i in range(200000)]
    def encode(rows):
        data = str(len(rows)) + '\n' + ''.join(f'{a} {b} {m}\n' for a,b,m in rows)
        expected = ''.join(f'{a*b % m} {pow(a,b,m)}\n' for a,b,m in rows)
        return data.encode(), expected.encode()
    cases = [('empty', *encode([])), ('exhaustive-boundary-random', *encode(triples)),
             ('maximum-query-count', *encode(boundary))]
    # Independently check the small Python pow reference by repeated multiplication.
    for a, b, m in triples[:15000]:
        value = 1 % m
        for _ in range(b):
            value = value * a % m
        assert value == pow(a, b, m)
    flags = ['-std=c++20', '-Wall', '-Wextra']
    flags += (['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
              if mode == 'sanitizer' else ['-O2'])
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                   UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    report = dict(mode=mode, source_before_sha256=before, flags=flags,
                  compiler=str(compiler),
                  compiler_sha256=sha(compiler.read_bytes()),
                  environment={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')},
                  cases=[], programs=[], negative_controls=[],
                  scope='Local exact integer reference checks; API demo only. No OJ, full-suite or LeakSanitizer certification.')
    for name, data, expected in cases:
        (out / (name + '.in')).write_bytes(data)
        (out / (name + '.expected')).write_bytes(expected)
        report['cases'].append(dict(name=name, input_sha256=sha(data), expected_sha256=sha(expected)))
    forms = [('direct', '#include "' + str(ROOT / row['driver']) + '"\n'),
             ('expanded', row['program']), ('copy', copy)]
    for form, source in forms:
        for ndebug in (False, True):
            name = form + ('-ndebug' if ndebug else '-assert')
            cpp, exe = out / (name + '.cpp'), out / name
            cpp.write_text(source + '\nstatic_assert(sizeof(unsigned long long) == 8);\n')
            cmd = [CXX, *flags, *(['-DNDEBUG'] if ndebug else []), str(cpp), '-o', str(exe)]
            subprocess.run(cmd, check=True, capture_output=True)
            entry = dict(name=name, command=cmd, source_sha256=sha(cpp.read_bytes()),
                         binary_sha256=sha(exe.read_bytes()), runs=[], invalid=[])
            for case, data, expected in cases:
                run = subprocess.run([str(exe)], input=data, capture_output=True, env=env, timeout=90)
                assert run.returncode == 0 and not run.stderr, (name, case, run.returncode, run.stderr)
                assert run.stdout == expected, (name, case)
                (out / (name + '-' + case + '.out')).write_bytes(run.stdout)
                entry['runs'].append(dict(case=case, returncode=run.returncode, output_sha256=sha(run.stdout)))
            invalid = [(data, b'') for data in (
                b'', b'-1\n', b'200001\n', b'1\n1 2 0\n', b'1\n1 2\n',
                b'1\n18446744073709551616 1 7\n',
                b'1\n1 18446744073709551616 7\n',
                b'1\n1 1 18446744073709551616\n')]
            invalid += [(b'2\n3 2 7\n' + suffix, b'6 2\n')
                        for suffix in (b'1 2 0\n', b'1 2\n', b'x 1 7\n')]
            for data, expected_prefix in invalid:
                run = subprocess.run([str(exe)], input=data, capture_output=True, env=env, timeout=10)
                assert run.returncode == 1 and run.stdout == expected_prefix and not run.stderr
                entry['invalid'].append(dict(input=data.decode(), returncode=run.returncode,
                                            output=run.stdout.decode()))
            report['programs'].append(entry)
    # Overflow-before-promotion and identity/bit-coverage mistakes must be observable.
    mutants = [('multiply-before-cast', 'u128(a) * b % m', 'u128(a * b) % m'),
               ('unreduced-identity', 'ull r = 1 % m;', 'ull r = 1;'),
               ('truncate-exponent', 'a %= m;', 'a %= m; b = (unsigned)b;')]
    for name, old, new in mutants:
        assert copy.count(old) == 1
        cpp, exe = out / (name + '.cpp'), out / name
        cpp.write_text(copy.replace(old, new))
        subprocess.run([CXX, *flags, str(cpp), '-o', str(exe)], check=True, capture_output=True)
        run = subprocess.run([str(exe)], input=cases[1][1], capture_output=True, env=env, timeout=90)
        assert run.returncode == 0 and not run.stderr
        assert run.stdout != cases[1][2], name
        report['negative_controls'].append(dict(name=name, rejected=True,
            source_sha256=sha(cpp.read_bytes()), binary_sha256=sha(exe.read_bytes()),
            output_sha256=sha(run.stdout)))
    report.update(source_after_sha256=snapshot(ROOT), finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), passed=True)
    assert before == report['source_after_sha256']
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Mod64 {mode}: {len(triples)} exact triples + 200000-query boundary x six program forms PASS; {out.relative_to(ROOT)}/report.json')


if __name__ == '__main__':
    main()
