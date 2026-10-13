"""Audit WIDA randomized double hashing and its small prime search."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-hash3.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_hash3'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'f60132a4f225aff184d57389ca594263e50bd0be'
text = blob.decode().replace('\r\n', '\n')
assert "i - 'a'" in text and 'findPrime' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-hash3-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0

def prime(n):
    if n < 2: return False
    d = 2
    while d * d <= n:
        if n % d == 0: return False
        d += 1
    return True

out = root / 'build/wida-hash3'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_hash3.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    small = subprocess.run([str(exe), 'small'], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert small.stderr == '' and small.stdout == '0101 17\n-49\n'
    if mode == 'normal':
        got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
        assert got.stderr == ''
        mod1, base1, mod2, base2 = map(int, got.stdout.split())
        assert 10**8 <= mod1 <= 5*10**8 + 300
        assert mod1 <= mod2 <= 10**9 + 300
        assert 2 <= base1 <= 120 and base1 <= base2 <= 250
        assert all(prime(x) for x in (mod1, base1, mod2, base2))
        report.append(dict(mode=mode, mods=[mod1, base1, mod2, base2]))
    else:
        report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
ub = out / 'overflow'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'overflow'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
report.append(dict(overflow=bad.stderr.strip().splitlines()[-1]))
print('overflow PASS', flush=True)
import json
(root / 'verification/wida-hash3.json').write_text(json.dumps(dict(
    scope='Random moduli found for a length-2 table were prime, and "ab" updated to "cb" matched nonnegative 64-bit arithmetic. Miller-Rabin on 1,2,9,17 and findPrime(14)=17 match. get("a0") stays negative. Building eight large powers overflows. The default 1<<21 table is not built. Source does not compile alone. No online AC.',
    blob='f60132a4f225aff184d57389ca594263e50bd0be', runs=report), indent=2) + '\n')
