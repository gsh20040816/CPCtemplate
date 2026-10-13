"""Audit the WIDA basic-algorithm printout."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-basic.md').read_bytes()
fix = root / 'tests/fixtures/wida_basicprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '227a378410344eba94b973647318d2311fdbfb8d'
text = blob.decode().replace('\r\n', '\n')
fences = [part.split('\n', 1)[1] for part in text.split('```')[1::2]]
header, helpers, logs, divs, mygcd, succ, pred, newsucc, newpred, realbin, tern, realtern = fences
assert 'return b ? gcd(b, a % b) : a;' in mygcd
assert '无法处理负数' in text
out = root / 'build/wida-basicprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')

def build(name, code, flags):
    path = out / (name + '.cpp')
    path.write_text(code)
    exe = out / name
    subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], check=True)
    return exe

(out / 'header.cpp').write_text(header)
body = r'''
#include <bits/stdc++.h>
#include <cassert>
using namespace std;
using i64 = long long;
''' + helpers + logs + divs + mygcd + r'''
static int successor(const vector<int> &a, int x) {
    int l = 0, r = (int)a.size() - 1;
''' + '\n'.join('    ' + line for line in succ.splitlines()) + r'''
}
static int predecessor(const vector<int> &a, int x) {
    int l = 0, r = (int)a.size() - 1;
''' + '\n'.join('    ' + line for line in pred.splitlines()) + r'''
}
static int newsucc(int goal) {
    auto judge = [&](int mid) { return mid >= goal; };
''' + '\n'.join('    ' + line for line in newsucc.splitlines()) + r'''
}
static int newpred(int goal) {
    auto judge = [&](int mid) { return mid <= goal; };
''' + '\n'.join('    ' + line for line in newpred.splitlines()) + r'''
}
static long double real_sqrt2() {
    long double l = 0, r = 2;
    auto judge = [&](long double mid) { return mid * mid >= 2; };
    using ld = long double;
''' + '\n'.join('    ' + line if not line.startswith('cout') else '    return l;' for line in realbin.splitlines()) + r'''
}
static int ternary_at() {
    auto check = [&](int x) { return (x - 3) * (x - 3); };
    int l = 0, r = 10;
''' + '\n'.join('    ' + line if not line.startswith('cout') else '    return l;' for line in tern.splitlines()) + r'''
}
static long double real_min() {
    auto judge = [&](long double x) { long double d = x - 1.5L; return d * d; };
    using ld = long double;
''' + '\n'.join('    ' + line if not line.startswith('cout') else '    return l;' for line in realtern.splitlines()) + r'''
}
int main(int argc, char **argv) {
    string mode = argc > 1 ? argv[1] : "ok";
    if (mode == "sqrtmax") { cout << mysqrt(LLONG_MAX) << '\n'; return 0; }
    if (mode == "log0") { cout << log2floor(0) << '\n'; return 0; }
    if (mode == "div0") { cout << floor(5, 0) << '\n'; return 0; }
    if (mode == "lcm") { cout << mylcm(100000, 100003) << '\n'; return 0; }
    for (i64 n = 0; n <= 5000; n++) {
        i64 s = mysqrt(n);
        if (s < 0 || s * s > n || (s + 1) * (s + 1) <= n) return 1;
    }
    vector<int> a = {-5, -1, 3};
    if (successor(a, -2) != -1 || predecessor(a, -2) != -5) return 1;
    if (successor(a, 4) != 3 || predecessor(a, -9) != -5) return 1;
    if (newsucc(5) != 5 || newpred(5) != 5) return 1;
    long double s2 = real_sqrt2();
    if (s2 < 1.414213 || s2 > 1.414214) return 1;
    if (ternary_at() != 3) return 1;
    long double best = real_min();
    if (best < 1.499 || best > 1.501) return 1;
    if (floor(5, 2) != 2 || floor(-5, 2) != -3 || ceil(5, 2) != 3 || ceil(-5, 2) != -2) return 1;
    if (log2floor<long long>(8) != 3 || log2ceil<long long>(3) != 2) return 1;
    if (log2floor(8) != 3 || log2ceil(3) != 2 || log2ceil(8) != 3) return 1;
    if (mygcd(15, 25) != 5 || mygcd(0, 5) != 5 || mygcd(-4, 6) != 2) return 1;
    if (mylcm(4, 6) != 12) return 1;
    cout << "ok\n";
}
'''
(out / 'body.cpp').write_text(body)
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = build('body-' + mode, body, flags) if False else None
    exe = out / ('body-' + mode)
    subprocess.run([CXX, '-std=c++20', *flags, str(out / 'body.cpp'), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == 'ok\n'
    prog = out / ('header-' + mode)
    subprocess.run([CXX, '-std=c++20', *flags, str(out / 'header.cpp'), '-o', str(prog)], check=True)
    for raw in ['', '0\n', '4\n']:
        run = subprocess.run([str(prog)], input=raw, text=True, capture_output=True, env=env, timeout=30, check=True)
        assert run.stderr == '' and run.stdout == ''
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
ub = out / 'ub'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(out / 'body.cpp'), '-o', str(ub)], check=True)
sqrtmax = subprocess.run([str(ub), 'sqrtmax'], text=True, capture_output=True, env=env, timeout=30)
log0 = subprocess.run([str(ub), 'log0'], text=True, capture_output=True, env=env, timeout=30)
div0 = subprocess.run([str(ub), 'div0'], text=True, capture_output=True, env=env, timeout=30)
lcm = subprocess.run([str(ub), 'lcm'], text=True, capture_output=True, env=env, timeout=30)
assert sqrtmax.returncode != 0 and 'signed integer overflow' in sqrtmax.stderr
assert log0.returncode != 0 and 'clz' in log0.stderr
assert div0.returncode != 0
assert lcm.returncode != 0 and 'signed integer overflow' in lcm.stderr
report.append(dict(
    sqrtmax=sqrtmax.stderr.strip().splitlines()[-1],
    log0=log0.stderr.strip().splitlines()[-1],
    lcm=lcm.stderr.strip().splitlines()[-1],
))
print('bounds PASS', flush=True)
import json
(root / 'verification/wida-basicprint.json').write_text(json.dumps(dict(
    scope='mysqrt matches through 5000. Old binary search handles the checked negative array values; a too-large query returns the last element. New search finds 5. Real binary is near sqrt(2), integer ternary finds 3, and real ternary is near 1.5. floor and ceil match. log2 matches the checked powers. mygcd forwards to std::gcd. The header program exits on empty, 0 and 4. LLONG_MAX square root, log2(0) and a large lcm overflow or are invalid. No online AC.',
    blob='227a378410344eba94b973647318d2311fdbfb8d', runs=report), indent=2) + '\n')
