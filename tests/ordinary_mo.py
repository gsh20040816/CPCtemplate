from pathlib import Path
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parents[1]
build = root / 'build/ordinary-mo'
build.mkdir(parents=True, exist_ok=True)
header = root / 'src/compact/mo.hpp'
test = root / 'tests/ordinary_mo.cpp'
copied = build / 'copied.cpp'
copied.write_text(test.read_text().replace('#include "../src/compact/mo.hpp"', header.read_text().replace('#pragma once\n', '')))
report = {'source_sha256': hashlib.sha256(header.read_bytes()).hexdigest(), 'oracle': 'exact active position set at every answer, legal add/delete transitions and final empty state', 'checks': {}}
for mode in ['normal', 'sanitizer']:
    flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    for form in ['header', 'ndebug', 'copied']:
        exe = build / (mode + '-' + form)
        subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', *flags, *(['-DNDEBUG'] if form == 'ndebug' else []), str(copied if form == 'copied' else test), '-o', str(exe)], check=True)
        result = subprocess.check_output([str(exe)], text=True).strip()
        report['checks'][mode + '-' + form] = result
        print(mode, form, result, flush=True)
report['status'] = 'pass'
(root / 'verification/ordinary-mo-local.json').write_text(json.dumps(report, indent=2) + '\n')
