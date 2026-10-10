import hashlib
import json
import os
import platform
import subprocess
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
work = root / 'build/infra-random'
work.mkdir(parents=True, exist_ok=True)
sources = [root / 'examples/infra' / name for name in
           ['random_demo.cpp', 'clock_demo.cpp', 'hash_demo.cpp']]
sources.append(root / 'tests/infra_random.cpp')
records = []
for flags in [['-O2'], ['-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=all']]:
    for source in sources:
        exe = work / source.stem
        cmd = [CXX, '-std=c++23', '-Wall', '-Wextra', *flags, str(source), '-o', str(exe)]
        subprocess.run(cmd, check=True, timeout=120)
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1')
        p = subprocess.run([str(exe), '42'], capture_output=True, text=True, env=env, check=True, timeout=10)
        if source.stem == 'random_demo':
            again = subprocess.check_output([str(exe), '42'], text=True, env=env)
            assert p.stdout == again
        if source.stem == 'hash_demo':
            assert p.stdout == '4 4\n'
        if source.stem == 'clock_demo':
            ms, seconds = p.stderr.split(' ms, ')
            assert int(ms) >= 20
            assert float(seconds.removesuffix(' s\n')) >= .02
        records.append(dict(command=cmd, stdout=p.stdout, stderr=p.stderr))
        print('PASS', source.name, flags[0], flush=True)
tracked = [*sources, root / 'examples/infra/random_tools.hpp', Path(__file__)]
report = dict(status='pass', compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0],
              platform=platform.platform(), records=records,
              source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in tracked},
              scope='Exact printed C++ examples at O2 and ASan/UBSan; 1000-seed structural checks. Not statistical proof of distribution quality or a performance benchmark.')
(root / 'verification/infra-random.json').write_text(json.dumps(report, indent=2) + '\n')
