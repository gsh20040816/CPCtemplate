"""Audit WIDA Z modulo 998244353, including the narrow int constructor."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-z.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_z'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '7b8778e7f670850df2c660f7d98b16c234f5178b'
text = blob.decode().replace('\r\n', '\n')
assert 'constexpr int P = 998244353;' in text
assert 'assume -P <= x < 2P' in text
assert 'assert(x != 0);' in text
P = 998244353
out = root / 'build/wida-z'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_z.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], input='-5\n', text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    rows = [list(map(int, line.split())) for line in got.stdout.splitlines()]
    assert rows[0] == [P - 1, P - 1]
    assert rows[1] == [0, P - 1, -1]
    assert rows[2] == [8, (3 - 5) % P, 15, 3 * pow(5, -1, P) % P]
    assert rows[3] == [pow(2, 10, P), P - 3]
    assert rows[4] == [P - 5]
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
inv = subprocess.run([str(out / 'normal'), 'inv0'], text=True, capture_output=True, env=env, timeout=30)
assert inv.returncode != 0
report.append(dict(inv0='nonzero', returncode=inv.returncode))
print('inv0', inv.returncode, flush=True)
import json
(root / 'verification/wida-z.json').write_text(json.dumps(dict(
    scope='Z modulo 998244353. i64 constructor reduces any representable value. int constructor only adds or subtracts P once. inv(0) aborts while asserts are enabled. No online AC.',
    blob='7b8778e7f670850df2c660f7d98b16c234f5178b', runs=report), indent=2) + '\n')
