from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
source = root / 'tests/fixtures/wida_splay_sources/original.inc'
assert hashlib.sha256(source.read_bytes()).hexdigest() == '7bd0d66fd1634c6a785b6d317e82fc63ddb2320bc9f144890b8756092c586085'
results = {}
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    exe = root / 'build/wida-splay' / ('original-' + mode)
    subprocess.run([CXX, *flags, str(root / 'tests/wida_splay_source.cpp'), '-o', str(exe)], check=True)
    p = subprocess.run([str(exe)], text=True, capture_output=True, env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'), timeout=120)
    assert p.returncode == 0 and not p.stderr, p.stderr
    results[mode] = p.stdout.strip()
    print(mode, p.stdout.strip(), flush=True)
report = {'source_blob': '4d7c728da88ac87eb4bccaadb44a6640fc784b5f', 'files': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in ['tests/fixtures/wida_splay_sources/original.inc', 'tests/wida_splay_source.cpp', 'tests/wida_splay_source.py']}, 'runs': results, 'scope': 'Unchanged source function bodies, missing standard headers/i64 supplied; source insert followed by caller splay, add only on non-null roots, ordered merge, pointwise nonnegative ancestor version differences. Signed32 Splay fields kept within range; no JOI complete protocol or new online verdict.'}
(root / 'verification/wida-splay-source.json').write_text(json.dumps(report, indent=2) + '\n')
