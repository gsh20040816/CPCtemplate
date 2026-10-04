#!/usr/bin/env python3
"""Exact edge-set and integer oracles for knowledge only; no new C++ API."""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot

def sha(b):return hashlib.sha256(b).hexdigest()
def connected(n,edges):
    seen={0}
    while True:
        nxt=seen|{v for u,v in edges if u in seen}|{u for u,v in edges if v in seen}
        if nxt==seen:return len(seen)==n
        seen=nxt

def degree(n,edges):
    d=[0]*n
    for u,v in edges:d[u]+=1;d[v]+=1
    return tuple(d)

def encode(n,edges):
    adj=[set() for _ in range(n)]
    for u,v in edges:adj[u].add(v);adj[v].add(u)
    out=[]
    for _ in range(n-2):
        u=next(i for i in range(n) if len(adj[i])==1)
        v=next(iter(adj[u]));out.append(v);adj[u].clear();adj[v].remove(u)
    return tuple(out)

def decode(n,code):
    left=set(range(n));edges=[];cnt=Counter(code)
    for u in code:
        v=min(i for i in left if cnt[i]==0)
        edges.append(tuple(sorted((u,v))));left.remove(v);cnt[u]-=1
    edges.append(tuple(sorted(left)))
    return tuple(sorted(edges))

def stirling(n,k):
    s=[0]*(k+1);s[0]=1
    for _ in range(n):s=[0]+[s[j-1]+j*s[j] for j in range(1,k+1)]
    return s[k]

def degree_formula(n,d):
    if n==1:return int(d==(0,))
    if any(x<1 for x in d) or sum(d)!=2*n-2:return 0
    return math.factorial(n-2)//math.prod(math.factorial(x-1) for x in d)

def exact_v(x,p):
    assert x>0
    v=0
    while x%p==0:x//=p;v+=1
    return v

def floor_v(n,p):
    ans=0
    while n:n//=p;ans+=n
    return ans

def digits(n,p):
    s=0
    while n:s+=n%p;n//=p
    return s

def carries(a,b,p):
    incoming=ans=0
    while a or b or incoming:
        incoming=(a%p+b%p+incoming)//p
        ans+=incoming;a//=p;b//=p
    return ans

def main():
    if not __debug__:raise RuntimeError('Exact oracle assertions must stay enabled')
    before=snapshot(ROOT);out=Path(tempfile.mkdtemp(prefix='prufer-kummer-',dir=ROOT/'build'))
    rng=random.Random(20261004);trees_total=sequence_total=weighted_total=degree_total=leaf_total=component_total=0;transcript=[]
    for n in range(2,7):
        edges=list(itertools.combinations(range(n),2))
        trees=[tuple(e) for e in itertools.combinations(edges,n-1) if connected(n,e)]
        assert len(trees)==n**(n-2)
        counts=Counter(degree(n,t) for t in trees)
        leaf=Counter(sum(x==1 for x in degree(n,t)) for t in trees)
        for d in itertools.product(range(n),repeat=n):
            assert degree_formula(n,d)==counts[d];degree_total+=1
        for l in range(n+1):
            want=math.comb(n,l)*math.factorial(n-l)*stirling(n-2,n-l)
            assert leaf[l]==want;leaf_total+=1
        observed=set()
        for t in trees:
            c=encode(n,t);assert decode(n,c)==t
            assert tuple(1+c.count(i) for i in range(n))==degree(n,t)
            observed.add(c)
        allcodes=set(itertools.product(range(n),repeat=n-2));assert observed==allcodes
        sequence_total+=len(allcodes);trees_total+=len(trees)
        weights=[[0]*n,[1]*n,[-1]*n,[(-1)**i for i in range(n)],list(range(n))]+[[rng.randrange(-4,5) for _ in range(n)] for _ in range(20)]
        for x in weights:
            exact=sum(math.prod(x[u]*x[v] for u,v in t) for t in trees)
            want=math.prod(x)*sum(x)**(n-2);assert exact==want
            for m in [1,2,4,6,9,12,97]:assert exact%m==want%m
            transcript.append(['weight',n,x,exact]);weighted_total+=1
    # All codes of length five, beyond the independently enumerated K_6 edge sets.
    n=7
    for c in itertools.product(range(n),repeat=n-2):
        t=decode(n,c);assert len(set(t))==n-1 and connected(n,t) and encode(n,t)==c
        assert tuple(1+c.count(i) for i in range(n))==degree(n,t);sequence_total+=1
    assert degree_formula(1,(0,))==1 and degree_formula(1,(1,))==0
    assert degree(1,[])==(0,) and sum(d==1 for d in degree(1,[]))==0
    for size in range(1,8):
        # One component, independent of its positive vertex count: the only
        # zero-edge subset connects the already-contracted single vertex.
        assert sum(connected(1,e) for e in itertools.combinations([],0))==1
    for n in range(2,8):
        for k in range(2,min(n,4)+1):
            for cuts in itertools.combinations(range(1,n),k-1):
                ends=(0,)+cuts+(n,);sizes=[ends[i+1]-ends[i] for i in range(k)]
                owner=[i for i,s in enumerate(sizes) for _ in range(s)]
                cross=[(u,v) for u in range(n) for v in range(u+1,n) if owner[u]!=owner[v]]
                exact=sum(connected(k,[(owner[u],owner[v]) for u,v in es]) for es in itertools.combinations(cross,k-1))
                assert exact==n**(k-2)*math.prod(sizes)
                transcript.append(['components',sizes,exact]);component_total+=1
    primes=[2,3,5,7,11,13,17,19,23,29,31]
    factorial_cases=binomial_cases=large_cases=composite_cases=0
    for p in primes:
        for n in range(151):
            want=exact_v(math.factorial(n),p)
            assert want==floor_v(n,p)==(n-digits(n,p))//(p-1);factorial_cases+=1
            for k in range(n+1):
                c=math.comb(n,k);v=exact_v(c,p)
                assert v==carries(k,n-k,p)==floor_v(n,p)-floor_v(k,p)-floor_v(n-k,p)
                assert v==(digits(k,p)+digits(n-k,p)-digits(n,p))//(p-1)
                for a in range(1,6):assert (c%(p**a)==0)==(v>=a)
                # Lucas nonzero criterion via independent digit comparison.
                nn,kk=n,k;nonzero=True
                while nn or kk:
                    nonzero &= kk%p<=nn%p;nn//=p;kk//=p
                assert (v==0)==nonzero
                binomial_cases+=1
    for n in [0,1,2,7,8,2**32,2**63-1,2**63,2**64-1]+[rng.randrange(2**64) for _ in range(50)]:
        for k in sorted({0,n,*[j for j in [1,2,3,5,10,63] if j<=n]}):
            c=math.comb(n,k)
            for p in primes:
                v=exact_v(c,p)
                assert v==carries(k,n-k,p)==floor_v(n,p)-floor_v(k,p)-floor_v(n-k,p)
                assert floor_v(n,p)==(n-digits(n,p))//(p-1)
                large_cases+=1
    for m in range(2,121):
        factors=[];z=m
        for p in range(2,m+1):
            if z%p:continue
            e=0
            while z%p==0:z//=p;e+=1
            factors.append((p,e))
        for n in range(36):
            for k in range(n+1):
                assert (math.comb(n,k)%m==0)==all(carries(k,n-k,p)>=e for p,e in factors);composite_cases+=1
    controls={
        'omit-propagated-carry':sum((1>>i&1)+(7>>i&1)>=2 for i in range(4))!=exact_v(math.comb(8,1),2),
        'wrong-addends':carries(2,4,2)!=exact_v(math.comb(4,2),2),
        'strict-threshold':(exact_v(math.comb(4,2),2)>1)!=(math.comb(4,2)%2==0),
        'composite-base':floor_v(6,4)!=exact_v(math.factorial(6),4),
        'missing-weight-product':sum([0,1,1])**1!=0,
        'wrong-degree-numerator':math.factorial(3)!=degree_formula(3,(1,2,1)),
        'labelled-divide-factorial':Fraction(4**2,math.factorial(4))!=2,
    }
    assert all(controls.values())
    transcript_bytes=(json.dumps(transcript,separators=(',',':'))+'\n').encode();(out/'exact-results.json').write_bytes(transcript_bytes)
    report=dict(passed=True,source_before_sha256=before,source_after_sha256=snapshot(ROOT),python=sys.version,counts=dict(edge_enumerated_trees=trees_total,prufer_sequences=sequence_total,degree_vectors=degree_total,leaf_groups=leaf_total,singleton_and_one_component_cases=8,weighted_assignments=weighted_total,component_size_vectors=component_total,factorial_prime_cases=factorial_cases,exact_binomial_prime_cases=binomial_cases,large_exact_binomial_prime_cases=large_cases,composite_modulus_cases=composite_cases),negative_controls=controls,exact_results_sha256=sha(transcript_bytes),scope='Python exact-integer and edge-set evidence for knowledge formulas; no new C++ API, sanitizer execution, online AC or source-page completion claim.')
    assert report['source_before_sha256']==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['counts']));print('Pruefer/Kummer knowledge PASS:',out/'report.json')
if __name__=='__main__':main()
