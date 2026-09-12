"""Widget Factory (POJ2947 / UVa1564), independent assignment enumeration."""
from pathlib import Path
import itertools
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(2947)
days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
cases = []


def brute(n, records):
    answers = []
    for x in itertools.product(range(3, 10), repeat=n):
        if all((sum(x[v] for v in ids) - (r - l + 1)) % 7 == 0
               for ids, l, r in records):
            answers.append(x)
            if len(answers) == 2:
                return 'Multiple solutions.'
    return ' '.join(map(str, answers[0])) if answers else 'Inconsistent data.'


for k in range(1, 15):
    for l in range(7):
        for r in range(7):
            records = [([0] * k, l, r)]
            cases.append((1, records, brute(1, records)))
for _ in range(220):
    n = rng.randrange(1, 5)
    records = [([rng.randrange(n) for _ in range(rng.randrange(1, 22))],
                rng.randrange(7), rng.randrange(7))
               for _ in range(rng.randrange(1, 8))]
    cases.append((n, records, brute(n, records)))
cases.append((1, [([0] * 10000, 6, 0)], brute(1, [([0] * 10000, 6, 0)])))
cases.append((2, [([0, 1], 0, 3), ([0, 0, 1], 0, 4), ([0, 1, 1], 0, 6)], '8 3'))
cases.append((10, [([2], 0, 1), ([2], 0, 2)], 'Inconsistent data.'))
# Invertible row operations on identity certify full rank independently of elimination.
n = 300
matrix = [[int(i == j) for j in range(n)] for i in range(n)]
for _ in range(3000):
    i, j = rng.sample(range(n), 2)
    factor = rng.randrange(1, 7)
    matrix[i] = [(a + factor * b) % 7 for a, b in zip(matrix[i], matrix[j])]
rng.shuffle(matrix)
planted = [rng.randrange(3, 10) for _ in range(n)]


def encode(rows, solution):
    records = []
    for row in rows:
        ids = [j for j, c in enumerate(row) for _ in range(c)] or [0] * 7
        rhs = sum(c * v for c, v in zip(row, solution)) % 7
        l = rng.randrange(7)
        records.append((ids, l, (l + rhs - 1) % 7))
    return records


cases.append((n, encode(matrix, planted), ' '.join(map(str, planted))))
# Dropping an independent row leaves exactly one free variable.
records = encode(matrix[:-1], planted)
cases.append((n, records, 'Multiple solutions.'))
cases.append((n, records + [([0] * 7, 0, 0)], 'Inconsistent data.'))
data = ''
for n, records, _ in cases:
    assert 1 <= n <= 300 and 1 <= len(records) <= 300
    data += f'{n} {len(records)}\n'
    for ids, l, r in records:
        assert 1 <= len(ids) <= 10000
        data += f'{len(ids)} {days[l]} {days[r]}\n'
        data += ' '.join(str(v + 1) for v in ids) + '\n'
data += '0 0\n'
expected = [answer for _, _, answer in cases]
for style in ['compact']:
    bundle = root / f'build/poj2947.{style}.cpp'
    exe = root / f'build/poj2947.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/poj/2947.{style}.cpp', str(bundle)], cwd=root, check=True)
    flags = ['-O2']
    if os.environ.get('SANITIZE') == '1':
        flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', *flags, str(bundle), '-o', str(exe)], check=True)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=60)
    assert result.stdout.splitlines() == expected
    assert not result.stderr, result.stderr
    print(f'Widget Factory {style}: {len(cases)} datasets; exhaustive weekdays/repeated counts, assignment oracle, sample, dense n=300 rank certificates and k=10000 PASS')
