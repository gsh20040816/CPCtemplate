"""P3369 adapter checked by sorted-list rank, kth and strict neighbors."""
from compiler_config import CXX
from pathlib import Path
import bisect
import os
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(3369110)
source = root / 'build/P3369.scapegoat.cpp'
exe = root / 'build/P3369.scapegoat'
subprocess.run(['python3', 'tools/bundle.py', 'verify/luogu/P3369.scapegoat.compact.cpp', str(source)], cwd=root, check=True)
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)

def check(ops, expected):
    data = str(len(ops))+'\n'+''.join(f'{op} {x}\n' for op, x in ops)
    run = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=120)
    assert not run.stderr, run.stderr
    assert list(map(int, run.stdout.split())) == expected

for case in range(200):
    values = []
    ops, expected = [], []
    for step in range(500):
        op = rng.randrange(1, 7) if values else 1
        x = rng.randrange(-100, 101)
        if op == 2:
            x = rng.choice(values)
            values.pop(bisect.bisect_left(values, x))
        elif op == 3:
            expected.append(bisect.bisect_left(values, x)+1)
        elif op == 4:
            x = rng.randrange(1, len(values)+1)
            expected.append(values[x-1])
        elif op == 5:
            x = max(x, values[0]+1)
            expected.append(values[bisect.bisect_left(values, x)-1])
        elif op == 6:
            x = min(x, values[-1]-1)
            expected.append(values[bisect.bisect_right(values, x)])
        else:
            bisect.insort(values, x)
        ops.append((op, x))
    check(ops, expected)
# Full operation limit, ascending build / deletion / missing-key ranks / kth.
ops = [(1, x) for x in range(50000)]
ops += [(2, x) for x in range(0, 50000, 2)]
ops += [(3, 50000)] * 12500
ops += [(4, 25000)] * 12500
check(ops, [25001] * 12500 + [49999] * 12500)
print('Scapegoat P3369: 201 programs, sorted-list oracle, absent-key ranks, duplicates, strict neighbors and 100000-operation scale PASS')
