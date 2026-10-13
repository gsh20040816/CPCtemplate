"""Audit the WIDA splitmix hash and its gp_hash_table alias."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-hash.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_hash'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '52848daa42461f0ebba6cef6eb4524e4ecc2933d'
text = blob.decode().replace('\r\n', '\n')
assert text.count('static const uint64_t SEED') == 2
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-hash-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-hash'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_hash.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == '1 0\n3 4 5 0\n9 0\n1000\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-hash.json').write_text(json.dumps(dict(
    scope='Same key hashes equal and 0..999 are distinct under one run seed. unordered_map<int,int,myhash> stores -1,0,1. gp_hash_table pair key {1,2} is distinct from {2,1}. The two operator() overloads have separate seeds. Numeric hash values are not fixed across runs. Source does not compile alone. No online AC.',
    blob='52848daa42461f0ebba6cef6eb4524e4ecc2933d', runs=report), indent=2) + '\n')
