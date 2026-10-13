"""Audit the WIDA range-add segment tree on a five-element array."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-segt.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_segt'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'f855e1e84e2e499e7e891b7060ac7bef6f225308'
text = blob.decode().replace('\r\n', '\n')
assert 'T ans = 1E18;' in text and '#undef GL' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-segt-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'vector' in bare.stderr
out = root / 'build/wida-segt'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_segt.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == 'ok\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
ub = out / 'sentinel'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'sentinel'], text=True, capture_output=True, env=env, timeout=30, check=True)
assert bad.stderr == '' and bad.stdout == '2147483647 0 0\n'
report.append(dict(sentinel=bad.stdout.strip()))
print('sentinel PASS', flush=True)
import json
(root / 'verification/wida-segt.json').write_text(json.dumps(dict(
    scope='Segt_<long long> range add, sum and minimum match a plain array on all subarrays of five elements. A split Ask returns bounds 0,0. On this compiler 1E18 becomes int 2147483647 and UBSan does not reject it; a partial minimum of zeros is still 0. n=0 is not constructed. Source does not compile alone. No online AC.',
    blob='f855e1e84e2e499e7e891b7060ac7bef6f225308', runs=report), indent=2) + '\n')
