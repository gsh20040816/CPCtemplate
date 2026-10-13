"""Audit WIDA HLPP against Edmonds-Karp on small graphs."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-hlpp.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_hlpp'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '1669a535c09dd16a9bf47a4eb7d68c297e98b142'
text = blob.decode().replace('\r\n', '\n')
assert 'gobalcnt' in text and 'ex[s] = INF' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-hlpp-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-hlpp'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_hlpp.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == 'ok\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-hlpp.json').write_text(json.dumps(dict(
    scope='PushRelabel<long long> matches Edmonds-Karp on four fixed graphs and five random graphs of at most 6 nodes. Capacities are int. Nodes 0 and a second work call are untested. Source does not compile alone. No online AC.',
    blob='1669a535c09dd16a9bf47a4eb7d68c297e98b142', runs=report), indent=2) + '\n')
