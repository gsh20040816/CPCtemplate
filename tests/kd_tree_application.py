"""P4148 XOR-dependent full inputs, independently decoded point-map oracle."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess
root = Path(__file__).resolve().parents[1]
source = root / 'build/P4148.cpp'
exe = root / 'build/P4148'
subprocess.run(['python3', 'tools/bundle.py', 'verify/luogu/P4148.compact.cpp', str(source)], cwd=root, check=True)
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)

def check(n, ops, answers=None):
    lines = [str(n)]
    last = 0
    values = {}
    expected = []
    for op in ops:
        lines.append(str(op[0])+' '+' '.join(str(x ^ last) for x in op[1:]))
        if op[0] == 1 and answers is None:
            _, x, y, w = op
            values[x,y] = values.get((x,y),0)+w
        if op[0] == 2:
            if answers is None:
                _, x1,y1,x2,y2 = op
                last = sum(w for (x,y),w in values.items() if x1<=x<=x2 and y1<=y<=y2)
            else:
                last = answers[len(expected)]
            expected.append(last)
    lines.append('3')
    p = subprocess.run([str(exe)], input='\n'.join(lines)+'\n', text=True, capture_output=True, check=True, timeout=120)
    assert not p.stderr, p.stderr
    assert list(map(int,p.stdout.split())) == expected

rng = random.Random(4148114)
for case in range(150):
    ops = [(2,1,1,100,100)]
    for _ in range(500):
        if rng.randrange(3):
            ops.append((1,rng.randrange(1,101),rng.randrange(1,101),rng.randrange(1,101)))
        else:
            x1,x2 = sorted((rng.randrange(1,101),rng.randrange(1,101)))
            y1,y2 = sorted((rng.randrange(1,101),rng.randrange(1,101)))
            ops.append((2,x1,y1,x2,y2))
    check(100,ops)
# 200000 operations: alternate increasing-coordinate insertion and query,
# preserving actual online dependence with a different answer at every step.
ops, answers = [], []
for i in range(1,100001):
    ops.append((1,i,i,1))
    ops.append((2,1,1,i,i))
    answers.append(i)
check(500000,ops,answers)
# Nearly maximum distinct allocation, then maximum answer fitting int.
ops = [(1,i,500001-i,1) for i in range(1,199999)]
ops += [(1,500000,500000,2147483647-199998),(2,1,1,500000,500000)]
check(500000,ops,[2147483647])
print('P4148: 150 random XOR streams, two 200000-operation cases, near-limit distinct allocation and INT_MAX answer PASS')
