"""P3811 output verification: individual inverse certificates."""
from pathlib import Path
import subprocess
root = Path(__file__).resolve().parents[1]
cases = [(1,2), (2,3), (100,101), (1,1009), (1008,1009), (3000000,10000019)]
assert all(10000019 % d for d in range(2,3163))
for style in ['compact']:
    bundle = root / f'build/P3811.{style}.cpp'
    exe = root / f'build/P3811.{style}'
    subprocess.run(['python3','tools/bundle.py',f'verify/luogu/P3811.{style}.cpp',str(bundle)],cwd=root,check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(bundle),'-o',str(exe)],check=True)
    for n,p in cases:
        result = subprocess.run([str(exe)],input=f'{n} {p}\n',text=True,capture_output=True,check=True,timeout=15)
        lines = result.stdout.splitlines()
        assert len(lines) == n
        for i,line in enumerate(lines,1):
            x = int(line)
            assert 0 < x < p and i * x % p == 1
    print(f'P3811 {style}: all output entries certified, prime boundaries and n=3000000 PASS')
