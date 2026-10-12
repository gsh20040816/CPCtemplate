import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'build/dynamic-peach-tree'
out.mkdir(parents=True, exist_ok=True)
report = {'runs': [], 'scope': 'Local static recurrence, unchanged WIDA source, random relabeled dynamic trees, copies and 200000-node chain/star. No online verdict.'}
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-Wall', '-Wextra']
    flags += ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    if platform.system() == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    exe = out / mode
    command = [CXX, *flags, str(ROOT / 'tests/dynamic_peach_tree.cpp'), '-o', str(exe)]
    subprocess.run(command, check=True)
    env = os.environ.copy()
    env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    run = subprocess.run([str(exe)], capture_output=True, text=True, env=env, timeout=240)
    assert run.returncode == 0 and not run.stderr, run.stderr
    entry = {'mode': mode, 'command': command, 'result': run.stdout.strip()}
    print(mode, run.stdout.strip(), flush=True)
    report['runs'].append(entry)
report['files'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in ['src/compact/dynamic_peach_tree.hpp', 'tests/dynamic_peach_tree.cpp', 'tests/dynamic_peach_tree.py', 'tests/fixtures/wida_peach/07B.cpp']}
(ROOT / 'verification/dynamic-peach-tree.json').write_text(json.dumps(report, indent=2) + '\n')
