"""Full source/copy/API checks; online AC is recorded separately."""
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
SAN = '--sanitize' in sys.argv
MODE = 'sanitizer' if SAN else 'normal'
WORK = ROOT / 'build/dominance4d' / MODE
WORK.mkdir(parents=True, exist_ok=True)
header = ROOT / 'src/compact/dominance_4d.hpp'
code = header.read_text().replace('#pragma once\n', '')
flags = ['-std=c++20', '-O1' if SAN else '-O2']
if SAN:
    flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
commands = []
def compile(src, exe, extra=()):
    cmd = [CXX, *flags, *extra, str(src), '-o', str(exe)]
    commands.append(cmd)
    subprocess.run(cmd, check=True, capture_output=True, text=True)
def run(exe, data=''):
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env=env, timeout=180)
    assert p.returncode == 0, p.stderr
    return p.stdout
core_path = ROOT / 'tests/dominance_4d.cpp'
core_source = core_path.read_text().replace('#include "../src/compact/dominance_4d.hpp"', code)
cores = {}
for form in ['header', 'ndebug', 'copied']:
    src = core_path
    exe = WORK / ('core-' + form)
    if form == 'copied':
        src = exe.with_suffix('.cpp')
        src.write_text(core_source)
    compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
    cores[form] = run(exe).strip()
    print(MODE, form, cores[form], flush=True)
samples = [('6\n2 1 4 1\n5 6 6 5\n3 3 3 4\n6 4 5 6\n4 5 2 3\n1 2 1 2\n', 9),
           ('15\n13 1 2 3\n2 2 13 11\n10 10 7 2\n3 6 14 14\n1 12 9 15\n12 14 8 8\n8 13 15 5\n4 8 12 10\n5 3 1 4\n7 5 11 1\n9 11 6 13\n6 15 10 9\n15 9 5 12\n14 4 4 6\n11 7 3 7\n', 15)]
cases = []
rng = random.Random(21566)
for trial in range(100):
    p = [[rng.randrange(-8, 9) for _ in range(4)] for _ in range(rng.randrange(60))]
    want = []
    for strict in [False, True]:
        want.append([sum(i != j and all((a < b if strict else a <= b) for a, b in zip(source, target))
                         for j, source in enumerate(p)) for i, target in enumerate(p)])
    cases.append((p, want))
drivers = ['verify/qoj/21566.compact.cpp', 'verify/api/dominance_4d.compact.cpp']
results = {}
for path in drivers:
    forms = {}
    for form in ['header', 'ndebug', 'expanded', 'copied']:
        exe = WORK / (Path(path).stem + '-' + form)
        src = ROOT / path
        program = src.read_text().replace('#include "../../src/compact/dominance_4d.hpp"', code)
        if form in ['expanded', 'copied']:
            src = exe.with_suffix('.cpp')
            if form == 'expanded':
                program = '#include <bits/stdc++.h>\nusing namespace std;\n' + program
            src.write_text(program)
        if path == drivers[0] and form == 'copied':
            (ROOT / 'build/dominance4d/21566.cpp').write_text(program)
        compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
        if path == drivers[0]:
            for data, want in samples:
                assert int(run(exe, data)) == want
        for p, want in cases:
            data = ''.join(' '.join(map(str, point)) + '\n' for point in p)
            if path == drivers[0]:
                assert int(run(exe, f'{len(p)}\n' + data)) == sum(want[1])
            else:
                for strict in [0, 1]:
                    assert list(map(int, run(exe, f'{len(p)} {strict}\n' + data).split())) == want[strict]
        forms[form] = 'pass'
        print(MODE, path, form, 'PASS', flush=True)
    results[path] = forms
large = WORK / 'large'
compile(ROOT / 'tests/dominance_4d_large.cpp', large)
large_output = run(large)
mutants = {}
if not SAN:
    for name, old, new in [('tie-order', 'strict ? a.query > b.query : a.query < b.query', 'a.query < b.query'),
                           ('fourth-dimension', 'sum(a[j].w - strict)', 'sum(a[j].w)'),
                           ('rollback', 'add(a[j].w, -1)', 'add(a[j].w, 0)'),
                           ('self', 'for (int &value : ans) value--;', 'for (int &value : ans) value -= 0;')]:
        assert old in core_source
        src = WORK / ('mutant-' + name + '.cpp')
        exe = src.with_suffix('')
        src.write_text(core_source.replace(old, new))
        compile(src, exe)
        p = subprocess.run([str(exe)], capture_output=True, timeout=20)
        assert p.returncode != 0, name
        mutants[name] = 'detected'
files = [str(header.relative_to(ROOT)), 'tests/dominance_4d.cpp', 'tests/dominance_4d_large.cpp', 'tests/dominance_4d.py', *drivers]
report = dict(status='pass', mode=MODE, core=cores, drivers=results, large=large_output, mutants=mutants, commands=commands,
              source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
              scope='Independent quadratic comparisons for both modes; all Boolean-grid subsets; signed64 extremes and duplicates; two official samples; n100000 formulas and reduction to independent 3D template. OJ and ranking separate.')
(ROOT / f'verification/dominance4d-{MODE}.json').write_text(json.dumps(report, indent=2)+'\n')
