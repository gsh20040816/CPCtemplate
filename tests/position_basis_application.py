"""CF1100F actual bundles: subset enumeration and full-size periodic independent bits."""
from pathlib import Path
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(1100)
cases = []
for trial in range(80):
    n = rng.randrange(1,14)
    values = [rng.randrange(1<<64) if trial%2 else rng.randrange(1<<10) for _ in range(n)]
    queries = [(l,r) for l in range(1,n+1) for r in range(l,n+1)]
    rng.shuffle(queries)
    expected = []
    for l,r in queries:
        span = {0}
        for x in values[l-1:r]:
            span |= {v^x for v in span}
        expected.append(max(span))
    text = f'{n}\n'+' '.join(map(str,values))+f'\n{len(queries)}\n'
    text += ''.join(f'{l} {r}\n' for l,r in queries)
    cases.append((text,expected))
n = 500000
values = [1<<(i%20) for i in range(n)]
queries = [(max(1,n-i-i%30),n-i) for i in range(n)]
expected = []
for l,r in queries:
    answer = 0
    if r-l+1 >= 20:
        answer = (1<<20)-1
    else:
        for i in range(l-1,r):
            answer |= 1<<(i%20)
    expected.append(answer)
text = f'{n}\n'+' '.join(map(str,values))+f'\n{n}\n'
text += ''.join(f'{l} {r}\n' for l,r in queries)
cases.append((text,expected))
for style in ['compact','classic']:
    source = root/f'build/CF1100F.{style}.cpp'
    exe = root/f'build/CF1100F.{style}'
    subprocess.run(['python3',str(root/'tools/bundle.py'),str(root/f'verify/luogu/CF1100F.{style}.cpp'),str(source)],check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(source),'-o',str(exe)],check=True)
    for text,expected in cases:
        got = list(map(int,subprocess.check_output([str(exe)],input=text.encode(),timeout=60).split()))
        assert got == expected
    print(f'CF1100F {style} bundled driver / all-interval subset oracle and n=q=500000 PASS')
