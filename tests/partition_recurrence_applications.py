"""Complete partition and BM/Kitamasa drivers with independent references."""
from compiler_config import CXX
from pathlib import Path
import hashlib
import itertools
import json
import os
import random
import subprocess
import time

root=Path(__file__).resolve().parents[1]
mod=998244353
mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
flags=['-O2'] if mode=='normal' else ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
exe={}
sources={'partition':'verify/library_checker/partition_function.compact.cpp','running':'verify/luogu/P6189.compact.cpp','recurrence':'verify/luogu/P5487.compact.cpp'}
for key,path in sources.items():
    exe[key]=root/f'build/math-usage-{key}-{mode}'
    subprocess.run([CXX,'-std=c++20',*flags,str(root/path),'-o',str(exe[key])],check=True)
for name in ['partition_split_oracle','recurrence_vandermonde']:
    exe[name]=root/f'build/{name}-{mode}'
    subprocess.run([CXX,'-std=c++20','-O2',str(root/f'tests/{name}.cpp'),'-o',str(exe[name])],check=True)
counts=dict(partition=0,running=0,recurrence=0)
timings=[]

def run(key,data,timeout=180):
    start=time.monotonic()
    p=subprocess.run([str(exe[key])],input=data,text=True,capture_output=True,check=True,timeout=timeout)
    assert not p.stderr,p.stderr
    return p.stdout,time.monotonic()-start

# Exact integer coin DP through1000; its reductions support arbitrary moduli.
exact=[1]+[0]*1000
for part in range(1,1001):
    for n in range(part,1001):
        exact[n]+=exact[n-part]
for n in [0,1,2,5,10,30,100,1000]:
    out,_=run('partition',f'{n}\n')
    assert list(map(int,out.split()))==[x%mod for x in exact[:n+1]]
    counts['partition']+=1
for p in [1,2,6,97,1000000006,1073741823]:
    for n in [1,2,5,30,100,1000,100000]:
        data=f'{n} {p}\n'
        reference,_=run('partition_split_oracle',data)
        if n<=1000:
            assert int(reference)==exact[n]%p
        out,elapsed=run('running',data)
        assert int(out)==int(reference)
        counts['running']+=1
        if n==100000:timings.append(dict(problem='P6189',n=n,mod=p,seconds=elapsed))


def solve_unique(sequence):
    # Search increasing order using Gaussian elimination on every observed
    # recurrence equation. No BM update or polynomial reduction is reused.
    for k in range(len(sequence)+1):
        rows=[[sequence[i-j-1] for j in range(k)]+[sequence[i]] for i in range(k,len(sequence))]
        rank=0
        pivots=[]
        for col in range(k):
            pivot=next((i for i in range(rank,len(rows)) if rows[i][col]),None)
            if pivot is None:continue
            rows[rank],rows[pivot]=rows[pivot],rows[rank]
            inv=pow(rows[rank][col],-1,mod)
            rows[rank]=[x*inv%mod for x in rows[rank]]
            for i in range(len(rows)):
                if i!=rank and rows[i][col]:
                    t=rows[i][col]
                    rows[i]=[(x-t*y)%mod for x,y in zip(rows[i],rows[rank])]
            pivots.append(col)
            rank+=1
        if any(all(x==0 for x in row[:k]) and row[k] for row in rows):continue
        assert rank==k,'Fixture violates official uniqueness guarantee'
        answer=[0]*k
        for i,col in enumerate(pivots):answer[col]=rows[i][-1]
        return answer
    raise AssertionError('No recurrence')

def nth(sequence,c,m):
    k=len(c)
    if not k:return 0
    def multiply(a,b):
        return [[sum(a[i][t]*b[t][j] for t in range(k))%mod for j in range(k)] for i in range(k)]
    a=[list(c)]+[[int(j==i-1) for j in range(k)] for i in range(1,k)]
    r=[[int(i==j) for j in range(k)] for i in range(k)]
    exponent=m-k+1
    while exponent:
        if exponent&1:r=multiply(r,a)
        a=multiply(a,a)
        exponent//=2
    return sum(r[0][i]*sequence[k-1-i] for i in range(k))%mod

def validate(output,c,value):
    lines=output.splitlines()
    assert len(lines)==2
    assert list(map(int,lines[0].split()))==c
    assert list(map(int,lines[1].split()))==[value]

def check(sequence,m):
    assert 1<=len(sequence)<m<=10**9
    c=solve_unique(sequence)
    want=nth(sequence,c,m)
    data=f'{len(sequence)} {m}\n'+' '.join(map(str,sequence))+'\n'
    out,_=run('recurrence',data)
    validate(out,c,want)
    counts['recurrence']+=1

check([1,1,2,3],10)
check([3,7,27,95,339],10)
check([0],2)
check([1,0,0,0],1000000000)
rng=random.Random(54876189)
for values in itertools.product(range(3),repeat=4):
    c=list(values[:2]);sequence=list(values[2:])
    for i in range(2,8):sequence.append(sum(c[j]*sequence[i-j-1] for j in range(2))%mod)
    check(sequence,1000000000)
for _ in range(200):
    k=rng.randrange(1,9)
    c=[rng.randrange(mod) for _ in range(k)]
    s=[rng.randrange(mod) for _ in range(k)]
    for i in range(k,2*k+3):s.append(sum(c[j]*s[i-j-1] for j in range(k))%mod)
    check(s,rng.randrange(len(s)+1,1000000001))
for k in [1,2,10,5000]:
    inp=root/f'build/recurrence-vander-{k}-{mode}.in'
    answer=inp.with_suffix('.ans')
    subprocess.run([str(exe['recurrence_vandermonde']),str(k),'1000000000',str(inp),str(answer)],check=True)
    expected=answer.read_text().splitlines()
    c=list(map(int,expected[0].split()));value=int(expected[1])
    if k<=10:
        seq=list(map(int,inp.read_text().splitlines()[1].split()))
        assert solve_unique(seq)==c and nth(seq,c,1000000000)==value
    out,elapsed=run('recurrence',inp.read_text())
    validate(out,c,value)
    counts['recurrence']+=1
    timings.append(dict(problem='P5487',k=k,n=2*k,m=1000000000,seconds=elapsed,fixture='Vandermonde distinct roots, provably unique order k'))
for output,c,value in [('2 1 1\n89\n',[1,1],89),('1 1\n88\n',[1,1],89),('2 3\n691707\n',[3,2],691707),('0\n',[],0),('1 1 89\n',[1,1],89)]:
    try:validate(output,c,value)
    except AssertionError:pass
    else:raise AssertionError('Invalid output accepted')
paths=[Path(__file__).resolve(),*[root/p for p in sources.values()],*[root/f'tests/{n}.cpp' for n in ['partition_split_oracle','recurrence_vandermonde']],root/'src/compact/partitions.hpp',root/'src/compact/recurrence.hpp']
proof=dict(mode=mode,cases=counts,negative_controls=5,timings=timings,scope='Local full drivers, no online AC or OJ speed ranking',references='Exact coin DP and small/large part decomposition; independent Gaussian minimality, matrix powers; order5000 Vandermonde fixture',sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
(root/f'verification/partition-recurrence-applications-{mode}.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof,indent=2))
