"""P5180 output checked by independent deletion reachability, plus maximum size."""
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
exe = root / 'build/dominator-application'
subprocess.run([CXX, *flags, str(root / 'verify/luogu/P5180.compact.cpp'), '-o', str(exe)], check=True)
def run(n, edges, expected):
    data = f'{n} {len(edges)}\n' + ''.join(f'{u+1} {v+1}\n' for u, v in edges)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
    assert not result.stderr, result.stderr
    assert list(map(int, result.stdout.split())) == expected
rng = random.Random(5180)
for trial in range(150):
    n = rng.randrange(1, 20)
    edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randrange(80))]
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
    def reach(removed):
        seen = set() if removed == 0 else {0}
        q = deque(seen)
        while q:
            for v in g[q.popleft()]:
                if v != removed and v not in seen:
                    seen.add(v)
                    q.append(v)
        return seen
    all_seen = reach(-1)
    run(n, edges, [len(all_seen - reach(u)) for u in range(n)])
n = 200000
edges = [(u, u+1) for u in range(n-1)] + [(u, u) for u in range(100001)]
run(n, edges, list(range(n, 0, -1)))
print('P5180: 150 deletion-reachability output oracles; 200000 vertices / 300000 edges PASS')
