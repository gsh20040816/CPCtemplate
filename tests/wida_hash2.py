"""Audit the WIDA double string hash on short strings."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-hash2.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_hash2'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'd755a66281a887e40454ae6ead94ed611a58e677'
text = blob.decode().replace('\r\n', '\n')
assert '1E9 + 7' in text and '1E9 + 9' in text and '1 << 21' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-hash2-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'pair' in bare.stderr
out = root / 'build/wida-hash2'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_hash2.cpp'
report = []

def pair_hash(s, mod, base):
    ans = 0
    for ch in s.encode():
        ans = (ans * base + ch) % mod
    return ans

expect = '%d %d 0 0\n' % (pair_hash('ab', 10**9 + 7, 127), pair_hash('ab', 10**9 + 9, 131))
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == expect
    report.append(dict(mode=mode, stdout=got.stdout.strip()))
    print(mode, 'PASS', flush=True)
ub = out / 'overflow'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'overflow'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
report.append(dict(overflow=bad.stderr.strip().splitlines()[-1]))
print('overflow PASS', flush=True)
import json
(root / 'verification/wida-hash2.json').write_text(json.dumps(dict(
    scope='With the power table limited to 2, the hashes of "ab" and the update to "cb" match 64-bit arithmetic. The empty string is (0,0). Building eight powers overflows a signed multiply. The default length 1<<21 is not timed. Source does not compile alone. No online AC.',
    blob='d755a66281a887e40454ae6ead94ed611a58e677', runs=report), indent=2) + '\n')
