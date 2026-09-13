from compiler_config import CXX
from pathlib import Path
import subprocess, random, itertools, time
root=Path(__file__).resolve().parents[1]
rng=random.Random(82340)
def simulate(a,l,r):
    stack=[]
    for x in a[l-1:r]:
        if x in stack: del stack[stack.index(x):]
        else: stack.append(x)
    return len(stack)
def run(exe,a,queries,want=None):
    last=0
    lines=[f'{len(a)} {len(queries)}',' '.join(map(str,a))]
    answers=[]
    for i,(l,r) in enumerate(queries):
        lines.append(f'{l^last} {r^last}')
        last=simulate(a,l,r) if want is None else want(i,l,r)
        answers.append(last)
    start=time.monotonic()
    output=subprocess.check_output([str(exe)],input='\n'.join(lines)+'\n',text=True)
    assert list(map(int,output.split()))==answers
    return time.monotonic()-start
for style in ['compact']:
    source=root/f'build/submit/QOJ8240.{style}.cpp'
    subprocess.run(['python3','tools/bundle.py',f'verify/qoj/8240.{style}.cpp',str(source)],cwd=root,check=True)
    exe=root/f'build/QOJ8240.{style}'
    subprocess.run([CXX,'-std=c++20','-O2',str(source),'-o',str(exe)],check=True)
    for n in range(1,8):
        for a in itertools.product(range(1,min(2,n)+1),repeat=n):
            queries=[(l,r) for l in range(1,n+1) for r in range(l,n+1)]
            rng.shuffle(queries)
            run(exe,a,queries)
    for t in range(100):
        n=rng.randrange(1,60)
        a=[rng.randrange(1,n+1) for _ in range(n)]
        queries=[tuple(sorted([rng.randrange(1,n+1),rng.randrange(1,n+1)])) for _ in range(100)]
        run(exe,a,queries)
    print(f'QOJ8240 {style}: exhaustive binary arrays through length 7 and random literal card-removal simulation with XOR queries PASS',flush=True)
    n=q=300000
    queries=[tuple(sorted([rng.randrange(1,n+1),rng.randrange(1,n+1)])) for _ in range(q)]
    for label,period in [('distinct',n),('equal',1),('periodic',1000)]:
        a=[i%period+1 for i in range(n)]
        seconds=run(exe,a,queries,lambda i,l,r:(r-l+1)%(period+1))
        print(f'QOJ8240 {style}: n=q=300000 {label} closed-form case PASS ({seconds:.3f}s)',flush=True)
    a=[rng.randrange(1,n//2+1) for _ in range(n)]
    queries=[]
    for _ in range(q):
        l=rng.randrange(1,n+1)
        queries.append((l,min(n,l+rng.randrange(25))))
    seconds=run(exe,a,queries)
    print(f'QOJ8240 {style}: n=q=300000 sparse-repeat array with literal short-query oracle PASS ({seconds:.3f}s)',flush=True)
