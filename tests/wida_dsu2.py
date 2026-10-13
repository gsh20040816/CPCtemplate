"""Audit WIDA DSU++ edge counts and self-loop flags."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-dsu2.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_dsu2'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '3b7ab7bf61d1cbf4653f794b87198463c72fa405'
text = blob.decode().replace('\r\n', '\n')
assert 'if (x == y) f[get(x)] = 1;' in text and 'e[x]++;' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-dsu2-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'vector' in bare.stderr
out = root / 'build/wida-dsu2'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_dsu2.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == 'ok\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-dsu2.json').write_text(json.dumps(dict(
    scope='A triangle does not set the self-loop flag. A later self-loop does. Edge counts include repeated edges. Sizes and roots match union by larger index. Node 0 stays separate. Out-of-range indexes are not called. Source does not compile alone. No online AC.',
    blob='3b7ab7bf61d1cbf4653f794b87198463c72fa405', runs=report), indent=2) + '\n')
