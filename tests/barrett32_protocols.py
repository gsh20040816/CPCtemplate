from pathlib import Path
import hashlib
import json
import os
import random
import subprocess
import sys
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records
row = next(r for r in records() if r['id'] == 'example-447')
assert (ROOT / row['snippet_file']).read_text() == row['snippet']
OUT = ROOT / 'build/mod-reduction'
rng = random.Random(665008)
mods = [1, 2, 3, 998244353, 2147483647, 2147483648, 4294967291, 4294967295]
mods += [rng.randrange(1, 1 << 32) for _ in range(30)]
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
           UBSAN_OPTIONS='halt_on_error=1')
report = {'scope': 'Independent Python integer multiplication for full uint32 modulus; exact printed and header programs, NDEBUG and sanitizer.', 'runs': []}
for form, source in [('header', '#include "' + str(ROOT / row['driver']) + '"\n'),
                     ('printed', row['program'])]:
    cpp = OUT / ('protocol-' + form + '.cpp')
    cpp.write_text(source)
    for mode, flags in [('normal', ['-O2', '-DNDEBUG']),
                        ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
        exe = OUT / (form + '-' + mode)
        subprocess.run([CXX, '-std=c++20', *flags, str(cpp), '-o', str(exe)], check=True)
        count = 0
        for mod in mods:
            pairs = [(rng.randrange(mod), rng.randrange(mod)) for _ in range(200)]
            pairs += [(0, 0), (mod - 1, mod - 1), (mod // 2, mod - 1)]
            data = f'{mod} {len(pairs)}\n' + ''.join(f'{a} {b}\n' for a, b in pairs)
            r = subprocess.run([str(exe)], input=data, text=True, capture_output=True,
                               env=env, timeout=10)
            assert r.returncode == 0 and not r.stderr, r.stderr
            assert list(map(int, r.stdout.split())) == [a * b % mod for a, b in pairs]
            count += len(pairs)
        report['runs'].append(dict(form=form, mode=mode, cases=count,
                                  source_sha256=hashlib.sha256(source.encode()).hexdigest()))
        print(form, mode, count, 'Python multiplication checks PASS', flush=True)
(ROOT / 'verification/barrett32-protocols.json').write_text(json.dumps(report, indent=2) + '\n')
