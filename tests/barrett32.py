from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/mod-reduction'
OUT.mkdir(parents=True, exist_ok=True)
raw = (ROOT / 'tests/fixtures/wida_mod_reduction/07E.cpp').read_bytes()
blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
assert blob == 'c5af9ebd28047a3c6bd7023cbe26150761c8e86b'
report = {'source_blob': blob, 'scope': 'Barrett32 and accelerated mint; not full 07E or Montgomery coverage.', 'runs': []}
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
           UBSAN_OPTIONS='halt_on_error=1')
for mode, flags in [('normal', ['-O2']),
                    ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    for name in ['barrett32', 'dynamic_modint', 'batch_units']:
        exe = OUT / (name + '-' + mode)
        subprocess.run([CXX, '-std=c++20', *flags, str(ROOT / 'tests' / (name + '.cpp')),
                        '-o', str(exe)], check=True)
        r = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=180)
        assert r.returncode == 0 and not r.stderr, r.stderr
        report['runs'].append(dict(mode=mode, test=name, output=r.stdout.strip()))
        print(mode, name, r.stdout.strip(), flush=True)
report['files'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in [
    'src/compact/barrett32.hpp', 'src/compact/dynamic_modint.hpp',
    'tests/barrett32.cpp', 'tests/barrett32.py', 'tests/dynamic_modint.cpp',
    'tests/batch_units.cpp', 'tests/fixtures/wida_mod_reduction/07E.cpp']}
(ROOT / 'verification/barrett32.json').write_text(json.dumps(report, indent=2) + '\n')
