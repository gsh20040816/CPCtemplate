"""Audit three incomplete WIDA misc snippets without promoting them to templates."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
fix = root / 'tests/fixtures/wida_misc'
blobs = {
    '03 - 字符调整.cpp': '37c6c358f1af2b5632e79b6b84e80400f5a8a38e',
    '04A - 二分算法（整数域）.cpp': '7a1e25df5b5ca0b0d07877d1fa97ca5e2d8edc32',
    '04B - 二分算法（实数域）.cpp': '9b36a370c76c04198dee56c3e40f0d296eb205cd',
}
texts = {}
for name, sha in blobs.items():
    data = (fix / name).read_bytes()
    assert hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == sha
    texts[name] = data.decode().replace('\r\n', '\n')
harness = (root / 'tests/wida_misc_snippets.cpp').read_text()
for snippet in [
    'int m = (lo + hi + 1) / 2;',
    'hi = m - 1;',
    'int m = (lo + hi) / 2;',
    'lo = m + 1;',
    'while (hi - lo > std::max(1.0, lo) * eps)',
    'while (hi - lo > 3 * eps)',
]:
    assert snippet in harness and any(snippet in text for text in texts.values())
chars = texts['03 - 字符调整.cpp']
assert 'for (int i = 1; i < l; i += 2)' in chars and "x = 26 + c - 'A';" in chars
assert 'int main' not in ''.join(texts.values())
assert 'constexpr real eps' in texts['04B - 二分算法（实数域）.cpp']
assert texts['04B - 二分算法（实数域）.cpp'].count('eps') == 5

out = root / 'build/wida-misc'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_misc_snippets.cpp'
expected = '\n'.join([
    'a1c',
    'aBcD',
    '0',
    'Z',
    '0 25 26 51 9',
    '7',
    '1',
    '1000000000',
    '5',
    '20',
    '1',
]) + '\n'
report = []
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe), 'cases'], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    lines = got.stdout.splitlines()
    assert lines[:11] == expected.splitlines()
    cut = float(lines[11])
    quad = float(lines[12])
    slope = float(lines[13])
    assert abs(cut - 2.5) < 1e-6
    assert quad < 1e-8
    assert abs(slope + 10000) < 1e-4
    report.append(dict(mode=mode, cut=cut, quadratic=quad, decreasing=slope))
    print(mode, 'cases PASS', cut, quad, slope, flush=True)

exe = out / 'overflow'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(exe)], check=True)
bad = subprocess.run([str(exe), 'overflow'], text=True, capture_output=True, env=env, timeout=30)
report.append(dict(mode='signed-overflow', returncode=bad.returncode, stderr=bad.stderr.strip()))
print('overflow', bad.returncode, bad.stderr.strip().splitlines()[-1] if bad.stderr else '', flush=True)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr

import json
(root / 'verification/wida-misc-snippets.json').write_text(json.dumps(dict(
    scope='Character toggle and two integer-search skeletons, plus relative real cut and ternary minimum. Snippets do not compile alone. No QOJ statement and no new template.',
    blobs=blobs, runs=report), indent=2) + '\n')
