"""P3835 bundled driver against independent sorted snapshots; no online AC."""
from pathlib import Path
from bisect import bisect_left, bisect_right, insort
import json
import os
import random
import subprocess
import tempfile
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
RNG = random.Random(3835001)
SANITIZE = os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1'
checks = queries = 0


def check(exe, ops, expected, env):
    global checks, queries
    data = str(len(ops)) + '\n' + ''.join(f'{v} {op} {x}\n' for v, op, x in ops)
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True,
                       env=env, timeout=180)
    assert p.returncode == 0, (p.returncode, p.stderr)
    assert not p.stderr, p.stderr
    actual = list(map(int, p.stdout.split()))
    assert actual == expected, (len(ops), actual[:20], expected[:20])
    checks += len(ops)
    queries += len(expected)


with tempfile.TemporaryDirectory(prefix='cpc-p3835-') as tmp:
    cpp, exe = Path(tmp) / 'main.cpp', Path(tmp) / 'main'
    subprocess.run(['python3', str(ROOT / 'tools/bundle.py'),
                    str(ROOT / 'verify/luogu/P3835.compact.cpp'), str(cpp)], check=True)
    flags = ['-std=c++20', '-Wall', '-Wextra', '-O2']
    if SANITIZE:
        flags = ['-std=c++20', '-Wall', '-Wextra', '-O1', '-g',
                 '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-no-pie']
    subprocess.run([CXX, *flags, str(cpp), '-o', str(exe)], check=True)
    env = os.environ.copy()
    if SANITIZE:
        env.setdefault('ASAN_OPTIONS', 'detect_leaks=0:abort_on_error=1')
        env.setdefault('UBSAN_OPTIONS', 'halt_on_error=1:print_stacktrace=1')
    for case in range(100):
        versions, ops, answers = [[]], [], []
        for i in range(1, 1001):
            v = RNG.randrange(i)
            if i % 3 == 0: v = i - 1
            values = versions[v].copy()
            op = RNG.randrange(1, 7)
            x = RNG.choice([-10**9, 10**9, RNG.randrange(-30, 31)])
            if op == 4 and not values: op = 3
            if op == 1:
                insort(values, x)
            elif op == 2:
                if values and RNG.randrange(2): x = RNG.choice(values)
                k = bisect_left(values, x)
                if k < len(values) and values[k] == x: values.pop(k)
            elif op == 3:
                answers.append(bisect_left(values, x) + 1)
            elif op == 4:
                x = RNG.randrange(1, len(values) + 1)
                answers.append(values[x - 1])
            elif op == 5:
                k = bisect_left(values, x)
                answers.append(values[k - 1] if k else -2147483647)
            else:
                k = bisect_right(values, x)
                answers.append(values[k] if k < len(values) else 2147483647)
            ops.append((v, op, x))
            versions.append(values)
        check(exe, ops, answers, env)
    # Full task limit: branch from a long sorted prefix, then alias versions.
    # The large expected output uses explicit interval/multiset facts, not Treap.
    count = 100000
    ops = [(i - 1, 1, i) for i in range(1, count + 1)]
    answers = []
    for j in range(100000):
        source = RNG.randrange(count + 1)
        op = (3, 4, 5, 6)[j % 4]
        x = source // 2
        if op == 3:
            x = source + 1
            ans = source + 1
        elif op == 4:
            if source == 0: op, x, ans = 3, 0, 1
            else: x = max(1, x); ans = x
        elif op == 5:
            ans = x - 1 if x > 1 else -2147483647
        else:
            ans = x + 1 if x < source else 2147483647
        ops.append((source, op, x)); answers.append(ans)
    for j in range(100000):
        # Every deletion starts at the same historic full set, never its sibling.
        x = 1 + j % count
        ops.append((count, 2, x))
        version = len(ops)
        ops.append((version, 3, x)); answers.append(x)
        # Query version must keep the deletion, including absent predecessor at 1.
        alias = len(ops)
        ops.append((alias, 5, x + 1)); answers.append(x - 1 if x > 1 else -2147483647)
    assert len(ops) == 500000
    check(exe, ops, answers, env)
print(json.dumps({'status': 'PASS', 'mode': 'ASan/UBSan' if SANITIZE else 'optimized',
                  'operations': checks, 'queries': queries, 'random_inputs': 100,
                  'maximum_input_operations': 500000,
                  'online_AC': False, 'leak_detection': 'not tested'}, ensure_ascii=False))
