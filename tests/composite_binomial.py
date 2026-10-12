from pathlib import Path
import hashlib
import json
import math
import os
import random
import subprocess
import sys
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/wida-binomial'
OUT.mkdir(parents=True, exist_ok=True)
raw = (ROOT / 'tests/fixtures/wida_composite_binomial/13C.cpp').read_bytes()
blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
assert blob == 'dc2eacad3e2e7eb6206c3fb9f9bc02d382bc3f60'
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
           UBSAN_OPTIONS='halt_on_error=1')
report = {'source_blob': blob, 'online_ac': False, 'runs': []}
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records
printed = {}
for row in records():
    if row['id'] in ['example-445', 'example-446']:
        assert (ROOT / row['snippet_file']).read_text() == row['snippet']
        path = OUT / (row['id'] + '.cpp')
        path.write_text(row['program'])
        printed[row['id']] = str(path)
report['printed_program_sha256'] = {
    name: hashlib.sha256(Path(path).read_bytes()).hexdigest()
    for name, path in printed.items()
}
rng = random.Random(896)
mods = [1, 2, 4, 8, 9, 16, 25, 27, 30, 97, 256, 1000, 65536,
        1000003, 1000000007, 1073741824, 1162261467, 1220703125,
        2000000000, 2147483647, 223092870]
mods += [rng.randrange(1, 2147483648) for _ in range(20)]
cases = [(0, 0), (1, 0), (1, 1), (-1, 0), (5, -1), (5, 6)]
cases += [(rng.randrange(0, 1001), rng.randrange(0, 1001)) for _ in range(100)]
cases += [(100000, k) for k in [0, 1, 2, 3, 7, 15, 20, 99980, 99999, 100000]]
cases += [(1000, 500), (999, 499)]
cinema = [(4, 97, 2, 3), (4, 100, 0, 4)]
cinema += [(n, rng.choice(mods), *sorted([rng.randrange(n + 1), rng.randrange(n + 1)]))
           for n in range(1, 41)]

def cinema_oracle(n, mod, l, r):
    row = [1] + [0] * n
    for _ in range(n):
        nxt = [0] * (n + 1)
        for h, count in enumerate(row):
            for d in [-1, 0, 1]:
                if 0 <= h + d <= n:
                    nxt[h + d] += count
        row = nxt
    return sum(row[l:r + 1]) % mod

for mode, flags in [('normal', ['-O2', '-DNDEBUG']),
                    ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    for kind, source in [('core', 'tests/composite_binomial.cpp'),
                         ('api', 'verify/api/composite_binomial.compact.cpp'),
                         ('cinema', 'verify/cf/896D.compact.cpp'),
                         ('api-printed', printed['example-445']),
                         ('cinema-printed', printed['example-446'])]:
        exe = OUT / (kind + '-' + mode)
        subprocess.run([CXX, '-std=c++20', *flags, str(ROOT / source), '-o', str(exe)], check=True)
        def run(data=''):
            r = subprocess.run([str(exe)], input=data, text=True, capture_output=True,
                               env=env, timeout=60)
            assert r.returncode == 0 and not r.stderr, r.stderr
            return r.stdout
        if kind == 'core':
            result = run().strip()
        elif kind.startswith('api'):
            for mod in mods:
                data = f'100000 {mod} {len(cases)}\n' + ''.join(f'{n} {k}\n' for n, k in cases)
                expected = [math.comb(n, k) % mod if 0 <= k <= n else 0 for n, k in cases]
                assert list(map(int, run(data).split())) == expected
            result = f'{len(mods) * len(cases)} Python exact binomial queries PASS'
        else:
            for n, mod, l, r in cinema:
                assert int(run(f'{n} {mod} {l} {r}\n')) == cinema_oracle(n, mod, l, r)
            for mod in [1, 223092870, 2000000000, 2147483647]:
                assert int(run(f'100000 {mod} 100000 100000\n')) == 1 % mod
            result = f'{len(cinema)} independent nonnegative-walk DP cases and four large endpoints PASS'
        report['runs'].append(dict(mode=mode, kind=kind, result=result))
        print(mode, kind, result, flush=True)

# Original integer power squares base even when the exponent becomes zero.
# This is called by the original constructor for a legal large prime modulus.
probe = OUT / 'source-overflow.cpp'
probe.write_text('#include <bits/stdc++.h>\nusing i64 = long long;\n' + raw.decode() +
                 '\nint main()\n{\n    Binomial b(1000003);\n}\n')
exe = OUT / 'source-overflow'
subprocess.run([CXX, '-std=c++20', '-O1', '-fsanitize=undefined', str(probe), '-o', str(exe)], check=True)
r = subprocess.run([str(exe)], capture_output=True, text=True, env=env)
assert r.returncode != 0 and 'signed integer overflow' in r.stderr, r.stderr
report['original_undefined_behavior'] = r.stderr
report['files'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in [
    'src/compact/composite_binomial.hpp', 'tests/composite_binomial.cpp',
    'tests/composite_binomial.py', 'tests/fixtures/wida_composite_binomial/13C.cpp',
    'verify/api/composite_binomial.compact.cpp', 'verify/cf/896D.compact.cpp']}
(ROOT / 'verification/composite-binomial.json').write_text(json.dumps(report, indent=2) + '\n')
