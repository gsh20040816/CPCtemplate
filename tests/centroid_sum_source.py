"""Original 177-line centroid/Fenwick program vs recursive library and BFS oracle.

The EOF/!/query protocol is taken from the fixed source, not an official HDU
statement. Original integer boundaries are isolated expected failures.
"""
from collections import deque
from pathlib import Path
import hashlib
import itertools
import json
import os
import platform
import random
import resource
import subprocess
import sys
import tempfile
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot


def digest(data):
    return hashlib.sha256(data).hexdigest()


def case(values, edges, operations):
    n = len(values)
    graph = [[] for _ in values]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    current = values[:]
    answers = []
    distances = {}
    for op, u, x in operations:
        if op == '!':
            current[u] = x
            continue
        if x < 0:
            answers.append(0)
        elif x >= n - 1:
            answers.append(sum(current))
        else:
            if u not in distances:
                d = [-1] * n
                d[u] = 0
                q = deque([u])
                while q:
                    a = q.popleft()
                    for b in graph[a]:
                        if d[b] == -1:
                            d[b] = d[a] + 1
                            q.append(b)
                distances[u] = d
            answers.append(sum(v for v, d in zip(current, distances[u]) if d <= x))
    raw = f'{n} {len(operations)}\n' + ' '.join(map(str, values)) + '\n'
    raw += ''.join(f'{u+1} {v+1}\n' for u, v in edges)
    raw += ''.join(f'{op} {u+1} {x}\n' for op, u, x in operations)
    return raw, answers


def prufer(n, code):
    degree = [1] * n
    for v in code:
        degree[v] += 1
    edges = []
    for v in code:
        u = next(i for i in range(n) if degree[i] == 1)
        edges.append((u, v))
        degree[u] -= 1
        degree[v] -= 1
    ends = [i for i in range(n) if degree[i] == 1]
    if len(ends) == 2:
        edges.append(tuple(ends))
    return edges


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='centroid-source-' + mode + '-', dir=ROOT / 'build'))
    flags = ['-std=c++20', '-O2'] if mode == 'normal' else [
        '-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    if platform.system() == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    else:
        _, hard = resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK, (min(512 << 20, hard) if hard != -1 else 512 << 20, hard))
    env = os.environ.copy()
    env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    report = dict(mode=mode, source_before_sha256=before, stack_mib=512,
                  programs=[], mutants=[], expected_failures=[], scope='Source protocol only; no official HDU/online AC claim.')

    def compile(name, text, extra=()):
        cpp = out / (name + '.cpp')
        exe = out / name
        cpp.write_text(text)
        command = [CXX, *flags, *extra, str(cpp), '-o', str(exe)]
        p = subprocess.run(command, capture_output=True, text=True)
        if p.returncode:
            raise RuntimeError(p.stderr)
        return exe, dict(name=name, command=command, source_sha256=digest(text.encode()),
                         binary_sha256=digest(exe.read_bytes()), compiler_stderr=p.stderr, runs=[])

    def run(exe, raw):
        return subprocess.run([str(exe)], input=raw, capture_output=True, text=True, timeout=180, env=env)

    rng = random.Random(49182026)
    cases = []
    small_count = 0
    for n in range(1, 6):
        for code in itertools.product(range(n), repeat=max(0, n - 2)):
            edges = prufer(n, code)
            values = [rng.randrange(-1000, 1001) for _ in range(n)]
            ops = [('?', u, r) for u in range(n) for r in range(-1, n + 1)]
            for u in range(n):
                ops += [('!', u, -19), ('!', u, -19)]
                ops += [('?', v, r) for v in range(n) for r in range(n + 1)]
            cases.append(case(values, edges, ops))
            small_count += 1
    for _ in range(180):
        n = rng.randrange(1, 61)
        edges = [(rng.randrange(v), v) for v in range(1, n)]
        rng.shuffle(edges)
        values = [rng.randrange(-1000, 1001) for _ in range(n)]
        ops = []
        for step in range(150):
            op = '!' if step % 3 == 0 else '?'
            x = rng.randrange(-1000, 1001) if op == '!' else rng.choice([-1, 0, n, 2147483647, rng.randrange(n)])
            ops.append((op, rng.randrange(n), x))
        cases.append(case(values, edges, ops))
    # One process, varying n/topology: exercises original TT/cc_tail/vec resets.
    raw = ''.join(c[0] for c in cases)
    want = [x for c in cases for x in c[1]]
    inputs = [('small-multicase', raw, want)]
    for shape in range(4):
        n = 100000
        edges = [(v - 1 if shape == 0 else 0 if shape == 1 else (v - 1) // 2 if shape == 2 else rng.randrange(v), v) for v in range(1, n)]
        ops = []
        for step in range(600):
            u = step % 5 * (n // 5)
            ops += [('!', u, step - 300), ('?', u, step % 3), ('?', u, n), ('?', u, -1)]
        large = case([1] * n, edges, ops)
        # Append a single-node dataset to detect failure to reset after a large tree.
        tail = case([7], [], [('?', 0, 0), ('!', 0, -3), ('?', 0, n)])
        inputs.append((f'100000-shape-{shape}', large[0] + tail[0], large[1] + tail[1]))

    original = '#include <bits/stdc++.h>\nusing namespace std;\nnamespace Original {\n' + (ROOT / 'tests/fixtures/centroid_sum_sources/kuangbin.inc').read_text() + '\n}\nint main() { return Original::main(); }\n'
    exe, entry = compile('source', original)
    source_exe = exe
    expanded_path = out / 'expanded.cpp'
    subprocess.run([sys.executable, str(ROOT / 'tools/bundle.py'), str(ROOT / 'tests/centroid_sum_source_driver.cpp'), str(expanded_path)], check=True)
    expanded = expanded_path.read_text()
    forms = [('source', exe, entry)]
    for form, text in [('header', '#include "' + str(ROOT / 'tests/centroid_sum_source_driver.cpp') + '"\n'), ('copied', expanded)]:
        for release in [False, True]:
            exe, entry = compile(form + ('-ndebug' if release else '-assert'), text, ['-DNDEBUG'] if release else [])
            forms.append((form, exe, entry))
    for form, exe, entry in forms:
        for name, raw, want in inputs:
            p = run(exe, raw)
            if p.returncode or p.stderr or list(map(int, p.stdout.split())) != want:
                raise RuntimeError((entry['name'], name, p.returncode, p.stderr[-2000:], p.stdout[:200]))
            entry['runs'].append(dict(name=name, input_sha256=digest(raw.encode()), output_sha256=digest(p.stdout.encode()), queries=len(want)))
        if form != 'source':
            # Extra API integer range beyond the original int implementation.
            raw, want = case([2147483647, 2147483647], [(0, 1)], [
                ('?', 0, 1), ('?', 1, -9223372036854775808), ('!', 0, -2147483648),
                ('?', 0, 0), ('!', 0, 2147483647), ('?', 1, 9223372036854775807)])
            p = run(exe, raw)
            if p.returncode or p.stderr or list(map(int, p.stdout.split())) != want:
                raise RuntimeError(('wide-integer', p.stderr, p.stdout))
            entry['runs'].append(dict(name='wide-integer', input_sha256=digest(raw.encode()), expected=want, passed=True))
        report['programs'].append(entry)
        print(entry['name'], 'PASS', len(entry['runs']), flush=True)
    for name, a, b in [
        ('omit-part-update', 'if (b != -1) part[c][b].add(d + 1, delta);', ';'),
        ('omit-part-subtraction', 'if (b != -1) answer -= prefix(part[c][b], radius - d);', ';'),
        ('set-as-add', 'T delta = x - value[u];', 'T delta = x;')]:
        if expanded.count(a) != 1:
            raise RuntimeError(('mutant anchor', name))
        exe, entry = compile(name, expanded.replace(a, b), ['-DNDEBUG'])
        p = run(exe, inputs[0][1])
        if p.returncode or p.stderr or list(map(int, p.stdout.split())) == inputs[0][2]:
            raise RuntimeError(('mutant not cleanly rejected', name, p.stderr))
        entry['oracle_rejected'] = True
        report['mutants'].append(entry)
        print(name, 'REJECT', flush=True)
    if mode == 'sanitizer':
        bad = [
            ('bucket-sum', '2 0\n2147483647 2147483647\n1 2\n'),
            ('assignment-delta', '1 1\n-2147483648\n! 1 2147483647\n'),
            ('radius-subtraction', '2 1\n0 0\n1 2\n? 1 -2147483648\n')]
        for name, raw in bad:
            p = run(source_exe, raw)
            if not p.returncode or 'signed integer overflow' not in p.stderr:
                raise RuntimeError(('missing source overflow', name, p.returncode, p.stderr))
            report['expected_failures'].append(dict(name=name, input=raw, returncode=p.returncode, diagnostic=p.stderr))
            print(name, 'UBSan reproduced', flush=True)
    after = snapshot(ROOT)
    if before != after:
        raise RuntimeError('Source snapshot changed during runner')
    report.update(source_after_sha256=after, small_labeled_trees=small_count, random_trees=180,
                  large_shapes=4, small_queries=len(inputs[0][2]), passed=True)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out / 'report.json', flush=True)


if __name__ == '__main__':
    main()
