"""Exercise alternate judge adapters; preserve independent original OJ status."""
from compiler_config import CXX
from pathlib import Path
import hashlib
import json
import math
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
build = root / 'build/alternate-judges'
build.mkdir(exist_ok=True)
reports = {}
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    if os.uname().sysname == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    for pid in ['U104310', 'U106005']:
        src = build / (pid + '.cpp')
        subprocess.run(['python3', str(root / 'tools/bundle.py'), str(root / 'verify/luogu' / (pid + '.compact.cpp')), str(src)], check=True)
        exe = build / (pid + '-' + mode)
        subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
        def run(data):
            result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, timeout=60, check=True)
            assert not result.stderr, result.stderr
            return result.stdout
        if pid == 'U104310':
            assert run('6 4\n3 2 4 2 5 3\n1 2\n1 3\n2 4\n2 5\n3 6\n1 4\n1 5\n2 6\n4 5\n').split() == ['2', '3', '3', '2']
            n = 100000
            rng = random.Random(104310)
            queries = [(1, n), (n, n), (1, 1)] + [(rng.randint(1, n), rng.randint(1, n)) for _ in range(n-3)]
            data = f'{n} {n}\n' + ' '.join(map(str, range(1,n+1))) + '\n'
            data += ''.join(f'{u} {u+1}\n' for u in range(1,n))
            data += ''.join(f'{u} {v}\n' for u,v in queries)
            assert list(map(int,run(data).split())) == [abs(u-v)+1 for u,v in queries]
            count = n + 4
        else:
            cases = [('1\n0 0 1\n', math.pi), ('3\n0 0 2\n0 0 2\n1 0 1\n',4*math.pi), ('2\n-1000 0 1\n1000 0 1\n',2*math.pi), ('2\n0 0 0\n1 1 0\n',0), ('2\n0 0 1\n1 0 1\n',4*math.pi/3+math.sqrt(3)/2)]
            for data,expected in cases:
                result = run(data).strip()
                assert '.' in result and len(result.split('.')[1]) >= 4
                assert abs(float(result)-expected) < 1e-9
            assert abs(float(run('6\n-79 45 1\n-23 16 79\n-49 15 83\n-6 54 63\n-30 28 10\n-66 -18 50\n'))-27615.296) < 1e-3
            count = len(cases)+1
        reports[pid+'-'+mode] = dict(status='pass',checks=count,expanded_sha256=hashlib.sha256(src.read_bytes()).hexdigest())
        print(pid,mode,'PASS',flush=True)
(root / 'verification/alternate-template-judges.json').write_text(json.dumps(dict(scope='Adapter and expanded-source checks; long recursive chain at user-template maximum size; analytic circle answers and output precision',forms=reports),indent=2)+'\n')
