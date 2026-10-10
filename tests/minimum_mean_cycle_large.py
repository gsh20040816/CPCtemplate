"""Native Linux GCC float128 P3199 stress with exact telescoping references."""
import hashlib
import json
import os
import platform
import random
import subprocess
from fractions import Fraction
from pathlib import Path
from compiler_config import CXX
root=Path(__file__).resolve().parents[1]
work=root/'build/min-mean-cycle/linux'
work.mkdir(parents=True,exist_ok=True)
(root/'verification').mkdir(exist_ok=True)
assert platform.system()=='Linux'
n,m=3000,10000
rng=random.Random(3199)
potential=[rng.randrange(-400000000000000000000,400000000000000000001) for _ in range(n)]
scale=10**14
base=12345678912345
edges=[]
for u in range(n):
 v=(u+1)%n
 edges.append((u,v,base+potential[v]-potential[u]))
while len(edges)<m:
 u,v=rng.randrange(n),rng.randrange(n)
 if u==v:continue
 edges.append((u,v,base+potential[v]-potential[u]+rng.randrange(100000)*scale))
def decimal(x):
 sign='-' if x<0 else ''
 x=abs(x)
 return f'{sign}{x//scale}.{x%scale:014d}'
data=f'{n} {m}\n'+''.join(f'{u+1} {v+1} {decimal(w)}\n' for u,v,w in edges)
input_path=work/'telescoping.in'
input_path.write_text(data)
want=Fraction(base,scale)
rows=[]
for san in [False,True]:
 mode='sanitizer' if san else 'normal'
 flags=['-std=c++20','-O1' if san else '-O2']
 if san:flags+=['-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
 exe=work/mode
 cmd=[CXX,*flags,str(root/'verify/luogu/P3199.compact.cpp'),'-o',str(exe)]
 subprocess.run(cmd,check=True)
 timer=work/(mode+'.time')
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
 with input_path.open() as inp:
  p=subprocess.run(['/usr/bin/time','-f','%e %M','-o',str(timer),str(exe)],stdin=inp,text=True,capture_output=True,env=env,timeout=240)
 assert p.returncode==0,p.stderr
 assert abs(Fraction(p.stdout.strip())-want)<=Fraction(51,10**10),(p.stdout,want)
 elapsed,rss=timer.read_text().split()
 rows.append(dict(mode=mode,command=cmd,output=p.stdout.strip(),elapsed_seconds=float(elapsed),peak_rss_kib=int(rss)))
 print(rows[-1],flush=True)
files=['src/compact/minimum_mean_cycle.hpp','verify/luogu/P3199.compact.cpp','tests/minimum_mean_cycle_large.py']
r=dict(status='pass',platform=platform.platform(),compiler=subprocess.check_output([CXX,'--version'],text=True).splitlines()[0],n=n,m=m,construction='w(u,v)=base+potential[v]-potential[u]+nonnegative slack; ring slack0. Every cycle mean>=base, ring attains it. 14-digit decimal weights and large cancellation.',expected=str(want),input_sha256=hashlib.sha256(data.encode()).hexdigest(),results=rows,source_sha256={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},scope='Native Linux local stress, not online rank. /usr/bin/time -f formatting; timings measured on executable only, compile excluded.')
(root/'verification/min-mean-cycle-linux-large.json').write_text(json.dumps(r,indent=2)+'\n')
