"""Audit WIDA small integer helpers after defining MOD."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-overload.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_overload'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '5fce17a4572dd6d7803e711f7d80362c8e862284'
text = blob.decode().replace('\r\n', '\n')
assert 'int p = MOD' in text and '__builtin_clz' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-overload-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'MOD' in bare.stderr
out = root / 'build/wida-overload'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_overload.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == 'ok\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
ub = out / 'ub'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'pow'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
zero = subprocess.run([str(ub), 'zero'], text=True, capture_output=True, env=env, timeout=30)
assert zero.returncode != 0
report.append(dict(pow=bad.stderr.strip().splitlines()[-1], zero=zero.stderr.strip().splitlines()[-1]))
print('bounds PASS', flush=True)
import json
(root / 'verification/wida-overload.json').write_text(json.dumps(dict(
    scope='MOD and std::__gcd are both missing. After supplying them, small powers, lcm, floor, ceil and positive logs match. Log2(-1) is 31. mypow(100000,2) overflows signed multiplication. Log2(0) is undefined. Negative exponents are not run. No online AC.',
    blob='5fce17a4572dd6d7803e711f7d80362c8e862284', runs=report), indent=2) + '\n')
