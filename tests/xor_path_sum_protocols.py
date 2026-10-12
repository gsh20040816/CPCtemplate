from pathlib import Path
import hashlib
import json
import os
import random
import subprocess
import sys
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records

rng = random.Random(20261013)
row = next(r for r in records() if r['id'] == 'example-439')
assert (ROOT / row['snippet_file']).read_text() == row['snippet']
cases = []
for case in range(80):
    n = rng.randrange(1, 31)
    order = list(range(n))
    rng.shuffle(order)
    parent = [-1] * n
    graph = [[] for _ in range(n)]
    for i in range(1, n):
        u, v = order[i], order[rng.randrange(i)]
        parent[u] = v
        graph[u].append(v)
        graph[v].append(u)
    a = [rng.randrange(1 << 27) for _ in range(n)]
    lines = [f'{n} 50', ' '.join(map(str, parent)), ' '.join(map(str, a))]
    def oracle():
        answer = 0
        def visit(s, u, fa, xor):
            nonlocal answer
            xor ^= a[u]
            if u >= s:
                answer += xor
            for v in graph[u]:
                if v != fa:
                    visit(s, v, u, xor)
        for s in range(n):
            visit(s, s, -1, 0)
        return answer
    want = [oracle()]
    for q in range(50):
        u, v = rng.randrange(n), rng.randrange(1 << 27)
        lines.append(f'{u} {v}')
        a[u] = v
        want.append(oracle())
    cases.append(('\n'.join(lines) + '\n', want))

out = ROOT / 'build/xor-path-sum'
report = {'scope': '80 complete API protocols with independent Python vertex-path enumeration per form/mode; not original contest protocol or online AC.', 'runs': []}
forms = {'header': '#include "' + str(ROOT / row['driver']) + '"\n', 'printed': row['program']}
for form, source in forms.items():
    cpp = out / (form + '-protocol.cpp')
    cpp.write_text(source)
    for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
        exe = out / (form + '-' + mode + '-protocol')
        subprocess.run([CXX, '-std=c++20', *flags, str(cpp), '-o', str(exe)], check=True)
        env = os.environ.copy()
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
        for data, expected in cases:
            result = subprocess.run([str(exe)], input=data, capture_output=True, text=True, env=env, timeout=20)
            assert result.returncode == 0 and not result.stderr, result.stderr
            assert list(map(int, result.stdout.split())) == expected
        print(form, mode, '80 complete protocols PASS', flush=True)
        report['runs'].append({'form': form, 'mode': mode, 'cases': 80, 'source_sha256': hashlib.sha256(source.encode()).hexdigest()})
report['files'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT / row['driver'], ROOT / 'tests/xor_path_sum_protocols.py', ROOT / 'src/compact/xor_path_sum.hpp']}
(ROOT / 'verification/xor-path-sum-protocols.json').write_text(json.dumps(report, indent=2) + '\n')
