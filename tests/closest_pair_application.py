from compiler_config import CXX
from pathlib import Path
import random, subprocess, math
root = Path(__file__).resolve().parents[1]
rng = random.Random(1429)
cases = []
for _ in range(100):
    p = [(rng.randrange(10**9+1), rng.randrange(10**9+1)) for _ in range(rng.randrange(2,50))]
    d = min((x-u)**2+(y-v)**2 for i,(x,y) in enumerate(p) for u,v in p[:i])
    cases.append((p, math.sqrt(d)))
cases += [([(i*4000,0) for i in range(200000)], 4000),
          ([(0,0)]*200000, 0),
          ([(0,0),(10**9,10**9)], math.sqrt(2)*10**9)]
for style in ['compact']:
    bundle = root/f'build/submit/P1429.{style}.cpp'
    subprocess.run(['python3','tools/bundle.py',f'verify/luogu/P1429.{style}.cpp',str(bundle)],cwd=root,check=True)
    exe = root/f'build/P1429.{style}'
    subprocess.run([CXX,'-std=c++20','-O2',str(bundle),'-o',str(exe)],check=True)
    for p,want in cases:
        text = str(len(p))+'\n'+''.join(f'{x} {y}\n' for x,y in p)
        result = subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True)
        got = float(result.stdout)
        assert abs(got-want) <= 0.000051, (style,got,want)
    print(f'P1429 {style}: 103 complete inputs, exact integer distance oracle and 200000-point cases PASS')
