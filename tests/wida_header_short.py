"""Audit the WIDA short online header as a complete program."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-header-short.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_header_short'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'b65beaf95791c63fad526c7f5be34fbcc130c43d'
text = blob.decode().replace('\r\n', '\n')
assert '#include <bits/wida.h>' in text and 'for (cin >> Task; Task; Task--)' in text
bare = subprocess.run([CXX, '-std=c++20', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-header-short-bare')], text=True, capture_output=True)
assert bare.returncode != 0 and 'wida.h' in bare.stderr
out = root / 'build/wida-header-short'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', '-DONLINE_JUDGE', *flags, str(fix / 'main.cpp'), '-o', str(exe)], check=True)
    for raw in ['', '0\n', '4\n']:
        got = subprocess.run([str(exe)], input=raw, text=True, capture_output=True, env=env, timeout=30, check=True)
        assert got.stderr == '' and got.stdout == ''
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-header-short.json').write_text(json.dumps(dict(
    scope='Without ONLINE_JUDGE the local build cannot find bits/wida.h. With that macro, empty input, 0 and 4 all exit and print nothing because the loop body is empty. A negative Task is not run. Precision is not observed. No online AC.',
    blob='b65beaf95791c63fad526c7f5be34fbcc130c43d', runs=report), indent=2) + '\n')
