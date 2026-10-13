"""Audit WIDA Fenwick++ kth and inversion count."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-fenwick2.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_fenwick2'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '1f629ef1f8fcdaceda008534f75627b0aa039689'
text = blob.decode().replace('\r\n', '\n')
assert 'add(x, k), add(y, -k)' in text and '查找第k大的值' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-fenwick2-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'vector' in bare.stderr
out = root / 'build/wida-fenwick2'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_fenwick2.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == '4 4 3 0\n'
    inv = subprocess.run([str(exe), 'inv'], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert inv.stderr == '' and inv.stdout == '7 7\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-fenwick2.json').write_text(json.dumps(dict(
    scope='kth matches the smallest index whose frequency prefix reaches k, including one past the total, which still returns 4. add(2,5,3) still excludes 5. Inversions of 3,1,2,2,0 are 7. Source does not compile alone. No online AC.',
    blob='1f629ef1f8fcdaceda008534f75627b0aa039689', runs=report), indent=2) + '\n')
