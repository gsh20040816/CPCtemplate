"""Persistent union-find adapter: copy a complete partition for each version."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
if os.uname().sysname == 'Darwin':
    flags += ['-Wl,-stack_size,0x20000000']
exe = root / 'build/rollback-application'
subprocess.run([CXX, *flags, str(root / 'verify/library_checker/persistent_unionfind.compact.cpp'), '-o', str(exe)], check=True)
rng = random.Random(20260915)
for trial in range(150):
    n, q = rng.randrange(1, 25), 300
    versions = {-1: list(range(n))}
    operations, expected = [], []
    for i in range(q):
        k = rng.choice(list(versions))
        u, v, t = rng.randrange(n), rng.randrange(n), rng.randrange(2)
        operations.append(f'{t} {k} {u} {v}')
        a = versions[k]
        if t:
            expected.append(int(a[u] == a[v]))
        else:
            versions[i] = [a[u] if x == a[v] else x for x in a]
    data = f'{n} {q}\n' + '\n'.join(operations) + '\n'
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
    assert not result.stderr, result.stderr
    assert list(map(int, result.stdout.split())) == expected
print('RollbackDSU version tree: 150 independent copied-partition traces, 300 operations each PASS')
