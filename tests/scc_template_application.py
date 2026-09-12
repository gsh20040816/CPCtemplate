from pathlib import Path
import os,random,subprocess
root=Path(__file__).resolve().parents[1]
rng=random.Random(906)
cxx='/opt/homebrew/bin/g++-16'
source=root/'build/submit/QOJ906.compact.cpp'
obj=root/'build/QOJ906.o';exe=root/'build/QOJ906'
subprocess.run(['python3','tools/bundle.py','verify/qoj/906.compact.cpp',str(source)],check=True)
flags=['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if os.getenv('CPC_SANITIZE')=='1' else ['-O2']
subprocess.run([cxx,'-std=c++20',*flags,'-Dmain=cpc_entry','-c',str(source),'-o',str(obj)],check=True)
subprocess.run([cxx,'-std=c++20',*flags,'tests/driver_stack.cpp','-DCPC_STACK_BYTES=1073741824ULL',str(obj),'-pthread','-o',str(exe)],check=True)
def run(n,e,want=None):
    data=f'{n} {len(e)}\n'+''.join(f'{u} {v}\n' for u,v in e)
    out=subprocess.check_output([str(exe)],input=data,text=True).splitlines()
    k=int(out[0]);assert len(out)==k+1
    bel=[-1]*n
    for i,line in enumerate(out[1:]):
        row=list(map(int,line.split()));assert row[0]==len(row)-1 and row[0]>0
        for u in row[1:]:
            assert 0<=u<n and bel[u]==-1
            bel[u]=i
    assert min(bel)>=0
    for u,v in e:assert bel[u]<=bel[v]
    if want is not None:
        assert bel==want
    else:
        reach=[[i==j for j in range(n)] for i in range(n)]
        for u,v in e:reach[u][v]=True
        for t in range(n):
            for u in range(n):
                if reach[u][t]:
                    for v in range(n):reach[u][v]|=reach[t][v]
        for u in range(n):
            for v in range(n):assert (bel[u]==bel[v])==(reach[u][v] and reach[v][u])
for _ in range(300):
    n=rng.randrange(1,20)
    e=[(rng.randrange(n),rng.randrange(n)) for _ in range(rng.randrange(1,n*n+1))]
    run(n,e)
n=500000
run(n,[(i,i+1) for i in range(n-1)],list(range(n)))
run(n,[(i,(i+1)%n) for i in range(n)],[0]*n)
# Distinct SCCs linked in a chain with duplicate edges and loops.
e=[]
for u in range(0,n,2):e.extend([(u,u+1),(u+1,u)])
run(n,e,[(n//2-1-i//2) for i in range(n)])
print('QOJ906 vector driver: independent reachability, topological partition certificates and 500000-vertex recursive chain/cycle PASS')
