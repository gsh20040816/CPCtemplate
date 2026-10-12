#!/usr/bin/env python3
"""Source formulas and actual printed STL examples; no OJ claim."""
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
out = root / 'build/kuangbin-formula-stl'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
           UBSAN_OPTIONS='halt_on_error=1')
# Count components in the undirected permutation graph, independently of gcd.
def cycles(p):
    parent = list(range(len(p)))
    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for i, j in enumerate(p):
        a, b = find(i), find(j)
        parent[a] = b
    return len({find(i) for i in range(len(p))})

checked = 0
for n in range(1, 201):
    reflection_counts = []
    for k in range(n):
        assert cycles([(i + k) % n for i in range(n)]) == math.gcd(n, k)
        reflection_counts.append(cycles([(k - i) % n for i in range(n)]))
        checked += 2
    if n % 2:
        assert set(reflection_counts) == {(n + 1) // 2}
    else:
        assert reflection_counts.count(n // 2) == n // 2
        assert reflection_counts.count(n // 2 + 1) == n // 2
tex = (root / 'docs/infra-body.tex').read_text()
blocks = re.findall(r'\\begin\{lstlisting\}(.*?)\\end\{lstlisting\}', tex, re.S)
selection = [next(b for b in blocks if marker in b) for marker in
             ('multiset<int, greater<int>> s', 'struct Node',
              'priority_queue<int, vector<int>, greater<int>> q;', 'using Item =')]
code = '#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'
code += selection[1] + '\nint main()\n{\n'
code += selection[0] + '\nassert((vector<int>(s.begin(), s.end()) == vector<int>{7, 2}));\n'
code += selection[2] + '\nassert(x == 2 && q.top() == 7);\n'
code += selection[3] + '\nassert(key == 3 && id == 2 && q2.top().second == 8);\n'
code += '''
    nodes.insert({1, 2});
    nodes.insert({1, 3});
    nodes.insert({0, 8});
    auto it = nodes.begin();
    assert(it->x == 0 && it->y == 8);
    ++it;
    assert(it->x == 1 && it->y == 3);
    ++it;
    assert(it->x == 1 && it->y == 2);
}
'''
printed = out / 'printed.cpp'
printed.write_text(code)
results = {}
for mode in ('normal', 'sanitizer'):
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
    for name, source in [('source', root / 'tests/kuangbin_stl.cpp'), ('printed', printed)]:
        exe = out / (name + '-' + mode)
        subprocess.run([CXX, *flags, str(source), '-o', str(exe)], check=True)
        r = subprocess.run([str(exe)], capture_output=True, text=True, env=env, timeout=60)
        assert r.returncode == 0, r.stderr
        results[name + '-' + mode] = {'status': 'pass', 'output': r.stdout.strip()}
paths = ['tests/kuangbin_stl.cpp', 'tests/kuangbin_formula_stl.py',
         'docs/infra-body.tex', 'src/compact/polya.hpp']
report = dict(status='pass', permutation_formula_cases=checked,
              cycle_oracle='Undirected permutation graph components; n=1..200 all rotations/reflections',
              stl=results, printed_sha256=hashlib.sha256(code.encode()).hexdigest(),
              hashes={p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths},
              source_pdf_sha256=hashlib.sha256((root / 'build/source-audit/kuangbin.pdf').read_bytes()).hexdigest(),
              physical_pages_reviewed=[56, 57, 258, 259, 260],
              scope='2.19 formulas, 8.5 comparator functions and container operations. 8.4 read only, no stack-pointer assembly executed. No new online AC.')
(root / 'verification/kuangbin-formula-stl.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
