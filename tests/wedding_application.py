"""POJ3648 parsing and full assignment certificate, not a lexical requirement."""
from pathlib import Path
import random
import subprocess
root = Path(__file__).resolve().parents[1]
rng = random.Random(3648)

def feasible(n, clauses):
    for mask in range(1 << n):
        if not (mask & 1):
            continue
        if all(((mask >> x) & 1) == a or ((mask >> y) & 1) == b for x, a, y, b in clauses):
            return True
    return False

cases = [(1, []), (1, [(0, 0, 0, 0)]), (12, [(10, 1, 11, 0), (0, 0, 11, 1)])]
for _ in range(180):
    n = rng.randrange(1, 9)
    clauses = [(rng.randrange(n), rng.randrange(2), rng.randrange(n), rng.randrange(2)) for _ in range(rng.randrange(30))]
    cases.append((n, clauses))
data = ''
for n, clauses in cases:
    data += f'{n} {len(clauses)}\n'
    for x, a, y, b in clauses:
        data += f"{x}{'w' if a else 'h'} {y}{'w' if b else 'h'}\n"
data += '0 0\n'
for style in ['compact']:
    bundle = root / f'build/poj3648.{style}.cpp'
    exe = root / f'build/poj3648.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/poj/3648.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    lines = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=10).stdout.splitlines()
    assert len(lines) == len(cases)
    for (n, clauses), line in zip(cases, lines):
        possible = feasible(n, clauses)
        if line == 'bad luck':
            assert not possible
            continue
        assert possible
        tokens = line.split()
        assert len(tokens) == n - 1
        answer = [1] + [None] * (n - 1)
        for token in tokens:
            i = int(token[:-1])
            assert 1 <= i < n and answer[i] is None and token[-1] in 'wh'
            answer[i] = int(token[-1] == 'w')
        assert all(answer[x] == a or answer[y] == b for x, a, y, b in clauses)
    print(f'POJ3648 {style}: {len(cases)} cases, exhaustive satisfiability, bride force, multi-digit IDs, empty output and full assignment certificates passed')
