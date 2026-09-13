"""Actual P1117 programs against independent A/B length enumeration."""
from compiler_config import CXX
from pathlib import Path
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(1117)
cases = ['a', 'aabbbb', 'cccccc', 'aabaabaa', 'ababa']
cases += [''.join(rng.choice('abc') for _ in range(rng.randrange(1, 25)))
          for _ in range(150)]
expected = []
for s in cases:
    answer = 0
    n = len(s)
    for i in range(n):
        for a in range(1, (n-i)//2+1):
            for b in range(1, (n-i-2*a)//2+1):
                j = i + 2*a
                if s[i:i+a] == s[i+a:j] and s[j:j+b] == s[j+b:j+2*b]:
                    answer += 1
    expected.append(answer)
n = 30000
cases.append('a'*n)
expected.append(sum((t-1)*(n-2*t+1) for t in range(2,n//2+1)))
for style in ['compact']:
    source = root / f'build/P1117.{style}.cpp'
    exe = root / f'build/P1117.{style}'
    subprocess.run(['python3', str(root/'tools/bundle.py'),
                    str(root/f'verify/luogu/P1117.{style}.cpp'), str(source)], check=True)
    subprocess.run([CXX, '-std=c++20', '-O2', str(source),
                    '-o', str(exe)], check=True)
    for begin in range(0, len(cases), 10):
        batch = cases[begin:begin+10]
        text = str(len(batch)) + '\n' + '\n'.join(batch) + '\n'
        got = list(map(int, subprocess.check_output([str(exe)],input=text.encode()).split()))
        assert got == expected[begin:begin+10]
    print(f'P1117 {style} bundled driver / exhaustive split oracle and 30000-character case PASS')
