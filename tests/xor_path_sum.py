import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'build/xor-path-sum'
out.mkdir(parents=True, exist_ok=True)
report = {'runs': [], 'scope': 'Local independent unordered simple vertex-path xor enumeration including singleton paths; unchanged source runtime in small domain, separate raw-source overflow probe. No original problem protocol or online verdict.'}
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-Wall', '-Wextra']
    flags += ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    if platform.system() == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    exe = out / mode
    command = [CXX, *flags, str(ROOT / 'tests/xor_path_sum.cpp'), '-o', str(exe)]
    subprocess.run(command, check=True)
    env = os.environ.copy()
    env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    run = subprocess.run([str(exe)], capture_output=True, text=True, env=env, timeout=240)
    assert run.returncode == 0 and not run.stderr, run.stderr
    entry = {'mode': mode, 'command': command, 'result': run.stdout.strip()}
    print(mode, run.stdout.strip(), flush=True)
    probe = subprocess.run([str(exe), 'source-wide'], capture_output=True, text=True, env=env, timeout=60)
    if mode == 'sanitizer':
        assert probe.returncode != 0 and 'signed integer overflow' in probe.stderr, probe.stderr
        entry['source_wide_expected_ubsan_failure'] = probe.stderr
    else:
        entry['source_wide_output'] = probe.stdout.strip()
        entry['independent_wide_expected'] = 2500100001
    report['runs'].append(entry)
report['files'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in ['src/compact/xor_path_sum.hpp', 'tests/xor_path_sum.cpp', 'tests/xor_path_sum.py', 'tests/fixtures/wida_xor_path/07C.cpp']}
(ROOT / 'verification/xor-path-sum.json').write_text(json.dumps(report, indent=2) + '\n')
