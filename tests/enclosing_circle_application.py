from compiler_config import CXX
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
cases=[([(0,0)],(0,0,0)), ([(2,3)]*5,(0,2,3)),
       ([(0,0),(6,0),(3,4)],(3.125,3,0.875)),
       ([(0,0),(2,0),(1,0.01)],(1,1,0)),
       ([(-10000,0),(10000,0)],(10000,0,0)),
       ([(5,0),(-5,0),(0,5),(0,-5),(0,0)]*20000,(5,0,0))]
for style in ['compact']:
    out=root/f'build/submit/P1742.{style}.cpp'
    subprocess.run(['python3','tools/bundle.py',f'verify/luogu/P1742.{style}.cpp',str(out)],cwd=root,check=True)
    exe=root/f'build/P1742.{style}'
    subprocess.run([CXX,'-std=c++20','-O2',str(out),'-o',str(exe)],check=True)
    for p,want in cases:
        text=str(len(p))+'\n'+''.join(f'{x} {y}\n' for x,y in p)
        got=list(map(float,subprocess.check_output([str(exe)],input=text,text=True).split()))
        assert len(got)==3 and all(abs(a-b)<1e-9 for a,b in zip(got,want)),(style,got,want)
    print(f'P1742 {style}: singleton/duplicate/acute/obtuse/boundary/100000-point drivers PASS')
