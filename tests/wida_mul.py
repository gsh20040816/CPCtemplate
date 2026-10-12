from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
out = root / 'build/wida-mul-audit'
out.mkdir(parents=True, exist_ok=True)
fixture = root / 'tests/fixtures/wida_poly_variants/12D-multiply.cpp'
data = fixture.read_bytes()
assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == '4c51d1709859104bb84e086e0d6d275691b6f81f'
report = dict(scope='Exact WIDA12D multiply source and current NttConvolution; independent integer convolution and direct DFT, full 2^23 analytic convolution. Local only, original QOJ application inaccessible.', runs=[])
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(root/'tests/wida_mul.cpp'), '-o', str(exe)], check=True)
    for task in ['small', 'empty', 'capacity-source', 'capacity-current', 'singleton']:
        r = subprocess.run([str(exe), task], capture_output=True, text=True, env=env, timeout=600)
        if task == 'singleton' and mode == 'sanitizer':
            assert r.returncode != 0 and 'shift exponent -1 is negative' in r.stderr, (mode, task, r)
        else:
            assert r.returncode == 0 and not r.stderr, (mode, task, r.returncode, r.stdout, r.stderr)
            assert 'PASS' in r.stdout or task == 'singleton', r.stdout
        report['runs'].append(dict(mode=mode, task=task, returncode=r.returncode, stdout=r.stdout, stderr=r.stderr))
        print(mode, task, r.stdout.strip() or 'expected singleton UB reproduced', flush=True)
paths = ['tests/wida_mul.cpp', 'tests/wida_mul.py', 'tests/fixtures/wida_poly_variants/12D-multiply.cpp', 'src/compact/ntt_convolution.hpp', 'src/compact/number_theory.hpp']
report['files'] = {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/wida-multiply.json').write_text(json.dumps(report, indent=2)+'\n')
