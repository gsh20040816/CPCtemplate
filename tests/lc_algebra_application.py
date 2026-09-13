"""Whole-driver validation using permutation minors and explicit certificates."""
from compiler_config import CXX
import itertools
import os
from pathlib import Path
import random
import subprocess
root = Path(__file__).resolve().parents[1]
p = 998244353
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
exes = {}
for name in ['system_of_linear_equations', 'matrix_det', 'matrix_product']:
    exe = root/('build/lc-'+name)
    subprocess.run([CXX,*flags,str(root/('verify/library_checker/'+name+'.compact.cpp')),'-o',str(exe)],check=True)
    exes[name] = exe

def run(name, lines):
    r = subprocess.run([str(exes[name])],input='\n'.join(lines)+'\n',text=True,capture_output=True,check=True,timeout=120)
    assert not r.stderr, r.stderr
    return r.stdout.splitlines()

def rows(a):
    return [' '.join(map(str,r)) for r in a]

def det(a):
    result = 0
    for order in itertools.permutations(range(len(a))):
        term = 1
        for i,j in enumerate(order):
            term = term*a[i][j]%p
        inv = sum(order[i]>order[j] for i in range(len(a)) for j in range(i+1,len(a)))
        result += -term if inv%2 else term
    return result%p

def rank(a):
    if not a: return 0
    for k in range(min(len(a),len(a[0])),0,-1):
        for rs in itertools.combinations(range(len(a)),k):
            for cs in itertools.combinations(range(len(a[0])),k):
                if det([[a[i][j] for j in cs] for i in rs]): return k
    return 0

rng = random.Random(234776)
for _ in range(55):
    n,m = rng.randrange(1,5),rng.randrange(1,5)
    a = [[rng.randrange(5) for _ in range(m)] for _ in range(n)]
    # Duplicate/zero rows force nontrivial null spaces and inconsistency cases.
    if rng.randrange(2): a[-1] = a[0][:]
    if rng.randrange(3)==0: a[0] = [0]*m
    b = [rng.randrange(5) for _ in range(n)]
    if rng.randrange(2):
        x = [rng.randrange(p) for _ in range(m)]
        b = [sum(c*v for c,v in zip(row,x))%p for row in a]
    r = rank(a)
    possible = rank([row+[v] for row,v in zip(a,b)]) == r
    out = run('system_of_linear_equations',[f'{n} {m}',*rows(a),' '.join(map(str,b))])
    if not possible:
        assert out == ['-1']
    else:
        k = int(out[0]);assert k == m-r and len(out)==k+2
        vecs = [list(map(int,line.split())) for line in out[1:]]
        assert all(len(v)==m and all(0<=x<p for x in v) for v in vecs)
        assert all(sum(c*v for c,v in zip(row,vecs[0]))%p==t for row,t in zip(a,b))
        assert all(sum(c*v for c,v in zip(row,z))%p==0 for row in a for z in vecs[1:])
        assert rank(vecs[1:]) == k
for n in range(1,7):
    for _ in range(8):
        a=[[rng.randrange(p) for _ in range(n)] for _ in range(n)]
        if rng.randrange(2): a[-1]=a[0][:]
        assert run('matrix_det',[str(n),*rows(a)])==[str(det(a))]
for _ in range(30):
    n,m,k=[rng.randrange(1,8) for _ in range(3)]
    a=[[rng.randrange(p) for _ in range(m)] for _ in range(n)]
    b=[[rng.randrange(p) for _ in range(k)] for _ in range(m)]
    c=[[sum(a[i][t]*b[t][j] for t in range(m))%p for j in range(k)] for i in range(n)]
    assert run('matrix_product',[f'{n} {m} {k}',*rows(a),*rows(b)])==rows(c)
# Large triangular determinant; large affine identity system.
n=500
a=[[0 if j<i else (p-1 if i==j else (i+j)%p) for j in range(n)] for i in range(n)]
assert run('matrix_det',[str(n),*rows(a)])==['1']
a=[[int(i==j) for j in range(n)] for i in range(n)]
b=list(range(n))
assert run('system_of_linear_equations',[f'{n} {n}',*rows(a),' '.join(map(str,b))])==['0',' '.join(map(str,b))]
# Maximum dimensions: every output coefficient has exactly m products of (-1)^2.
n=1024
line=' '.join([str(p-1)]*n)
out=run('matrix_product',[f'{n} {n} {n}',*[line]*(2*n)])
assert out==[' '.join([str(n)]*n)]*n
print('LC algebra drivers: permutation-minor ranks, affine basis certificates, rectangular product oracle and maximal structured matrices PASS')
