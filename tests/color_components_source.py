#!/usr/bin/env python3
"""Locked QTREE6 complete source versus BFS and current minimal-copy program."""
import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess
import sys
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import records
from audit_copy_context import candidate, extract_components
build = root / 'build/color-components'
pdf = root / 'build/source-audit/kuangbin.pdf'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(pdf) == 'f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad'
text = pdf.with_suffix('.txt').read_text()
start = text.index(' 1   //http://www.spoj.com/problems/QTREE6/')
end = text.index('3.5.6 SPOJQTREE7', start)
lines = []
for line in text[start:end].splitlines():
    match = re.match(r'^\s*(\d+)\s+(.*)$', line)
    if match:
        assert int(match[1]) == len(lines) + 1
        lines.append(match[2].replace('−', '-'))
    elif line.strip() == ';':
        lines[-1] += ';'
assert len(lines) == 140
original = build / 'upstream.cpp'
original.write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + '\n'.join(lines) + '\n')
components = {r['symbol']: r for r in extract_components(json.loads((root / 'docs/catalog.json').read_text()))}
row = next(r for r in records() if r['id'] == 'example-406')
minimal = build / 'QTREE6-minimal.cpp'
minimal.write_text(candidate(row, row['requires'], components)['program'])
assert minimal.read_bytes() == (root / 'verification/submitted/SP16549.compact.cpp').read_bytes()
rng = random.Random(20261012)
cases = [('5\n1 2\n1 3\n1 4\n1 5\n3\n0 1\n1 1\n0 1\n', [5, 1])]
for case in range(100):
    n = case + 1
    edges = [(u, rng.randrange(1, u)) for u in range(2, n + 1)]
    g = [[] for _ in range(n + 1)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    col = [0] * (n + 1)
    ops, ans = [], []
    for _ in range(300):
        op, u = rng.randrange(2), rng.randrange(1, n + 1)
        ops.append((op, u))
        if op:
            col[u] ^= 1
        else:
            seen = {u}
            q = [u]
            for v in q:
                for w in g[v]:
                    if w not in seen and col[w] == col[u]:
                        seen.add(w)
                        q.append(w)
            ans.append(len(q))
    data = str(n) + '\n' + ''.join(f'{u} {v}\n' for u, v in edges) + str(len(ops)) + '\n' + ''.join(f'{op} {u}\n' for op, u in ops)
    cases.append((data, ans))
report = {'source_pdf_sha256': sha(pdf), 'numbered_lines': 140, 'physical_pages': [87, 88, 89], 'original_sha256': sha(original), 'minimal_sha256': sha(minimal), 'cases': len(cases), 'scope': 'Every case uses a fresh complete program process; upstream return inside EOF loop is unchanged. Only Unicode minus and wrapped semicolon normalized; common headers prepended.', 'runs': []}
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=all'])]:
    for name, path in [('original', original), ('driver', root / row['driver']), ('minimal', minimal)]:
        exe = build / (name + '-' + mode)
        subprocess.run([CXX, '-std=c++17', *flags, str(path), '-o', str(exe)], check=True)
        for data, expected in cases:
            run = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=10, env=env)
            assert not run.stderr, run.stderr
            assert list(map(int, run.stdout.split())) == expected
        report['runs'].append({'mode': mode, 'form': name, 'cases': len(cases), 'status': 'pass'})
        print(mode, name, len(cases), 'PASS', flush=True)
(root / 'verification/color-components-source.json').write_text(json.dumps(report, indent=2) + '\n')
