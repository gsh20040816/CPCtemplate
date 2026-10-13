"""Audit the two WIDA linear sieves separately."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-sieve.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_sieve'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '0bd397ab79b5ae363938682c46d3274167a621d0'
text = blob.decode().replace('\r\n', '\n')
mark = text.index('/**   欧拉筛\n *    2023-03-22:')
basic, phi = text[:mark], text[mark:]
assert basic.count('void sieve') == 1 and phi.count('void sieve') == 1
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-sieve-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-sieve'
out.mkdir(parents=True, exist_ok=True)
(out / 'basic.cpp').write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + basic + r'''
int main() {
    int n; cin >> n; sieve(n);
    cout << primes.size();
    if (n >= 1) cout << ' ' << isprime(1);
    if (n >= 2) cout << ' ' << isprime(2) << ' ' << isprime(n);
    cout << '\n';
    for (int i = 2; i <= n; i++) cout << minp[i] << (i == n ? '\n' : ' ');
}
''')
(out / 'phi.cpp').write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + phi + r'''
int main() {
    int n; cin >> n; sieve(n);
    cout << primes.size() << ' ' << phi[1] << '\n';
    for (int i = 1; i <= n; i++) cout << phi[i] << (i == n ? '\n' : ' ');
}
''')

def ref(n):
    prime = [True] * (n + 1)
    primes, minp = [], [0] * (n + 1)
    phi = [0] * (n + 1)
    if n >= 1:
        phi[1] = 1
    for i in range(2, n + 1):
        if prime[i]:
            primes.append(i)
            minp[i] = i
            phi[i] = i - 1
        for p in primes:
            if i * p > n:
                break
            prime[i * p] = False
            minp[i * p] = p
            if i % p == 0:
                phi[i * p] = phi[i] * p
                break
            phi[i * p] = phi[i] * (p - 1)
    return primes, minp, phi

env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    basic_exe = out / ('basic-' + mode)
    phi_exe = out / ('phi-' + mode)
    subprocess.run([CXX, '-std=c++20', *flags, str(out / 'basic.cpp'), '-o', str(basic_exe)], check=True)
    subprocess.run([CXX, '-std=c++20', *flags, str(out / 'phi.cpp'), '-o', str(phi_exe)], check=True)
    for n in (0, 1, 2, 30, 100000):
        primes, minp, totient = ref(n)
        got = subprocess.run([str(basic_exe)], input=f'{n}\n', text=True, capture_output=True, env=env, timeout=30, check=True)
        assert got.stderr == ''
        rows = got.stdout.splitlines()
        head = list(map(int, rows[0].split()))
        assert head[0] == len(primes)
        if n >= 1:
            assert head[1] == 0
        if n >= 2:
            assert head[2] == 1 and head[3] == int(minp[n] == n)
            assert list(map(int, rows[1].split())) == minp[2:]
        if n == 0:
            continue
        got = subprocess.run([str(phi_exe)], input=f'{n}\n', text=True, capture_output=True, env=env, timeout=30, check=True)
        assert got.stderr == ''
        rows = got.stdout.splitlines()
        assert list(map(int, rows[0].split())) == [len(primes), 1]
        assert list(map(int, rows[1].split())) == totient[1:]
    report.append(dict(mode=mode, ns=[0, 1, 2, 30, 100000]))
    print(mode, 'PASS', flush=True)
bad = subprocess.run([str(out / 'phi-sanitizer')], input='0\n', text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'AddressSanitizer' in bad.stderr
report.append(dict(phi_n0='writes phi[1]'))
print('phi n=0 overflow recorded', flush=True)
import json
(root / 'verification/wida-sieve.json').write_text(json.dumps(dict(
    scope='Two same-named sieves, so the file does not compile together. Each half matches an independent linear sieve through n=100000, including phi. No near-INT_MAX overflow test and no online AC.',
    blob='0bd397ab79b5ae363938682c46d3274167a621d0', runs=report), indent=2) + '\n')
