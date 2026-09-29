"""P3690 driver versus adjacency-matrix forest paths."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(3690)
source = root / 'build/P3690.current.cpp'
exe = root / 'build/P3690.current'
subprocess.run(['python3', 'tools/bundle.py', 'verify/luogu/P3690.compact.cpp', str(source)], cwd=root, check=True)
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)
for case in range(200):
    n = rng.randrange(1, 36)
    g = [set() for _ in range(n)]
    weight = [rng.randrange(1 << 20) for _ in range(n)]
    lines = [f'{n} 500', ' '.join(map(str, weight))]
    want = []
    def path(s, t):
        parent = {s: -1}
        queue = [s]
        for u in queue:
            for v in g[u]:
                if v not in parent:
                    parent[v] = u
                    queue.append(v)
        if t not in parent:
            return None
        answer = 0
        while t != -1:
            answer ^= weight[t]
            t = parent[t]
        return answer
    for step in range(500):
        op = rng.randrange(4)
        x, y = rng.randrange(n), rng.randrange(n)
        if op == 0:
            answer = path(x, y)
            if answer is None:
                y = x
                answer = weight[x]
            want.append(answer)
        elif op == 1:
            if path(x, y) is None:
                g[x].add(y)
                g[y].add(x)
        elif op == 2:
            g[x].discard(y)
            g[y].discard(x)
        else:
            value = rng.randrange(1 << 20)
            weight[x] = value
        lines.append(f'{op} {x+1} {value if op == 3 else y+1}')
    run = subprocess.run([str(exe)], input='\n'.join(lines)+'\n', text=True,
                         capture_output=True, check=True, timeout=30)
    assert not run.stderr, run.stderr
    assert list(map(int, run.stdout.split())) == want
print('P3690: 200 forests, 100000 operations, independent BFS/XOR, rejected cycles and absent cuts PASS')
