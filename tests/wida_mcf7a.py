"""Audit the old WIDA cost-flow edge orientation and potential update."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
fix = root / 'tests/fixtures/wida_mcf7a'
fix.mkdir(parents=True, exist_ok=True)
blob = Path('/tmp/wida-mcf7a.cpp').read_bytes()
(fix / 'main.cpp').write_bytes(blob)
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '478da7e5f988c4959a9af238ec9d0e975515d6a3'
text = blob.decode().replace('\r\n', '\n')
assert 'e.emplace_back(v, 0, f);' in text
assert 'e.emplace_back(u, c, -f);' in text
assert 'h[i] += dis[i]' in text
(root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes()
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())

out = root / 'build/wida-mcf7a'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_mcf7a.cpp'
report = []
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe), 'cases'], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    assert got.stdout == '0 0\n5 -15\n5 15\n'
    report.append(dict(mode=mode, stdout=got.stdout))
    print(mode, 'PASS', flush=True)

ub = out / 'overflow'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'overflow'], text=True, capture_output=True, env=env, timeout=30)
line = bad.stderr.strip().splitlines()[-1] if bad.stderr else ''
print('overflow', bad.returncode, line, flush=True)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
report.append(dict(mode='overflow', returncode=bad.returncode, stderr=line))

import json
(root / 'verification/wida-mcf7a.json').write_text(json.dumps(dict(
    scope='Commented addEdge keeps only the negative-cost orientation: requested u->v has cap 0, and v->u has cap c and cost -f. Two-node positive cost therefore sends nothing from u to v. Unreachable potential update overflows. Not the library MinCostFlow. No online AC.',
    blob='478da7e5f988c4959a9af238ec9d0e975515d6a3', runs=report), indent=2) + '\n')
