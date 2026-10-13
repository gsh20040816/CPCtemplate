"""Audit the WIDA split convex hull, including vertical edges."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-hullb.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_hullb'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '8bceff9d4901e0ac952b41c47d10a19a045c56d9'
text = blob.decode().replace('\r\n', '\n')
assert 'struct Point' in text and 'i64 x' in text
assert 'return std::make_pair(hi, lo);' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-hullb-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'i64' in bare.stderr

def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def chains(points):
    p = sorted(points)
    hi, lo = [], []
    for x, y in p:
        while len(hi) > 1 and cross(hi[-2], hi[-1], (x, y)) >= 0:
            hi.pop()
        while hi and hi[-1][0] == x:
            hi.pop()
        hi.append((x, y))
        while len(lo) > 1 and cross(lo[-2], lo[-1], (x, y)) <= 0:
            lo.pop()
        if not lo or lo[-1][0] < x:
            lo.append((x, y))
    return hi, lo

cases = [
    [],
    [(1, 2)],
    [(0, 0), (0, 2)],
    [(0, 0), (2, 0), (1, 0)],
    [(0, 0), (0, 2), (1, 1)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    [(0, 0), (3, 0), (0, 3), (1, 1)],
]
out = root / 'build/wida-hullb'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_hullb.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    for pts in cases:
        payload = str(len(pts)) + '\n' + '\n'.join(f'{x} {y}' for x, y in pts) + '\n'
        got = subprocess.run([str(exe)], input=payload, text=True, capture_output=True, env=env, timeout=30, check=True)
        assert got.stderr == ''
        rows = got.stdout.splitlines()
        assert list(map(int, rows[0].split())) == [3, -4]
        body = [list(map(int, line.split())) for line in rows[1:]]
        def parse(nums):
            count, rest = nums[0], nums[1:]
            pts = [(rest[i], rest[i + 1]) for i in range(0, len(rest), 2)]
            assert count == len(pts)
            return pts
        hi, lo = chains(pts)
        assert parse(body[0]) == hi and parse(body[1]) == lo
    report.append(dict(mode=mode, cases=len(cases)))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-hullb.json').write_text(json.dumps(dict(
    scope='Split upper and lower chains. Same-x points keep the higher point on the upper chain and the lower point on the lower chain. i64 is undefined in the source. Empty input is safe. No online AC.',
    blob='8bceff9d4901e0ac952b41c47d10a19a045c56d9', runs=report), indent=2) + '\n')
