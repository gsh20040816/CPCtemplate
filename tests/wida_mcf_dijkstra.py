"""Audit WIDA Dijkstra min-cost flow on small 0-based graphs."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-mcf-dijkstra.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_mcf_dijkstra'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '5962310cf2167a3559b9285ae18bd71fef59d01c'
text = blob.decode().replace('\r\n', '\n')
assert 'h[i] += dis[i]' in text
assert 'if (f < 0)' in text and text.count('//') >= 4
bare = subprocess.run([CXX, '-std=c++20', '-c', str(fix / 'main.cpp'), '-o', str(root / 'build/wida-mcf-dijkstra-bare.o')], text=True, capture_output=True)
assert bare.returncode != 0
out = root / 'build/wida-mcf-dijkstra'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_mcf_dijkstra.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe), 'ok'], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == '2 7\n2 5\n1 -5\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
ub = out / 'island'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(src), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub), 'island'], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
report.append(dict(island=bad.stderr.strip().splitlines()[-1]))
print('island PASS', flush=True)
import json
(root / 'verification/wida-mcf-dijkstra.json').write_text(json.dumps(dict(
    scope='0-based. Fully reached graphs: flow 2 cost 7, parallel edges flow 2 cost 5, and one negative edge flow 1 cost -5. An unreachable node makes h += INF overflow. Negative-cost reversal is commented out. Source does not compile alone. No online AC.',
    blob='5962310cf2167a3559b9285ae18bd71fef59d01c', runs=report), indent=2) + '\n')
