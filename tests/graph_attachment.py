"""Full attachment graph drivers: independent assignments and deletion oracles."""
from compiler_config import CXX
from pathlib import Path
import itertools
import os
import random
import resource
import subprocess

root = Path(__file__).resolve().parents[1]
rng = random.Random(20260930)
sanitize = os.environ.get('CPC_SANITIZE') == '1'
mode = 'san' if sanitize else 'normal'
flags = ['-std=c++20', '-O2']
if sanitize:
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
if os.uname().sysname == 'Darwin':
    flags += ['-Wl,-stack_size,0x20000000']
else:
    _, hard = resource.getrlimit(resource.RLIMIT_STACK)
    resource.setrlimit(resource.RLIMIT_STACK, (hard, hard))
exes = {}
for problem in ['P4782', 'P8435', 'P8436']:
    exe = root / f'build/graph-attachment-{problem}-{mode}'
    source = root / f'verify/luogu/{problem}.compact.cpp'
    if sanitize and problem == 'P4782':
        # ASan expands the two-million-literal recursion beyond the macOS main-stack limit.
        # The driver has an explicit return; renaming main preserves its semantics.
        obj = exe.with_suffix('.o')
        compile_flags = [f for f in flags if not f.startswith('-Wl,')]
        subprocess.run([CXX, *compile_flags, '-Dmain=cpc_entry', '-c', str(source), '-o', str(obj)], check=True)
        subprocess.run([CXX, *compile_flags, '-pthread', '-DCPC_STACK_BYTES=1073741824ULL',
                        str(root / 'tests/driver_stack.cpp'), str(obj), '-o', str(exe)], check=True)
    else:
        subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)
    exes[problem] = exe


def run(problem, n, rows):
    data = f'{n} {len(rows)}\n' + ''.join(' '.join(map(str, r)) + '\n' for r in rows)
    result = subprocess.run([str(exes[problem])], input=data, text=True, capture_output=True, timeout=120)
    assert result.returncode == 0, (problem, result.returncode, result.stderr)
    assert not result.stderr, result.stderr
    return result.stdout.splitlines()


def sat(n, clauses, expected=None):
    def valid(a):
        return all(a[x - 1] == p or a[y - 1] == q for x, p, y, q in clauses)
    if expected is None:
        expected = any(valid(a) for a in itertools.product([0, 1], repeat=n))
    out = run('P4782', n, clauses)
    if not expected:
        assert out == ['IMPOSSIBLE']
    else:
        assert len(out) == 2 and out[0] == 'POSSIBLE'
        a = list(map(int, out[1].split()))
        assert len(a) == n and all(x in [0, 1] for x in a) and valid(a)


for _ in range(200):
    n = rng.randint(1, 9)
    clauses = [(rng.randint(1, n), rng.randrange(2), rng.randint(1, n), rng.randrange(2)) for _ in range(rng.randrange(35))]
    sat(n, clauses)
n = 1000000
clauses = [(1, 1, 1, 1)] + [(u, 0, u + 1, 1) for u in range(1, n)]
sat(n, clauses, True)
# Contradiction at the end of a long implication chain; n-1 variables leave room for two units.
clauses = clauses[:-1] + [(n - 1, 0, n - 1, 0)]
sat(n, clauses, False)
del clauses
print('P4782: 200 exhaustive assignment oracles, one million variables/clauses, long forced chain and contradiction PASS', flush=True)


def components(n, edges, mask, skip=-1):
    labels = [0] * (n + 1)
    count = 0
    for u in range(1, n + 1):
        if labels[u] or not (mask >> (u - 1) & 1):
            continue
        count += 1
        labels[u] = count
        todo = [u]
        for x in todo:
            for i, (a, b) in enumerate(edges):
                if i == skip:
                    continue
                if b == x:
                    a, b = b, a
                if a == x and not labels[b] and mask >> (b - 1) & 1:
                    labels[b] = count
                    todo.append(b)
    return labels, count


def parse(out, n):
    assert len(out) == int(out[0]) + 1
    blocks = set()
    for line in out[1:]:
        row = list(map(int, line.split()))
        assert row[0] == len(row) - 1 and row[0] > 0
        block = frozenset(row[1:])
        assert len(block) == row[0] and all(1 <= u <= n for u in block)
        assert block not in blocks
        blocks.add(block)
    return blocks


for _ in range(200):
    n = rng.randint(1, 7)
    edges = [(rng.randint(1, n), rng.randint(1, n)) for _ in range(rng.randrange(18))]
    allv = (1 << n) - 1
    candidates = []
    for mask in range(1, allv + 1):
        if components(n, edges, mask)[1] != 1:
            continue
        if all(components(n, edges, mask ^ (1 << u))[1] <= 1 for u in range(n) if mask >> u & 1):
            candidates.append(mask)
    maximal = [s for s in candidates if not any(s != t and s & t == s for t in candidates)]
    expected = {frozenset(u + 1 for u in range(n) if s >> u & 1) for s in maximal}
    assert parse(run('P8435', n, edges), n) == expected
    count = components(n, edges, allv)[1]
    remaining = [e for i, e in enumerate(edges) if components(n, edges, allv, i)[1] == count]
    labels, count = components(n, remaining, allv)
    expected = {frozenset(u for u in range(1, n + 1) if labels[u] == k) for k in range(1, count + 1)}
    assert parse(run('P8436', n, edges), n) == expected
print('P8435/P8436: each 200 maximal-subset / individual-edge-deletion oracles, disconnected graphs, loops and parallel edges PASS', flush=True)

# Parse large closed forms incrementally instead of duplicating a set of half a million frozensets.
def large(n, edges, kind, vertex):
    out = run('P8435' if vertex else 'P8436', n, edges)
    if kind == 'cycle':
        assert len(out) == 2 and out[0] == '1'
        row = list(map(int, out[1].split()))
        assert row[0] == n and len(row) == n + 1 and sorted(row[1:]) == list(range(1, n + 1))
    else:
        expected = n - 1 if vertex else n
        assert int(out[0]) == expected and len(out) == expected + 1
        seen = bytearray(n + 1)
        for line in out[1:]:
            row = list(map(int, line.split()))
            if vertex:
                assert row[0] == 2 and len(row) == 3
                u, v = sorted(row[1:])
                assert v == u + 1 and 1 <= u < n
            else:
                assert row[0] == 1 and len(row) == 2
                u = row[1]
                assert 1 <= u <= n
            assert not seen[u]
            seen[u] = 1
        assert sum(seen) == expected

n = 500000
edges = [(u, u + 1) for u in range(1, n)] + [(n, n)] * (2000000 - n + 1)
for vertex in [True, False]:
    large(n, edges, 'chain', vertex)
# All two million input edges are non-loop; four parallel copies of a full cycle.
edges = [(u, u + 1) for u in range(1, n)] + [(n, 1)]
edges *= 4
for vertex in [True, False]:
    large(n, edges, 'cycle', vertex)
print('P8435/P8436: 500000 vertices / 2000000 edges, recursive chain with loops and four-copy non-loop cycle PASS', flush=True)
