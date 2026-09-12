"""Check P4781 bundles against direct evaluation of generated polynomials."""
import random
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rng = random.Random(4781)
p = 998244353
for style in ['compact']:
    source = root / f'build/P4781.{style}.cpp'
    exe = root / f'build/P4781.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P4781.{style}.cpp'), str(source)], check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(source), '-o', str(exe)], check=True)
    for trial in range(100):
        n = rng.randrange(1, 40)
        c = [rng.randrange(p) for _ in range(n)]
        xs = rng.sample(range(1, p), n)
        k = xs[0] if trial % 2 else rng.randrange(1, p)
        def evaluate(x):
            value = 0
            for a in reversed(c):
                value = (value * x + a) % p
            return value
        data = f'{n} {k}\n' + ''.join(f'{x} {evaluate(x)}\n' for x in xs)
        answer = int(subprocess.check_output([str(exe)], input=data.encode()))
        assert answer == evaluate(k)
    print(f'P4781 {style} bundled driver / independent polynomial evaluation PASS')
