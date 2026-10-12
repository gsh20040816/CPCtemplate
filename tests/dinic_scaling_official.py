"""Compare normal/scaled Dinic against downloaded LOJ127 official answers."""
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from compiler_config import CXX
from dinic_scaling import core, enabled

ROOT = Path(__file__).resolve().parents[1]
data = Path(sys.argv[1]).resolve()
out = ROOT / 'build/dinic-scaling'
prelude = '#include <cassert>\n#include <bits/stdc++.h>\nusing namespace std;\n'
main = (ROOT / 'verify/luogu/P3376.compact.cpp').read_text().split('\n', 1)[1]
report = {'source': 'https://loj.ac/p/127/files', 'timing': 'Local process wall seconds including input/output; not OJ verdict or ranking.', 'runs': []}
inputs = sorted(data.glob('*.in'))
assert len(inputs) == 25
for variant, code, sanitize in [('ordinary', core(), False), ('scaling', enabled(core()), False), ('scaling-sanitizer', enabled(core()), True)]:
    cpp = out / (variant + '-loj127.cpp')
    cpp.write_text(prelude + code + main)
    exe = out / (variant + '-loj127')
    flags = ['-std=c++20', '-O2'] if not sanitize else ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    if platform.system() == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    command = [CXX, *flags, str(cpp), '-o', str(exe)]
    subprocess.run(command, check=True)
    env = os.environ.copy()
    env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    entry = {'variant': variant, 'source_sha256': hashlib.sha256(cpp.read_bytes()).hexdigest(), 'command': command, 'cases': []}
    report['runs'].append(entry)
    for inp in inputs:
        raw = inp.read_bytes()
        expected = inp.with_suffix('.out').read_bytes()
        start = time.monotonic()
        try:
            run = subprocess.run([str(exe)], input=raw, capture_output=True, env=env, timeout=120)
            seconds = time.monotonic() - start
            passed = run.returncode == 0 and not run.stderr and run.stdout.split() == expected.split()
            result = {'case': inp.name, 'passed': passed, 'seconds': seconds, 'returncode': run.returncode, 'stderr': run.stderr.decode(), 'actual': run.stdout.decode().strip(), 'expected': expected.decode().strip()}
        except subprocess.TimeoutExpired:
            result = {'case': inp.name, 'passed': False, 'timeout_seconds': 120}
        result.update(input_sha256=hashlib.sha256(raw).hexdigest(), answer_sha256=hashlib.sha256(expected).hexdigest())
        entry['cases'].append(result)
        (ROOT / 'verification/dinic-scaling-loj127.json').write_text(json.dumps(report, indent=2) + '\n')
        print(variant, inp.name, result, flush=True)
