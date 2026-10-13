"""Audit the WIDA permutation printer against the sorted distinct order."""
import hashlib, itertools, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-perm.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_perm'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'ffa41b5e4a9fe8bc71d8b9edf357e38cbc54d4fe'
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-perm-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-perm'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_perm.cpp'
cases = {
    '3\n3 1 2\n': [1, 2, 3],
    '2\n1 1\n': [1, 1],
    '0\n': [],
}
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    for raw, seq in cases.items():
        got = subprocess.run([str(exe)], input=raw, text=True, capture_output=True, env=env, timeout=30, check=True)
        assert got.stderr == ''
        lines = [tuple(int(x) for x in line.split()) for line in got.stdout.splitlines() if line.split()]
        if not seq:
            assert got.stdout == '\n' and lines == []
        else:
            expect = sorted(set(itertools.permutations(sorted(seq))))
            assert lines == expect
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-perm.json').write_text(json.dumps(dict(
    scope='After sorting, distinct permutations of 3 1 2 and the single permutation of 1 1 match. n=0 prints one blank line. Failed input leaves n uninitialized and was not executed. The snippet does not compile alone. No online AC.',
    blob='ffa41b5e4a9fe8bc71d8b9edf357e38cbc54d4fe', runs=report), indent=2) + '\n')
