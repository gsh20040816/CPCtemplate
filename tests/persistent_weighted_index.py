from pathlib import Path
import hashlib
import json
import os
import resource
import subprocess
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
out = root / 'build/wida-splay'
out.mkdir(parents=True, exist_ok=True)
results = {}
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    if os.uname().sysname == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    else:
        soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK, (hard, hard))
    exe = out / ('weighted-' + mode)
    subprocess.run([CXX, *flags, str(root / 'tests/persistent_weighted_index.cpp'), '-o', str(exe)], check=True)
    p = subprocess.run([str(exe)], text=True, capture_output=True, env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'), timeout=120)
    assert p.returncode == 0 and not p.stderr, p.stderr
    results[mode] = p.stdout.strip()
    print(mode, p.stdout.strip(), flush=True)
report = {'runs': results, 'files': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in ['src/compact/persistent_weighted_index.hpp', 'tests/persistent_weighted_index.cpp', 'tests/persistent_weighted_index.py']}, 'scope': 'Local core only; count and intermediate sums must fit int/signed64; successor differences must be pointwise nonnegative. Integration, printed examples and official protocol remain pending.'}
(root / 'verification/persistent-weighted-index-core.json').write_text(json.dumps(report, indent=2) + '\n')
