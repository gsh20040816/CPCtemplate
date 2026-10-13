"""Audit WIDA weighted binary lifting: edge counts and maximum edge weights."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-lca-w.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_lca_w'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '1f17e2d09d329a6416881397db9864debd40f35d'
text = blob.decode().replace('\r\n', '\n')
assert 'return dep[x] + dep[y] - 2 * dep[lca(x, y)];' in text
assert 'int ans = 0;' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-lca-w-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-lca-w'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_lca_w.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == '1 0\n'
    report.append(dict(mode=mode, negative=got.stdout.strip()))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-lca-w.json').write_text(json.dumps(dict(
    scope='Positive edge weights: clac matches the edge count and query matches the path maximum, with the maximum seeded at 0. A single edge of -5 yields query 0. The 30-column table and other components are untested. Source does not compile alone. No online AC.',
    blob='1f17e2d09d329a6416881397db9864debd40f35d', runs=report), indent=2) + '\n')
