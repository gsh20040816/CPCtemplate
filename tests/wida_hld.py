"""Audit the WIDA HLD against parent climbing and rerooted subtree queries."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-hld.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_hld'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '3f383ecf74fcc60cfc60c86cfcbd4670149e32b5'
text = blob.decode().replace('\r\n', '\n')
assert 'bool isAncester(int u, int v)' in text
assert 'return lca(a, b) ^ lca(b, c) ^ lca(c, a);' in text
out = root / 'build/wida-hld'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_hld.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=60, check=True)
    assert got.stderr == ''
    checks = int(got.stdout.strip())
    assert checks > 1000
    report.append(dict(mode=mode, checks=checks))
    print(mode, checks, 'PASS', flush=True)

ub = out / 'twice'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=address', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'twice'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'heap-buffer-overflow' in bad.stderr
report.append(dict(second_work='seq overflow', stderr=bad.stderr.strip().splitlines()[-1]))
print('second work overflow recorded', flush=True)
import json
(root / 'verification/wida-hld.json').write_text(json.dumps(dict(
    scope='0-based HLD. One work() matches parent climbing for lca, distance, jump, ancestor and rerooted parent/size/lca. A second work() does not reset cur and writes past seq. No online AC.',
    blob='3f383ecf74fcc60cfc60c86cfcbd4670149e32b5', runs=report), indent=2) + '\n')
