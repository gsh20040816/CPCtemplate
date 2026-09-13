"""UVa10006: all allowed inputs, independent Korselt criterion."""
from compiler_config import CXX
from pathlib import Path
import os
import subprocess
root = Path(__file__).resolve().parents[1]
spf = list(range(65000))
for p in range(2, 65000):
    if spf[p] == p:
        for x in range(p * p, 65000, p):
            if spf[x] == x:
                spf[x] = p
expected = []
for n in range(3, 65000):
    good = spf[n] != n
    x = n
    while x > 1:
        p = spf[x]
        x //= p
        if x % p == 0 or (n - 1) % (p - 1):
            good = False
        while x % p == 0:
            x //= p
    expected.append(f'The number {n} is a Carmichael number.' if good else f'{n} is normal.')
data = ''.join(f'{n}\n' for n in range(3, 65000)) + '0\n'
for style in ['compact']:
    bundle = root / f'build/uva10006.{style}.cpp'
    exe = root / f'build/uva10006.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/uva/10006.{style}.cpp', str(bundle)], cwd=root, check=True)
    flags = ['-std=c++20', '-O2']
    if os.environ.get('SANITIZE') == '1':
        flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    subprocess.run([CXX, *flags, str(bundle), '-o', str(exe)], check=True)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=15)
    assert not result.stderr, result.stderr
    assert result.stdout.splitlines() == expected
    print(f'UVa10006 {style}: all 64997 legal inputs, Korselt oracle, composite filtering and exact output PASS')
