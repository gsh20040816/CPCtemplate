"""P3377 adapter oracle: independently maintain live vertex sets per heap."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
(root / 'build').mkdir(exist_ok=True)
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
exe = root / 'build/leftist-application'
subprocess.run([CXX, *flags, str(root / 'verify/luogu/P3377.compact.cpp'), '-o', str(exe)], check=True)
rng = random.Random(337700)
for trial in range(100):
    n, m = rng.randrange(1, 31), 300
    keys = [rng.randrange(1, 8) for _ in range(n)]
    groups = [{i} for i in range(n)]
    removed = set()
    operations, expected = [], []
    for _ in range(m):
        x, y = rng.randrange(n), rng.randrange(n)
        if rng.randrange(2):
            operations.append(f'1 {x + 1} {y + 1}')
            if x in removed or y in removed:
                continue
            a = next(g for g in groups if x in g)
            b = next(g for g in groups if y in g)
            if a is not b:
                groups.remove(b)
                a.update(b)
        else:
            operations.append(f'2 {x + 1}')
            if x in removed:
                expected.append(-1)
                continue
            group = next(g for g in groups if x in g)
            v = min(group, key=lambda i: (keys[i], i))
            expected.append(keys[v])
            group.remove(v)
            removed.add(v)
    data = f'{n} {m}\n' + ' '.join(map(str, keys)) + '\n' + '\n'.join(operations) + '\n'
    run = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
    assert not run.stderr, run.stderr
    assert list(map(int, run.stdout.split())) == expected, (trial, data, run.stdout, expected)
print('P3377: 100 independent set-oracle traces, 300 operations each; ties, deleted handles and repeated merges PASS')
