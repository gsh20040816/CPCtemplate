#!/usr/bin/env python3
"""Independent BFS oracle, exhaustive states, and recursive large-tree tests."""
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
build = root / 'build/color-components'
build.mkdir(parents=True, exist_ok=True)

def stack():
    if sys.platform == 'darwin':
        return
    _, hard = resource.getrlimit(resource.RLIMIT_STACK)
    resource.setrlimit(resource.RLIMIT_STACK, (min(512 << 20, hard) if hard != -1 else 512 << 20, hard))

env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
report = {'scope': 'Local BFS oracle and shape formulas; no judge acceptance or runtime-ranking claim.', 'runs': []}
for mode, flags in [('normal', ['-O2']), ('ndebug', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'])]:
    exe = build / ('probe-' + mode)
    command = [CXX, '-std=c++17', *flags, str(root / 'tests/color_components_probe.cpp'), '-o', str(exe)]
    if sys.platform == 'darwin':
        command.append('-Wl,-stack_size,0x20000000')
    subprocess.run(command, check=True)
    for args in [[], ['large']]:
        run = subprocess.run([str(exe), *args], check=True, capture_output=True, text=True, env=env, preexec_fn=stack, timeout=240)
        report['runs'].append({'mode': mode, 'args': args, 'stdout': run.stdout.strip()})
        print(mode, args, run.stdout.strip(), flush=True)
report['sha256'] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [root / 'src/compact/color_components.hpp', root / 'tests/color_components_probe.cpp', Path(__file__)]}
(root / 'verification/color-components.json').write_text(json.dumps(report, indent=2) + '\n')
