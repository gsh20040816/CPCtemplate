"""Validate four Library Checker bundles by their output spaces, not vector order."""
from pathlib import Path
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(923)
def span(values):
    result = {0}
    for x in values:
        result |= {x^y for y in result}
    return result
cases = []
for _ in range(300):
    a = [rng.randrange(128) for _ in range(rng.randrange(8))]
    b = [rng.randrange(128) for _ in range(rng.randrange(8))]
    cases.append((a,b))
text = str(len(cases))+'\n'
for a,b in cases:
    text += str(len(a))+' '+' '.join(map(str,a))+'\n'
    text += str(len(b))+' '+' '.join(map(str,b))+'\n'
expected = [span(a)&span(b) for a,b in cases]
unit_line = '30 '+' '.join(str(1<<i) for i in range(30))+'\n'
scale = '100000\n'+(unit_line*2)*100000
for style in ['compact']:
    for method in ['intersection','zassenhaus']:
        name = f'intersection_{method}.{style}'
        source = root/f'build/{name}.cpp'
        exe = root/f'build/{name}'
        subprocess.run(['python3',str(root/'tools/bundle.py'),str(root/f'verify/library_checker/{name}.cpp'),str(source)],check=True)
        subprocess.run(['/opt/homebrew/bin/g++-16','-std=c++20','-O2',str(source),'-o',str(exe)],check=True)
        lines = subprocess.check_output([str(exe)],input=text.encode(),timeout=60).decode().splitlines()
        assert len(lines) == len(cases)
        for line,want in zip(lines,expected):
            k,*vectors = map(int,line.split())
            assert k == len(vectors)
            got = span(vectors)
            assert len(got) == 1<<k and got == want
        lines = subprocess.check_output([str(exe)],input=scale.encode(),timeout=60).decode().splitlines()
        assert len(lines) == 100000
        for line in lines:
            k,*vectors = map(int,line.split())
            assert k == len(vectors) == 30
            assert all(0 < v < 1<<30 for v in vectors)
            assert len({v.bit_length() for v in vectors}) == 30
        print(f'Library Checker {name} / independent span oracle and T=100000 full rank PASS')
