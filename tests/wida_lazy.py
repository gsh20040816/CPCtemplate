#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/wida-lazy'
OUT.mkdir(parents=True, exist_ok=True)
blobs = {'03A': 'e144f0105035446cece1b23d822df818807aab61', '04': 'ccda0bd0805bd83ced71a6b1ea517b15a968ffb5'}
for name, expected in blobs.items():
    b = (ROOT / f'tests/fixtures/wida_lazy/{name}.cpp').read_bytes()
    assert hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest() == expected
paths = ['tests/wida_lazy.cpp', 'tests/wida_lazy.py', 'src/compact/lazy_segtree.hpp']
paths += [f'tests/fixtures/wida_lazy/{name}.cpp' for name in blobs]
report = dict(scope='Exact WIDA03A max-add/point-set with supplied Info; WIDA04 generic additive summaries and search with supplied types. Source-only nonnegative all-active half. maintainL/R and original applications unverified; no online AC.', runs=[])
report['files'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = OUT / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(ROOT / 'tests/wida_lazy.cpp'), '-o', str(exe)], check=True)
    proc = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=300)
    assert proc.returncode == 0 and not proc.stderr and 'PASS' in proc.stdout, (mode, proc.returncode, proc.stdout, proc.stderr)
    report['runs'].append(dict(mode=mode, returncode=proc.returncode, stdout=proc.stdout))
    print(mode, proc.stdout.strip(), flush=True)
assert report['files'] == {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
(ROOT / 'verification/wida-lazy.json').write_text(json.dumps(report, indent=2) + '\n')
