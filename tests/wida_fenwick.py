"""Audit the WIDA one-dimensional Fenwick tree."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-fenwick.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_fenwick'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '864bd2178ce95e18ebfdf34d0eab893e2e7d4dc0'
text = blob.decode().replace('\r\n', '\n')
assert 'add(x, k), add(y, -k)' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-fenwick-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'vector' in bare.stderr
out = root / 'build/wida-fenwick'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_fenwick.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == '0 3 3 0 0\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
ub = out / 'overflow'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'overflow'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
report.append(dict(overflow=bad.stderr.strip().splitlines()[-1]))
print('overflow PASS', flush=True)
import json
(root / 'verification/wida-fenwick.json').write_text(json.dumps(dict(
    scope='Point adds and range sums on 1..6 match a plain array. add(2,5,3) changes indices 2,3,4 and not 5, so the third argument is an exclusive end. Two large point adds overflow int. Index 0 is not called. Source does not compile alone. No online AC.',
    blob='864bd2178ce95e18ebfdf34d0eab893e2e7d4dc0', runs=report), indent=2) + '\n')
