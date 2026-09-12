from pathlib import Path
import subprocess, random
root=Path(__file__).resolve().parents[1]
p=998244353
rng=random.Random(3171)
limit=524288
# Sum_{i=j}^{n-1} binom(i,j) = binom(n,j+1).
shift_want=[]
binomial=1
for j in range(limit):
    binomial=binomial*(limit-j)*pow(j+1,p-2,p)%p
    shift_want.append(binomial)
points=[]
x=123
for i in range(limit):
    points.append(limit if x==1 else (pow(x,limit,p)-1)*pow((x-1)%p,p-2,p)%p)
    x=x*3%p
for style in ['compact','classic']:
    for problem in ['polynomial_taylor_shift','multipoint_evaluation_on_geometric_sequence']:
        path=root/f'build/submit/{problem}.{style}.cpp'
        subprocess.run(['python3','tools/bundle.py',f'verify/library_checker/{problem}.{style}.cpp',str(path)],cwd=root,check=True)
        exe=root/f'build/{problem}.{style}'
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(path),'-o',str(exe)],check=True)
        for case in range(60):
            n=rng.randrange(1,40)
            f=[rng.randrange(p) for _ in range(n)]
            if problem=='polynomial_taylor_shift':
                c=case%3 and rng.randrange(p)
                want=[0]*n
                choose=[1]
                for i in range(n):
                    for j in range(i+1): want[j]=(want[j]+f[i]*choose[j]*pow(c,i-j,p))%p
                    choose=[1]+[(choose[j-1]+choose[j])%p for j in range(1,i+1)]+[1]
                first=f'{n} {c}'
            else:
                m=rng.randrange(1,60)
                a=rng.randrange(p) if case%7 else 0
                r=rng.randrange(p) if case%5 else case%2
                first=f'{n} {m} {a} {r}'
                want=[]
                point=a
                for i in range(m):
                    v=0
                    for c in reversed(f): v=(v*point+c)%p
                    want.append(v)
                    point=point*r%p
            data=first+'\n'+' '.join(map(str,f))+'\n'
            got=list(map(int,subprocess.check_output([str(exe)],input=data,text=True).split()))
            assert got==want,(style,problem,case)
        first=f'{limit} 1' if problem=='polynomial_taylor_shift' else f'{limit} {limit} 123 3'
        data=first+'\n'+' '.join(['1']*limit)+'\n'
        got=list(map(int,subprocess.check_output([str(exe)],input=data,text=True).split()))
        assert got==(shift_want if problem=='polynomial_taylor_shift' else points)
        print(f'{problem} {style}: 60 independent small cases and full 524288-size closed-form driver checks PASS',flush=True)
