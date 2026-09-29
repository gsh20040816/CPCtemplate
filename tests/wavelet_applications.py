"""Full wavelet drivers against sorting/counting, including P3834 conversion."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
mode = 'san' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-std=c++20', '-O2'] if mode == 'normal' else ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
drivers = {
    'kth': 'verify/library_checker/range_kth_smallest.wavelet.compact.cpp',
    'freq': 'verify/library_checker/static_range_frequency.wavelet.compact.cpp',
    'P3834': 'verify/luogu/P3834.wavelet.compact.cpp',
}
exe = {}
for name, driver in drivers.items():
    dest = root / f'build/wavelet-{name}-{mode}.cpp'
    subprocess.run(['python3', str(root / 'tools/bundle.py'), str(root / driver), str(dest)], check=True)
    exe[name] = dest.with_suffix('')
    subprocess.run([CXX, *flags, str(dest), '-o', str(exe[name])], check=True)


def run(name, a, qs, answers):
    data = f'{len(a)} {len(qs)}\n' + ' '.join(map(str, a)) + '\n'
    data += ''.join(' '.join(map(str, q)) + '\n' for q in qs)
    p = subprocess.run([str(exe[name])], input=data, text=True, capture_output=True, check=True, timeout=90)
    assert not p.stderr, p.stderr
    assert p.stdout.split() == list(map(str, answers)), name


rng = random.Random(2026092902)
for t in range(160):
    n = rng.randrange(1, 100)
    a = [rng.randrange(9) if t % 2 else rng.randrange(10**9 + 1) for _ in range(n)]
    qs, ans = [], []
    fs, counts = [], []
    for _ in range(60):
        l = rng.randrange(n)
        r = rng.randrange(l + 1, n + 1)
        k = rng.randrange(r - l)
        qs.append((l, r, k))
        ans.append(sorted(a[l:r])[k])
        l = rng.randrange(n + 1)
        r = rng.randrange(l, n + 1)
        x = rng.choice(a) if rng.randrange(2) else rng.randrange(10**9 + 1)
        fs.append((l, r, x))
        counts.append(a[l:r].count(x))
    run('kth', a, qs, ans)
    run('P3834', a, [(l + 1, r, k + 1) for l, r, k in qs], ans)
    run('freq', a, fs, counts)
run('freq', [], [(0, 0, 0), (0, 0, 10**9)], [0, 0])
run('freq', [], [], [])
for name, n in [('kth', 200000), ('P3834', 200000), ('freq', 500000)]:
    a = [10**9 - i for i in range(n)]
    qs, ans = [], []
    for _ in range(n):
        l = rng.randrange(n)
        r = rng.randrange(l + 1, n + 1)
        if name == 'freq':
            x = rng.randrange(10**9 - n, 10**9 + 1)
            qs.append((l, r, x))
            ans.append(int(l <= 10**9 - x < r))
        else:
            k = rng.randrange(r - l)
            qs.append((l, r, k) if name == 'kth' else (l + 1, r, k + 1))
            ans.append(10**9 - (r - 1 - k))
    run(name, a, qs, ans)
print('Wavelet full drivers PASS: 160 independent inputs x 3 drivers; empty input/query; 200000/200000/500000 maximum N=Q with closed-form answers')
