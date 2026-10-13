"""Audit the WIDA __int128 stream operators."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-i128.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_i128'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '29f875f2fe00ce7f1ef7232860d394784af4f738'
text = blob.decode().replace('\r\n', '\n')
assert 'val.pop_back()' in text and 'reverse(val.begin(), val.end())' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-i128-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-i128'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_i128.cpp'
report = []
exe = out / 'normal'
subprocess.run([CXX, '-std=c++20', '-O2', str(src), '-o', str(exe)], check=True)
got = subprocess.run([str(exe)], input='-12 34\n', text=True, capture_output=True, env=env, timeout=30, check=True)
assert got.stderr == '' and got.stdout == '-12 34 12\n'
report.append(dict(mode='normal'))
print('normal PASS', flush=True)
ub = out / 'sanitizer'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub)], input='-12 34\n', text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'unreachable' in bad.stderr
mn = subprocess.run([str(ub), 'min'], text=True, capture_output=True, env=env, timeout=30)
assert mn.returncode != 0 and 'negation' in mn.stderr
report.append(dict(empty_back=bad.stderr.strip().splitlines()[-1], minimum=mn.stderr.strip().splitlines()[-1]))
print('bounds PASS', flush=True)
import json
(root / 'verification/wida-i128.json').write_text(json.dumps(dict(
    scope='At -O2, "-12 34" prints back and my128::abs(-12) is 12. UBSan says the reader reaches an unreachable point after the last character. Negating the int128 minimum is undefined. using namespace my128 makes abs ambiguous with std::abs. Source does not compile alone. No online AC.',
    blob='29f875f2fe00ce7f1ef7232860d394784af4f738', runs=report), indent=2) + '\n')
