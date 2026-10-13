"""Audit the WIDA plane-geometry namespace on exact integer operations."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-plane.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_plane'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '23de33672e259d662d64cd99d4bb4f43f4ac664e'
text = blob.decode().replace('\r\n', '\n')
assert 'return {-vec.y, vec.x};' in text and '#define cc(x)' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-plane-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-plane'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_plane.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    rows = got.stdout.splitlines()
    assert rows[0] == '3 -4 6'
    assert rows[1] == '-4 2'
    assert rows[2] == '13 14'
    assert rows[3] == '1 1'
    assert rows[4] == '0 0 -1'
    dist, g1, g2 = map(float, rows[5].split())
    assert abs(dist - 5) < 1e-9 and abs(g1 - 3) < 1e-9 and abs(g2 - 3) < 1e-9
    ux, uy, finite = rows[6].split()
    assert abs(float(ux) - 0.6) < 1e-9 and abs(float(uy) - 0.8) < 1e-9 and finite == '0'
    assert rows[7] == '1'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
ub = out / 'overflow'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'overflow'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
report.append(dict(overflow=bad.stderr.strip().splitlines()[-1]))
print('overflow PASS', flush=True)
import json
(root / 'verification/wida-plane.json').write_text(json.dumps(dict(
    scope='Integer dot, cross, Manhattan distance and the 90-degree vector match. Adding a scalar changes both coordinates. Zero standardize is not finite. int dis overflows 100000^2. The cc macro escapes the namespace. Source does not compile alone. No online AC.',
    blob='23de33672e259d662d64cd99d4bb4f43f4ac664e', runs=report), indent=2) + '\n')
