"""Audit WIDA coordinate compression, including its sentinel and lookup."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-compress.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_compress'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '2f1e5e673740c415155d99322b59683e89654ba4'
text = blob.decode().replace('\r\n', '\n')
assert 'upper_bound' in text and 'numeric_limits<T>::max()' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-compress-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'vector' in bare.stderr
out = root / 'build/wida-compress'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_compress.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    rows = got.stdout.splitlines()
    assert rows[0] == '4 1 2 3 1 2'
    assert rows[1] == '3 2147483647'
    assert rows[2] == '1 0 1'
    assert rows[3] == '2'
    assert rows[4] == '{'
    assert rows[5] == '1 3 5 2147483647 }'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
ub = out / 'bad'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'bad'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'Assertion' in bad.stderr
report.append(dict(get=bad.stderr.strip().splitlines()[-1]))
print('assert PASS', flush=True)
import json
(root / 'verification/wida-compress.json').write_text(json.dumps(dict(
    scope='Values 1,3,5 plus the int maximum occupy four ranks. operator[] is the count of stored values <= x, so a missing value shares the previous rank and Get of that rank returns the next stored value. count(INT_MAX) is true. Printing sends the opening brace to cout and the values to the requested stream. Get past the end asserts. Source does not compile alone. No online AC.',
    blob='2f1e5e673740c415155d99322b59683e89654ba4', runs=report), indent=2) + '\n')
