"""Audit WIDA Zmod<998244353> on small values."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-modclass.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_modclass'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '93b40a4c52c2df389ca66d3cf72394610c7d1ef7'
text = blob.decode().replace('\r\n', '\n')
assert '998244353' in text and 'x %= i' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-modclass-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-modclass'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_modclass.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == 'ok\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
inv = subprocess.run([str(out / 'normal'), 'inv'], text=True, capture_output=True, env=env, timeout=30)
assert inv.returncode != 0
ub = out / 'mod0'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'mod0'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'division by zero' in bad.stderr
report.append(dict(inv=inv.returncode, mod0=bad.stderr.strip().splitlines()[-1]))
print('bounds PASS', flush=True)
import json
(root / 'verification/wida-modclass.json').write_text(json.dumps(dict(
    scope='Zmod<998244353> matches the checked add, subtract, multiply, divide, increment and power(10). Z(10)%4 is 2. inv(0) aborts and Z(10)%0 divides by zero. Composite moduli are not covered. Source does not compile alone. No online AC.',
    blob='93b40a4c52c2df389ca66d3cf72394610c7d1ef7', runs=report), indent=2) + '\n')
