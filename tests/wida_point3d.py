"""Audit the WIDA double 3D point on exact vector examples."""
import hashlib, math, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-point3d.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_point3d'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '4acee66bdb971659f99ec1a83ff8c836d66957c8'
text = blob.decode().replace('\r\n', '\n')
assert 'using real = double;' in text and 'std::acos' in text
assert 'using i64 = long long;' in text
assert text.split('using i64 = long long;', 1)[1].count('i64') == 0
out = root / 'build/wida-point3d'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_point3d.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    rows = [list(map(float, line.split())) for line in got.stdout.splitlines()]
    assert rows[0] == [5, 1, 5]
    assert rows[1] == [-3, 3, 1]
    assert rows[2] == [2, 4, 6]
    assert rows[3] == [2, -0.5, 1]
    assert rows[4] == [8]
    assert rows[5] == [0, 0, 1]
    assert abs(rows[6][0] - 13) < 1e-12
    assert all(abs(a - b) < 1e-12 for a, b in zip(rows[7], [0, 0.6, 0.8]))
    assert abs(rows[8][0] - math.pi / 2) < 1e-12
    assert all(math.isnan(x) for x in rows[9])
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-point3d.json').write_text(json.dumps(dict(
    scope='double 3D point. Checked addition, scaling, dot, cross, length, normalize and a right angle. Zero-vector normalize is NaN. i64 is unused. No online AC.',
    blob='4acee66bdb971659f99ec1a83ff8c836d66957c8', runs=report), indent=2) + '\n')
