#!/usr/bin/env python3
"""Compare exact attachment programs and current drivers to independent oracles."""
from pathlib import Path
import hashlib,itertools,json,math,os,random,re,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1];out=root/'build/matrix-source';out.mkdir(parents=True,exist_ok=True)
text=(root/'build/issue11-reference.txt').read_text()
for name,start,end,count in [('inverse','    3.6      6. 矩阵求逆','3.7     7. Matrix-Tree',75),('tree','3.7     7. Matrix-Tree','3.8       8. 中国剩余定理',86)]:
 section=text[text.index(start):text.index(end,text.index(start)+len(start))]
 pairs=[(int(m[1]),m[2]) for line in section.splitlines() if (m:=re.match(r'^\s*(\d+)\s+(.*)$',line)) and not re.match(r'数学',m[2])]
 assert [n for n,_ in pairs]==list(range(1,count+1))
 (out/(name+'.cpp')).write_text('\n'.join(c for n,c in pairs)+'\n')
P=1000000007;rng=random.Random(47836178)
def determinant(a):
 n=len(a);ans=0
 for p in itertools.permutations(range(n)):
  inversions=sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
  v=(-1)**inversions
  for i in range(n):v*=a[i][p[i]]
  ans+=v
 return ans%P
inverse_cases=[]
for _ in range(200):
 n=rng.randrange(1,6);a=[[rng.randrange(P) for j in range(n)] for i in range(n)]
 if n>1 and rng.randrange(3)==0:a[-1]=a[0][:]
 inverse_cases.append((a,determinant(a)!=0))
for n in [1,2,5,40,400]:
 a=[[int(j==n-1-i) for j in range(n)] for i in range(n)]
 inverse_cases.append((a,True))
tree_cases=[]
for _ in range(160):
 n=rng.randrange(1,6);kind=rng.randrange(2)
 edges=[(rng.randrange(n),rng.randrange(n),rng.randrange(1,10**9+1)) for i in range(rng.randrange(10))]
 answer=0
 for selected in itertools.combinations(range(len(edges)),n-1):
  reach=[[i==j for j in range(n)] for i in range(n)];ind=[0]*n;prod=1
  for k in selected:
   u,v,w=edges[k];reach[u][v]=True;ind[v]+=1;prod*=w
   if kind==0:reach[v][u]=True
  for k in range(n):
   for i in range(n):
    for j in range(n):reach[i][j]|=reach[i][k] and reach[k][j]
  if all(reach[0]) and (kind==0 or ind==[0]+[1]*(n-1)):answer+=prod
 tree_cases.append((n,kind,edges,answer%P))
for kind in [0,1]:
 n=300;edges=[(u,v,7) for u in range(n) for v in range(n) if u!=v and (kind or u<v)]
 edges += [(0,0,10**9)]*(100000-len(edges))
 tree_cases.append((n,kind,edges,pow(n,n-2,P)*pow(7,n-1,P)%P))
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
result={}
for mode in ['normal','sanitizer']:
 flags=['-std=c++20','-O2']+(['-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else [])
 for kind in ['inverse','tree']:
  for form in ['source','current']:
   src=out/(kind+'.cpp') if form=='source' else root/('verify/luogu/'+('P4783' if kind=='inverse' else 'P6178')+'.compact.cpp')
   exe=out/(kind+'-'+form+'-'+mode)
   subprocess.run([CXX,*flags,str(src),'-o',str(exe)],check=True)
   def run(data):
    r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,env=env,timeout=60)
    assert not r.stderr,r.stderr
    return r.stdout.split()
   if kind=='inverse':
    for a,invertible in inverse_cases:
     n=len(a);got=run(str(n)+'\n'+'\n'.join(' '.join(map(str,row)) for row in a)+'\n')
     if not invertible:assert got==['No','Solution'];continue
     v=list(map(int,got));assert len(v)==n*n
     b=[v[i*n:(i+1)*n] for i in range(n)]
     if n>5:
      assert b==a
     else:
      for i in range(n):
       for j in range(n):
        assert sum(a[i][k]*b[k][j] for k in range(n))%P==int(i==j)
        assert sum(b[i][k]*a[k][j] for k in range(n))%P==int(i==j)
    result[kind+'-'+form+'-'+mode]=len(inverse_cases)
   else:
    for n,typ,edges,expected in tree_cases:
     got=run(f'{n} {len(edges)} {typ}\n'+''.join(f'{u+1} {v+1} {w}\n' for u,v,w in edges))
     assert got==[str(expected)],(n,typ,got,expected)
    result[kind+'-'+form+'-'+mode]=len(tree_cases)
   print(kind,form,mode,'PASS',flush=True)
paths=['src/compact/matrix_inverse.hpp','src/compact/matrix_tree.hpp','src/compact/det_prime.hpp','verify/luogu/P4783.compact.cpp','verify/luogu/P6178.compact.cpp','tests/matrix_source_audit.py']
report=dict(status='pass',results=result,hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},pdf_sha256=hashlib.sha256((root/'build/issue11-reference.pdf').read_bytes()).hexdigest(),original_hashes={n:hashlib.sha256((out/(n+'.cpp')).read_bytes()).hexdigest() for n in ['inverse','tree']},source_pages=list(range(82,90)),scope='Attachment 3.6 full inverse and 3.7.1 P6178 core protocol. P4336/P3317/P4455 modelling not covered. Local tests only, no new online record.')
(root/'verification/matrix-source-audit.json').write_text(json.dumps(report,indent=2)+'\n')
