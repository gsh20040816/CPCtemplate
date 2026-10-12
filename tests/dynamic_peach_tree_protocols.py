from pathlib import Path
from collections import deque
import hashlib
import json
import os
import random
import subprocess
import sys
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records
rng = random.Random(1942)
row = next(r for r in records() if r['id'] == 'example-440')
assert (ROOT / row['snippet_file']).read_text() == row['snippet']
def solve(p,b,g,h):
 n=len(p); N=3*n+2; s=N-2;t=N-1;c=[[0]*N for _ in range(N)]
 for x in range(n):
  c[s][x]=g[x];c[n+x][t]=b[x];c[2*n+x][t]=h[x]
  for v in range(n):
   u=v
   while u!=-1 and u!=x:u=p[u]
   if u==x:
    c[x][n+v]=10**9;c[n+v][2*n+x]=10**9
  if p[x]!=-1:c[x][n+p[x]]=10**9
 f=0
 while True:
  prev=[-1]*N;prev[s]=s;q=deque([s])
  while q and prev[t]<0:
   u=q.popleft()
   for v in range(N):
    if c[u][v] and prev[v]<0:prev[v]=u;q.append(v)
  if prev[t]<0:break
  add=10**9;v=t
  while v!=s:add=min(add,c[prev[v]][v]);v=prev[v]
  v=t
  while v!=s:u=prev[v];c[u][v]-=add;c[v][u]+=add;v=u
  f+=add
 return f

cases = []
for case in range(200):
    n = rng.randrange(1, 13)
    p = [-1] + [rng.randrange(i) for i in range(1,n)]
    b = [rng.randrange(10) for _ in range(n)]
    g, h = [0]*n, [0]*n
    lines = ['1', f'{n} 50', ' '.join(str(x+1) for x in p[1:]), ' '.join(map(str,b))]
    want = []
    for q in range(50):
        x, typ, v = rng.randrange(n), rng.randrange(1,3), rng.randrange(1,20)
        lines.append(f'{typ} {x+1} {v}')
        (g if typ == 1 else h)[x] += v
        want.append('YES' if solve(p,b,g,h) == sum(b)+sum(h) else 'NO')
    cases.append(('\n'.join(lines)+'\n', want))
cases.append(('1\n8 8\n1 1 1 4 3 6 6\n5 6 2 9 8 4 1 3\n1 3 14\n1 4 17\n1 2 7\n2 2 1\n1 6 1\n2 1 1000000\n1 4 999999\n1 3 1\n', 'NO NO YES NO YES NO NO YES'.split()))
# Batch random cases together also checks per-test object reset.
cases.append((str(200)+'\n'+''.join(x.split('\n',1)[1] for x,y in cases[:200]), [z for x,y in cases[:200] for z in y]))
out = ROOT / 'build/dynamic-peach-tree'
report = {'scope': '200 random CF1942H complete protocols / 10000 prefixes, independent Edmonds-Karp oracle; first official sample; multi-test reset. Local only, no online verdict.', 'runs': []}
forms = {'header': '#include "' + str(ROOT / row['driver']) + '"\n', 'printed': row['program']}
for form, source in forms.items():
    cpp = out / (form + '-protocol.cpp')
    cpp.write_text(source)
    for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
        exe = out / (form + '-' + mode + '-protocol')
        subprocess.run([CXX, '-std=c++20', *flags, str(cpp), '-o', str(exe)], check=True)
        env = os.environ.copy()
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
        for data, expected in cases:
            result = subprocess.run([str(exe)], input=data, capture_output=True, text=True, env=env, timeout=20)
            assert result.returncode == 0 and not result.stderr, result.stderr
            assert result.stdout.split() == expected
        print(form, mode, '202 complete protocols PASS', flush=True)
        report['runs'].append({'form': form, 'mode': mode, 'cases': 202, 'source_sha256': hashlib.sha256(source.encode()).hexdigest()})
report['files'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT / row['driver'], ROOT / 'tests/dynamic_peach_tree_protocols.py', ROOT / 'src/compact/dynamic_peach_tree.hpp']}
(ROOT / 'verification/dynamic-peach-tree-protocols.json').write_text(json.dumps(report, indent=2) + '\n')
