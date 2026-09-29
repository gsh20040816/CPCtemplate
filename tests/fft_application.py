from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess
import time

root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1':
    flags += ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
rng = random.Random(42453803)

for problem, name in [('P3803', 'P3803.fft'), ('P4245', 'P4245')]:
    exe = root / f'build/{name}-fft-driver'
    subprocess.run([CXX, *flags, str(root / f'verify/luogu/{name}.compact.cpp'), '-o', str(exe)], check=True)

    def run(a, b, want, mod=None):
        text = f'{len(a)-1} {len(b)-1}' + (f' {mod}' if mod else '') + '\n'
        text += ' '.join(map(str, a)) + '\n' + ' '.join(map(str, b)) + '\n'
        start = time.monotonic()
        result = subprocess.run([str(exe)], input=text, text=True, capture_output=True, check=True, timeout=120)
        assert not result.stderr, result.stderr
        assert list(map(int, result.stdout.split())) == want
        return time.monotonic() - start

    for t in range(100):
        n = rng.randrange(1, 51) if problem == 'P3803' else rng.randrange(2, 51)
        m = rng.randrange(1, 51) if problem == 'P3803' else rng.randrange(2, 51)
        a = [rng.randrange(10 if problem == 'P3803' else 10**9+1) for _ in range(n)]
        b = [rng.randrange(10 if problem == 'P3803' else 10**9+1) for _ in range(m)]
        mod = None if problem == 'P3803' else rng.choice([2, 8, 9, 998244353, 1000000009])
        want = [0] * (n + m - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                want[i+j] += x * y
        if mod:
            want = [v % mod for v in want]
        run(a, b, want, mod)
    if problem == 'P3803':
        n = 1000001
        elapsed = run([9]*n, [9]*n, [81*min(i+1, 2*n-1-i) for i in range(2*n-1)])
    else:
        n, mod, value = 100001, 1000000009, 1000000000
        want = [value*value*min(i+1, 2*n-1-i) % mod for i in range(2*n-1)]
        elapsed = run([value]*n, [value]*n, want, mod)
    print(f'{problem}: 100 schoolbook programs and maximum-degree closed form PASS; full driver wall time {elapsed:.3f}s')
