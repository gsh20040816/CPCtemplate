"""Audit the executable pieces of the WIDA polynomial printout."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-poly.md').read_bytes()
fix = root / 'tests/fixtures/wida_polyprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
(fix / 'README.md').write_text(
    '# WIDA polynomial-printout fixture\n\n'
    'main.md is the exact CRLF blob `5ccf93566b4e7dce4235e81c670c08a32ffa863b` '
    'from hh2048/XCPC tree `cfdb12db6792eb2303798541fb5c760ed2bc618b`.\n\n'
    'Path: `02 - 打印稿模板汇总/07 - 多项式.md`.\n\n'
    'The upstream GPL-3.0 license is preserved in LICENSE. This fixture is not '
    'relicensed under the root MIT license. See docs/WIDA-POLYPRINT.md.\n'
)
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '5ccf93566b4e7dce4235e81c670c08a32ffa863b'
text = blob.decode().replace('\r\n', '\n')
poly, dft, bm, lin, fft, ntt, lag = [part.split('\n', 1)[1] for part in text.split('```')[1::2]]
out = root / 'build/wida-polyprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
head = '#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\nusing i64 = long long;\nusing LL = long long;\n'
mint = r'''
template<int P> struct MInt {
    int x;
    constexpr MInt(long long v = 0) : x((int)(v % P)) { if (x < 0) x += P; }
    constexpr MInt operator+(MInt o) const { int y = x + o.x; return y >= P ? y - P : y; }
    constexpr MInt operator-(MInt o) const { int y = x - o.x; return y < 0 ? y + P : y; }
    constexpr MInt operator*(MInt o) const { return 1LL * x * o.x % P; }
    constexpr MInt operator/(MInt o) const { return *this * o.inv(); }
    constexpr MInt operator*(long long o) const { return *this * MInt(o); }
    constexpr MInt operator/(long long o) const { return *this / MInt(o); }
    friend constexpr MInt operator*(long long a, MInt b) { return b * a; }
    constexpr MInt& operator+=(MInt o) { return *this = *this + o; }
    constexpr MInt& operator-=(MInt o) { return *this = *this - o; }
    constexpr MInt& operator*=(MInt o) { return *this = *this * o; }
    constexpr MInt operator-() const { return MInt(-x); }
    constexpr bool operator==(MInt o) const { return x == o.x; }
    constexpr MInt inv() const { return power(*this, P - 2); }
    friend ostream& operator<<(ostream& os, MInt a) { return os << a.x; }
};
template<class T> constexpr T power(T a, long long b) {
    T r = 1;
    for (; b; b >>= 1, a *= a) if (b & 1) r *= a;
    return r;
}
template<int V, int P> constexpr MInt<P> CInv = MInt<P>(V).inv();
'''
zntt = r'''
constexpr int mod = 998244353;
struct Z {
    int x;
    Z(long long v = 0) : x((int)(v % mod)) { if (x < 0) x += mod; }
    Z operator+(Z o) const { int y = x + o.x; return y >= mod ? y - mod : y; }
    Z operator-(Z o) const { int y = x - o.x; return y < 0 ? y + mod : y; }
    Z operator*(Z o) const { return 1LL * x * o.x % mod; }
    Z& operator+=(Z o) { return *this = *this + o; }
    Z& operator-=(Z o) { return *this = *this - o; }
    Z& operator*=(Z o) { return *this = *this * o; }
    friend ostream& operator<<(ostream& os, Z a) { return os << a.x; }
};
'''
zlag = r'''
constexpr int mod = 998244353;
struct Z {
    int x;
    Z(long long v = 0) : x((int)(v % mod)) { if (x < 0) x += mod; }
    Z operator+(Z o) const { int y = x + o.x; return y >= mod ? y - mod : y; }
    Z operator-(Z o) const { int y = x - o.x; return y < 0 ? y + mod : y; }
    Z operator*(Z o) const { return 1LL * x * o.x % mod; }
    Z& operator+=(Z o) { return *this = *this + o; }
    Z& operator-=(Z o) { return *this = *this - o; }
    Z& operator*=(Z o) { return *this = *this * o; }
    Z inv() const { long long a = x, b = mod - 2, r = 1; for (; b; b >>= 1, a = a * a % mod) if (b & 1) r = r * a % mod; return r; }
    Z power(long long a, long long b) const { Z r = 1, x = a; for (; b; b >>= 1, x *= x) if (b & 1) r *= x; return r; }
    friend Z operator-(long long a, Z b) { return Z(a) - b; }
    friend ostream& operator<<(ostream& os, Z a) { return os << a.x; }
};
'''
body = r'''
int main() {
    using P = Poly<998244353>;
    auto show = [](const P& a) { for (auto x : a) cout << x << ' '; cout << '\n'; };
    if ((P{} * P{}).size() != 0) return 1;
    show(P{1, 1} * P{1, 1});
    show(P{1, 2, 3}.deriv());
    show(P{1, 2}.integr());
    show(P{1, 1}.inv(4));
    show(P{1, 1}.log(4));
    show(P{0, 1}.exp(4));
    show(P{1, 1}.pow(3, 4));
    show(P{0, 1}.pow(2, 4));
    show(P{1}.sqrt(4));
    show(berlekampMassey(P{1, 1, 2, 3, 5, 8, 13, 21}));
    cout << linearRecurrence(P{0, 1}, P{1, 998244352, 998244352}, 10) << '\n';
    vector<MInt<998244353>> a(128), b(128);
    for (int i = 0; i < 5; i++) a[i] = i + 1, b[i] = 1;
    auto c = P(a) * P(b);
    for (int i = 0; i < 10; i++) {
        long long s = 0;
        for (int j = 0; j <= i && j < 5; j++) if (i - j < 5) s += j + 1;
        if (c[i].x != s) return 1;
    }
    cout << "ok\n";
}
'''
expect = ''.join([
    '1 2 1 \n',
    '2 6 \n',
    '0 1 1 \n',
    '1 998244352 1 998244352 \n',
    '0 1 499122176 332748118 \n',
    '1 1 499122177 166374059 \n',
    '1 3 3 1 \n',
    '0 0 1 0 \n',
    '1 0 0 0 \n',
    '1 998244352 998244352 \n',
    '55\n',
    'ok\n',
])
fftmain = r'''
int main() {
    vector<int> a = {1, 2, 0, 0}, b = {3, 4, 0, 0};
    Polynomial A(a), B(b);
    for (int i = 0; i < 4; i++) A.c[i] = A.c[i] * B.c[i];
    A.fft(A.c, 4, -1);
    for (int i = 0; i < 4; i++) cout << llround(A.c[i].x) << ' ';
    cout << '\n';
}
'''
nttmain = r'''
int main() {
    vector<int> a = {1, 2, 0, 0}, b = {3, 4, 0, 0};
    Polynomial A(a), B(b);
    for (int i = 0; i < 4; i++) A.z[i] = A.z[i] * B.z[i];
    A.ntt(A.z, 4, -1);
    for (int i = 0; i < 4; i++) cout << A.z[i] << ' ';
    cout << '\n';
}
'''
lagmain = r'''
int main() {
    Lagrange L(2);
    cout << L.solve(3) << ' ' << L.solve(5) << '\n';
}
'''
eval_fix = poly.replace(
    'work(2 * p, l, m, num.mulT(q[2 * p + 1]).resize(m - l));',
    'Poly left = num.mulT(q[2 * p + 1]); left.resize(m - l); work(2 * p, l, m, left);'
).replace(
    'work(2 * p + 1, m, r, num.mulT(q[2 * p]).resize(r - m));',
    'Poly right = num.mulT(q[2 * p]); right.resize(r - m); work(2 * p + 1, m, r, right);'
)
evalmain = r'''
int main() {
    using P = Poly<998244353>;
    auto y = P{1, 2, 3}.eval({2, 3});
    cout << y[0] << ' ' << y[1] << '\n';
}
'''

def run(name, code, flags):
    path = out / (name + '.cpp')
    path.write_text(head + code)
    exe = out / name
    compiled = subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], text=True, capture_output=True)
    if compiled.returncode != 0:
        compiled.stdout = ''
        return compiled
    return subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30)

for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    got = run('poly-' + mode, mint + dft + poly + bm + lin + body, flags)
    assert got.returncode == 0 and got.stdout == expect, (got.returncode, got.stdout, got.stderr[-500:])
    transforms = run('fft-' + mode, fft + fftmain, flags)
    assert transforms.returncode == 0 and transforms.stdout == '3 10 8 0 \n'
    modular = run('ntt-' + mode, zntt + ntt + nttmain, flags)
    assert modular.returncode == 0 and modular.stdout == '3 10 8 0 \n'
    power_sum = run('lag-' + mode, zlag + lag + lagmain, flags)
    assert power_sum.returncode == 0 and power_sum.stdout == '14 55\n'
    print(mode, 'PASS')

bare_path = out / 'bm-no-cassert.cpp'
bare_path.write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + mint + dft + poly + bm + 'int main(){ berlekampMassey(Poly<998244353>{1, 1, 2}); return 0; }\n')
bare = subprocess.run([CXX, '-std=c++20', '-O2', str(bare_path), '-o', str(out / 'bm-no-cassert')], text=True, capture_output=True)
assert bare.returncode != 0 and 'assert' in bare.stderr
printed_eval = run('eval-printed', mint + dft + poly + evalmain, ['-O2'])
assert printed_eval.returncode != 0 and 'void' in printed_eval.stderr
fixed_eval = run('eval-fixed', mint + dft + eval_fix + evalmain, ['-O2'])
assert fixed_eval.returncode == 0 and fixed_eval.stdout == '17 34\n'
report = {
    'scope': 'With a local MInt, the printed polynomial operations, Berlekamp-Massey and linear recurrence match the checked values. Length-128 multiplication matches the naive product. FFT and NTT round-trips of (1+2x)(3+4x) are 3 10 8. The Lagrange power-sum snippet returns 14 and 55. Printed eval does not compile. No online AC.',
    'blob': '5ccf93566b4e7dce4235e81c670c08a32ffa863b',
    'eval': 'printed call uses resize as a value; a copy resized before the call returns 17 34',
    'assert': 'bits/stdc++.h in this libstdc++ does not declare assert',
}
(root / 'verification/wida-polyprint.json').write_text(json.dumps(report, indent=2) + '\n')
print('bounds PASS')
