from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
build = root / 'build/plug-cycles'
build.mkdir(parents=True, exist_ok=True)
header = root / 'src/compact/plug_cycles.hpp'
test = root / 'tests/plug_cycles.cpp'
copied = build / 'copied.cpp'
copied.write_text(test.read_text().replace('#include "../src/compact/plug_cycles.hpp"', header.read_text().replace('#pragma once\n', '')).replace('#include "../src/compact/plug_cycle.hpp"', '#include "' + str(root / 'src/compact/plug_cycle.hpp') + '"'))
report = {'status': 'pass', 'source_sha256': hashlib.sha256(header.read_bytes()).hexdigest(), 'checks': {}}
for mode in ['normal', 'sanitizer']:
    flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=all']
    for form in ['header', 'ndebug', 'copied']:
        exe = build / (mode + '-' + form)
        cmd = [CXX, '-std=c++20', '-I/opt/homebrew/include', *flags, *(['-DNDEBUG'] if form == 'ndebug' else []), str(copied if form == 'copied' else test), '-o', str(exe)]
        subprocess.run(cmd, check=True)
        start = time.monotonic()
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
        output = subprocess.check_output([str(exe)], text=True, timeout=240, env=env).strip()
        report['checks'][mode + '-' + form] = {'result': output, 'seconds': round(time.monotonic() - start, 3)}
        print(mode, form, output, flush=True)
(root / 'verification/plug-cycles-local.json').write_text(json.dumps(report, indent=2) + '\n')
