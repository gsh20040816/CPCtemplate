"""P1593: trial factorization and invertible geometric quotient oracle."""
from pathlib import Path
import math,os,random,subprocess
root=Path(__file__).resolve().parents[1]
mod=9901
assert all(mod%d for d in range(2,math.isqrt(mod)+1))
def oracle(a,b):
    answer=1
    p=2
    while p<=a//p:
        if a%p==0:
            e=0
            while a%p==0:
                a//=p
                e+=1
            length=e*b+1
            term=length%mod if p%mod==1 else (pow(p,length,mod)-1)*pow((p-1)%mod,-1,mod)%mod
            answer=answer*term%mod
        p+=1
    if a>1:
        term=(b+1)%mod if a%mod==1 else (pow(a,b+1,mod)-1)*pow((a-1)%mod,-1,mod)%mod
        answer=answer*term%mod
    return str(answer)
prime_one=next(p for p in range(9902,50000001,9901) if all(p%d for d in range(2,math.isqrt(p)+1)))
cases=[(1,0),(1,50000000),(50000000,0),(50000000,50000000),(9901,50000000),(prime_one,50000000)]
rng=random.Random(1593)
cases += [(rng.randint(1,50000000),rng.randint(0,50000000)) for _ in range(120)]
for style in ['compact','classic']:
    bundle=root/f'build/P1593.{style}.cpp'; exe=root/f'build/P1593.{style}'
    subprocess.run(['python3','tools/bundle.py',f'verify/luogu/P1593.{style}.cpp',str(bundle)],cwd=root,check=True)
    flags=['-O2'] if os.environ.get('SANITIZE')!='1' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    subprocess.run([os.environ.get('CXX','/opt/homebrew/bin/g++-16'),'-std=c++20',*flags,str(bundle),'-o',str(exe)],check=True)
    for a,b in cases:
        result=subprocess.run([str(exe)],input=f'{a} {b}\n',text=True,capture_output=True,check=True,timeout=10)
        assert result.stdout.strip()==oracle(a,b)
        assert not result.stderr,result.stderr
    print(f'P1593 {style}: 126 trial-factor/geometric-quotient cases, zero exponent, maximum inputs and p=0/1 mod 9901 PASS')
