"""Audit the prefix of WIDA plane geometry: vectors, distances, and integer intersection."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-point2d.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_point2d'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '12c52bc3dcd33f17c815c09ffdcf8715201f7639'
text = blob.decode().replace('\r\n', '\n')
assert 'lineIntersection' in text and 'pointInPolygon' in text and 'halfPlane' not in text[:text.find('pointInPolygon')]
out = root / 'build/wida-point2d'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_point2d.cpp'
# The harness includes the saved fixture, not the /tmp path, after the copy above.
src.write_text(src.read_text().replace('#include "/tmp/wida-point2d.cpp"', '#include "fixtures/wida_point2d/main.cpp"'))
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    rows = got.stdout.splitlines()
    assert rows[0] == '3 -4 25'
    assert rows[1] == '-4 3'
    assert rows[2] == '1 1 -1 -1'
    assert rows[3] == '0 1'
    assert rows[4] == '1 1 0'
    assert rows[5] == '0 0'
    dist, pl, ps = map(float, rows[6].split())
    assert abs(dist - 5) < 1e-9 and abs(pl - 1) < 1e-9 and abs(ps - 2 ** 0.5) < 1e-9
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-point2d.json').write_text(json.dumps(dict(
    scope='Only Point, Line, dot, cross, length, distances, rotate, sgn, parallel, segment test, and lineIntersection. Integer division makes the checked intersection (0,0) instead of (1,0). Polygon and half-plane code later in the file is not verified. No online AC.',
    blob='12c52bc3dcd33f17c815c09ffdcf8715201f7639', runs=report), indent=2) + '\n')
