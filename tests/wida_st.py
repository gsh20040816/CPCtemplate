"""Audit the WIDA sparse table against brute-force ranges."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-st.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_st'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '06a677a1266cfbf065cf103431af670b25091e7c'
text = blob.decode().replace('\r\n', '\n')
assert 'Max[0][i] = in1[i]' in text and 'Min[0][i] = in2[i]' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-st-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-st'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_st.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == '7 -4\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-st.json').write_text(json.dumps(dict(
    scope='Max reads in1 and min reads in2. Every ordered pair of endpoints on 1..8 matches a scan, including reversed endpoints. A one-element table matches. n=0 is not constructed. Source does not compile alone. No online AC.',
    blob='06a677a1266cfbf065cf103431af670b25091e7c', runs=report), indent=2) + '\n')
