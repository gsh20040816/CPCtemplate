"""Final bitstring checked by an independent XOR difference array."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(109)
source = root / 'build/sequence-flip-driver.cpp'
exe = root / 'build/sequence-flip-driver'
subprocess.run(['python3', 'tools/bundle.py', 'verify/examples/sequence_flip.compact.cpp', str(source)], cwd=root, check=True)
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)
for case in range(151):
    n, q = (200000, 200000) if case == 150 else (rng.randrange(1, 100), 200)
    bits = [rng.randrange(2) for _ in range(n)]
    diff = [0] * (n + 1)
    lines = [f'{n} {q}', ''.join(map(str, bits))]
    for _ in range(q):
        l, r = sorted([rng.randrange(n), rng.randrange(n)])
        lines.append(f'{l+1} {r+1}')
        diff[l] ^= 1
        diff[r+1] ^= 1
    flip = 0
    expected = []
    for i, b in enumerate(bits):
        flip ^= diff[i]
        expected.append(str(b ^ flip))
    run = subprocess.run([str(exe)], input='\n'.join(lines)+'\n', text=True,
                         capture_output=True, check=True, timeout=120)
    assert not run.stderr, run.stderr
    assert run.stdout.strip() == ''.join(expected)
print('Sequence flip driver: 151 cases, XOR difference oracle, n=q=200000 PASS')
