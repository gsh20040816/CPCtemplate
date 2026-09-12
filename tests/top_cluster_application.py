from pathlib import Path
import subprocess,random,time
root=Path(__file__).resolve().parents[1]
rng=random.Random(8235)
def run(exe,w,edges,queries,want):
    lines=[f'{len(w)} {len(queries)}',' '.join(map(str,w))]
    lines += [f'{u} {v} {c}' for u,v,c in edges]
    lines += [f'{x} {k}' for x,k in queries]
    start=time.monotonic()
    output=subprocess.check_output([str(exe)],input='\n'.join(lines)+'\n',text=True)
    assert list(map(int,output.split()))==want
    return time.monotonic()-start
for style in ['compact']:
    source=root/f'build/submit/QOJ8235.{style}.cpp'
    subprocess.run(['python3','tools/bundle.py',f'verify/qoj/8235.{style}.cpp',str(source)],cwd=root,check=True)
    obj=root/f'build/QOJ8235.{style}.o'
    exe=root/f'build/QOJ8235.{style}'
    subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2','-Dmain=cpc_entry','-c',str(source),'-o',str(obj)],check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2','tests/driver_stack.cpp',str(obj),'-pthread','-o',str(exe)],cwd=root,check=True)
    for case in range(100):
        n=rng.randrange(1,40)
        w=rng.sample(range(0,n+10),n)
        if case%3==0:
            w=list(range(n))
            rng.shuffle(w)
        edges=[(v,rng.randrange(1,v),rng.randrange(1,1000000001)) for v in range(2,n+1)]
        g=[[] for _ in range(n)]
        for u,v,c in edges:
            g[u-1].append((v-1,c))
            g[v-1].append((u-1,c))
        queries=[]
        want=[]
        for x in range(n):
            dist=[None]*n
            dist[x]=0
            q=[x]
            for u in q:
                for v,c in g[u]:
                    if dist[v] is None:
                        dist[v]=dist[u]+c
                        q.append(v)
            for k in {0,10**15,*dist,*[max(0,d-1) for d in dist]}:
                values={w[v] for v in range(n) if dist[v]<=k}
                mex=0
                while mex in values: mex+=1
                queries.append((x+1,k))
                want.append(mex)
        run(exe,w,edges,queries,want)
    print(f'QOJ8235 {style}: independent weighted paths, radius boundaries, missing values and mex set oracle PASS',flush=True)
    n=q=500000
    w=list(range(n))
    queries=[]
    want=[]
    for i in range(q):
        x=rng.randrange(1,n+1)
        radius=rng.randrange(n+1) if i%4 else n
        k=radius*10**9
        queries.append((x,k))
        want.append(0 if x-radius>1 else min(n,x+radius))
    edges=[(i-1,i,10**9) for i in range(2,n+1)]
    elapsed=run(exe,w,edges,queries,want)
    print(f'QOJ8235 {style}: n=q=500000 recursive weighted chain closed form PASS ({elapsed:.3f}s)',flush=True)
    queries=[]
    want=[]
    for i in range(q):
        x=rng.randrange(1,n+1)
        k=[0,10**9-1,10**9,2*10**9,10**15][i%5]
        queries.append((x,k))
        if k<10**9: v=1 if x==1 else 0
        elif k>=2*10**9 or x==1: v=n
        else: v=2 if x==2 else 1
        want.append(v)
    edges=[(1,i,10**9) for i in range(2,n+1)]
    elapsed=run(exe,w,edges,queries,want)
    print(f'QOJ8235 {style}: n=q=500000 weighted star closed form PASS ({elapsed:.3f}s)',flush=True)
print('Local driver runner uses a 256 MiB pthread stack with main renamed only at compilation; submitted sources retain ordinary main and recursive DFS.')
