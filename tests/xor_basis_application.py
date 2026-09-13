"""P3812 bundles versus exhaustive subset XOR, with unsigned boundary extensions."""
from compiler_config import CXX
from pathlib import Path
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(3812)
cases = [[0], [1,2,3], [(1<<64)-1], [1<<63,1]]
for _ in range(100):
    cases.append([rng.randrange(1<<64) for _ in range(rng.randrange(1,12))])
for style in ['compact']:
    source = root/f'build/P3812.{style}.cpp'
    exe = root/f'build/P3812.{style}'
    subprocess.run(['python3',str(root/'tools/bundle.py'),
                    str(root/f'verify/luogu/P3812.{style}.cpp'),str(source)],check=True)
    subprocess.run([CXX,'-std=c++20','-O2',str(source),'-o',str(exe)],check=True)
    for values in cases:
        possible = {0}
        for x in values:
            possible |= {y^x for y in possible}
        text = str(len(values))+'\n'+' '.join(map(str,values))+'\n'
        got = int(subprocess.check_output([str(exe)],input=text.encode()))
        assert got == max(possible)
    print(f'P3812 {style} bundled driver / exhaustive subset XOR and unsigned endpoints PASS')
