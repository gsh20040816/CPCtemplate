"""Audit the exact WIDA fragment in the original Gaussian-binomial caller."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/q-int'
OUT.mkdir(parents=True, exist_ok=True)
fixture = ROOT / 'tests/fixtures/wida_q_int/13A.cpp'
raw = fixture.read_bytes()
blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
assert blob == '1e9fba7eaa91e176b6e53d6d80d8514d767a7909'
# Same arithmetic and loop as the original main shown by QOJ 163986.
# Batch framing is solely for the local test harness.
caller = r'''
int main()
{
    int q, n, k, p;
    while (std::cin >> q >> n >> k >> p)
    {
        int num = 1;
        int den = 1;
        int e = 0;
        for (int i = 1; i <= k; i++)
        {
            auto [v1, e1] = qint(q, n - i + 1, p);
            num = 1LL * num * v1 % p;
            e += e1;
            auto [v2, e2] = qint(q, i, p);
            den = 1LL * den * v2 % p;
            e -= e2;
        }
        int ans;
        if (e)
        {
            ans = 0;
        }
        else
        {
            ans = 1LL * num * power(den, p - 2, p) % p;
        }
        std::cout << ans << '\n';
    }
}
'''
source = '#include <bits/stdc++.h>\n#include <cassert>\n' + raw.decode() + caller
cpp = OUT / 'original-caller.cpp'
cpp.write_text(source)
exe = OUT / 'original-caller'
subprocess.run([CXX, '-std=c++20', '-O2', str(cpp), '-o', str(exe)], check=True)

def exact(q, n, k):
    # Count ordered independent bases, then divide by the bases per subspace.
    numerator = 1
    denominator = 1
    for i in range(k):
        numerator *= q ** n - q ** i
        denominator *= q ** k - q ** i
    assert numerator % denominator == 0
    return numerator // denominator

cases = [(2, 3, 2, 100003), (3, 2, 2, 2), (3, 3, 2, 2),
         (7, 3, 3, 3), (2, 6, 3, 3)]
data = ''.join(' '.join(map(str, c)) + '\n' for c in cases)
result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True)
actual = list(map(int, result.stdout.split()))
want = [exact(q, n, k) % p for q, n, k, p in cases]
assert actual[0] == want[0] == 7
assert actual[1] == 0 and want[1] == 1
report = {
    'source_blob': blob,
    'original_submission': 'https://qoj.ac/submission/163986',
    'observed_verdict': 'TL',
    'problem': 'https://qoj.ac/contest/1341/problem/4281',
    'source_cases': [dict(input=list(c), original=a, exact=w)
                     for c, a, w in zip(cases, actual, want)],
    'scope': 'Exact source fragment plus original arithmetic caller; not an online submission.',
    'replacement_runs': []
}
primes = [2, 3, 5, 7, 11, 17, 31]
checks = [(q, n, k, p) for q in primes for p in primes
          for n in range(1, 11) for k in range(1, n + 1)]
checks = cases + checks
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
           UBSAN_OPTIONS='halt_on_error=1')
for mode, flags in [('normal', ['-O2', '-DNDEBUG']),
                    ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = OUT / ('replacement-' + mode)
    subprocess.run([CXX, '-std=c++20', *flags,
                    str(ROOT / 'verify/qoj/4281.compact.cpp'), '-o', str(exe)], check=True)
    for q, n, k, p in checks:
        r = subprocess.run([str(exe)], input=f'{q} {n} {k} {p}\n', text=True,
                           capture_output=True, env=env, timeout=5)
        assert r.returncode == 0 and not r.stderr, r.stderr
        assert int(r.stdout) == exact(q, n, k) % p, (q, n, k, p, r.stdout)
    report['replacement_runs'].append(dict(mode=mode, exact_cases=len(checks)))
    print(mode, len(checks), 'exact subspace counts PASS', flush=True)
report['files'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in [
    'tests/fixtures/wida_q_int/13A.cpp', 'tests/wida_q_int.py',
    'verify/qoj/4281.compact.cpp', 'src/compact/q_binomial.hpp']}
(ROOT / 'verification/wida-q-int.json').write_text(json.dumps(report, indent=2) + '\n')
