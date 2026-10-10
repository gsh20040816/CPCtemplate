#!/usr/bin/env python3
"""Execute the actual paper-candidate scripts, including failure paths."""
import hashlib
import json
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'examples/infra'
checks = []
with tempfile.TemporaryDirectory(prefix='infra scripts ') as tmp:
    work = Path(tmp)
    bindir = work / 'bin'
    bindir.mkdir()
    (bindir / 'g++').symlink_to(shutil.which(CXX))
    env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ['PATH'],
               ASAN_OPTIONS='detect_leaks=0:halt_on_error=1')
    for file in source.iterdir():
        shutil.copy2(file, work / file.name)
    def run(args, ok=True, data=''):
        p = subprocess.run(args, cwd=work, env=env, input=data, text=True,
                           capture_output=True, timeout=25)
        assert (p.returncode == 0) == ok, (args, p.returncode, p.stdout, p.stderr)
        return p
    def checked(name):
        checks.append(name)
        print('PASS', name, flush=True)
    data = '4\n-4 3 -1 5\n'
    assert run(['bash', 'compile.sh', 'main'], data=data).stdout == '7\n'
    checked('debug compile and run')
    assert run(['bash', 'compile.sh', '-O2', 'main.cpp'], data=data).stdout == '7\n'
    checked('optimized compile and run')
    shutil.copy2(work / 'main.cpp', work / 'name with spaces.cpp')
    run(['bash', 'compile.sh', 'name with spaces.cpp', '-O2', '-o', str(work / 'binary with spaces')])
    assert run([str(work / 'binary with spaces')], data=data).stdout == '7\n'
    checked('quoted source and absolute output; explicit output does not run')
    before = (work / 'main.cpp').read_bytes()
    (work / 'text').write_text('keep')
    (work / 'link').symlink_to(work / 'text')
    (work / 'directory').mkdir()
    os.chmod(work / 'main.cpp', 0o755)
    for target in ['main.cpp', './main.cpp', 'text', 'link', 'directory']:
        run(['bash', 'compile.sh', 'main', '-o', target], ok=False)
    assert (work / 'main.cpp').read_bytes() == before
    assert (work / 'text').read_text() == 'keep'
    checked('source, text, symlink and directory are not overwritten')
    for args in [[], ['-o'], ['main', '-o'], ['main', '-o', '-O2'],
                 ['main', 'main'], ['-bad', 'main'], ['missing']]:
        run(['bash', 'compile.sh', *args], ok=False)
    checked('invalid arguments fail')
    (work / 'broken.cpp').write_text('not valid C++;')
    (work / 'old').write_text('#!/bin/sh\necho stale > marker\n')
    os.chmod(work / 'old', 0o755)
    run(['bash', 'compile.sh', 'broken', '-o', 'old'], ok=False)
    assert not (work / 'marker').exists()
    (work / 'crash.cpp').write_text('int main() { return 17; }\n')
    p = run(['bash', 'compile.sh', 'crash', '-O2'], ok=False)
    assert p.returncode == 17
    checked('compile failure never runs old binary; nonzero run status propagates')
    (work / 'ub.cpp').write_text('#include <climits>\nint main() { volatile int x = INT_MAX; return x + 1; }\n')
    p = run(['bash', 'compile.sh', 'ub'], ok=False)
    assert 'runtime error' in p.stderr
    checked('UBSan exits on signed overflow')
    shutil.copy2(work / 'gen.py', work / 'gen')
    shutil.copy2(work / 'brute.py', work / 'brute')
    run(['bash', 'compile.sh', 'main', '-O2', '-o', 'main'])
    run(['bash', 'stress.sh', '30'])
    checked('30 fixed seeds match independent nonempty subarray oracle')
    for failure in ['wrong_answer', 'runtime', 'generator', 'reference', 'timeout']:
        for f in ['gen', 'brute']:
            shutil.copy2(work / (f + '.py'), work / f)
        # Restore the tested optimized program after a fixture replaced it.
        run(['bash', 'compile.sh', 'main', '-O2', '-o', 'main'])
        target = 'gen' if failure == 'generator' else 'brute' if failure == 'reference' else 'main'
        code = 'echo wrong' if failure == 'wrong_answer' else 'sleep 5' if failure == 'timeout' else 'exit 17'
        (work / target).write_text('#!/bin/sh\n' + code + '\n')
        os.chmod(work / target, 0o755)
        old = set(work.glob('stress.*'))
        p = run(['bash', 'stress.sh', '3'], ok=False)
        folder, = set(work.glob('stress.*')) - old
        assert (folder / 'seed').read_text().strip() == '1'
        assert (folder / 'input').exists()
        assert 'stopped at seed 1' in p.stderr
        if failure == 'wrong_answer':
            assert (folder / 'diff').stat().st_size > 0
        if failure == 'timeout':
            assert p.returncode == 124
        checked('first ' + failure + ' stops and retains reproduction files')
    shutil.copy2(work / 'brute.py', work / 'brute')
    run(['bash', 'compile.sh', 'main', '-O2', '-o', 'main'])
    (work / 'gen').write_text('#!/bin/sh\nif [ "$1" = 2 ]; then exit 17; fi\nexec python3 gen.py "$1"\n')
    os.chmod(work / 'gen', 0o755)
    old = set(work.glob('stress.*'))
    run(['bash', 'stress.sh', '3'], ok=False)
    folder, = set(work.glob('stress.*')) - old
    assert (folder / 'seed').read_text().strip() == '2'
    for name in ['input', 'expected', 'actual', 'diff', 'brute.err', 'main.err']:
        assert (folder / name).read_bytes() == b''
    checked('second-seed failure cannot leave previous outputs in saved case')
report = dict(status='pass',checks=checks,platform=platform.platform(),
              compiler=subprocess.check_output([CXX,'--version'],text=True).splitlines()[0],
              bash=subprocess.check_output(['bash','--version'],text=True).splitlines()[0],
              timeout=subprocess.check_output(['timeout','--version'],text=True).splitlines()[0],
              source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [*source.iterdir(),Path(__file__)]},
              scope='Actual scripts executed on host shown; test-only PATH binds g++ to configured GNU compiler. Not a native Linux test or complete issue17 validation.')
(ROOT/'verification/infra-scripts.json').write_text(json.dumps(report,indent=2)+'\n')
