"""Run the exact printed programs against independent operation histories."""
from pathlib import Path
import hashlib
import json
import os
import random
import subprocess
import sys
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import records
rng = random.Random(430431)
cases = {'example-430': [], 'example-431': []}
for trial in range(80):
    values = {}
    slots = [[]]
    commands = []
    expected = []
    for step in range(200):
        r = rng.randrange(len(slots))
        op = rng.randrange(5)
        if op == 0 or not values:
            x = rng.randrange(-1000, 1001)
            node = len(values) + 1
            values[node] = x
            slots[r].append(node)
            commands.append(f'1 {r} {x}')
            expected.append(node)
        elif op == 1:
            key = rng.randrange(-1200, 1201)
            left = [i for i in slots[r] if values[i] < key]
            right = [i for i in slots[r] if values[i] >= key]
            slots[r] = left
            slots.append(right)
            commands.append(f'2 {r} {key}')
            expected.append(len(slots) - 1)
        elif op == 2:
            delta = rng.randrange(-10, 11)
            for i in slots[r]:
                values[i] += delta
            commands.append(f'3 {r} {delta}')
        elif op == 3 and slots[r]:
            node = rng.choice(slots[r])
            commands.append(f'5 {r} {node}')
            expected.append(values[node])
        elif len(slots) > 1:
            s = rng.randrange(len(slots))
            if r != s and (not slots[r] or not slots[s] or max(values[i] for i in slots[r]) <= min(values[i] for i in slots[s])):
                commands.append(f'4 {r} {s}')
                slots[r] += slots[s]
                slots[s] = []
    for r, ids in enumerate(slots):
        for node in ids:
            commands.append(f'5 {r} {node}')
            expected.append(values[node])
    cases['example-430'].append((str(len(commands)) + '\n' + '\n'.join(commands) + '\n', expected))
for trial in range(80):
    n = rng.randrange(1, 35)
    versions = [[]]
    parent = [-1]
    commands = []
    expected = []
    for step in range(200):
        v = rng.randrange(len(versions))
        op = rng.randrange(3)
        if op == 0:
            pos = rng.randrange(n)
            weight = rng.randrange(-1000, 1001)
            versions.append(versions[v] + [(pos, weight)])
            parent.append(v)
            commands.append(f'1 {v} {pos} {weight}')
            expected.append(len(versions) - 1)
        elif op == 1:
            l, r = sorted([rng.randrange(n + 1), rng.randrange(n + 1)])
            selected = [w for p, w in versions[v] if l <= p < r]
            commands.append(f'2 {v} {l} {r}')
            expected += [len(selected), sum(selected)]
        else:
            before = v
            for _ in range(rng.randrange(10)):
                if parent[before] != -1:
                    before = parent[before]
            key = rng.randrange(-2, n + 3)
            positions = [p for p, w in versions[v][len(versions[before]):] if p >= key]
            commands.append(f'3 {before} {v} {key}')
            expected.append(min(positions, default=-1))
    cases['example-431'].append((f'{n} {len(commands)}\n' + '\n'.join(commands) + '\n', expected))
out = root / 'build/wida-splay'
results = {}
for row in records():
    if row['id'] not in cases:
        continue
    source = out / (row['id'] + '-printed.cpp')
    source.write_text(row['program'])
    for mode in ['normal', 'sanitizer']:
        flags = ['-std=c++20', '-O2']
        if mode == 'sanitizer':
            flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        exe = out / (row['id'] + '-' + mode)
        subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)
        for data, expected in cases[row['id']]:
            p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'), timeout=30)
            assert p.returncode == 0 and not p.stderr, p.stderr
            assert list(map(int, p.stdout.split())) == expected
        results[row['id'] + '-' + mode] = {'protocols': len(cases[row['id']]), 'program_sha256': row['program_sha256']}
        print(row['id'], mode, '80 independent histories PASS', flush=True)
(root / 'verification/wida-splay-integration.json').write_text(json.dumps(results, indent=2) + '\n')
