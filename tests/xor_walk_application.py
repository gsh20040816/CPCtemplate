"""P4151 bundles against finite product-graph reachability and maximum-size multigraph."""
from compiler_config import CXX
from pathlib import Path
from collections import deque
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(4151)
cases = []
for trial in range(150):
    n = rng.randrange(1,9)
    edges = [(i,rng.randrange(1,i),rng.randrange(8)) for i in range(2,n+1)]
    edges += [(rng.randrange(1,n+1),rng.randrange(1,n+1),rng.randrange(8))
              for _ in range(rng.randrange(20))]
    g = [[] for _ in range(n+1)]
    for u,v,w in edges:
        g[u].append((v,w))
        g[v].append((u,w))
    seen = {(1,0)}
    q = deque([(1,0)])
    while q:
        u,x = q.popleft()
        for v,w in g[u]:
            state = (v,x^w)
            if state not in seen:
                seen.add(state)
                q.append(state)
    expected = max(x for u,x in seen if u == n)
    cases.append((n,edges,expected))
cases.append((2,[(1,2,(1<<64)-1)],(1<<64)-1))
n = 50000
edges = [(i,i+1,0) for i in range(1,n)]
edges += [(1,1,1<<i) for i in range(59)]
edges += [(1,1,0)]*(100000-len(edges))
cases.append((n,edges,(1<<59)-1))
for style in ['compact']:
    source = root/f'build/P4151.{style}.cpp'
    exe = root/f'build/P4151.{style}'
    subprocess.run(['python3',str(root/'tools/bundle.py'),str(root/f'verify/luogu/P4151.{style}.cpp'),str(source)],check=True)
    subprocess.run([CXX,'-std=c++20','-O2',str(source),'-o',str(exe)],check=True)
    for n,edges,expected in cases:
        text = f'{n} {len(edges)}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in edges)
        got = int(subprocess.check_output([str(exe)],input=text.encode(),timeout=60))
        assert got == expected
    print(f'P4151 {style} bundled driver / product-state oracle and N=50000 M=100000 PASS')
