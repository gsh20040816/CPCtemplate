"""Complete input/output tests against spanning-tree subsets and row chasing."""
from compiler_config import CXX
from pathlib import Path
import itertools
import os
import random
import subprocess

root = Path(__file__).resolve().parents[1]
mode = 'san' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
flags = ['-std=c++20', '-O2'] if mode == 'normal' else ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
if os.uname().sysname == 'Darwin':
    flags += ['-Wl,-stack_size,0x20000000']
exe = {}
for name, driver in [('mst', 'verify/luogu/P4180.compact.cpp'), ('switch', 'verify/poj/1681.compact.cpp')]:
    dest = root / f'build/mst-switch-{name}-{mode}.cpp'
    exe[name] = dest.with_suffix('')
    subprocess.run(['python3', str(root / 'tools/bundle.py'), str(root / driver), str(dest)], check=True)
    subprocess.run([CXX, *flags, str(dest), '-o', str(exe[name])], check=True)


def run(name, data):
    p = subprocess.run([str(exe[name])], input=data, text=True, capture_output=True, check=True, timeout=90)
    assert not p.stderr, p.stderr
    return p.stdout.split()


def tree_sums(n, edges):
    sums = set()
    for ids in itertools.combinations(range(len(edges)), n - 1):
        graph = [[] for _ in range(n)]
        for i in ids:
            u, v, w = edges[i]
            graph[u].append(v)
            graph[v].append(u)
        seen = {0}
        queue = [0]
        for u in queue:
            for v in graph[u]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        if len(seen) == n:
            sums.add(sum(edges[i][2] for i in ids))
    return sorted(sums)


def mst_input(n, e):
    return f'{n} {len(e)}\n' + ''.join(f'{u + 1} {v + 1} {w}\n' for u, v, w in e)


rng = random.Random(2026093002)
for _ in range(260):
    n = rng.randrange(2, 8)
    e = [(rng.randrange(v), v, rng.randrange(6)) for v in range(1, n)]
    e += [(rng.randrange(n), rng.randrange(n), rng.randrange(6)) for _ in range(rng.randrange(6))]
    u, v, w = e[0]
    e.append((u, v, w + 20))  # Ensure strict second exists within official limits.
    sums = tree_sums(n, e)
    assert len(sums) >= 2
    assert run('mst', mst_input(n, e)) == [str(sums[1])]
n = 100000
e = [(v - 1, v, v % 2) for v in range(1, n)]
e += [(0, n - 1, 1)] * (300000 - len(e))
assert run('mst', mst_input(n, e)) == ['50001']
e = [(0, v, 10**9 - 1) for v in range(1, n)]
e += [(v, v, 0) for v in range(n)]
e += [(1, 2, 10**9)] * (300000 - len(e))
assert run('mst', mst_input(n, e)) == [str((n - 1) * (10**9 - 1) + 1)]
print('P4180 PASS: 260 independent spanning-tree subsets; 100000 vertices/300000 edges chain and star/self-loops with 64-bit total', flush=True)


def direct_table(n):
    # Enumerate physical brush presses, without constructing linear equations.
    moves = []
    for u in range(n):
        for v in range(n):
            mask = 0
            for i in range(n):
                for j in range(n):
                    if abs(i - u) + abs(j - v) <= 1:
                        mask |= 1 << (i * n + j)
            moves.append(mask)
    table = {}
    for pressed in range(1 << (n * n)):
        board = 0
        for j, mask in enumerate(moves):
            if pressed >> j & 1:
                board ^= mask
        table[board] = min(table.get(board, n * n), pressed.bit_count())
    return table


def chase(n, board):
    full = (1 << n) - 1
    rows = [(board >> (i * n)) & full for i in range(n)]
    best = None
    for first in range(1 << n):
        prev, cur, cost = 0, first, 0
        for i in range(n):
            cost += cur.bit_count()
            following = rows[i] ^ prev ^ cur ^ ((cur << 1) & full) ^ (cur >> 1)
            prev, cur = cur, following
        if cur == 0 and (best is None or cost < best):
            best = cost
    return 'inf' if best is None else str(best)


cases = []
for n in range(1, 4):
    table = direct_table(n)
    for board in range(1 << (n * n)):
        answer = str(table[board]) if board in table else 'inf'
        assert chase(n, board) == answer
        cases.append((n, board, answer))
for n in range(4, 16):
    for board in [0, (1 << (n * n)) - 1] + [rng.getrandbits(n * n) for _ in range(4)]:
        cases.append((n, board, chase(n, board)))
for _ in range(20):
    n = 15
    board = rng.getrandbits(n * n)
    cases.append((n, board, chase(n, board)))
for start in range(0, len(cases), 20):
    group = cases[start:start + 20]
    data = str(len(group)) + '\n'
    for n, board, _ in group:
        data += str(n) + '\n'
        data += ''.join(''.join('w' if board >> (i * n + j) & 1 else 'y' for j in range(n)) + '\n' for i in range(n))
    assert run('switch', data) == [a for _, _, a in group]
assert run('switch', '2\n3\nyyy\nyyy\nyyy\n5\nwwwww\nwwwww\nwwwww\nwwwww\nwwwww\n') == ['0', '15']
print(f'POJ1681 modeled application PASS: {len(cases)} boards; all boards through 3x3 checked by physical press enumeration; independent first-row chase through 15x15; multi-case reset and inf', flush=True)
