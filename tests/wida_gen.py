"""Audit the WIDA random tree and graph generator."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-gen.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_gen'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '33b3a24292968479385753f2ff6b1d820484ac44'
text = blob.decode().replace('\r\n', '\n')
assert 'random_shuffle' in text and 'steady_clock' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-gen-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
src = root / 'tests/wida_gen.cpp'
cxx20 = subprocess.run([CXX, '-std=c++20', '-c', str(src), '-o', str(root / 'build/wida-gen-cxx20.o')], text=True, capture_output=True)
assert cxx20.returncode == 0 and 'deprecated' in cxx20.stderr and 'random_shuffle' in cxx20.stderr
out = root / 'build/wida-gen'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')

def edges(exe, n, m=None):
    cmd = [str(exe), 'graph', str(n)] + ([] if m is None else [str(m)])
    got = subprocess.run(cmd, text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    rows = [tuple(map(int, line.split())) for line in got.stdout.splitlines()]
    return rows

def connected(n, rows):
    g = [[] for _ in range(n + 1)]
    for x, y in rows:
        g[x].append(y)
        g[y].append(x)
    seen = [0] * (n + 1)
    stack = [1]
    seen[1] = 1
    while stack:
        u = stack.pop()
        for v in g[u]:
            if not seen[v]:
                seen[v] = 1
                stack.append(v)
    return all(seen[1:])

report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    for n in (1, 2, 6):
        rows = edges(exe, n)
        assert len(rows) == max(n - 1, 0)
        assert all(1 <= x <= n and 1 <= y <= n and x != y for x, y in rows)
        undirected = {frozenset(e) for e in rows}
        assert len(undirected) == len(rows)
        if n:
            assert connected(n, rows)
    one = subprocess.run([str(exe), 'range'], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert one.stderr == '' and one.stdout == '3 0\n'
    full = edges(exe, 4, 6)
    assert len(full) == 6 and len({frozenset(e) for e in full}) == 6
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
try:
    subprocess.run([str(out / 'normal'), 'graph', '3', '4'], text=True, capture_output=True, env=env, timeout=2, check=True)
    raise SystemExit('expected hang')
except subprocess.TimeoutExpired:
    pass
print('hang PASS', flush=True)
import json
(root / 'verification/wida-gen.json').write_text(json.dumps(dict(
    scope='This libstdc++ still compiles random_shuffle in C++20 and warns that it is deprecated. Trees on 1, 2 and 6 nodes are connected and simple, K4 has 6 edges, and asking for 4 edges on 3 nodes does not finish. r(3,3) is 3 and r(0,0) is 0. The clock seed is not fixed. Source does not compile alone. No online AC.',
    blob='33b3a24292968479385753f2ff6b1d820484ac44', runs=report), indent=2) + '\n')
