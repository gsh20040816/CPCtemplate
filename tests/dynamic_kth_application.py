"""Check P2617 bundles, including values introduced only by later changes."""
from compiler_config import CXX
from pathlib import Path
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(2617)
cases = []
for _ in range(12):
    n = rng.randrange(1, 60)
    a = [rng.randrange(5) for _ in range(n)]
    lines = [f'{n} 300', ' '.join(map(str, a))]
    expected = []
    for step in range(300):
        if step % 3:
            pos = rng.randrange(n)
            value = rng.randrange(10**9 + 1)
            lines.append(f'C {pos + 1} {value}')
            a[pos] = value
        else:
            l = rng.randrange(n)
            r = rng.randrange(l, n)
            k = rng.randrange(1, r - l + 2)
            lines.append(f'Q {l + 1} {r + 1} {k}')
            expected.append(sorted(a[l:r + 1])[k - 1])
    cases.append(('\n'.join(lines) + '\n', expected))
for style in ['compact']:
    source = root / f'build/P2617.{style}.cpp'
    exe = root / f'build/P2617.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P2617.{style}.cpp'), str(source)], check=True)
    subprocess.run([CXX, '-std=c++20', '-O2', str(source), '-o', str(exe)], check=True)
    for text, expected in cases:
        got = list(map(int, subprocess.check_output([str(exe)], input=text.encode()).split()))
        assert got == expected
    print(f'P2617 {style} bundled driver / changes, future values and sorted-slice oracle PASS')
