from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
out = root / 'build/wida-fraction'
out.mkdir(parents=True, exist_ok=True)
report = {'scope': 'Unchanged source audit: x/=x aliasing counterexample, not new fraction-template coverage.', 'runs': []}
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    cmd = [CXX, '-std=c++20', *flags, str(root / 'tests/wida_fraction_source.cpp'), '-o', str(exe)]
    subprocess.run(cmd, check=True)
    env = os.environ.copy()
    env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    run = subprocess.run([str(exe)], capture_output=True, text=True, env=env, check=True)
    assert not run.stderr
    assert run.stdout.strip() == 'original x / x = 1; original x /= x = 1/3'
    report['runs'].append({'mode': mode, 'command': cmd, 'result': run.stdout.strip()})
    print(mode, run.stdout.strip())
report['files'] = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in ['tests/fixtures/wida_fraction/Frac.cpp', 'tests/wida_fraction_source.cpp', 'tests/wida_fraction_source.py']}
(root / 'verification/wida-fraction-source.json').write_text(json.dumps(report, indent=2)+'\n')
