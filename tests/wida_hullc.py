"""Audit the WIDA complex convex hull for sets of at least two points."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-hullc.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_hullc'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '9f831125f80c5236db53eefd13ede34cd5c1ecaf'
text = blob.decode().replace('\r\n', '\n')
assert 'using Point = std::complex<i64>;' in text and 'i64' not in text.split('using Point', 1)[0]
assert '#define x real' in text and 'cross(' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-hullc-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'i64' in bare.stderr

def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def hull(points):
    a = sorted(set(points))
    l, h = [], []
    for p in a:
        while len(l) > 1 and cross(l[-2], l[-1], p) <= 0:
            l.pop()
        while len(h) > 1 and cross(h[-2], h[-1], p) >= 0:
            h.pop()
        l.append(p)
        h.append(p)
    h.reverse()
    return h + l[1:-1]

cases = [
    [(0, 0), (1, 0)],
    [(0, 0), (2, 0), (1, 0)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    [(0, 0), (3, 0), (0, 3), (1, 1)],
    [(0, 0), (4, 0), (4, 3), (0, 3), (2, 1), (2, 5)],
]
out = root / 'build/wida-hullc'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_hullc.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    for pts in cases:
        payload = str(len(pts)) + '\n' + '\n'.join(f'{x} {y}' for x, y in pts) + '\n'
        got = subprocess.run([str(exe), 'hull'], input=payload, text=True, capture_output=True, env=env, timeout=30, check=True)
        assert got.stderr == ''
        nums = list(map(int, got.stdout.split()))
        count, body = nums[0], nums[1:]
        parsed = [(body[i], body[i + 1]) for i in range(0, len(body), 2)]
        assert count == len(parsed) == len(hull(pts))
        assert parsed == hull(pts)
    extra = subprocess.run([str(exe), 'labels'], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert extra.stderr == ''
    head = extra.stdout.splitlines()
    assert head[0] == '-4 3'
    assert head[1] == '0 1 0 1'
    report.append(dict(mode=mode, cases=len(cases)))
    print(mode, 'PASS', flush=True)
bad = subprocess.run([str(out / 'sanitizer'), 'tiny'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0
report.append(dict(tiny='nonzero', returncode=bad.returncode))
print('tiny', bad.returncode, flush=True)
import json
(root / 'verification/wida-hullc.json').write_text(json.dumps(dict(
    scope='complex<i64> monotone chain after defining i64. Collinear points are removed. Empty and single-point inputs are not safe. x/y macros rename identifiers. No online AC.',
    blob='9f831125f80c5236db53eefd13ede34cd5c1ecaf', runs=report), indent=2) + '\n')
