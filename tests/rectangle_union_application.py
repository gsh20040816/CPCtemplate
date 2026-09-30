"""Exact bundled driver versus independent integer cell enumeration."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
mode = 'san' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-std=c++20', '-O2'] if mode == 'normal' else [
    '-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
source = root / f'build/rectangle-union-driver-{mode}.cpp'
subprocess.run(['python3', str(root / 'tools/bundle.py'),
                str(root / 'verify/library_checker/area_of_union_of_rectangles.compact.cpp'),
                str(source)], check=True)
exe = source.with_suffix('')
subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)


def run(rect, expected):
    data = f'{len(rect)}\n' + ''.join(' '.join(map(str, a)) + '\n' for a in rect)
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True,
                       check=True, timeout=90)
    assert not p.stderr, p.stderr
    assert p.stdout.split() == [str(expected)]


rng = random.Random(20260930)
for _ in range(180):
    rect, cells = [], set()
    for _ in range(rng.randrange(1, 40)):
        l, r = sorted(rng.sample(range(21), 2))
        d, u = sorted(rng.sample(range(21), 2))
        rect.append((l, d, r, u))
        cells.update((x, y) for x in range(l, r) for y in range(d, u))
    run(rect, len(cells))
n = 500000
run([(2*i, 2*i, 2*i+1, 2*i+1) for i in range(n)], n)
run([(i, i, 10**9-i, 10**9-i) for i in range(n)], 10**18)
run([(0, 0, 10**9, 10**9)] * n, 10**18)
print('Rectangle union driver: 180 cell-oracle inputs and three N=500000 cases PASS')
