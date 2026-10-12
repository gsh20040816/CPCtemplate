from pathlib import Path
import json
import os
import subprocess
import sys
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from audit_copy_context import extract_components, PRELUDE
entries = {r['symbol']: r for r in extract_components(json.loads((root / 'docs/catalog.json').read_text()))}
results = {}
for name, symbol in [('shift_splay', 'ShiftSplay'), ('persistent_weighted_index', 'PersistentWeightedIndex')]:
    test = (root / 'tests' / (name + '.cpp')).read_text().split('\n', 1)[1]
    src = root / 'build/wida-splay' / (name + '-copy.cpp')
    src.write_text(PRELUDE + entries[symbol]['code'] + '\n' + test)
    for mode in ['normal', 'sanitizer']:
        flags = ['-std=c++20', '-O2']
        if mode == 'sanitizer':
            flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        if os.uname().sysname == 'Darwin':
            flags += ['-Wl,-stack_size,0x20000000']
        exe = src.with_suffix('.' + mode)
        subprocess.run([CXX, *flags, str(src), '-o', str(exe)], check=True)
        p = subprocess.run([str(exe)], text=True, capture_output=True, env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'), timeout=120)
        assert p.returncode == 0 and not p.stderr, p.stderr
        results[symbol + '-' + mode] = {'code_sha256': entries[symbol]['code_sha256'], 'output': p.stdout.strip()}
        print(symbol, mode, p.stdout.strip(), flush=True)
(root / 'verification/wida-splay-copy.json').write_text(json.dumps(results, indent=2) + '\n')
