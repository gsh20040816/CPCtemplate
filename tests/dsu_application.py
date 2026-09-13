from compiler_config import CXX
from pathlib import Path
import random,subprocess,os
root=Path(__file__).resolve().parents[1]
rng=random.Random(3367)
src=root/'build/submit/P3367.compact.cpp';exe=root/'build/P3367'
subprocess.run(['python3','tools/bundle.py','verify/luogu/P3367.compact.cpp',str(src)],check=True)
flags=['-O1','-g','-fsanitize=address,undefined'] if os.getenv('CPC_SANITIZE')=='1' else ['-O2']
subprocess.run([CXX,'-std=c++20',*flags,str(src),'-o',str(exe)],check=True)
for trial in range(30):
 n=1+rng.randrange(100);m=1000;c=list(range(n));ops=[];want=[]
 for _ in range(m):
  x=rng.randrange(n);y=rng.randrange(n);op=1+rng.randrange(2);ops.append(f'{op} {x+1} {y+1}')
  if op==1:
   old=c[y];new=c[x];c=[new if v==old else v for v in c]
  else:want.append('Y' if c[x]==c[y] else 'N')
 got=subprocess.check_output([str(exe)],input=f'{n} {m}\n'+'\n'.join(ops)+'\n',text=True).split()
 assert got==want
n=200000;m=1000000
ops=[f'1 {i+1} {i}' for i in range(1,n)]
ops += [f'2 {i%n+1} {n}' for i in range(m-n+1)]
got=subprocess.check_output([str(exe)],input=f'{n} {m}\n'+'\n'.join(ops)+'\n',text=True).split()
assert got==['Y']*(m-n+1)
print('P3367 vector driver: independent component labels, 1-based adapter and n=200000 m=1000000 PASS')
