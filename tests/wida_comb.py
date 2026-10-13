"""Audit the WIDA small binomial table and the mod-7 prefix sums."""
import hashlib, math, os, random, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-comb.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_comb'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'a4516bc3dc14a2b13b381606f30dc6c778dff976'
text = blob.decode().replace('\r\n', '\n')
assert 'constexpr int L = 10000;' in text
assert 'sumbinom[i - 1][(j + 6) % 7]' in text
body = text.replace('int main()', 'int init_all()', 1).rstrip()
body = body[:body.rfind('}')] + '\n    return 0;\n}\n'
source = body + r'''
#include <bits/stdc++.h>
int main() {
    init_all();
    int q; std::cin >> q;
    while (q--) {
        int n, m; std::cin >> n >> m;
        std::cout << binom(n, m) << '\n';
    }
    std::cout << fac[10] << ' ' << (1LL * fac[10] * invfac[10] % P) << '\n';
    for (int i = 0; i <= 40; i++) {
        for (int j = 0; j < 7; j++) std::cout << sumbinom[i][j] << (j == 6 ? '\n' : ' ');
    }
}
'''
out = root / 'build/wida-comb'
out.mkdir(parents=True, exist_ok=True)
(out / 'main.cpp').write_text(source)
P = 1000000007
queries = [(0, 0), (5, 0), (5, 1), (5, 2), (5, 5), (5, 6), (10, -1), (3, 5), (10000, 0), (10000, 5000)]
rng = random.Random(12)
for _ in range(30):
    n = rng.randrange(0, 10001)
    m = rng.randrange(-2, n + 3)
    queries.append((n, m))
lines = [str(len(queries))] + [f'{n} {m}' for n, m in queries]
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(out / 'main.cpp'), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], input='\n'.join(lines) + '\n', text=True, capture_output=True, env=env, timeout=60, check=True)
    assert got.stderr == ''
    rows = got.stdout.splitlines()
    for row, (n, m) in zip(rows, queries):
        expect = 0 if n < m or m < 0 else math.comb(n, m) % P
        assert int(row) == expect
    fac10, prod = map(int, rows[len(queries)].split())
    assert fac10 == math.factorial(10) % P and prod == 1
    table = [list(map(int, line.split())) for line in rows[len(queries) + 1:]]
    assert len(table) == 41
    manual = [[0] * 7 for _ in range(41)]
    manual[0][0] = 1
    for i in range(1, 41):
        for j in range(7):
            manual[i][j] = (manual[i - 1][j] + manual[i - 1][(j + 6) % 7]) % P
            expect = sum(math.comb(i, k) for k in range(j, i + 1, 7)) % P
            assert manual[i][j] == expect
    assert table == manual
    report.append(dict(mode=mode, queries=len(queries)))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-comb.json').write_text(json.dumps(dict(
    scope='Factorials and binomial coefficients modulo 1000000007 for n<=10000. sumbinom[n][j] is the sum of C(n,k) over k congruent to j mod 7. n above 10000 is not tested. No online AC.',
    blob='a4516bc3dc14a2b13b381606f30dc6c778dff976', runs=report), indent=2) + '\n')
