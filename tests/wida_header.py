"""Audit the WIDA contest header macros and the empty ONLINE_JUDGE program."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-header.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_header'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'bf2c922a8bca7f3bbf97f1b5be2ca61d222b5c87'
text = blob.decode().replace('\r\n', '\n')
assert '#include <bits/wida.h>' in text and '#define int long long' in text and 'freopen("in.txt"' in text
bare = subprocess.run([CXX, '-std=c++20', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-header-bare')], text=True, capture_output=True)
assert bare.returncode != 0 and 'wida.h' in bare.stderr
out = root / 'build/wida-header'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / ('prog-' + mode)
    subprocess.run([CXX, '-std=c++20', '-DONLINE_JUDGE', *flags, str(fix / 'main.cpp'), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == ''
    report.append(dict(program=mode))
    print('program', mode, 'PASS', flush=True)
head = text.split('void solve()', 1)[0]
body = (root / 'tests/wida_header.cpp').read_text()
wrapped = '#include <cassert>\n' + head + '\nsigned main(int argc, char **argv) {\nstring mode = argc > 1 ? argv[1] : "ok";\n' + body + '\n}\n'
(out / 'wrapped.cpp').write_text(wrapped)
expect = '\n'.join([
    '1000007 2147483647',
    '1 3 6',
    '1 2 3 ',
    '3 2 1 ',
    '2 -3 3 -2',
    '0 -1 1',
    '24',
    '1 2 3 ',
    '1 2 3 ',
    '1 3 ',
    '3 2 1 ',
    'Yes',
    '1 7 8',
    '2',
]) + '\n'
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', '-DONLINE_JUDGE', *flags, str(out / 'wrapped.cpp'), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == expect
    report.append(dict(helpers=mode))
    print('helpers', mode, 'PASS', flush=True)
zero = subprocess.run([str(out / 'normal'), 'zero'], text=True, capture_output=True, env=env, timeout=30)
assert zero.returncode != 0
ub = out / 'pow'
subprocess.run([CXX, '-std=c++20', '-DONLINE_JUDGE', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(out / 'wrapped.cpp'), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'pow'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
report.append(dict(zero=zero.returncode, pow=bad.stderr.strip().splitlines()[-1]))
print('bounds PASS', flush=True)
import json
(root / 'verification/wida-header.json').write_text(json.dumps(dict(
    scope='Without ONLINE_JUDGE the build stops at bits/wida.h. With it, the empty program prints nothing. Helpers match the checked min, sum, sort, floor, loops and macros. floor(5,0) aborts and mypow(100000,2) overflows int. The int macro and freopen are not used by the empty program. No online AC.',
    blob='bf2c922a8bca7f3bbf97f1b5be2ca61d222b5c87', runs=report), indent=2) + '\n')
