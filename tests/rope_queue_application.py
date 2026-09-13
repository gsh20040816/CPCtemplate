#!/usr/bin/env python3
import os
import random
import shutil
import subprocess
from pathlib import Path
root = Path(__file__).resolve().parents[1]
rng = random.Random(16741)
exe = root / 'build/rope-queue-driver'
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
subprocess.run([os.environ.get('CXX') or shutil.which('g++-16') or 'g++', *flags,
                str(root / 'verify/library_checker/persistent_queue.compact.cpp'), '-o', str(exe)], check=True)
versions = [[]]
queries, expected = [], []
for i in range(20000):
    t = rng.randrange(len(versions))
    old = versions[t]
    if not old or rng.randrange(2):
        x = rng.randrange(10**9 + 1)
        queries.append(f'0 {t-1} {x}')
        versions.append(old + [x])
    else:
        queries.append(f'1 {t-1}')
        versions.append(old[1:])
        expected.append(str(old[0]))
p = subprocess.run([str(exe)], input=str(len(queries))+'\n'+'\n'.join(queries)+'\n',
                   text=True, capture_output=True, check=True)
assert p.stdout.splitlines() == expected
assert not p.stderr
print('Fixed rope persistent-queue driver: independent branching list oracle PASS')
