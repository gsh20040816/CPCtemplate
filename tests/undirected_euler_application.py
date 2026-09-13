"""P2731 vertex lexical output and SGU101 domino IDs/directions."""
from compiler_config import CXX
from pathlib import Path
import subprocess
import random
root = Path(__file__).resolve().parents[1]
rng = random.Random(2731)

def brute(edges):
    best = None
    def visit(u, mask, path):
        nonlocal best
        if mask == (1 << len(edges)) - 1:
            if best is None or path < best:
                best = path[:]
            return
        for i, (a, b) in enumerate(edges):
            if not (mask >> i & 1) and u in (a, b):
                v = a ^ b ^ u
                visit(v, mask | (1 << i), path + [v])
    for u in sorted(set(x for e in edges for x in e)):
        visit(u, 0, [u])
    return best

small = []
for _ in range(100):
    edges = [(rng.randrange(7), rng.randrange(7)) for _ in range(rng.randrange(1, 8))]
    small.append((edges, brute(edges)))
valid = [( [(u + 20, v + 20) for u, v in edges], [u + 20 for u in expected]) for edges, expected in small if expected]
valid += [([(499, 500)] * 1024, [499 if i % 2 == 0 else 500 for i in range(1025)])]
for style in ['compact']:
    bundle = root / f'build/P2731.{style}.cpp'
    exe = root / f'build/P2731.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/luogu/P2731.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run([CXX, '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    for edges, expected in valid:
        data = str(len(edges)) + '\n' + ''.join(f'{u} {v}\n' for u, v in edges)
        output = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True).stdout
        assert list(map(int, output.splitlines())) == expected
    print(f'P2731 {style}: {len(valid)} feasible cases, lexical brute oracle, labels excluding 1 and 1024 parallel edges passed')
    bundle = root / f'build/sgu101.{style}.cpp'
    exe = root / f'build/sgu101.{style}'
    subprocess.run(['python3', 'tools/bundle.py', f'verify/sgu/101.{style}.cpp', str(bundle)], cwd=root, check=True)
    subprocess.run([CXX, '-std=c++20', '-O2', str(bundle), '-o', str(exe)], check=True)
    for edges, expected in small + [([(0, 6)] * 100, True), ([(0, 0)] * 100, True)]:
        data = str(len(edges)) + '\n' + ''.join(f'{u} {v}\n' for u, v in edges)
        # Two consecutive datasets also test resetting IDs and used[] state.
        lines = subprocess.run([str(exe)], input=data * 2, text=True, capture_output=True, check=True).stdout.splitlines()
        if expected is None:
            assert lines == ['No solution'] * 2
            continue
        assert len(lines) == 2 * len(edges)
        for offset in [0, len(edges)]:
            seen = set()
            last = None
            for line in lines[offset:offset + len(edges)]:
                i, sign = line.split()
                i = int(i) - 1
                assert 0 <= i < len(edges) and i not in seen and sign in ['+', '-']
                seen.add(i)
                u, v = edges[i]
                if sign == '-':
                    u, v = v, u
                assert last is None or last == u
                last = v
    print(f'SGU101 {style}: 102 cases repeated twice, exhaustive feasibility and full domino ID/direction certificate passed')
