from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
out = root / 'build/fps-newton'
rows = []
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / ('wida-capacity-' + mode)
    subprocess.run([CXX, '-std=c++20', *flags, str(root/'tests/wida_poly_capacity.cpp'), '-o', str(exe)], check=True)
    r = subprocess.run([str(exe)], capture_output=True, text=True, timeout=600, env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'))
    assert r.returncode == 0 and not r.stderr, (r.returncode, r.stdout, r.stderr)
    rows.append(dict(mode=mode, output=r.stdout))
    print(mode, r.stdout, flush=True)
paths = ['tests/wida_poly_capacity.cpp', 'tests/wida_poly_capacity.py', 'tests/fixtures/wida_montgomery_poly/12C.cpp', 'src/compact/ntt_convolution.hpp', 'src/compact/number_theory.hpp']
report = dict(scope='Original 12C convolution/inverse/first inverse-root capacity at 998244353,167772161,469762049; independent small convolution and analytic full-length outputs. Mod97 hidden root-table precondition counterexample. Not all operations/moduli, repeated inverse-root, applications, or online AC.', runs=rows, files={p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths})
(root/'verification/wida-poly-capacity.json').write_text(json.dumps(report, indent=2)+'\n')
