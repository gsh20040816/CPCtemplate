from pathlib import Path
import itertools,math,random,subprocess,time,os
root=Path(__file__).resolve().parents[1]
p=1000000007
rng=random.Random(8237)
def oracle(a,b,w):
    n=len(a)
    total=[0]*n
    for order in itertools.permutations(range(n)):
        v=list(a)
        for u in order:
            if v[u]<v[b[u]]: v[u]+=w[u]
        for u in range(n): total[u]+=v[u]
    inverse=pow(math.factorial(n),p-2,p)
    return [v*inverse%p for v in total]
cases=[]
for n in range(1,4):
    for a in itertools.product(range(1,4),repeat=n):
        for b in itertools.product(range(n),repeat=n):
            for w in itertools.product(range(1,3),repeat=n):
                cases.append((a,b,w,oracle(a,b,w)))
for n,count in [(4,60),(5,60),(6,40),(7,20),(8,6)]:
    for _ in range(count):
        a=[rng.randrange(1,7) for _ in range(n)]
        b=[rng.randrange(n) for _ in range(n)]
        w=[rng.randrange(1,7) for _ in range(n)]
        cases.append((a,b,w,oracle(a,b,w)))
def run(exe,items):
    lines=[str(len(items))]
    want=[]
    for a,b,w,expected in items:
        lines += [str(len(a)),' '.join(map(str,a)),' '.join(str(x+1) for x in b),' '.join(map(str,w))]
        want.append(expected)
    start=time.monotonic()
    got=[list(map(int,line.split())) for line in subprocess.check_output([str(exe)],input='\n'.join(lines)+'\n',text=True).splitlines()]
    assert got==want
    return time.monotonic()-start
n=500000
inverse=[1]*n
for i in range(1,n): inverse[i]=inverse[i-1]*i%p
inverse[-1]=pow(inverse[-1],p-2,p)
for i in range(n-1,0,-1): inverse[i-1]=inverse[i]*i%p
chain=([1]*(n-1)+[2],list(range(1,n))+[n-1],[1]*n,[(1+inverse[n-1-i])%p for i in range(n-1)]+[2])
cycle=([10**9]*n,list(range(1,n))+[0],[10**9]*n,[10**9]*n)
for style in ['compact','classic']:
    source=root/f'build/submit/QOJ8237.{style}.cpp'
    sanitized=os.environ.get('CPC_SANITIZE')=='1'
    exe=root/f'build/QOJ8237.{style}{"-san" if sanitized else ""}'
    subprocess.run(['python3','tools/bundle.py',f'verify/qoj/8237.{style}.cpp',str(source)],cwd=root,check=True)
    flags=['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if sanitized else ['-O2']
    subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20',*flags,str(source),'-o',str(exe)],check=True)
    run(exe,cases)
    print(f'QOJ8237 {style}: exhaustive n<=3 inputs and all-permutation simulation through n=8 PASS',flush=True)
    for name,case in [('chain',chain),('cycle',cycle)]:
        elapsed=run(exe,[case])
        print(f'QOJ8237 {style}: n=500000 {name} closed-form checks PASS ({elapsed:.3f}s)',flush=True)
    singleton=([10**9],[0],[10**9],[10**9])
    elapsed=run(exe,[singleton]*500000)
    print(f'QOJ8237 {style}: 500000 singleton test cases and factorial-cache reuse PASS ({elapsed:.3f}s)',flush=True)
