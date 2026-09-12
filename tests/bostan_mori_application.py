from pathlib import Path
import subprocess, random
root=Path(__file__).resolve().parents[1]
P=998244353
rng=random.Random(1024)
for style in ['compact']:
    source=root/f'build/submit/P4723.{style}.cpp'
    subprocess.run(['python3','tools/bundle.py',f'verify/luogu/P4723.{style}.cpp',str(source)],cwd=root,check=True)
    exe=root/f'build/P4723.{style}'
    subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(source),'-o',str(exe)],check=True)
    def check(n,c,init,want):
        data=f'{n} {len(c)}\n'+ ' '.join(map(str,c))+'\n'+' '.join(map(str,init))+'\n'
        got=int(subprocess.check_output([str(exe)],input=data,text=True))
        assert got==want,(style,n,len(c),got,want)
    for case in range(100):
        k=rng.randrange(1,16)
        n=rng.randrange(150)
        c=[rng.randint(-10**9,10**9) for _ in range(k)]
        init=[rng.randint(-10**9,10**9) for _ in range(k)]
        a=[x%P for x in init]
        for i in range(k,n+1):
            a.append(sum(c[j]*a[i-1-j] for j in range(k))%P)
        check(n,c,init,a[n])
    k=32000
    n=10**9
    c=[]
    a=[]
    binomial=value=1
    for i in range(k):
        a.append(value)
        value=value*(k+i)*pow(i+1,P-2,P)%P
        binomial=binomial*(k-i)*pow(i+1,P-2,P)%P
        c.append(binomial if i%2==0 else -binomial)
    want=1
    for i in range(1,k): want=want*(n+i)*pow(i,P-2,P)%P
    check(n,c,a,want)
    print(f'P4723 {style}: signed-input recurrence DP and dense maximum-order binomial oracle PASS')
