"""Audit the WIDA complex geometry helpers on exact examples."""
import hashlib, math, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-complex.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_complex'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '4ef14be1f9d5b7f2207742e28a952bfeb5c59818'
text = blob.decode().replace('\r\n', '\n')
assert '#define x real' in text and '#define y imag' in text
assert 'cross(c - a, d - a) / cross(b - a, d - c)' in text
out = root / 'build/wida-complex'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_complex.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    rows = got.stdout.splitlines()
    dot, cross, zero, length, dist = map(float, rows[0].split())
    assert abs(dot - 3) < 1e-12 and abs(cross - 1) < 1e-12 and abs(zero) < 1e-12
    assert abs(length - 5) < 1e-12 and abs(dist - 5) < 1e-12
    near, parallel = map(float, (rows[1], rows[2]))
    assert abs(near - 3) < 1e-9
    assert math.isinf(parallel) or math.isnan(parallel)
    report.append(dict(mode=mode, near=near, parallel=parallel))
    print(mode, 'PASS', near, parallel, flush=True)
import json
(root / 'verification/wida-complex.json').write_text(json.dumps(dict(
    scope='complex<long double> dot, cross, length and distance. get returns the distance from d to the intersection of lines ab and cd. Parallel lines are not finite. The x/y macros pollute the translation unit. No online AC.',
    blob='4ef14be1f9d5b7f2207742e28a952bfeb5c59818', runs=report), indent=2) + '\n')
