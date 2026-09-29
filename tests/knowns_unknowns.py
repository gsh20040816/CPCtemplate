"""Full permutation application; enumerate selected subsets, never flow as oracle."""
from compiler_config import CXX
from pathlib import Path
from itertools import combinations, permutations, product
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
mode = 'san' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-std=c++20','-O2'] if mode == 'normal' else ['-std=c++20','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
source = root / f'build/knowns-unknowns-{mode}.cpp'
exe = source.with_suffix('')
subprocess.run(['python3',str(root/'tools/bundle.py'),str(root/'verify/qoj/10424.compact.cpp'),str(source)],check=True)
subprocess.run([CXX,*flags,str(source),'-o',str(exe)],check=True)


def oracle(case):
    p,q,a,b = case
    n,k = len(p),len(a)
    solutions = []
    for chosen in combinations(range(1,n+1),k):
        chosen=set(chosen)
        if all(all(x==-1 or x==y for x,y in zip(s,[v for v in order if v in chosen])) for order,s in [(p,a),(q,b)]):
            solutions.append(chosen)
    if not solutions:return 'Inconsistent'
    return ''.join('Y' if all(v in s for s in solutions) else '?' if any(v in s for s in solutions) else 'N' for v in range(1,n+1))


def text(case):
    p,q,a,b=case
    return '\n'.join([str(len(p)), ' '.join(map(str,p)), ' '.join(map(str,q)),str(len(a)), ' '.join(map(str,a)), ' '.join(map(str,b))])+'\n'


def check(cases,expected=None):
    # Respect the official sum(n)<=2000 even for generated batched input.
    assert sum(len(c[0]) for c in cases)<=2000
    expected=expected or [oracle(c) for c in cases]
    p=subprocess.run([str(exe)],input=str(len(cases))+'\n'+''.join(map(text,cases)),text=True,capture_output=True,check=True,timeout=60)
    assert not p.stderr,p.stderr
    got=p.stdout.splitlines()
    if got!=expected:
        for c,g,w in zip(cases,got,expected):
            if g!=w:raise AssertionError((c,g,w))
        raise AssertionError((got,expected))


sample=[([1,2,3,4],[3,2,4,1],[1,-1,-1],[3,-1,1]),([1,2,3,4],[3,2,4,1],[1,-1,2],[3,-1,1]),([1,2,3],[2,1,3],[-1,2],[-1,-1]),([1,2,3],[3,2,1],[1,3],[2,-1])]
check(sample,['Y?Y?','Inconsistent','YYN','Inconsistent'])
pending=[]
count=0

def append(case):
    global pending,count
    if sum(len(c[0]) for c in pending)+len(case[0])>2000:
        check(pending)
        pending=[]
    pending.append(case)
    count+=1


# Every valid input shape for n<=3, with first permutation normalized to identity.
# Value relabelling accounts for other first permutations.
for n in range(1,4):
    p=list(range(1,n+1))
    for q in permutations(p):
        for k in range(1,n+1):
            lists=[x for x in product([-1]+p,repeat=k) if len([v for v in x if v!=-1])==len({v for v in x if v!=-1})]
            for a in lists:
                for b in lists:append((p,list(q),list(a),list(b)))
check(pending);pending=[]
exhaustive=count
rng=random.Random(2052)
for trial in range(2000):
    n=rng.randint(1,10);k=rng.randint(1,n)
    p=list(range(1,n+1));q=p.copy();rng.shuffle(p);rng.shuffle(q)
    if trial%2:
        chosen=set(rng.sample(p,k))
        a=[v if rng.randrange(3) else -1 for v in p if v in chosen]
        b=[v if rng.randrange(3) else -1 for v in q if v in chosen]
    else:
        a=[v if rng.randrange(2) else -1 for v in rng.sample(p,k)]
        b=[v if rng.randrange(2) else -1 for v in rng.sample(q,k)]
    append((p,q,a,b))
check(pending)
print(f'Knowns and Unknowns: four official sample cases, {exhaustive} exhaustive normalized n<=3 inputs and 2000 independent selected-subset oracles PASS',flush=True)
n=2000;p=list(range(1,n+1));q=p[::-1]
check([(p,q,[-1]*1000,[-1]*1000)],['?'*n])
check([(p,q,[-1]*n,[-1]*n)],['Y'*n])
chosen=set(p[::2]);a=[v for v in p if v in chosen];b=[-1]*len(a)
check([(p,q,a,b)],[''.join('Y' if v in chosen else 'N' for v in p)])
check([(p,q,[1],[2])],['Inconsistent'])
check([(p,q,[-1,1],[-1,-1])],['Inconsistent'])
check([(p,q,[2,1],[-1,-1])],['Inconsistent'])
# 666 independent optional pairs, separated by forced anchors; both professors agree.
# In each consecutive triple, choose one of the first two elements plus the third.
n=1998;p=list(range(1,n+1));a=[]
for v in range(3,n+1,3):a.extend([-1,v])
check([(p,p,a,a)],['??Y'*(n//3)])
# Maximum test count with total n=2000; confirms no cross-test state leakage.
check([([1],[1],[-1],[-1])]*2000,['Y']*2000)
print('Knowns and Unknowns: n=2000 all-unknown/all-selected/exact-set/conflicting-anchor cases, 666 independent choice blocks and 2000-case reset PASS',flush=True)
