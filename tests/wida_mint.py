"""Audit WIDA MInt and the floating MLong multiplication."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-mint.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_mint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'c0c6ceb5a52f5f248fbbfc1d70ecd099bdc851ae'
text = blob.decode().replace('\r\n', '\n')
assert 'MLong<0LL>::Mod = i64(1E18) + 9' in text
assert 'MInt<0>::Mod = 998244353' in text
assert '1.L * a * b / p' in text and '- 0.5L' not in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-mint-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'i64' in bare.stderr
P = 1000000007
out = root / 'build/wida-mint'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_mint.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    rows = [list(map(int, line.split())) for line in got.stdout.splitlines()]
    assert rows[0] == [8, (3 - 5) % P, 15, 3 * pow(5, -1, P) % P]
    assert rows[1] == [pow(2, 10, P), P - 3, P - 5]
    assert rows[2] == [998244353]
    assert rows[3] == [3]
    assert rows[4] == [0]
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
inv = subprocess.run([str(out / 'normal'), 'inv0'], text=True, capture_output=True, env=env, timeout=30)
assert inv.returncode != 0
ub = out / 'overflow'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'overflow'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
report.append(dict(inv0=inv.returncode, overflow=bad.stderr.strip().splitlines()[-1]))
print('boundaries PASS', flush=True)
import json
(root / 'verification/wida-mint.json').write_text(json.dumps(dict(
    scope='MInt<1000000007> matches integers. MInt<0> starts at 998244353 and setMod(7) works. inv(0) aborts. mul uses signed a*b and long double without the 0.5 bias; large products overflow. i64 is undefined in the source. No online AC.',
    blob='c0c6ceb5a52f5f248fbbfc1d70ecd099bdc851ae', runs=report), indent=2) + '\n')
