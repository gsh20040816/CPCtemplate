"""Audit the WIDA 0-based TwoSat against exhaustive assignments and the library."""
import hashlib, itertools, os, random, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = (root / 'tests/fixtures/wida_twosat/main.cpp').read_bytes()
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '3964b5b9bdd16bc9de0e3558078d13691617bda4'
text = blob.decode().replace('\r\n', '\n')
assert 'addClause(int u, bool f, int v, bool g)' in text
assert 'ans[i] = id[2 * i] > id[2 * i + 1]' in text

def brute(n, clauses):
    good = []
    for mask in range(1 << n):
        values = [(mask >> i) & 1 for i in range(n)]
        if all(values[u] == f or values[v] == g for u, f, v, g in clauses):
            good.append(values)
    return good

rng = random.Random(5)
cases = [
    (0, []),
    (1, []),
    (1, [(0, 1, 0, 1)]),
    (1, [(0, 0, 0, 0)]),
    (1, [(0, 1, 0, 1), (0, 0, 0, 0)]),
    (2, [(0, 1, 1, 1), (0, 0, 1, 0), (1, 1, 0, 0)]),
]
for _ in range(80):
    n = rng.randrange(0, 11)
    clauses = []
    for _k in range(rng.randrange(0, 16)):
        clauses.append((rng.randrange(n) if n else 0, rng.randrange(2), rng.randrange(n) if n else 0, rng.randrange(2)))
    if n == 0:
        clauses = []
    cases.append((n, clauses))

lines = [str(len(cases))]
for n, clauses in cases:
    lines.append(f'{n} {len(clauses)}')
    lines += [f'{u} {f} {v} {g}' for u, f, v, g in clauses]
payload = '\n'.join(lines) + '\n'
out = root / 'build/wida-twosat'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_twosat.cpp'
report = []
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], input=payload, text=True, capture_output=True, env=env, timeout=60, check=True)
    assert got.stderr == ''
    rows = got.stdout.splitlines()
    assert len(rows) == len(cases)
    checks = 0
    for row, (n, clauses) in zip(rows, cases):
        parts = list(map(int, row.split()))
        first, second, known = parts[:3]
        assert parts[3] == n
        bits = parts[4::2]
        again = parts[5::2]
        assert bits == again and first == second
        good = brute(n, clauses)
        assert first == known
        if good:
            assert first == 1 and bits in good
        else:
            assert first == 0
        checks += 1 + n
    report.append(dict(mode=mode, cases=len(cases), checks=checks))
    print(mode, checks, 'checks PASS', flush=True)

import json
(root / 'verification/wida-twosat.json').write_text(json.dumps(dict(
    scope='0-based WIDA TwoSat. Clause (u==f or v==g). Exhaustive assignments through n=10 and the existing 1-based TwoSAT agree on satisfiability. Returned bits must satisfy the clauses; they are not required to equal another solver. No online AC.',
    blob='3964b5b9bdd16bc9de0e3558078d13691617bda4', runs=report), indent=2) + '\n')
