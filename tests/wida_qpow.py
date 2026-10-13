"""Audit both WIDA modular powers against __int128 arithmetic."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-qpow.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_qpow'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '73f8c65c32b46ef3bc067a263a5c542f55352e12'
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-qpow-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'i64' in bare.stderr
out = root / 'build/wida-qpow'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_qpow.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30)
    print(mode, got.returncode, got.stdout.strip(), flush=True)
    if mode == 'normal':
        assert got.returncode == 0 and got.stdout == '20 0 0\n0 0 0 0 0\n1 1\n'
    else:
        assert got.returncode != 0 and 'signed integer overflow' in got.stderr
    report.append(dict(mode=mode, returncode=got.returncode, stdout=got.stdout.strip(), stderr=(got.stderr or '').strip().splitlines()[-1:]))
import json
(root / 'verification/wida-qpow.json').write_text(json.dumps(dict(
    scope='Two modular powers. The file does not compile until i64 is declared. Integer power matches __int128 on the small domain except mod 1 and exponent 0. Floating mul is compared on 20000 products. No new basic template and no online AC.',
    blob='73f8c65c32b46ef3bc067a263a5c542f55352e12', runs=report), indent=2) + '\n')
