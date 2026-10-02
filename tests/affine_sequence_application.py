#!/usr/bin/env python3
"""Independent literal-list checks of the full dynamic affine-sequence driver."""
from compiler_config import CXX
from pathlib import Path
import datetime
import hashlib
import json
import os
import random
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records, expand

MOD = 998244353
DRIVER = ROOT / 'verify/library_checker/dynamic_sequence_range_affine_range_sum.compact.cpp'
SAN = os.environ.get('SANITIZE', os.environ.get('CPC_SANITIZE', '0')) == '1'
MODE = 'sanitizer' if SAN else 'normal'
OUT = ROOT / 'build' / ('affine-sequence-application-' + MODE)
OUT.mkdir(parents=True, exist_ok=True)
sha = lambda data: hashlib.sha256(data).hexdigest()


def make(initial, operations, label):
    a = initial[:]
    answer = []
    for op in operations:
        t = op[0]
        if t == 0:
            _, i, x = op
            assert 0 <= i <= len(a) and 0 <= x < MOD
            a.insert(i, x)
        elif t == 1:
            assert 0 <= op[1] < len(a)
            a.pop(op[1])
        else:
            l, r = op[1:3]
            assert 0 <= l < r <= len(a)
            if t == 2:
                a[l:r] = a[l:r][::-1]
            elif t == 3:
                b, c = op[3:]
                assert 0 <= b < MOD and 0 <= c < MOD
                a[l:r] = [(b * x + c) % MOD for x in a[l:r]]
            else:
                assert t == 4
                answer.append(str(sum(a[l:r]) % MOD))
    data = (f'{len(initial)} {len(operations)}\n' + ' '.join(map(str, initial)) + '\n'
            + '\n'.join(' '.join(map(str, op)) for op in operations) + '\n')
    return label, data, ''.join(x + '\n' for x in answer)


def cases():
    yield make([0], [[1, 0], [0, 0, MOD - 1], [1, 0]], 'erase-reinsert-no-output')
    yield make([1, 2, 3, 4], [[3, 0, 4, 2, 3], [3, 0, 4, 5, 7], [2, 0, 4],
                            [4, 0, 1], [4, 1, 3], [3, 1, 3, 0, MOD - 1],
                            [0, 2, 0], [1, 0], [4, 0, 4]], 'composition-position-boundaries')
    rng = random.Random(21420261002)
    for trial in range(240):
        initial = [rng.choice([0, 1, MOD - 1, rng.randrange(MOD)]) for _ in range(1 + trial % 40)]
        n = len(initial)
        ops = []
        for step in range(240):
            kind = rng.randrange(5) if n else 0
            if kind == 0:
                pos = rng.choice([0, n, rng.randrange(n + 1)])
                ops.append([0, pos, rng.choice([0, 1, MOD - 1, rng.randrange(MOD)])])
                n += 1
            elif kind == 1:
                ops.append([1, rng.choice([0, n - 1, rng.randrange(n)])])
                n -= 1
            else:
                l = rng.randrange(n)
                r = rng.randrange(l + 1, n + 1)
                if step % 7 == 0:
                    l, r = 0, n
                op = [kind, l, r]
                if kind == 3:
                    op += [rng.choice([0, 1, MOD - 1, rng.randrange(MOD)]) for _ in range(2)]
                ops.append(op)
        if n:
            ops += [[4, 0, n], [4, 0, 1], [4, n - 1, n]]
        yield make(initial, ops, f'random-{trial}')


row = next(r for r in records() if r['id'] == 'example-214')
programs = {'standalone': expand(DRIVER.read_text(), DRIVER.parent, set()), 'printed': row['program']}
flags = ['-std=c++20', '-O2'] if not SAN else ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
env = os.environ.copy()
if SAN:
    env.setdefault('ASAN_OPTIONS', 'detect_leaks=0:halt_on_error=1')
    env.setdefault('UBSAN_OPTIONS', 'halt_on_error=1:print_stacktrace=1')
report = {'status': 'running', 'mode': MODE, 'scope': 'Literal-list full-driver oracle; not online AC or maximum-size evidence',
          'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'script_sha256': sha(Path(__file__).read_bytes()), 'driver_sha256': sha(DRIVER.read_bytes()),
          'printed_program_sha256': row['program_sha256'], 'compiler': subprocess.check_output([CXX, '--version'], text=True),
          'flags': flags, 'environment': {k: env.get(k) for k in ['ASAN_OPTIONS', 'UBSAN_OPTIONS']}, 'programs': {}}
path = OUT / 'report.json'
def save():
    path.write_text(json.dumps(report, indent=2) + '\n')

save()
try:
    for form, source in programs.items():
        cpp, exe = OUT / (form + '.cpp'), OUT / form
        cpp.write_text(source)
        subprocess.run([CXX, *flags, str(cpp), '-o', str(exe)], check=True)
        info = {'source_sha256': sha(source.encode()), 'binary_sha256': sha(exe.read_bytes()), 'cases': []}
        report['programs'][form] = info
        for label, data, expected in cases():
            started = time.monotonic()
            result = subprocess.run([str(exe)], input=data, capture_output=True, text=True, env=env, timeout=60)
            item = {'case': label, 'input_sha256': sha(data.encode()), 'expected_sha256': sha(expected.encode()),
                    'actual_sha256': sha(result.stdout.encode()), 'returncode': result.returncode,
                    'stderr': result.stderr, 'wall_seconds': round(time.monotonic() - started, 6)}
            info['cases'].append(item)
            if result.returncode or result.stderr or result.stdout != expected:
                (OUT / 'failed.in').write_text(data)
                (OUT / 'failed.expected').write_text(expected)
                (OUT / 'failed.actual').write_text(result.stdout)
                raise AssertionError((form, label, result.returncode, result.stderr))
            save()
    assert sha(DRIVER.read_bytes()) == report['driver_sha256']
    assert next(r for r in records() if r['id'] == 'example-214')['program_sha256'] == report['printed_program_sha256']
    report['status'] = 'passed'
except Exception as error:
    report['status'] = 'failed'
    report['error'] = repr(error)
    raise
finally:
    report['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save()
print(f'Affine sequence {MODE}: 242 literal-list datasets per standalone/printed program PASS; {path}')
