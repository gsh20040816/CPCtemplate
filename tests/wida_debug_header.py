"""Audit the WIDA debug printers in wida.h."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida.h').read_bytes()
fix = root / 'tests/fixtures/wida_wida_h'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.h').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '316ac267170adf57303e93ea0e8a45f7b53ffce8'
text = blob.decode().replace('\r\n', '\n')
assert 'using namespace std;' in text and 'operator<<' in text
out = root / 'build/wida-wida-h'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_debug_header.cpp'
expect = '\n'.join([
    '[',
    '[7]',
    '[1, 2, 3]',
    '[4,5]',
    '[1,2,3]',
    'ab',
    'S[3,2,1>',
    'Q<1,2,3]',
    '[3, 2, 1]',
    '[1, 2, 3]',
    '●1▏2▏',
    '123',
]) + '\n'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == expect
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-wida-h.json').write_text(json.dumps(dict(
    scope='Empty vector prints an opening bracket only. One and three elements, pair, tuple, string, stack, queue and both heaps match the checked text. The debug printer uses its bullet marker. This file is not installed as bits/wida.h. No online AC.',
    blob='316ac267170adf57303e93ea0e8a45f7b53ffce8', runs=report), indent=2) + '\n')
