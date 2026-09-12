from pathlib import Path
import subprocess, random
root=Path(__file__).resolve().parents[1]
rng=random.Random(6178)
P=1000000007
cases=[]
for _ in range(100):
    n=rng.randrange(1,6)
    kind=rng.randrange(2)
    edges=[(rng.randrange(n),rng.randrange(n),rng.randrange(1,10**9+1)) for _ in range(rng.randrange(1,10))]
    want=0
    for mask in range(1<<len(edges)):
        if mask.bit_count()!=n-1: continue
        reach=[[i==j for j in range(n)] for i in range(n)]
        indegree=[0]*n
        weight=1
        for i,(u,v,w) in enumerate(edges):
            if mask>>i&1:
                reach[u][v]=True
                indegree[v]+=1
                if not kind: reach[v][u]=True
                weight*=w
        for k in range(n):
            for i in range(n):
                for j in range(n): reach[i][j]|=reach[i][k] and reach[k][j]
        if all(reach[0]) and (not kind or indegree==[0]+[1]*(n-1)): want=(want+weight)%P
    cases.append((n,kind,edges,want))
for kind in [0,1]:
    n=300
    edges=[(u,v,7) for u in range(n) for v in range(n) if u!=v and (kind or u<v)]
    edges += [(0,0,10**9)]*(100000-len(edges))
    want=pow(n,n-2,P)*pow(7,n-1,P)%P
    cases.append((n,kind,edges,want))
cases.append((1,1,[(0,0,10**9)],1))
for style in ['compact','classic']:
    path=root/f'build/submit/P6178.{style}.cpp'
    subprocess.run(['python3','tools/bundle.py',f'verify/luogu/P6178.{style}.cpp',str(path)],cwd=root,check=True)
    exe=root/f'build/P6178.{style}'
    subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(path),'-o',str(exe)],check=True)
    for n,kind,edges,want in cases:
        data=f'{n} {len(edges)} {kind}\n'+''.join(f'{u+1} {v+1} {w}\n' for u,v,w in edges)
        got=int(subprocess.check_output([str(exe)],input=data,text=True))
        assert got==want,(style,n,kind,got,want)
    print(f'P6178 {style}: 103 complete drivers, directed outward convention and 300 vertices/100000 edges PASS')
