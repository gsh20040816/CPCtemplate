"""Audit WIDA solid geometry after supplying the missing ld and P3 aliases."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-solid.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_solid'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'ae89fba9d6351b6356331ee586ec17c6a626b6e0'
text = blob.decode().replace('\r\n', '\n')
assert 'using ld' not in text and 'using P3' not in text and 'struct Point3' in text
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-solid-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'ld' in bare.stderr
body = (root / 'tests/wida_solid.cpp').read_text()
patched = text.replace('namespace Geometry { // 立体几何基础\n', 'namespace Geometry { // 立体几何基础\n    using ld = long double;\n', 1)
patched = patched.replace('    struct Line3 {', '    using P3 = Point3;\n    struct Line3 {', 1)
out = root / 'build/wida-solid'
out.mkdir(parents=True, exist_ok=True)
wrapped = '#include <bits/stdc++.h>\nusing namespace std;\n' + patched + '\nint main() {\nusing namespace Geometry;\n' + body + '\n}\n'
(out / 'wrapped.cpp').write_text(wrapped)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(out / 'wrapped.cpp'), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    rows = got.stdout.splitlines()
    assert rows[0] == '0 0 1 1'
    assert rows[1] == '12'
    assert rows[2] == '10 18 28'
    d, ln = map(float, rows[3].split())
    assert abs(d - 13) < 1e-9 and abs(ln - 13) < 1e-9
    assert rows[4] == '0 0 1'
    ux, uy, uz, finite = rows[5].split()
    assert abs(float(ux)) < 1e-9 and abs(float(uy)) < 1e-9 and abs(float(uz) - 1) < 1e-9 and finite == '0'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
import json
(root / 'verification/wida-solid.json').write_text(json.dumps(dict(
    scope='After defining ld and P3, cross, dot, distance and a plane normal match. operator* on two points is componentwise. Zero standardize is not finite. The source defines neither alias and does not compile alone. No online AC.',
    blob='ae89fba9d6351b6356331ee586ec17c6a626b6e0', runs=report), indent=2) + '\n')
