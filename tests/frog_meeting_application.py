"""P1516 full drivers: direct motion simulation and planted unique time."""
from pathlib import Path
import os
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(1516)
cases = []
for _ in range(180):
    length = rng.randrange(1, 40)
    x, y = rng.sample(range(1, 80), 2)
    m, n = rng.choices(range(1, 80), k=2)
    answer = next((str(t) for t in range(length) if (x+m*t) % length == (y+n*t) % length), 'Impossible')
    cases.append(((x,y,m,n,length),answer))
cases += [((1,2,1,1,1),'0'), ((1,2,1,1,2100000000),'Impossible')]
for _ in range(30):
    length = 1 << 30
    speed = 2 * rng.randrange(1,500000000) + 1
    t = rng.randrange(1,length)
    y = (1 + speed * t) % length or length
    assert y != 1
    cases.append(((1,y,speed+1,1,length),str(t)))
    # Swap frogs: the speed difference changes sign, the meeting time does not.
    cases.append(((y,1,1,speed+1,length),str(t)))
for style in ['compact']:
    bundle = root / f'build/P1516.{style}.cpp'
    exe = root / f'build/P1516.{style}'
    subprocess.run(['python3','tools/bundle.py',f'verify/luogu/P1516.{style}.cpp',str(bundle)],cwd=root,check=True)
    flags = ['-O2']
    if os.environ.get('SANITIZE') == '1':
        flags = ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    subprocess.run([os.environ.get('CXX','/opt/homebrew/bin/g++-16'),'-std=c++20',*flags,str(bundle),'-o',str(exe)],check=True)
    for case, expected in cases:
        result = subprocess.run([str(exe)],input=' '.join(map(str,case))+'\n',text=True,capture_output=True,check=True,timeout=10)
        assert result.stdout.strip() == expected, (case,expected,result.stdout)
        assert not result.stderr, result.stderr
    print(f'P1516 {style}: 242 simulated/planted cases, swapped speeds, equal speeds, initial coincidence and large minimal time PASS')
