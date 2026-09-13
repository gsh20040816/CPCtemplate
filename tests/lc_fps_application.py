"""Validate FPS drivers with independent coefficient recurrences and closed forms."""
from compiler_config import CXX
import os
from pathlib import Path
import random
import subprocess
root=Path(__file__).resolve().parents[1]
p=998244353
flags=['-std=c++20','-O2']
if os.environ.get('SANITIZE')=='1':
    flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined']
rng=random.Random(415739)
for op in ['inv','log','exp']:
    exe=root/('build/lc-fps-'+op)
    src=root/('verify/library_checker/'+op+'_of_formal_power_series.compact.cpp')
    subprocess.run([CXX,*flags,str(src),'-o',str(exe)],check=True)
    def check(a,want):
        data=str(len(a))+'\n'+' '.join(map(str,a))+'\n'
        r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=120)
        assert not r.stderr,r.stderr
        assert list(map(int,r.stdout.split()))==want,(op,len(a))
    for n in [1,2,3,7,8,9,31,32,33,63]:
        for _ in range(4):
            a=[rng.randrange(p) for _ in range(n)]
            a[0]=rng.randrange(1,p) if op=='inv' else (1 if op=='log' else 0)
            b=[0]*n
            b[0]=pow(a[0],p-2,p) if op=='inv' else (1 if op=='exp' else 0)
            for k in range(1,n):
                if op=='inv':
                    b[k]=-sum(a[i]*b[k-i] for i in range(1,k+1))*b[0]%p
                elif op=='log':
                    b[k]=(k*a[k]-sum(i*b[i]*a[k-i] for i in range(1,k)))*pow(k,p-2,p)%p
                else:
                    b[k]=sum(i*a[i]*b[k-i] for i in range(1,k+1))*pow(k,p-2,p)%p
            check(a,b)
    n=500000
    a=[0]*n
    if op=='inv':
        a[0],a[1]=2,p-1
        inv2=(p+1)//2
        want=[inv2]
        for i in range(1,n):want.append(want[-1]*inv2%p)
    elif op=='log':
        a[0],a[1]=1,p-1
        want=[0]+[p-pow(i,p-2,p) for i in range(1,n)]
    else:
        a[1]=1
        fac=1
        for i in range(1,n):fac=fac*i%p
        want=[0]*n
        want[-1]=pow(fac,p-2,p)
        for i in range(n-1,0,-1):want[i-1]=want[i]*i%p
    check(a,want)
    # Constant input at a non-power-of-two truncation boundary.
    n=262145
    a=[0]*n
    a[0]=3 if op=='inv' else (1 if op=='log' else 0)
    want=[0]*n
    want[0]=pow(3,p-2,p) if op=='inv' else (1 if op=='exp' else 0)
    check(a,want)
print('LC FPS drivers: triangular coefficient oracles, constant terms, 262145 truncation and 500000-term analytic series PASS')
