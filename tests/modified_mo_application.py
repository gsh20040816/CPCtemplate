from compiler_config import CXX
from pathlib import Path
import os,random,subprocess
root=Path(__file__).resolve().parents[1]
rng=random.Random(1903)
source=root/'build/submit/P1903.compact.cpp'
exe=root/'build/P1903.compact'
subprocess.run(['python3','tools/bundle.py','verify/luogu/P1903.compact.cpp',str(source)],check=True)
flags=['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if os.getenv('CPC_SANITIZE')=='1' else ['-O2']
subprocess.run([CXX,'-std=c++20',*flags,str(source),'-o',str(exe)],check=True)
def run(a,ops,want):
    data=f'{len(a)} {len(ops)}\n'+' '.join(map(str,a))+'\n'+'\n'.join(ops)+'\n'
    got=list(map(int,subprocess.check_output([str(exe)],input=data,text=True).split()))
    assert got==want
for trial in range(60):
    n=rng.randint(1,100)
    a=[rng.randint(1,50) for _ in range(n)]
    current=a[:];ops=[];want=[]
    for _ in range(400):
        if rng.randrange(2):
            l=rng.randrange(n);r=rng.randrange(l+1,n+1)
            ops.append(f'Q {l+1} {r}');want.append(len(set(current[l:r])))
        else:
            p=rng.randrange(n);v=rng.randint(1,50)
            ops.append(f'R {p+1} {v}');current[p]=v
    run(a,ops,want)
run([1],['R 1 2']*133333,[])
run([1],['Q 1 1']*133333,[1]*133333)
n=133333
a=list(range(1,n+1));ops=[];want=[]
for i in range(n):
    if i%2:
        p=rng.randrange(n)
        ops.append(f'R {p+1} {n+i+1}')
    else:
        l=rng.randrange(n);r=rng.randrange(l+1,n+1)
        ops.append(f'Q {l+1} {r}');want.append(r-l)
run(a,ops,want)
print('P1903 vector driver: sequential set oracle, all-update/all-query cases and 133333 unique-color random ranges PASS')
