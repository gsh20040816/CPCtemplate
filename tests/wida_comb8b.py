"""Audit WIDA Comb once a prime modular Z is supplied."""
import hashlib, math, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-comb8b.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_comb8b'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'a5e737ce7e6bd1dc8be55aaabe0e1a4b6dc6be8c'
text = blob.decode().replace('\r\n', '\n')
assert 'std::vector<Z>' in text and 'if (n < m || m < 0) return 0;' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-comb8b-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'Z' in bare.stderr
P = 1000000007
queries = [(0, 0), (5, 2), (5, 6), (8, -3), (20, 7), (100, 0), (100, 50)]
lines = [str(len(queries))] + [f'{n} {m}' for n, m in queries]
out = root / 'build/wida-comb8b'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_comb8b.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], input='\n'.join(lines) + '\n', text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    rows = got.stdout.splitlines()
    for row, (n, m) in zip(rows, queries):
        expect = 0 if n < m or m < 0 else math.comb(n, m) % P
        assert int(row) == expect
    fac10, inv1, inv0 = map(int, rows[len(queries)].split())
    fac100 = int(rows[len(queries) + 1])
    assert fac10 == math.factorial(10) % P and inv1 == 1 and inv0 == 0
    expect100 = 1
    for i in range(1, 101):
        expect100 = expect100 * i % P
    assert fac100 == expect100
    report.append(dict(mode=mode, queries=len(queries)))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-comb8b.json').write_text(json.dumps(dict(
    scope='Comb needs an external modular type Z. With a prime-1000000007 Z, binomial values match integers and inv(0) stays 0. The source does not compile alone. No online AC.',
    blob='a5e737ce7e6bd1dc8be55aaabe0e1a4b6dc6be8c', runs=report), indent=2) + '\n')
