"""Check the actual P3388 adapter against deletion component counts."""
from compiler_config import CXX
from pathlib import Path
from collections import deque
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
if os.uname().sysname == 'Darwin':
    flags += ['-Wl,-stack_size,0x20000000']
exe = root / 'build/lowlink-application'
subprocess.run([CXX, *flags, str(root / 'verify/luogu/P3388.compact.cpp'), '-o', str(exe)], check=True)
def run(n, edges, expected):
    data = f'{n} {len(edges)}\n' + ''.join(f'{u+1} {v+1}\n' for u, v in edges)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
    assert not result.stderr, result.stderr
    lines = result.stdout.splitlines()
    assert len(lines) == 2
    assert int(lines[0]) == len(expected)
    assert list(map(int, lines[1].split())) == expected
rng = random.Random(3388)
for trial in range(200):
    n = rng.randrange(1, 20)
    edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randrange(1, 75))]
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    def components(removed):
        seen = {removed}
        count = 0
        for s in range(n):
            if s in seen:
                continue
            count += 1
            q = deque([s])
            seen.add(s)
            while q:
                for v in g[q.popleft()]:
                    if v not in seen:
                        seen.add(v)
                        q.append(v)
        return count
    base = components(-1)
    run(n, edges, [u+1 for u in range(n) if components(u) > base])
n = 20000
edges = [(u, u+1) for u in range(n-1)]
edges += [edges[i % (n-1)] for i in range(100000 - len(edges))]
run(n, edges, list(range(2, n)))
print('P3388: 200 deletion-component output oracles; 20000 vertices / 100000 edges PASS')
