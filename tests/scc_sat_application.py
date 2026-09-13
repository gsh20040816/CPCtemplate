#!/usr/bin/env python3
"""Independent whole-driver SCC partition and SAT assignment certificates."""
import itertools
import os
from pathlib import Path
import random
import resource
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
flags = ['-std=c++20', '-O2']
if os.environ.get('SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
if os.uname().sysname == 'Darwin':
    flags += ['-Wl,-stack_size,0x20000000']
else:
    soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
    resource.setrlimit(resource.RLIMIT_STACK, (hard, hard))
exes = {}
for name in ['scc', 'two_sat']:
    exe = root / ('build/lc-' + name)
    subprocess.run([CXX, *flags, str(root / ('verify/library_checker/' + name + '.compact.cpp')), '-o', str(exe)], check=True)
    exes[name] = exe

def run(name, lines):
    r = subprocess.run([str(exes[name])], input='\n'.join(lines)+'\n', text=True, capture_output=True, check=True, timeout=60)
    assert not r.stderr, r.stderr
    return r.stdout.splitlines()

rng = random.Random(95771)
for n in range(1, 9):
    for _ in range(12):
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randrange(1, n*n+2))]
        reach = [[i == j for j in range(n)] for i in range(n)]
        for u, v in edges:
            reach[u][v] = True
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    reach[i][j] |= reach[i][k] and reach[k][j]
        out = run('scc', [f'{n} {len(edges)}', *[f'{u} {v}' for u, v in edges]])
        assert len(out) == int(out[0])+1
        bel = [-1]*n
        for k, line in enumerate(out[1:]):
            row = list(map(int, line.split()))
            assert row[0] == len(row)-1 and row[0] > 0
            for u in row[1:]:
                assert 0 <= u < n and bel[u] == -1
                bel[u] = k
        assert -1 not in bel
        for i in range(n):
            for j in range(n):
                assert (bel[i] == bel[j]) == (reach[i][j] and reach[j][i])
        assert all(bel[u] <= bel[v] for u, v in edges)

for n in range(1, 9):
    for _ in range(12):
        literals = list(range(1, n+1)) + list(range(-n, 0))
        clauses = [(rng.choice(literals), rng.choice(literals)) for _ in range(rng.randrange(1, 4*n+1))]
        def valid(bits):
            return all((bits[abs(a)-1] == (a > 0)) or (bits[abs(b)-1] == (b > 0)) for a, b in clauses)
        exists = any(valid(bits) for bits in itertools.product([False, True], repeat=n))
        out = run('two_sat', [f'p cnf {n} {len(clauses)}', *[f'{a} {b} 0' for a, b in clauses]])
        if not exists:
            assert out == ['s UNSATISFIABLE']
        else:
            assert len(out) == 2 and out[0] == 's SATISFIABLE'
            row = out[1].split()
            assert row[0] == 'v' and row[-1] == '0' and len(row) == n+2
            values = list(map(int, row[1:-1]))
            assert [abs(x) for x in values] == list(range(1, n+1))
            assert valid([x > 0 for x in values])

n = 500000
out = run('scc', [f'{n} {n-1}', *[f'{i} {i+1}' for i in range(n-1)]])
assert out[0] == str(n)
assert out[1:] == [f'1 {i}' for i in range(n)]
# x1 and each implication xi => x(i+1) force all variables true.
lines = [f'p cnf {n} {n}', '1 1 0', *[f'{-i} {i+1} 0' for i in range(1, n)]]
out = run('two_sat', lines)
assert out == ['s SATISFIABLE', 'v ' + ' '.join(map(str, range(1, n+1))) + ' 0']
print('LC SCC/SAT drivers: reachability partitions, topological edges, exhaustive assignments and 500000-variable recursive chains PASS')
