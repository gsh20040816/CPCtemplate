from pathlib import Path
import hashlib
import json
import os
import random
import subprocess
import sys
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'tools'))
from usage_examples import records
P = 998244353
rng = random.Random(452)
cases = {'example-451': [], 'example-452': []}
for t in range(100):
    n,m,h,w = [rng.randrange(1,8) for _ in range(4)]
    if t < 4:
        n,m,h,w = [(0,0,1,1),(1,1,1,1),(1,65,9,1),(17,1,1,9)][t]
    a = [[rng.randrange(-10**12,10**12) for _ in range(m)] for _ in range(n)]
    b = [[rng.randrange(-10**12,10**12) for _ in range(w)] for _ in range(h)]
    data = f'{n} {m} {h} {w}\n' + ''.join(' '.join(map(str,row))+'\n' for row in a+b)
    c = [[0]*(m+w-1) for _ in range(n+h-1)] if n and m and h and w else []
    for i in range(n):
        for j in range(m):
            for u in range(h):
                for v in range(w):
                    c[i+u][j+v] = (c[i+u][j+v]+a[i][j]*b[u][v])%P
    expected = [len(c), len(c[0]) if c else 0] + [x for row in c for x in row]
    cases['example-451'].append((data,expected))
for t in range(100):
    n,m,h,w = [rng.randrange(1,10) for _ in range(4)]
    if t < 4:
        n,m,h,w = [(1,129,1,2),(65,1,2,1),(1,1,3,3),(3,3,0,0)][t]
    a = [[rng.randrange(-10**12,10**12) for _ in range(w)] for _ in range(h)]
    if t%13 == 0 and h and w:
        a[0][0] = P
    data = f'{n} {m} {h} {w}\n' + ''.join(' '.join(map(str,row))+'\n' for row in a)
    if not a or not a[0] or a[0][0]%P == 0:
        expected = [-1]
    else:
        c = [[0]*m for _ in range(n)]
        iv = pow(a[0][0],-1,P)
        for i in range(n):
            for j in range(m):
                total = sum(a[u][v]*c[i-u][j-v] for u in range(min(i+1,h)) for v in range(min(j+1,w)) if u or v)
                c[i][j] = iv if i == j == 0 else -total*iv%P
        expected = [x for row in c for x in row]
    cases['example-452'].append((data,expected))
report = dict(scope='Exact printed and header API drivers with independent Python integer truth, including empty/zero/negative/rectangular/truncation cases. No online AC.',runs=[])
for row in records():
    if row['id'] not in cases:
        continue
    assert (root/row['snippet_file']).read_text() == row['snippet']
    for form, source in [('header','#include "'+str(root/row['driver'])+'"\n'),('printed',row['program'])]:
        cpp = root/'build/bivariate'/f'{row["id"]}-{form}.cpp'
        cpp.write_text(source)
        for mode, flags in [('normal',['-O2','-DNDEBUG']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
            exe = cpp.with_suffix('.'+mode)
            subprocess.run([CXX,'-std=c++20',*flags,str(cpp),'-o',str(exe)],check=True)
            for data,expected in cases[row['id']]:
                r = subprocess.run([str(exe)],input=data,text=True,capture_output=True,timeout=30,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
                assert r.returncode == 0 and not r.stderr,(r.returncode,r.stderr)
                assert list(map(int,r.stdout.split())) == expected,(row['id'],form,mode,data,r.stdout,expected)
            report['runs'].append(dict(id=row['id'],form=form,mode=mode,cases=len(cases[row['id']]),source_sha256=hashlib.sha256(source.encode()).hexdigest()))
            print(row['id'],form,mode,'100 independent protocol cases PASS',flush=True)
(root/'verification/bivariate-protocols.json').write_text(json.dumps(report,indent=2)+'\n')
