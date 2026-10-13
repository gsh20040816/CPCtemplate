"""Audit the old WIDA convex hull, including its cross argument order."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-hulla.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_hulla'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'e2dc852fc236b66f55be847d8dbd6f1f4fed1e68'
text = blob.decode().replace('\r\n', '\n')
assert 'if (p.size() <= 1)' in text
assert 'cross(a - h.back(), a - h[h.size() - 2])' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-hulla-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'i64' in bare.stderr

def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])

def cross(u, v):
    return u[0] * v[1] - u[1] * v[0]

def hull(points):
    p = sorted(set(points))
    if len(p) <= 1:
        return p
    h, l = [], []
    for a in p:
        while len(h) > 1 and cross(sub(a, h[-1]), sub(a, h[-2])) <= 0:
            h.pop()
        while len(l) > 1 and cross(sub(a, l[-1]), sub(a, l[-2])) >= 0:
            l.pop()
        l.append(a)
        h.append(a)
    l.pop()
    h.reverse()
    h.pop()
    return l + h

cases = [
    [],
    [(1, 2)],
    [(0, 0), (0, 0), (1, 1)],
    [(0, 0), (2, 0), (1, 0)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    [(0, 0), (3, 0), (0, 3), (1, 1)],
    [(0, 0), (0, 2), (1, 1)],
]
out = root / 'build/wida-hulla'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_hulla.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    for pts in cases:
        payload = str(len(pts)) + '\n' + '\n'.join(f'{x} {y}' for x, y in pts) + '\n'
        got = subprocess.run([str(exe)], input=payload, text=True, capture_output=True, env=env, timeout=30, check=True)
        assert got.stderr == ''
        rows = got.stdout.splitlines()
        assert rows[0] == '3 -4'
        assert rows[1] == '0 0 1 1'
        assert rows[2] == '-1 0'
        nums = list(map(int, rows[3].split()))
        parsed = [(nums[i], nums[i + 1]) for i in range(1, len(nums), 2)]
        assert nums[0] == len(parsed) == len(hull(pts))
        assert parsed == hull(pts)
    report.append(dict(mode=mode, cases=len(cases)))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-hulla.json').write_text(json.dumps(dict(
    scope='Old monotone chain. Cross arguments are a-back and a-previous, not the usual edge vectors. Duplicates are removed and size<=1 is returned unchanged. i64 is undefined. No online AC.',
    blob='e2dc852fc236b66f55be847d8dbd6f1f4fed1e68', runs=report), indent=2) + '\n')
