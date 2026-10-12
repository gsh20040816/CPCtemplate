from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
out = root / 'build/bivariate'
report = dict(scope='Original exact 12A C=1024 bivariate inverse and current replacement, a=1-x-y, every coefficient checked by integer Pascal recurrence. Source constant-product UB is separately expected. No online AC.', runs=[])
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / ('capacity-' + mode)
    subprocess.run([CXX, '-std=c++20', *flags, str(root/'tests/bivariate_capacity.cpp'), '-o', str(exe)], check=True)
    for implementation in ['original', 'current']:
        r = subprocess.run([str(exe), implementation], text=True, capture_output=True, env=env, timeout=600)
        assert r.returncode == 0 and not r.stderr, (mode, implementation, r.returncode, r.stdout, r.stderr)
        print(mode, implementation, r.stdout, flush=True)
        report['runs'].append(dict(mode=mode, implementation=implementation, output=r.stdout))
    r = subprocess.run([str(exe), 'constant'], text=True, capture_output=True, env=env, timeout=30)
    if mode == 'sanitizer':
        assert r.returncode != 0 and 'shift exponent -1 is negative' in r.stderr, (r.returncode, r.stdout, r.stderr)
    else:
        assert r.returncode == 0 and r.stdout.strip() == '6' and not r.stderr
    report['runs'].append(dict(mode=mode, test='original-constant-product', returncode=r.returncode, stdout=r.stdout, stderr=r.stderr))
paths = ['tests/bivariate_capacity.cpp', 'tests/bivariate_capacity.py', 'tests/fixtures/wida_poly_variants/12A.cpp', 'src/compact/bivariate_inverse.hpp', 'src/compact/ntt_2d.hpp', 'src/compact/fps_inverse.hpp', 'src/compact/ntt_convolution.hpp', 'src/compact/number_theory.hpp']
report['files'] = {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(root/'verification/bivariate-capacity.json').write_text(json.dumps(report, indent=2)+'\n')
