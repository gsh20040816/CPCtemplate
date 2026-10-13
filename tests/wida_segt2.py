"""Audit the WIDA segment tree with range add and range multiply."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-segt2.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_segt2'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '70f64fe0d8fb9db507246830308a0edb9f917a38'
text = blob.decode().replace('\r\n', '\n')
assert 'void modify2' in text and 'using Segt' not in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-segt2-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'vector' in bare.stderr
out = root / 'build/wida-segt2'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_segt2.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == 'ok\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
ub = out / 'overflow'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'overflow'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
report.append(dict(overflow=bad.stderr.strip().splitlines()[-1]))
print('overflow PASS', flush=True)
import json
(root / 'verification/wida-segt2.json').write_text(json.dumps(dict(
    scope='Range add and range multiply on 1..4 match a plain array for every subarray sum. There is no Segt alias. Multiplying a length by 1000000000 overflows int. n=0 is not constructed. Source does not compile alone. No online AC.',
    blob='70f64fe0d8fb9db507246830308a0edb9f917a38', runs=report), indent=2) + '\n')
