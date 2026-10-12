from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
out = root / 'build/wida-balanced'
out.mkdir(exist_ok=True)
results = {}
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    exe = out / ('parity-core-' + mode)
    subprocess.run([CXX, *flags, str(root / 'tests/persistent_parity_index.cpp'), '-o', str(exe)], check=True)
    p = subprocess.run([str(exe)], text=True, capture_output=True,
                       env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'), timeout=120)
    assert p.returncode == 0 and not p.stderr, p.stderr
    results[mode] = p.stdout.strip()
    print(mode, p.stdout.strip(), flush=True)
files = ['src/compact/persistent_parity_index.hpp', 'tests/persistent_parity_index.cpp',
         'tests/persistent_parity_index.py', 'tests/fixtures/wida_parity_index/08A.cpp']
(root / 'verification/persistent-parity-index.json').write_text(json.dumps({
    'runs': results, 'original_problem_protocol_verified': False,
    'files': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in files}
}, indent=2) + '\n')
