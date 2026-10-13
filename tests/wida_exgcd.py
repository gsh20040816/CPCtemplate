"""Audit WIDA exgcd and the ax+by=c printer."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-exgcd.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_exgcd'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '0c03386ef4af4cc3465115665ff30b3e079ab14a'
text = blob.decode().replace('\r\n', '\n')
head, tail = text.split('auto clac', 1)
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-exgcd-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'capture-default' in bare.stderr
out = root / 'build/wida-exgcd'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
body = (root / 'tests/wida_exgcd.cpp').read_text()
wrapped = '#include <bits/stdc++.h>\n#include <cassert>\nusing std::abs;\nusing std::cout;\nusing std::endl;\n' + head + 'int main(int argc, char **argv) {\nauto clac' + tail + '\nstd::string mode = argc > 1 ? argv[1] : "ok";\nif (mode == "zero") { clac(0, 5, 10); return 0; }\n' + body + '\n}\n'
(out / 'wrapped.cpp').write_text(wrapped)
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(out / 'wrapped.cpp'), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == 'ok 2 44\n'
    report.append(dict(mode=mode, gcd_sign=got.stdout.strip()))
    print(mode, 'PASS', flush=True)
ub = out / 'zero'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(out / 'wrapped.cpp'), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'zero'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'division by zero' in bad.stderr
report.append(dict(zero=bad.stderr.strip().splitlines()[-1]))
print('zero PASS', flush=True)
import json
(root / 'verification/wida-exgcd.json').write_text(json.dumps(dict(
    scope='For a,b in 1..8 and c in 1..20 the printer matches an independent scan. All 44 mismatches are c=0, where x can stay 0; ax+2y=0 prints x=0 instead of 2. exgcd(-4,6) returns 2 and satisfies Bezout. clac(0,5,10) divides by zero. The global lambda does not compile. No online AC.',
    blob='0c03386ef4af4cc3465115665ff30b3e079ab14a', runs=report), indent=2) + '\n')
