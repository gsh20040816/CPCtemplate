"""Audit WIDA ModIntBase after supplying the missing unsigned aliases."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-modint.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_modint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'feb38dce787b7469cc183b02927933cd72ca5a70'
text = blob.decode().replace('\r\n', '\n')
assert 'TODO: Dynamic ModInt' in text
assert '1.L * a * b / P - 0.5L' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-modint-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'u32' in bare.stderr
P = 998244353
out = root / 'build/wida-modint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_modint.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe), 'mod'], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    rows = [list(map(int, line.split())) for line in got.stdout.splitlines()]
    assert rows[0] == [8, (3 - 5) % P, 15, 3 * pow(5, -1, P) % P]
    assert rows[1] == [pow(2, 10, P), P - 3, P - 1, P - 5]
    assert rows[2] == [0, 1, 1]
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
mul = subprocess.run([str(out / 'normal'), 'mul64'], text=True, capture_output=True, env=env, timeout=30, check=True)
assert mul.stderr == ''
assert mul.stdout.strip() == '4840048882768193505 1319689441135291815'
report.append(dict(mul64=mul.stdout.strip()))
print('mul64', mul.stdout.strip(), flush=True)
import json
(root / 'verification/wida-modint.json').write_text(json.dumps(dict(
    scope='ModInt<998244353> matches integer modular arithmetic on the checked values, and inv(0) returns 0. u64 mulMod uses long double and mismatches __int128. The source does not compile until u32/u64 exist. Dynamic modulus is only a TODO. No online AC.',
    blob='feb38dce787b7469cc183b02927933cd72ca5a70', runs=report), indent=2) + '\n')
