"""Validate the complete P5357 adapter with direct substring counts and scale cases."""
from compiler_config import CXX
from pathlib import Path
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
(root / 'build').mkdir(exist_ok=True)
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
exe = root / 'build/ac-application'
subprocess.run([CXX, *flags, str(root / 'verify/luogu/P5357.compact.cpp'), '-o', str(exe)], check=True)
def check(patterns, text, expected):
    data = str(len(patterns)) + '\n' + '\n'.join(patterns) + '\n' + text + '\n'
    run = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=60)
    assert not run.stderr, run.stderr
    assert list(map(int, run.stdout.split())) == expected
rng = random.Random(5357)
for _ in range(100):
    patterns = [''.join(rng.choice('abc') for _ in range(rng.randrange(1, 8))) for _ in range(20)]
    text = ''.join(rng.choice('abc') for _ in range(100))
    check(patterns, text, [sum(text.startswith(p, i) for i in range(len(text))) for p in patterns])
check(['a' * 200000], 'a' * 2000000, [1800001])
check(['a'] * 200000, 'a' * 2000000, [2000000] * 200000)
print('P5357: direct substring oracle, 200000 pattern length/count, 2000000 text length, overlap and duplicates PASS')
