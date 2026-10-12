"""Independent exact vertex and recession-cone oracle; no simplex in oracle."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations, product
import random, subprocess, json, hashlib, time
root = Path(__file__).resolve().parents[1]
build = root / 'build/simplex'
build.mkdir(exist_ok=True)
def vertex(a, b, n):
    aa = [[F(v) for v in row] for row in a] + [[F(-int(i == j)) for j in range(n)] for i in range(n)]
    bb = list(map(F, b)) + [F(0)] * n
    for pick in combinations(range(len(aa)), n):
        mat = [aa[i][:] + [bb[i]] for i in pick]
        for j in range(n):
            k = next((i for i in range(j, n) if mat[i][j]), None)
            if k is None:
                break
            mat[j], mat[k] = mat[k], mat[j]
            v = mat[j][j]
            mat[j] = [x / v for x in mat[j]]
            for i in range(n):
                if i != j:
                    v = mat[i][j]
                    mat[i] = [x - v * y for x, y in zip(mat[i], mat[j])]
        else:
            x = [row[-1] for row in mat]
            if all(sum(u*v for u,v in zip(row,x)) <= rhs for row,rhs in zip(aa,bb)):
                yield x

def oracle(a,b,c):
    n = len(c)
    points = list(vertex(a,b,n))
    if not points:
        return 1, 0
    direction = next(vertex(a + [[-v for v in c]], [0]*len(b) + [-1], n), None)
    if direction is not None:
        return 2, 0
    return 0, max(sum(u*v for u,v in zip(c,x)) for x in points)

cases=[]
def add(a,b,c):
    cases.append((a,b,c,*oracle(a,b,c)))
for n in range(4):
    for m in range(7):
        for repeat in range(30):
            rng=random.Random(190000+n*10000+m*100+repeat)
            add([[rng.randint(-4,4) for _ in range(n)] for _ in range(m)],
                [rng.randint(-5,5) for _ in range(m)], [rng.randint(-4,4) for _ in range(n)])
# Exhaust all pairs of 1D integer constraints and objectives.
rows=list(product(range(-2,3),repeat=2))
for u in rows:
    for v in rows:
        for c in [-1,0,1]:
            add([[u[0]],[v[0]]],[u[1],v[1]],[c])
# Beale's cycling instance, scaled to integer coefficients.
add([[1,-11,-5,18],[1,-3,-1,2],[1,0,0,0]],[0,0,1],[10,-57,-9,-24])
add([[-1,-1],[1,1],[0,0],[-2,-2]],[ -2,2,0,-4],[3,3])
add([[1,1],[-1,-1],[0,0]],[1,-2,0],[1,1])
# Diagonal 100x100 instance with unique known optimum.
n=100
a=[];b=[];c=list(range(1,n+1))
for i in range(n):
    a.append([int(i==j) for j in range(n)]);b.append(i+1)
cases.append((a,b,c,0,sum((i+1)**2 for i in range(n))))
# Dense feasible bounded n=m=100: one sum bound, other redundant constraints.
rng=random.Random(13337)
a=[[1]*100]+[[rng.randint(0,100) for _ in range(100)] for _ in range(99)]
b=[1]+[100]*99;c=list(range(100))
cases.append((a,b,c,0,99))
text=str(len(cases))+'\n'
for a,b,c,_,_ in cases:
    text+=f'{len(c)} {len(b)}\n'+' '.join(map(str,c))+'\n'
    text+=''.join(' '.join(map(str,row+[rhs]))+'\n' for row,rhs in zip(a,b))
source=(root/'src/compact/simplex.hpp').read_text()
body=source.split('// BEGIN Simplex\n')[1].split('// END Simplex')[0]
driver=(root/'tests/simplex.cpp').read_text()
copy='#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'+body+driver.split('\n',1)[1]
(build/'copied.cpp').write_text(copy)
reports={}
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
    for form in ['header','ndebug','copied']:
        exe=build/f'{mode}-{form}'
        src=build/'copied.cpp' if form=='copied' else root/'tests/simplex.cpp'
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
        t=time.monotonic()
        result=subprocess.run([str(exe)],input=text,text=True,capture_output=True,timeout=60,check=True)
        assert not result.stderr, result.stderr
        lines=result.stdout.splitlines()
        assert len(lines)==len(cases)
        for k,(line,(a,b,c,status,value)) in enumerate(zip(lines,cases)):
            out=line.split();assert int(out[0])==status,(k,line,a,b,c,status,value)
            if status:continue
            val=float(out[1]);x=list(map(float,out[2:]));assert len(x)==len(c)
            assert abs(val-float(value))<=1e-8*(1+abs(float(value))),(k,line,value)
            assert all(v>=-1e-8 for v in x),(k,line)
            assert all(sum(u*v for u,v in zip(row,x))<=rhs+1e-8*(1+abs(rhs)) for row,rhs in zip(a,b)),(k,line)
            assert abs(sum(u*v for u,v in zip(c,x))-val)<=1e-8*(1+abs(val)),(k,line)
        reports[f'{mode}-{form}']={'status':'pass','cases':len(cases),'seconds':round(time.monotonic()-t,3)}
        print(mode,form,len(cases),'PASS',flush=True)
(root/'verification/simplex-local.json').write_text(json.dumps({'status':'pass','oracle':'Exact Fraction vertex enumeration; unbounded iff feasible recession direction with c*d>=1','cases':len(cases),'status_counts':{str(s):sum(x[3]==s for x in cases) for s in range(3)},'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'forms':reports},indent=2)+'\n')
