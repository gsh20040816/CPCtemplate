"""Run actual bundled P2495 drivers against exhaustive edge-cut enumeration."""
import os
from pathlib import Path
import random
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(892117)
cxx = os.environ.get('CXX') or shutil.which('g++-16') or 'g++'
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags += ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
programs = []
for style in ['compact']:
    source = root / f'build/P2495.{style}.cpp'
    binary = root / f'build/P2495.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P2495.{style}.cpp'), str(source)], check=True)
    subprocess.run([cxx, *flags, str(source), '-o', str(binary)], check=True)
    programs.append(binary)
for trial in range(30):
    n = rng.randrange(2, 9)
    edges = [(rng.randrange(1, v), v, rng.randrange(1, 20)) for v in range(2, n + 1)]
    queries = [rng.sample(range(2, n + 1), rng.randrange(1, n)) for _ in range(8)]
    expected = []
    for keys in queries:
        best = sum(w for u, v, w in edges)
        for mask in range(1 << len(edges)):
            adjacency = [[] for _ in range(n + 1)]
            cost = 0
            for i, (u, v, w) in enumerate(edges):
                if mask >> i & 1:
                    cost += w
                else:
                    adjacency[u].append(v)
                    adjacency[v].append(u)
            seen = {1}
            queue = [1]
            for u in queue:
                for v in adjacency[u]:
                    if v not in seen:
                        seen.add(v)
                        queue.append(v)
            if not seen.intersection(keys):
                best = min(best, cost)
        expected.append(best)
    lines = [str(n)] + [f'{u} {v} {w}' for u, v, w in edges] + [str(len(queries))]
    lines += [str(len(keys)) + ' ' + ' '.join(map(str, keys)) for keys in queries]
    for binary in programs:
        result = subprocess.run([str(binary)], input='\n'.join(lines) + '\n',
                                text=True, capture_output=True, check=True)
        assert not result.stderr, result.stderr
        assert list(map(int, result.stdout.split())) == expected, (trial, binary, result.stdout)
print('P2495 dual-style bundled drivers / exhaustive edge cuts PASS')
