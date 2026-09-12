"""P5170 inclusive endpoint and output-order verification."""
from pathlib import Path
import os,random,subprocess
root=Path(__file__).resolve().parents[1]
mod=998244353
rng=random.Random(5170)
cases=[]
for _ in range(500):
    n=rng.randrange(50); a=rng.randrange(10**9+1); b=rng.randrange(10**9+1); c=rng.randrange(1,10**9+1)
    ys=[(a*i+b)//c for i in range(n+1)]
    cases.append(((n,a,b,c),(sum(ys)%mod,sum(y*y for y in ys)%mod,sum(i*y for i,y in enumerate(ys))%mod)))
fixtures=[]
for n,a,b,c in [(10**9,10**9,10**9,1),(10**9,999999999,10**9,3),(0,0,0,1),(10**9,0,10**9,7)]:
    assert a%c==0
    aa=a//c; bb=b//c; count=n+1; s1=n*(n+1)//2; s2=n*(n+1)*(2*n+1)//6
    fixtures.append(((n,a,b,c),((aa*s1+bb*count)%mod,(aa*aa*s2+2*aa*bb*s1+bb*bb*count)%mod,(aa*s2+bb*s1)%mod)))
fixtures.append(((10**9,1,0,10**9),(1,1,10**9%mod)))
while len(cases)<100000: cases.append(fixtures[len(cases)%len(fixtures)])
data=str(len(cases))+'\n'+''.join(' '.join(map(str,q))+'\n' for q,ans in cases)
expected=[' '.join(map(str,ans)) for q,ans in cases]
for style in ['compact']:
    bundle=root/f'build/P5170.{style}.cpp'; exe=root/f'build/P5170.{style}'
    subprocess.run(['python3','tools/bundle.py',f'verify/luogu/P5170.{style}.cpp',str(bundle)],cwd=root,check=True)
    flags=['-O2'] if os.environ.get('SANITIZE')!='1' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    subprocess.run([os.environ.get('CXX','/opt/homebrew/bin/g++-16'),'-std=c++20',*flags,str(bundle),'-o',str(exe)],check=True)
    result=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,timeout=30)
    assert result.stdout.splitlines()==expected
    assert not result.stderr,result.stderr
    print(f'P5170 {style}: 100000 queries, inclusive 1e9 endpoint, all three outputs and direct/polynomial oracles PASS')
