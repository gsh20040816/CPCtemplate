"""POJ2337 exact output checked by independent permutations."""
from pathlib import Path
from itertools import permutations
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(2337)

def oracle(words):
    valid = [p for p in permutations(words) if all(p[i][-1] == p[i+1][0] for i in range(len(p)-1))]
    return '.'.join(min(valid)) if valid else '***'

cases = [['aab', 'aza', 'ba'], ['a', 'b'], ['aa', 'aa'], ['ab'], ['a', 'aa', 'aba']]
for _ in range(100):
    cases.append([''.join(rng.choice('abc') for _ in range(rng.randrange(1, 6))) for _ in range(rng.randrange(1, 8))])
expected = [oracle(words) for words in cases]
cases += [['aa'] * 1000, ['ab'] * 1000]
expected += ['.'.join(['aa'] * 1000), '***']
data = str(len(cases)) + '\n'
for words in cases:
    data += str(len(words)) + '\n' + '\n'.join(words) + '\n'
for style in ['compact']:
    bundle = root / f'build/poj2337.{style}.cpp'
    exe = root / f'build/poj2337.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/poj/2337.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=10)
    assert result.stdout.splitlines() == expected
    print(f'POJ2337 {style}: {len(cases)} cases, exact permutation oracle, dotted word order, failure marker and 1000 words passed')
