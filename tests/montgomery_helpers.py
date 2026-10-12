from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/montgomery'
OUT.mkdir(parents=True, exist_ok=True)
raw = (ROOT / 'tests/fixtures/wida_mod_reduction/07D.cpp').read_bytes()
blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
assert blob == '17db0d506f744f101a8b40329b0e649265320b1a'
report = {'source_blob': blob, 'scope': 'Exact 07D source helpers against brute roots, multiplicative cycles, and power-of-two boundaries; no online AC', 'runs': []}
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = OUT / ('helpers-' + mode)
    subprocess.run([CXX, '-std=c++20', *flags, str(ROOT / 'tests/montgomery_helpers.cpp'), '-o', str(exe)], check=True)
    r = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=180)
    assert r.returncode == 0 and not r.stderr, r.stderr
    report['runs'].append(dict(mode=mode, output=r.stdout.strip()))
    print(mode, r.stdout.strip(), flush=True)
report['files'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in ['src/compact/montgomery_modint.hpp', 'tests/montgomery_helpers.cpp', 'tests/montgomery_helpers.py', 'tests/fixtures/wida_mod_reduction/07D.cpp', 'src/compact/primitive_root.hpp', 'src/compact/modular_sqrt.hpp', 'src/compact/mod64.hpp']}
(ROOT / 'verification/montgomery-helpers.json').write_text(json.dumps(report, indent=2) + '\n')
