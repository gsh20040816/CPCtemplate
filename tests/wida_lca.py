"""Audit the WIDA binary-lifting LCA on four rooted trees."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-lca.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_lca'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '177db56e1ae065103835ad3125bb304cf866040b'
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-lca-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-lca'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_lca.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == 'ok\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-lca.json').write_text(json.dumps(dict(
    scope='1-based binary lifting. Root depth is 1. LCA and edge distance match parent climbing on a point, an edge, a path and a small tree. Nodes outside the worked component are not tested. Source does not compile alone. No online AC.',
    blob='177db56e1ae065103835ad3125bb304cf866040b', runs=report), indent=2) + '\n')
