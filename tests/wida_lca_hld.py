"""Audit the WIDA heavy-light LCA on four small trees."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-lca-hld.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_lca_hld'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'f71f21dda2565060cd2d8f371f9c241ab507d593'
text = blob.decode().replace('\r\n', '\n')
assert 'int n, idx;' in text and 'idx' not in text.split('int n, idx;', 1)[1]
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-lca-hld-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-lca-hld'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_lca_hld.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == 'ok\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-lca-hld.json').write_text(json.dumps(dict(
    scope='Heavy-light LCA and edge distance match parent walks on four small trees. idx is unused. There is no segment tree. Other components and a second work call are untested. Source does not compile alone. No online AC.',
    blob='f71f21dda2565060cd2d8f371f9c241ab507d593', runs=report), indent=2) + '\n')
