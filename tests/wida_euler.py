"""Audit the WIDA linear sieve snippet against trial division."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-euler.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_euler'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '844e97ecb9184a0341139803268cdbba85bcf6a3'
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-euler-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-euler'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_euler.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == '0\n1\n14\n'
    report.append(dict(mode=mode, stdout=got.stdout.strip()))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-euler.json').write_text(json.dumps(dict(
    scope='Pasted inside a function, primes through 30 match trial division and n=1 yields none. A second call appends another copy. The snippet does not compile alone. No online AC.',
    blob='844e97ecb9184a0341139803268cdbba85bcf6a3', runs=report), indent=2) + '\n')
