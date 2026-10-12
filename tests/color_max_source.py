#!/usr/bin/env python3
"""Full 152-line original, current driver and minimal copy against BFS."""
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
build = root / 'build/color-max'
pdf = root / 'build/source-audit/kuangbin.pdf'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(pdf) == 'f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad'
text = pdf.with_suffix('.txt').read_text()
start = text.index(' 1   //http://www.spoj.com/problems/QTREE7/')
end = text.index('3.5.7 HDU4010', start)
lines = []
for line in text[start:end].splitlines():
    match = re.match(r'^\s*(\d+)\s+(.*)$', line)
    if match:
        assert int(match[1]) == len(lines) + 1
        lines.append(match[2].replace('−', '-'))
    elif line.strip() and 'kuangbin' not in line:
        assert line.startswith(' '), line
        lines[-1] += line.strip().replace('−', '-')
assert len(lines) == 152
original = build / 'upstream.cpp'
original.write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + '\n'.join(lines) + '\n')
components = {r['symbol']: r for r in extract_components(json.loads((root / 'docs/catalog.json').read_text()))}
row = next(r for r in records() if r['id'] == 'example-408')
minimal = build / 'QTREE7-minimal.cpp'
minimal.write_text(candidate(row, row['requires'], components)['program'])
assert minimal.read_bytes() == (root / 'verification/submitted/SP16580.compact.cpp').read_bytes()
rng = random.Random(20261012)
cases = [('5\n1 2\n1 3\n1 4\n1 5\n0 1 1 1 1\n1 2 3 4 5\n3\n0 1\n1 1\n0 1\n', [1, 5]), ('7\n1 2\n1 3\n2 4\n2 5\n3 6\n3 7\n0 0 0 0 0 0 0\n1 2 3 4 5 6 7\n4\n0 1\n1 1\n0 2\n0 3\n', [7, 5, 7])]
for case in range(100):
    n = case + 1
    edges = [(u, rng.randrange(1, u)) for u in range(2, n + 1)]
    g = [[] for _ in range(n + 1)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    col = [rng.randrange(2) for _ in range(n + 1)]
    w = [rng.choice([-1000000, -1, 0, 1, 1000000]) for _ in range(n + 1)]
    data = str(n) + '\n' + ''.join(f'{u} {v}\n' for u, v in edges) + ' '.join(map(str, col[1:])) + '\n' + ' '.join(map(str, w[1:])) + '\n300\n'
    ans = []
    for _ in range(300):
        op, u = rng.randrange(3), rng.randrange(1, n + 1)
        data += f'{op} {u}'
        if op == 1:
            col[u] ^= 1
        elif op == 2:
            w[u] = rng.choice([-1000000, -1, 0, 1, 1000000])
            data += f' {w[u]}'
        else:
            seen = {u}
            q = [u]
            for v in q:
                for x in g[v]:
                    if x not in seen and col[x] == col[u]:
                        seen.add(x)
                        q.append(x)
            ans.append(max(w[v] for v in q))
        data += '\n'
    cases.append((data, ans))
# Repeated different sizes in one EOF input also exercise full initialization/reset.
raw = ''.join(data for data, _ in cases)
expected = [x for _, answers in cases for x in answers]
report = {'source_pdf_sha256': sha(pdf), 'numbered_lines': 152, 'physical_pages': [90, 91, 92, 93], 'original_sha256': sha(original), 'minimal_sha256': sha(minimal), 'cases': len(cases), 'scope': 'Unmodified full EOF source; normalized PDF minus and wrapped lines, prepended headers. Values within +/-1000000 avoid upstream -INF sentinel limit; full signed64 library testing separate. Mirror numeric bounds malformed, no inferred official domain.', 'runs': []}
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=all'])]:
    for name, path in [('original', original), ('driver', root / row['driver']), ('minimal', minimal)]:
        exe = build / (name + '-' + mode)
        subprocess.run([CXX, '-std=c++17', *flags, str(path), '-o', str(exe)], check=True)
        run = subprocess.run([str(exe)], input=raw, text=True, capture_output=True, check=True, timeout=60, env=env)
        assert not run.stderr, run.stderr
        assert list(map(int, run.stdout.split())) == expected
        report['runs'].append({'mode': mode, 'form': name, 'cases': len(cases), 'status': 'pass'})
        print(mode, name, len(cases), 'PASS', flush=True)
(root / 'verification/color-max-source.json').write_text(json.dumps(report, indent=2) + '\n')
