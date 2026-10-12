"""Reject wrong square factors, prefixes, quotient blocks and rectangle signs."""
from pathlib import Path
import hashlib,json,math,subprocess
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
build=root/'build/mobius-source'
source=(build/'printed-2522.cpp').read_text()
cases=[(a,b,c,d,k) for a in range(1,5) for b in range(a,9) for c in range(1,5) for d in range(c,9) for k in range(1,10)]
truth=[sum(math.gcd(x,y)==k for x in range(a,b+1) for y in range(c,d+1)) for a,b,c,d,k in cases]
# Independent maximum-square totient identity catches pre-widening overflow.
phi=list(range(50001))
for p in range(2,50001):
 if phi[p]==p:
  for i in range(p,50001,p):phi[i]-=phi[i]//p
cases.append((1,50000,1,50000,1));truth.append(2*sum(phi[1:])-1)
data=str(len(cases))+'\n'+''.join(' '.join(map(str,q))+'\n' for q in cases)
mutants={
 'mu-one':('if (n) phi[1] = mu[1] = 1;','if (n) phi[1] = 1;'),
 'square-factor':('mu[j] = 0;','mu[j] = -mu[i];'),
 'block-end':('r = min(a / x, b / y);','r = max(a / x, b / y);'),
 'lower-end':('count((a - 1) / k, d / k)','count(a / k, d / k)'),
 'intersection-sign':('+ count((a - 1) / k, (c - 1) / k)','- count((a - 1) / k, (c - 1) / k)'),
 'late-widening':('__int128_t(sum[r] - sum[l - 1]) * x * y','(sum[r] - sum[l - 1]) * x * y')}
results={}
for name,(old,new) in mutants.items():
 assert source.count(old)==1,name
 src=build/('mutant-'+name+'.cpp');src.write_text(source.replace(old,new))
 exe=src.with_suffix('')
 subprocess.run([CXX,'-std=c++20','-O1','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(src),'-o',str(exe)],check=True)
 out=subprocess.run([str(exe)],input=data,text=True,capture_output=True,timeout=30)
 mismatch=next((i for i,(v,w) in enumerate(zip(out.stdout.splitlines(),truth)) if v!=str(w)),None)
 assert out.returncode or mismatch is not None or len(out.stdout.splitlines())!=len(truth),name
 results[name]=dict(rejected=True,returncode=out.returncode,first_mismatch_query=cases[mismatch] if mismatch is not None else None,diagnostic=out.stderr[:300])
 print(name,'rejected',flush=True)
(root/'verification/mobius-source-negative-controls.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.encode()).hexdigest(),queries=len(cases),mutants=results),indent=2)+'\n')
