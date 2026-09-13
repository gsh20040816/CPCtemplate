from compiler_config import CXX
from pathlib import Path
import os,random,subprocess
root=Path(__file__).resolve().parents[1]
flags=['-std=c++20','-O2']
if os.environ.get('SANITIZE')=='1':flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined']
exe=root/'build/cc-associative-driver'
subprocess.run([CXX,*flags,str(root/'verify/library_checker/associative_array.cc.compact.cpp'),'-o',str(exe)],check=True)
rng=random.Random(94013)
keys=[0,10**18,1<<59]+[rng.randrange(10**18+1) for _ in range(1000)]
lines=[];expected=[];ref={}
for i in range(10000):
 k=rng.choice(keys)
 if rng.randrange(2):
  v=0 if i%7==0 else rng.randrange(10**18+1)
  lines.append(f'0 {k} {v}');ref[k]=v
 else:
  lines.append(f'1 {k}');expected.append(str(ref.get(k,0)))
r=subprocess.run([str(exe)],input=str(len(lines))+'\n'+'\n'.join(lines)+'\n',text=True,capture_output=True,check=True)
assert not r.stderr and r.stdout.split()==expected
print('CC associative driver: Python dictionary oracle, absent/stored zeros and 1e18 endpoints PASS')
