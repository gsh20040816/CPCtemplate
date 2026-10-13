"""Audit WIDA bigint against Python integers for nonnegative values."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-bigint.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_bigint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '0ea72a039abf01bd3654e3d8e57019a01c580e13'
text = blob.decode().replace('\r\n', '\n')
assert 'void check(int v)' in text and 'karatsubaMultiply' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-bigint-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'vector' in bare.stderr
a = 123456789012345678901234567890
b = 987654321098765432109876543210
expect = [
    str(a + b), str(a - b), str(a * b), str(a // b), str(a % b),
    str(a * 7), str(a // 7), str(a % 7), '6', '36', '111',
    '-0 0', '--36', '--2', '2', '-2 -2',
]
out = root / 'build/wida-bigint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_bigint.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout.splitlines() == expect
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
ub = out / 'min'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'min'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'negation' in bad.stderr
report.append(dict(minimum=bad.stderr.strip().splitlines()[-1]))
print('min PASS', flush=True)
import json
(root / 'verification/wida-bigint.json').write_text(json.dumps(dict(
    scope='Nonnegative addition, subtraction, product, quotient, remainder, gcd and lcm match Python. Unary minus of zero prints -0, while the string -0 becomes 0. Multiplying or dividing by a negative int keeps the negative divisor and prints a doubled sign. LLONG_MIN overflows when negated. Division by zero is not run. Source does not compile alone. No online AC.',
    blob='0ea72a039abf01bd3654e3d8e57019a01c580e13', runs=report), indent=2) + '\n')
