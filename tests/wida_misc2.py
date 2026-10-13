"""Audit WIDA int128 helpers, numeric overloads, and the fread reader."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
fix = root / 'tests/fixtures/wida_misc2'
blobs = {
    '01 - int128 库函数自定义.cpp': '91a016e76a923cedf9f15636d39064f06c0a27ce',
    '02 - 常用库函数重载.cpp': '0b91ba07bf4066c04479a158f5507d7939b2ed66',
    '05 - 快读.cpp': '8f665a510e27028bcd803f274c9cc741f2a0eee6',
}
for name, sha in blobs.items():
    data = (fix / name).read_bytes()
    assert hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == sha
text = {name: (fix / name).read_text().replace('\r\n', '\n') for name in blobs}
assert 'while (n > 0)' in text['01 - int128 库函数自定义.cpp']
assert 'hi = 1E16' in text['01 - int128 库函数自定义.cpp']
assert 'std::sqrt(n)' in text['02 - 常用库函数重载.cpp']
assert 'a[std::fread(a, 1, sizeof a, stdin)] = 0' in text['05 - 快读.cpp']
assert text['05 - 快读.cpp'].count('IO &operator>>') == 4
assert text['05 - 快读.cpp'].count('while (*s') == 2

out = root / 'build/wida-misc2'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')

def build(name, src, flags):
    exe = out / name
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    return exe

def run(exe, args=(), data='', timeout=30, check=True):
    return subprocess.run([str(exe), *args], input=data, text=True, capture_output=True, env=env, timeout=timeout, check=check)

report = []
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = build('int128-' + mode, root / 'tests/wida_int128_misc.cpp', flags)
    got = run(exe)
    assert got.stderr == ''
    assert got.stdout == '\n'.join([
        '0|1234567890123456789||',
        '123|0|-288|',
        '10000000000000000|0|1|1|10000000000000000|10000000000000000|0|',
        '0|5|-5|',
        '',
    ])
    over = build('over-' + mode, root / 'tests/wida_overloads.cpp', flags)
    got = run(over)
    assert got.stderr == ''
    lines = got.stdout.splitlines()
    assert 'T 1 1' in lines and 'T 2 2' in lines and 'T 3 2' in lines
    assert 'T 10 4' in lines and 'T 11 5' in lines
    assert 'C 2 -1 -2 1' in lines and 'F 1 -2 -2 0' in lines
    assert 'M 4' in lines and 'G 5 -5' in lines and 'L 0 1 2 3 2 -1' in lines
    squares = {}
    for line in lines:
        parts = line.split()
        if len(parts) != 2 or not all(part.lstrip('-').isdigit() for part in parts):
            continue
        n, s = map(int, parts)
        squares[n] = s
        assert s * s <= n < (s + 1) * (s + 1)
    fast = build('fast-' + mode, root / 'tests/wida_fastio.cpp', flags)
    got = run(fast, ('nums',), '0012 34\n4294967296\n')
    assert got.stderr == '' and got.stdout == '12 34 0\n'
    got = run(fast, ('one',), '0\n')
    assert got.stderr == '' and got.stdout == '0\n'
    report.append(dict(mode=mode, squares=squares))
    print(mode, 'core PASS', flush=True)

hangs = []
exe = build('get0', root / 'tests/wida_overloads.cpp', ['-O2', '-DNDEBUG'])
got = run(exe, ('get0',))
assert got.stderr == '' and got.stdout == '-3037000500\n'
hangs.append(dict(label='get0-o2', stdout=got.stdout.strip()))
exe = build('logi', root / 'tests/wida_overloads.cpp', ['-O2', '-DNDEBUG'])
try:
    run(exe, ('logi',), timeout=2)
    raise SystemExit('logi(1, 2) returned')
except subprocess.TimeoutExpired:
    hangs.append(dict(label='logi-one', finished=False))

ub = build('ub', root / 'tests/wida_overloads.cpp', ['-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined'])
for arg in ('ceil-overflow', 'sqrt-overflow', 'get0'):
    bad = run(ub, (arg,), check=False)
    assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
    hangs.append(dict(label=arg, returncode=bad.returncode, stderr=bad.stderr.strip().splitlines()[-1]))

empty = build('empty', root / 'tests/wida_fastio.cpp', ['-O1', '-g', '-fsanitize=address'])
bad = run(empty, ('one',), '', check=False)
assert bad.returncode != 0 and 'AddressSanitizer' in bad.stderr
report.append(dict(empty_read=True))

layout = build('layout', root / 'tests/wida_fastio.cpp', ['-O2', '-DNDEBUG'])
got = run(layout, ('layout',), '')
assert got.returncode == 0 and got.stdout == '1\n'
report.append(dict(full_buffer_lands_on_output_array=True))

link = subprocess.run([CXX, '-std=c++20', '-O2', str(root / 'tests/wida_fastio_missing.cpp'), '-o', str(out / 'missing')], text=True, capture_output=True)
assert link.returncode != 0 and 'undefined symbol' in (link.stderr + link.stdout).lower()
report.append(dict(missing_int64_reader=True, hangs=hangs))
print('boundaries PASS', flush=True)

import json
(root / 'verification/wida-misc2.json').write_text(json.dumps(dict(
    scope='int128 output skips negatives and sqrt search stops at 1e16. floor/ceil formulas are for the tested signs only. get(0) decrements until signed overflow; logi(1,2) does not advance. A full fread lands on the output array, and a missing number walks off the global. No new template or online AC.',
    blobs=blobs, runs=report), indent=2) + '\n')
