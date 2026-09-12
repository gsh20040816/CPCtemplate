"""Run after dynamic_kth_application.py has built the two P2617 executables."""
from pathlib import Path
import random
import subprocess
import time

root = Path(__file__).resolve().parents[1]
rng = random.Random(261700)
n = 100000
a = list(range(n))
lines = [f'{n} 100000', ' '.join(map(str, a))]
want = []
for i in range(100000):
    if i % 1000 == 0:
        k = rng.randrange(1, n + 1)
        lines.append(f'Q 1 {n} {k}')
        want.append(sorted(a)[k - 1])
    else:
        p = rng.randrange(n)
        a[p] = n + i
        lines.append(f'C {p + 1} {n + i}')
text = ('\n'.join(lines) + '\n').encode()
for style in ['compact']:
    start = time.monotonic()
    got = list(map(int, subprocess.check_output([str(root / f'build/P2617.{style}')], input=text).split()))
    assert got == want
    print(f'P2617 {style}: n=100000, operations=100000, all 100 answers matched sorted-array oracle; '
          f'{time.monotonic() - start:.3f}s local wall time (not OJ timing)')
