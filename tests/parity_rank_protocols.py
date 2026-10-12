from pathlib import Path
import hashlib
import json
import os
import random
import subprocess
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
out = root / 'build/wida-balanced'
rng = random.Random(202608)
protocols = {'persistent_parity_index': [], 'rank_split': []}
for trial in range(60):
    n = rng.randrange(1, 30)
    versions = [[0] * n]
    ops, expected = [], []
    for _ in range(150):
        if rng.randrange(2) == 0:
            v = rng.randrange(len(versions))
            x = rng.randrange(n)
            delta = max(-versions[v][x], rng.randrange(-5, 6))
            nxt = versions[v].copy()
            nxt[x] += delta
            versions.append(nxt)
            ops.append(f'1 {v} {x} {delta}')
            expected.append(len(versions) - 1)
        else:
            before, after = [rng.randrange(len(versions)) for _ in range(2)]
            if any(x > y for x, y in zip(versions[before], versions[after])):
                before = 0
            all_values = [x for x in range(n - 1, -1, -1) for _ in range(versions[after][x] - versions[before][x])]
            odds = [x for x in all_values if x % 2]
            k = rng.randrange(len(all_values) + 5)
            op = rng.randrange(2, 5)
            if op == 2:
                remaining = all_values.copy()
                for _ in range(k):
                    if not remaining or remaining[0] % 2:
                        break
                    remaining.pop(0)
                expected.append(remaining[0] if remaining else -1)
            elif op == 3:
                if k >= len(odds):
                    expected += [-1, 0, k - len(odds)]
                else:
                    x = odds[k]
                    expected += [x, odds.count(x), k - odds.index(x)]
            else:
                expected += [len(all_values), len(odds)]
            ops.append(f'{op} {before} {after}' + (f' {k}' if op != 4 else ''))
    protocols['persistent_parity_index'].append((f'{n} {len(ops)}\n' + '\n'.join(ops) + '\n', expected))
    sets = [[]]
    ops, expected = [], []
    for _ in range(150):
        s = rng.randrange(len(sets))
        op = rng.randrange(1, 6)
        if op == 1:
            x = rng.randrange(n)
            count = sets[s].count(x)
            delta = rng.randrange(-count, 5)
            if delta < 0:
                for _ in range(-delta):
                    sets[s].remove(x)
            else:
                sets[s] += [x] * delta
                sets[s].sort()
            ops.append(f'1 {s} {x} {delta}')
        elif op == 2:
            k = rng.randrange(len(sets[s]) + 1)
            reverse = rng.randrange(2)
            ordered = sorted(sets[s], reverse=bool(reverse))
            sets[s] = sorted(ordered[k:])
            sets.append(sorted(ordered[:k]))
            expected.append(len(sets) - 1)
            ops.append(f'2 {s} {k} {reverse}')
        elif op == 3:
            l, r = sorted([rng.randrange(n + 1), rng.randrange(n + 1)])
            expected.append(sum(l <= x < r for x in sets[s]))
            ops.append(f'3 {s} {l} {r}')
        elif op == 4:
            other = rng.randrange(len(sets))
            if s == other:
                continue
            sets[s] = sorted(sets[s] + sets[other])
            sets[other] = []
            ops.append(f'4 {s} {other}')
        else:
            k = rng.randrange(len(sets[s]) + 3)
            expected.append(sets[s][k - 1] if 1 <= k <= len(sets[s]) else -1)
            ops.append(f'5 {s} {k}')
    protocols['rank_split'].append((f'{n} {len(ops)}\n' + '\n'.join(ops) + '\n', expected))
results = {}
for name, cases in protocols.items():
    for mode in ['normal', 'sanitizer']:
        flags = ['-std=c++20', '-O2']
        if mode == 'sanitizer':
            flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        exe = out / (name + '-protocol-' + mode)
        subprocess.run([CXX, *flags, str(root / f'verify/api/{name}.compact.cpp'), '-o', str(exe)], check=True)
        for data, expected in cases:
            run = subprocess.run([str(exe)], input=data, text=True, capture_output=True, timeout=15,
                                 env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'))
            assert run.returncode == 0 and not run.stderr, run.stderr
            assert list(map(int, run.stdout.split())) == expected
        results[name + '-' + mode] = len(cases)
        print(name, mode, len(cases), 'full API protocols PASS', flush=True)
files = ['src/compact/persistent_parity_index.hpp', 'src/compact/merge_split_tree.hpp',
         'verify/api/persistent_parity_index.compact.cpp', 'verify/api/rank_split.compact.cpp', 'tests/parity_rank_protocols.py']
(root / 'verification/parity-rank-protocols.json').write_text(json.dumps(dict(runs=results,scope='Custom API protocols, not OJ verdict',files={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files}),indent=2)+'\n')
