"""Audit WIDA Miller-Rabin and Pollard-Rho on small integers."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-pollard.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_pollard'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '52991fffeb1f8b3664b7bcc6bb7df866b984c861'
text = blob.decode().replace('\r\n', '\n')
assert 'int r = a * b - m * (int)(1.L / m * a * b);' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-pollard-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-pollard'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_pollard.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe), 'small'], text=True, capture_output=True, env=env, timeout=120, check=True)
    assert got.stderr == '' and got.stdout == 'ok\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
ub = out / 'big'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'big'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
report.append(dict(big=bad.stderr.strip().splitlines()[-1]))
print('big PASS', flush=True)
import json
(root / 'verification/wida-pollard.json').write_text(json.dumps(dict(
    scope='MR matches trial division through 20000, and fac matches through 4000. MR(1000000007) overflows signed int multiplication. fac(0) is not run. Source does not compile alone. No online AC.',
    blob='52991fffeb1f8b3664b7bcc6bb7df866b984c861', runs=report), indent=2) + '\n')
