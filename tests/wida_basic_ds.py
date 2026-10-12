#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/wida-basic-ds'
OUT.mkdir(parents=True, exist_ok=True)
fixture = ROOT / 'tests/fixtures/wida_basic_ds'
for item in json.loads((fixture / 'provenance.json').read_text()):
    name = item['path'].split('/')[-1][:3] + '.cpp'
    b = (fixture / name).read_bytes()
    assert hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest() == item['sha']
paths = ['tests/wida_basic_ds.cpp', 'tests/wida_basic_ds.py',
         'src/compact/data_structure.hpp', 'src/compact/segtree.hpp']
paths += [str(p.relative_to(ROOT)) for p in sorted(fixture.glob('*.cpp'))]
report = dict(scope='Six exact WIDA sources: exhaustive small frequencies, literal partition snapshots, random max search and noncommutative concatenation. Original applications and generic algebraic types not exhaustively covered; no new online AC.', runs=[])
report['files'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for mode, flags in [('normal', ['-O2', '-DNDEBUG']),
                    ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = OUT / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(ROOT / 'tests/wida_basic_ds.cpp'), '-o', str(exe)], check=True)
    tasks = ['normal'] if mode == 'normal' else ['normal', 'empty-old', 'empty-new']
    for task in tasks:
        proc = subprocess.run([str(exe), task], text=True, capture_output=True, env=env, timeout=300)
        if task == 'normal':
            assert proc.returncode == 0 and not proc.stderr and 'PASS' in proc.stdout, (mode, proc.returncode, proc.stdout, proc.stderr)
        else:
            assert proc.returncode != 0 and 'runtime error' in proc.stderr, (mode, task, proc.returncode, proc.stderr)
        report['runs'].append(dict(mode=mode, task=task, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr))
        print(mode, task, proc.stdout.strip() or 'expected empty-source failure', flush=True)
assert report['files'] == {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
(ROOT / 'verification/wida-basic-ds.json').write_text(json.dumps(report, indent=2) + '\n')
