"""Official samples and independent BFS checks for the LOJ121 adapter."""
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records
from audit_copy_context import candidate, extract_components

out = ROOT / 'build/loj121'
out.mkdir(parents=True, exist_ok=True)
row = next(r for r in records() if r['symbol'] == 'TimeConnectivity')
components = {r['symbol']: r for r in extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))}
prefix = candidate(row, row['requires'], components)['program'].split('int main()')[0]
driver = ROOT / 'verify/loj/121.compact.cpp'
source = out / '121.cpp'
source.write_text(prefix + driver.read_text().split('\n', 1)[1])
cases = [('200 5\n2 123 127\n0 123 127\n2 123 127\n1 127 123\n2 123 127\n', 'N Y N'), ('4 10\n0 1 2\n0 2 3\n0 3 1\n2 1 4\n0 4 3\n2 1 4\n1 2 3\n2 1 4\n1 1 3\n2 1 4\n', 'N Y Y N'), ('1 0\n', '')]
rng = random.Random(121)
for repeat in range(250):
    n = rng.randint(1, 20)
    edges = set()
    ops = []
    answers = []
    for t in range(200):
        u, v = sorted([rng.randint(1, n), rng.randint(1, n)])
        edge = (u, v)
        op = rng.randrange(3)
        if op == 0 and u != v and edge not in edges:
            edges.add(edge)
        elif op == 1 and edge in edges:
            edges.remove(edge)
        else:
            op = 2
            seen = {u}
            todo = [u]
            for x in todo:
                for a, b in edges:
                    y = b if a == x else a if b == x else 0
                    if y and y not in seen:
                        seen.add(y)
                        todo.append(y)
            answers.append('Y' if v in seen else 'N')
        if rng.randrange(2):
            u, v = v, u
        ops.append(f'{op} {u} {v}')
    cases.append((f'{n} {len(ops)}\n' + '\n'.join(ops) + '\n', ' '.join(answers)))
report = {'official_samples': 2, 'random_streams': 250, 'oracle': 'BFS on current simple graph', 'forms': {}, 'submitted_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
for mode in ['normal', 'sanitizer']:
    flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    for form in ['header', 'ndebug', 'copied']:
        exe = out / (mode + '-' + form)
        subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', *flags, *(['-DNDEBUG'] if form == 'ndebug' else []), str(source if form == 'copied' else driver), '-o', str(exe)], check=True)
        for data, want in cases:
            got = subprocess.check_output([str(exe)], input=data, text=True, timeout=20)
            assert got.split() == want.split()
        report['forms'][mode + '-' + form] = 'pass'
        print(mode, form, 'PASS', flush=True)
report['status'] = 'pass'
(ROOT / 'verification/loj121-local.json').write_text(json.dumps(report, indent=2) + '\n')
