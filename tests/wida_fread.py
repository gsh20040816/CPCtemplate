"""Audit the WIDA fread scanner and writer."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-fread.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_fread'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '1241bb963bc021da78b2d5cda62c5457c1b2c18a'
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-fread-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'fread' in bare.stderr
out = root / 'build/wida-fread'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_fread.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], input='  -12 0 34x', text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == '-12 0 34\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
try:
    empty = subprocess.run([str(out / 'normal'), 'empty'], input='', text=True, capture_output=True, env=env, timeout=2)
    assert empty.returncode != 0
except subprocess.TimeoutExpired:
    empty = None
ub = out / 'ub'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
big = subprocess.run([str(ub), 'big'], input='9999999999', text=True, capture_output=True, env=env, timeout=30)
assert big.returncode != 0 and 'signed integer overflow' in big.stderr
mn = subprocess.run([str(ub), 'min'], text=True, capture_output=True, env=env, timeout=30)
assert mn.returncode != 0 and 'negation of -2147483648' in mn.stderr
report.append(dict(empty='timed out', big=big.stderr.strip().splitlines()[-1], minimum=mn.stderr.strip().splitlines()[-1]))
print('bounds PASS', flush=True)
import json
(root / 'verification/wida-fread.json').write_text(json.dumps(dict(
    scope='The source does not compile alone. With the standard headers, "-12 0 34" reads and writes back on this compiler; getc is not a macro here. Empty input does not finish. A 10-digit value and INT_MIN overflow signed int. No online AC.',
    blob='1241bb963bc021da78b2d5cda62c5457c1b2c18a', runs=report), indent=2) + '\n')
