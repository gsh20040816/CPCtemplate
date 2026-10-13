"""Audit the WIDA unweighted tree-diameter length."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-diameter.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_diameter'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '67eb91943e0cf0234a3181d847b74e5f19109624'
text = blob.decode().replace('\r\n', '\n')
assert 'return dep[root];' in text and 'int st = root;' in text and 'st' not in text.split('int st = root;', 1)[1].split('return', 1)[0]
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-diameter-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-diameter'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_diameter.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == '0 1 3 2 1 1\n'
    report.append(dict(mode=mode, stdout=got.stdout.strip()))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-diameter.json').write_text(json.dumps(dict(
    scope='Unweighted diameter length of the component containing the start, counted in edges. Endpoints are computed and discarded. A separate component is not included. The source does not compile alone. No online AC.',
    blob='67eb91943e0cf0234a3181d847b74e5f19109624', runs=report), indent=2) + '\n')
