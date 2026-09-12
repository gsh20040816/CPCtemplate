"""HDU1814 representative selection, checked by enumerating all assignments."""
from pathlib import Path
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(1814)

def oracle(n, conflicts):
    for mask in range(1 << n):
        chosen = [2 * x - 1 + ((mask >> (n - x)) & 1) for x in range(1, n + 1)]
        selected = set(chosen)
        if all(u not in selected or v not in selected for u, v in conflicts):
            return list(map(str, chosen))
    return ['NIE']

cases = []
for _ in range(160):
    n = rng.randrange(1, 9)
    conflicts = [tuple(rng.sample(range(1, 2 * n + 1), 2)) for _ in range(rng.randrange(30))]
    cases.append((n, conflicts, oracle(n, conflicts)))
n = 10000
conflicts = []
for x in range(1, n):
    conflicts += [(2*x-1, 2*x+2), (2*x, 2*x+1)]
conflicts += [(1, 3), (1, 4)]
cases.append((n, conflicts, [str(2*x) for x in range(1, n + 1)]))
data = ''
expected = []
for n, conflicts, answer in cases:
    data += f'{n} {len(conflicts)}\n' + ''.join(f'{u} {v}\n' for u, v in conflicts)
    expected += answer
for style in ['compact']:
    bundle = root / f'build/hdu1814.{style}.cpp'
    exe = root / f'build/hdu1814.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/hdu/1814.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=15)
    assert result.stdout.splitlines() == expected
    print(f'HDU1814 {style}: 161 datasets, exhaustive minimum representative oracle, NIE output, reset and n=10000 implication chain passed')
