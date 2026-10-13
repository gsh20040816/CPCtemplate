"""Audit the small executable pieces of the WIDA number-theory printout."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-nta.md').read_bytes()
fix = root / 'tests/fixtures/wida_ntaprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
(fix / 'README.md').write_text(
    '# WIDA number-theory printout fixture\n\n'
    'main.md is the exact CRLF blob `be99abb7807fa28dfbd49b034c21ba37613dd101` '
    'from hh2048/XCPC tree `cfdb12db6792eb2303798541fb5c760ed2bc618b`.\n\n'
    'Path: `02 - 打印稿模板汇总/05A - 数论.md`.\n\n'
    'The upstream GPL-3.0 license is preserved in LICENSE. This fixture is not '
    'relicensed under the root MIT license. See docs/WIDA-NTAPRINT.md.\n'
)
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'be99abb7807fa28dfbd49b034c21ba37613dd101'
text = blob.decode().replace('\r\n', '\n')
fences = []
pos = 0
while True:
    a = text.find('```', pos)
    if a < 0:
        break
    b = text.find('\n', a)
    c = text.find('```', b + 1)
    fences.append(text[b + 1:c])
    pos = c + 3
pow_small, mul_block, trial, sieve, miller, factor, pollard, bezout = fences[1:9]
linear = fences[11]
phi, xor_u, xor_i = fences[15], fences[25], fences[26]
yang, divisors, incl, dfs = fences[20], fences[21], fences[22], fences[23]
cantor, cantor_bit = fences[28], fences[29]
floor = fences[36]
out = root / 'build/wida-ntaprint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
head = '#include <bits/stdc++.h>\nusing namespace std;\nusing i64 = long long;\nusing LL = long long;\n'

def run(name, code, flags, input_text=''):
    path = out / (name + '.cpp')
    path.write_text(head + code)
    exe = out / name
    compiled = subprocess.run([CXX, '-std=c++20', *flags, str(path), '-o', str(exe)], text=True, capture_output=True)
    if compiled.returncode != 0:
        compiled.stdout = ''
        return compiled
    return subprocess.run([str(exe)], input=input_text, text=True, capture_output=True, env=env, timeout=30)

parts = mul_block.split('i64 mul')
first_mul = 'i64 mul' + parts[1]
pow_part = 'i64 pow' + mul_block.split('i64 pow', 1)[1]
slow = 'i64 mul128' + parts[2].split('i64 pow', 1)[0][parts[2].find('('):]
core = r'''
int exgcd(int a, int b, int &x, int &y) {
    if (!b) { x = 1; y = 0; return a; }
    int d = exgcd(b, a % b, y, x);
    y -= a / b * x;
    return d;
}
LL getInv(int a, int mod) {
    int x, y, d = exgcd(a, mod, x, y);
    return d == 1 ? (x % mod + mod) % mod : -1;
}
'''
# The printed getInv declares LL x,y but calls exgcd with int&. Use the printed exgcd2.
mr = miller.replace('bool isprime', 'bool mr', 1).replace('i64 mul(', 'i64 mul_mr(', 1).replace('mul(', 'mul_mr(').replace('i64 pow(', 'i64 pow_mr(', 1).replace('pow(', 'pow_mr(')
fs = factor.replace('minp', 'fminp').replace('maxp', 'fmaxp').replace('prime', 'fprime').replace('void sieve', 'void fsieve').replace('vector<array<int, 2>> factorize', 'vector<array<int, 2>> split')
body = pow_small + first_mul + slow + pow_part + trial.replace('bool isprime', 'bool trial', 1) + sieve.replace('bool isprime', 'bool sieved', 1) + fs + mr + pollard.replace('mul(', 'mul_mr(').replace('isprime', 'mr') + phi + xor_u + xor_i + core + r'''
int main() {
    if (pow(2, 10, 1000) != 24 || pow(5, 0, 7) != 1) return 1;
    if (mul(20, 30, 97) != mul128(20, 30, 97)) return 1;
    if (!trial(97) || trial(1) || trial(9)) return 1;
    sieve(30);
    if (!sieved(29) || sieved(1) || sieved(25)) return 1;
    fsieve(30);
    auto f = split(12);
    if (f.size() != 2 || f[0][0] != 2 || f[0][1] != 2 || f[1][0] != 3 || f[1][1] != 1) return 1;
    if (!mr(97) || mr(9) || mr(1)) return 1;
    auto g = factorize((i64)91);
    if (g.size() != 2 || g[0] != 7 || g[1] != 13) return 1;
    if (phi(10) != 4 || phi(1) != 1) return 1;
    unsigned xs = 0; i64 xl = 0;
    for (unsigned n = 0; n <= 20; n++) {
        if (xor_n(n) != xs || xor_n((i64)n) != xl) return 1;
        xs ^= n + 1; xl ^= n + 1;
    }
    if (getInv(3, 7) != 5) return 1;
    cout << "ok\n";
}
'''
# The replacement of mul( inside miller also rewrote the function header and the pollard calls.
# Verify by compiling; fix if the first mul definition was damaged.
yang_code = r'''
int main() {
    int n = 5, m = 2;
''' + yang + '}\n'
div_code = divisors
inc_code = incl.replace('LL', 'long long')
dfs_code = dfs.replace('LL', 'long long')
floor_code = floor.replace('LL', 'long long')
cantor_code = cantor
bit_code = cantor_bit
inv_code = r'''
int main() {
    int n = 6, p = 7; vector<int> inv(n + 1);
''' + linear + r'''
    cout << inv[1] << ' ' << inv[2] << ' ' << inv[3] << "\n";
}
'''
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    got = run('core-' + mode, body, flags)
    assert got.returncode == 0 and got.stdout.endswith('ok\n'), (got.returncode, got.stdout, got.stderr[-500:])
    assert run('yang-' + mode, yang_code, flags).stdout == '10\n'
    assert run('div-' + mode, div_code, flags, '6\n').stdout == '1 \n1 2 \n1 3 \n1 2 4 \n1 5 \n1 2 3 6 \n'
    assert run('inc-' + mode, inc_code, flags, '10 3\n2 3 5\n').stdout == '8\n'
    assert run('dfs-' + mode, dfs_code, flags, '10 3\n2 3 5\n').stdout == '8\n'
    assert run('floor-' + mode, floor_code, flags, '1\n10\n').stdout == '27\n'
    assert run('cantor-' + mode, cantor_code, flags).stdout == '1\n'
    assert run('rank-' + mode, bit_code, flags, '5\n5 2 4 1 3\n').stdout == '107\n'
    assert run('inv-' + mode, inv_code, flags).stdout == '1 4 5\n'
    print(mode, 'PASS')
huge_code = first_mul + slow + r'''
int main() {
    i64 a = 1000000000000000000LL, m = 1000000000000000003LL;
    cout << mul(a, a, m) << ' ' << mul128(a, a, m) << "\n";
}
'''
huge = run('huge', huge_code, ['-O2'])
assert huge.returncode == 0 and huge.stdout == '-1999999999999999997 9\n'
assert run('huge-san', huge_code, ['-O1', '-g', '-fsanitize=address,undefined']).returncode != 0
raw = run('bezout', bezout, ['-O1', '-g', '-fsanitize=address,undefined'], '3\n6 9 15\n')
assert raw.returncode == 0 and raw.stdout == '3\n'
euler = fences[16]
assert run('euler', euler, ['-O2'], '5\n').returncode != 0
report = {
    'scope': 'Small powers, trial division, the sieve, Miller-Rabin, Pollard factor 91, phi, prefix xor, inverses, Yanghui, divisors, inclusion and floor sums match. The long-double product of 10^18 overflows and prints -1999999999999999997 instead of 9. The Bezout sample prints 3 because the global answer starts at 0. The plain Cantor program prints 1 because its string is shadowed. Euler sieve needs ms. BSGS, Gaussian elimination, Min_25, matrices, Lucas and exCRT were not executed. No online AC.',
    'blob': 'be99abb7807fa28dfbd49b034c21ba37613dd101',
}
(root / 'verification/wida-ntaprint.json').write_text(json.dumps(report, indent=2) + '\n')
print('bounds PASS')
