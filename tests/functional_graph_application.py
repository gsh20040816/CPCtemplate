from pathlib import Path
import subprocess,random
root=Path(__file__).resolve().parents[1]
rng=random.Random(11075)
for style in ['compact']:
    for problem in ['P2921','1750','1160']:
        folder='luogu' if problem=='P2921' else 'cses'
        source=root/f'build/submit/{problem}.{style}.cpp'
        exe=root/f'build/{problem}.{style}'
        subprocess.run(['python3','tools/bundle.py',f'verify/{folder}/{problem}.{style}.cpp',str(source)],cwd=root,check=True)
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(source),'-o',str(exe)],check=True)
        def check(to,queries,want):
            n=len(to)
            first=str(n) if problem=='P2921' else f'{n} {len(queries)}'
            data=first+'\n'+' '.join(str(x+1) for x in to)+'\n'
            data+=''.join(f'{u+1} {v if problem=="1750" else v+1}\n' for u,v in queries)
            got=list(map(int,subprocess.check_output([str(exe)],input=data,text=True).split()))
            assert got==want,(style,problem,n)
        for trial in range(100):
            n=rng.randrange(1,70)
            to=[rng.randrange(n) for _ in range(n)]
            queries=[]
            want=[]
            for u in range(n):
                path=[]
                seen={}
                v=u
                while v not in seen:
                    seen[v]=len(path)
                    path.append(v)
                    v=to[v]
                tail=seen[v]
                length=len(path)-tail
                if problem=='P2921': want.append(len(path))
                elif problem=='1750':
                    for k in [0,1,n,10**9]:
                        queries.append((u,k))
                        want.append(path[k if k<len(path) else tail+(k-tail)%length]+1)
                else:
                    for v in range(n):
                        queries.append((u,v))
                        want.append(seen.get(v,-1))
            check(to,queries,want)
        n=100000 if problem=='P2921' else 200000
        start=n//3
        to=list(range(1,n))+[start]
        queries=[]
        want=[]
        if problem=='P2921': want=[n-i if i<start else n-start for i in range(n)]
        else:
            for _ in range(200000):
                u=rng.randrange(n)
                if problem=='1750':
                    k=rng.randrange(10**9+1)
                    queries.append((u,k))
                    if u+k<n: v=u+k
                    else: v=start+(u+k-start)%(n-start)
                    want.append(v+1)
                else:
                    v=rng.randrange(n)
                    queries.append((u,v))
                    want.append(v-u if v>=u else n-u+v-start if v>=start else -1)
        check(to,queries,want)
        print(f'{problem} {style}: first-visit walk oracle and maximum-size tail/cycle drivers PASS',flush=True)
