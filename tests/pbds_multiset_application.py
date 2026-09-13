#!/usr/bin/env python3
"""Exercise both complete drivers with independent sorted-list references."""
import bisect
import os
from pathlib import Path
import random
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(916423)
cxx = os.environ.get('CXX') or shutil.which('g++-16') or 'g++'
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']

for pid in ['P3369', 'P6136']:
    exe = root / f'build/{pid}-pbds'
    subprocess.run([cxx, *flags, str(root/f'verify/luogu/{pid}.pbds.compact.cpp'), '-o', str(exe)], check=True)
    def run(lines, expected):
        p = subprocess.run([str(exe)], input='\n'.join(lines)+'\n', text=True, capture_output=True, check=True)
        assert p.stdout.split() == [str(x) for x in expected], pid
        assert not p.stderr, p.stderr
    initial = [rng.randrange(50) for _ in range(100)] if pid == 'P6136' else []
    a = sorted(initial)
    ops, answers = [], []
    last = 0
    for t in range(20000):
        op = rng.randint(1, 6) if a else 1
        if op == 1:
            x = rng.randint(0, 100) if pid == 'P6136' else rng.randint(-100, 100)
        elif op == 2:
            x = rng.choice(a)
        elif op == 3:
            x = rng.randint(0, 110) if pid == 'P6136' else rng.randint(-110, 110)
        elif op == 4:
            x = rng.randint(1, len(a))
        elif op == 5:
            x = rng.choice(a) + 1
        else:
            x = rng.choice(a) - 1
            if pid == 'P6136' and x < 0:
                op, x = 3, 0
        ops.append(f'{op} {x ^ last if pid == "P6136" else x}')
        if op == 1:
            bisect.insort(a, x)
        elif op == 2:
            a.pop(bisect.bisect_left(a, x))
        else:
            if op == 3: last = bisect.bisect_left(a, x) + 1
            if op == 4: last = a[x - 1]
            if op == 5: last = a[bisect.bisect_left(a, x) - 1]
            if op == 6: last = a[bisect.bisect_right(a, x)]
            answers.append(last)
    if pid == 'P3369':
        run([str(len(ops)), *ops], answers)
    else:
        checksum = 0
        for x in answers: checksum ^= x
        run([f'{len(initial)} {len(ops)}', ' '.join(map(str, initial)), *ops], [checksum])
        # Maximum operation count with duplicate insertion/erasure and online XOR.
        n, m = 100000, 1000000
        ops, last, checksum = [], 0, 0
        for i in range(m // 4):
            ops += [f'1 {7 ^ last}', f'4 {1 ^ last}']
            last = 7
            checksum ^= last
            ops += [f'2 {7 ^ last}', f'3 {7 ^ last}']
            last = 1
            checksum ^= last
        run([f'{n} {m}', ' '.join(['7']*n), *ops], [checksum])
print('PBDS multiset drivers: duplicate sorted-list oracle, legal strict neighbors, online XOR and million operations PASS')
