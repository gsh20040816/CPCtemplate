"""Independent Prüfer tree probability oracle, using exact integer numerators."""
from pathlib import Path
import itertools,random,subprocess,os,json,hashlib,math
from decimal import Decimal,localcontext
from compiler_config import CXX
root=Path(__file__).resolve().parents[1];out=root/'build/tree-probability';out.mkdir(exist_ok=True)
rng=random.Random(3317);cases=[]
def trees(n):
 if n==1:return [set()]
 ans=[]
 for seq in itertools.product(range(n),repeat=n-2):
  degree=[1]*n
  for v in seq:degree[v]+=1
  edges=set()
  for v in seq:
   u=next(i for i,d in enumerate(degree) if d==1)
   edges.add(tuple(sorted((u,v))));degree[u]-=1;degree[v]-=1
  edges.add(tuple(i for i,d in enumerate(degree) if d==1));ans.append(edges)
 return ans
alltrees={n:trees(n) for n in range(1,7)}
def add(n,weights):
 edges=list(itertools.combinations(range(n),2));numerator=0
 for tree in alltrees[n]:
  v=1
  for e,w in zip(edges,weights):v*=w if e in tree else 100-w
  numerator+=v
 with localcontext() as ctx:
  ctx.prec=90;want=Decimal(numerator)/Decimal(100)**len(edges)
 p=[[0]*n for _ in range(n)]
 for (u,v),w in zip(edges,weights):p[u][v]=p[v][u]=w
 cases.append((p,want))
add(1,[])
for n in range(2,5):
 for w in itertools.product([0,50,100],repeat=n*(n-1)//2):add(n,w)
for _ in range(500):
 n=rng.randrange(2,7);add(n,[rng.choice([0,1,2,33,50,98,99,100]) for _ in range(n*(n-1)//2)])
# Maximum size: known unique tree, forced forest with parallel choices, cut bridge.
for w in [1,50,99,100]:
 p=[[0]*50 for _ in range(50)]
 for u in range(49):p[u][u+1]=p[u+1][u]=w
 with localcontext() as ctx:
  ctx.prec=90;want=(Decimal(w)/100)**49
 cases.append((p,want))
for count in [1,2,20,49]:
 p=[[0]*50 for _ in range(50)]
 for u in range(48):p[u][u+1]=p[u+1][u]=100
 for u in range(count):p[u][49]=p[49][u]=1
 with localcontext() as ctx:
  ctx.prec=90;want=Decimal(count)/100*(Decimal(99)/100)**(count-1)
 cases.append((p,want))
for n in [10,20,50]:
 p=[[int(u!=v) for v in range(n)] for u in range(n)]
 with localcontext() as ctx:
  ctx.prec=90;want=Decimal(n)**(n-2)*Decimal('.01')**(n-1)*Decimal('.99')**((n-1)*(n-2)//2)
 cases.append((p,want))
# Product of all absent-edge factors underflows double, final result does not.
n=50
p=[[50*int(u!=v) for v in range(n)] for u in range(n)]
with localcontext() as ctx:
 ctx.prec=90;want=Decimal(n)**(n-2)*Decimal('.5')**(n*(n-1)//2)
cases.append((p,want))
# Two dense blocks joined by a weak bridge, independent block factorization.
n=20
p=[[0]*n for _ in range(n)]
for u in range(n):
 for v in range(n):
  if u!=v and u//10==v//10:p[u][v]=99
p[9][10]=p[10][9]=1
with localcontext() as ctx:
 ctx.prec=90;block=Decimal(10)**8*Decimal('.99')**9*Decimal('.01')**36
 want=block*block/100
cases.append((p,want))
# Forced cycle and positive-edge disconnection at maximum n.
for typ in ['cycle','disconnected']:
 p=[[0]*50 for _ in range(50)]
 for u in range(48):p[u][u+1]=p[u+1][u]=100
 if typ=='cycle':p[0][2]=p[2][0]=100;p[48][49]=p[49][48]=50
 cases.append((p,Decimal(0)))
data=str(len(cases))+'\n'+''.join(str(len(p))+'\n'+'\n'.join(' '.join(map(str,r)) for r in p)+'\n' for p,_ in cases)
harness='''
int main()
{
    int t;
    cin >> t;
    while (t--)
    {
        int n;
        cin >> n;
        vector<vector<int>> p(n, vector<int>(n));
        for (auto &row : p)
            for (int &v : row)
                cin >> v;
        cout << setprecision(20) << tree_probability(p) << '\\n';
    }
}
'''
header='#include "../../src/compact/tree_probability.hpp"\n'
core=(root/'src/compact/tree_probability.hpp').read_text().split('// BEGIN tree_probability')[1].split('// END tree_probability')[0]
(out/'header.cpp').write_text(header+harness)
(out/'copied.cpp').write_text('#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'+core+harness)
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1');results={}
for mode in ['normal','sanitizer']:
 flags=['-std=c++20','-O2']+(['-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else [])
 for form in ['header','copied','ndebug']:
  exe=out/(form+'-'+mode);src=out/('header.cpp' if form=='ndebug' else form+'.cpp')
  subprocess.run([CXX,*flags,*(['-DNDEBUG'] if form=='ndebug' else []),str(src),'-o',str(exe)],check=True)
  r=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True,env=env)
  assert not r.stderr,r.stderr
  got=list(map(Decimal,r.stdout.split()));assert len(got)==len(cases)
  errors=[]
  for (p,w),v in zip(cases,got):
   assert v.is_finite()
   if w==0:assert v==0,(p,w,v)
   else:
    err=abs(v/w-1);assert err<Decimal('1e-8'),(p,w,v,err);errors.append(err)
  results[form+'-'+mode]={'cases':len(cases),'max_relative_error':str(max(errors))}
  print(form,mode,results[form+'-'+mode],flush=True)
 exe=out/('driver-'+mode)
 subprocess.run([CXX,*flags,str(root/'verify/luogu/P3317.compact.cpp'),'-o',str(exe)],check=True)
 selected=[(p,w) for p,w in cases if len(p)>1 and (w==0 or w>=Decimal('0.0001'))][::17]
 selected += [(p,w) for p,w in cases if len(p)==50 and (w==0 or w>=Decimal('0.0001'))]
 for p,w in selected:
  text=str(len(p))+'\n'+'\n'.join(' '.join(f'{x/100:.2f}' for x in row) for row in p)+'\n'
  r=subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True,env=env)
  v=Decimal(r.stdout.strip());assert v==0 if w==0 else abs(v/w-1)<Decimal('.0001'),(p,w,v)
 results['driver-'+mode]=len(selected)
paths=['src/compact/tree_probability.hpp','verify/luogu/P3317.compact.cpp','tests/tree_probability.py']
(root/'verification/tree-probability.json').write_text(json.dumps({'status':'pass','results':results,'scope':'Exact Prüfer enumeration and analytic maximum-size identities; local only, no online verdict. Driver cases meet nonzero answer>=1e-4.','hashes':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}},indent=2)+'\n')
