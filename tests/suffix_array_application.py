"""Validate the two actual P3809 bundles against Python suffix sorting."""
from pathlib import Path
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(3809)
cases = ['a', 'banana', 'a' * 100, 'zZ0zZ0', '9876543210']
for _ in range(100):
    cases.append(''.join(rng.choice('abcxyzABCXYZ0123456789')
                         for _ in range(rng.randrange(1, 250))))
for style in ['compact', 'classic']:
    source = root / f'build/P3809.{style}.cpp'
    exe = root / f'build/P3809.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P3809.{style}.cpp'), str(source)], check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(source),
                    '-o', str(exe)], check=True)
    for s in cases:
        got = list(map(int, subprocess.check_output([str(exe)],
                        input=(s + '\n').encode()).split()))
        assert got == [i + 1 for i in sorted(range(len(s)), key=lambda i: s[i:])]
    n = 1000000
    got = list(map(int, subprocess.check_output([str(exe)],
                        input=('a' * n + '\n').encode()).split()))
    assert got == list(range(n, 0, -1))
    print(f'P3809 {style} bundled driver / Python suffix oracle and million-character output PASS')
