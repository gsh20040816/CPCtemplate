import hashlib
import json
import platform
import subprocess
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
work = root / 'build/infra-environment'
work.mkdir(parents=True, exist_ok=True)
records = []

def run(cmd, expected=0, **kwargs):
    p = subprocess.run(cmd, cwd=work, text=True, capture_output=True, timeout=30, **kwargs)
    records.append(dict(command=cmd, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr))
    assert p.returncode == expected, records[-1]
    return p

for name in ['environment', 'debug_local', 'memory', 'interactive']:
    flags = ['-O0', '-g', '-DLOCAL'] if name == 'debug_local' else ['-O2']
    run([CXX, '-std=c++23', '-Wall', '-Wextra', *flags,
         str(root / f'examples/infra/{name}.cpp'), '-o', str(work / name)])
p = run(['./environment'])
assert 'pbds 9' in p.stdout and 'int128 16' in p.stdout
p = run(['./debug_local'], input='7\n')
assert p.stdout == '49\n' and 'x=7' in p.stderr
p = run(['bash', '-c', 'ulimit -c 0; ./debug_local <<< -1'], expected=134)
assert 'Assertion' in p.stderr
(work / 'input.txt').write_text('7\n')
p = run(['gdb', '-q', '-batch', '-x', str(root / 'examples/infra/debug.gdb'), './debug_local'])
assert '$1 = 7' in p.stdout and '$2 = 49' in p.stdout and '#1' in p.stdout
p = run(['/usr/bin/time', '-f', '%es %MKB', './memory'])
assert p.stdout == '499999500000\n' and 'VmPeak:' in p.stderr and 'VmHWM:' in p.stderr
run(['/usr/bin/time', '-v', './memory'])
run(['bash', '-c', 'time ./memory'])
run(['bash', '-c', '(ulimit -Sv 262144 && ulimit -Ss 65536 && ./memory)'])
p = run(['timeout', '-k', '1s', '0.1s', 'sleep', '2'], expected=124)
run(['bash', '-c', 'g++ --version; python3 --version; ulimit -Ss; ulimit -Hs; lscpu'])
for secret in range(1, 101):
    p = run(['timeout', '-k', '1s', '3s', 'python3',
             str(root / 'examples/infra/interactor.py'), str(secret), './interactive'])
    assert p.stderr.rstrip().endswith('AC')
# Deliberately broken contestants exercise failure paths without changing printed code.
for name, body, expected in [
    ('wrong', 'print("! 0", flush=True)\n', 1),
    ('malformed', 'print("garbage", flush=True)\n', 1),
    ('noflush', 'import sys\nprint("? 50")\nsys.stdin.readline()\n', 124),
    ('extra', 'print("! 42", flush=True)\nprint("extra", flush=True)\n', 1),
    ('exitbad', 'import sys\nprint("! 42", flush=True)\nsys.exit(3)\n', 1),
]:
    file = work / name
    file.write_text('#!/usr/bin/env python3\n' + body)
    file.chmod(0o755)
    run(['timeout', '-k', '1s', '0.3s', 'python3',
         str(root / 'examples/infra/interactor.py'), '42', str(file)], expected=expected)
files = [root / f'examples/infra/{p}' for p in [
    'environment.cpp', 'debug_local.cpp', 'debug.gdb', 'memory.cpp',
    'interactive.cpp', 'interactor.py']]
files.append(Path(__file__))
report = dict(status='pass', platform=platform.platform(),
              compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0],
              records=records, source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
              scope='Native Linux examples, GDB, time/proc/soft limits; all 100 secrets; five broken protocol variants. Local environment only, no OJ submission or measured judge environment.')
(root / 'verification/infra-environment.json').write_text(json.dumps(report, indent=2) + '\n')
print('environment, GDB, time/memory, 100 interactive cases and 5 failure paths PASS')
