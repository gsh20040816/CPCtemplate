"""Forest BFS oracle for full kuangbin HDU4010 source protocol and new LCT."""
from pathlib import Path
from collections import deque
import hashlib
import json
import os
import random
import subprocess
import sys
import tempfile
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot
from usage_examples import records


def dataset(n, edges, values, ops):
    g = [set() for _ in range(n)]
    for x, y in edges:
        g[x - 1].add(y - 1)
        g[y - 1].add(x - 1)
    v = values[:]
    output = []
    lines = [str(n), *[f'{x} {y}' for x, y in edges], ' '.join(map(str, v)), str(len(ops))]
    for op in ops:
        lines.append(' '.join(map(str, op)))
        kind = op[0]
        x, y = op[-2] - 1, op[-1] - 1
        parent = {x: x}
        q = deque([x])
        while q:
            u = q.popleft()
            for w in g[u]:
                if w not in parent:
                    parent[w] = u
                    q.append(w)
        path = []
        if y in parent:
            u = y
            path.append(u)
            while u != x:
                u = parent[u]
                path.append(u)
        if kind == 1:
            if path:
                output.append(-1)
            else:
                g[x].add(y)
                g[y].add(x)
        elif kind == 2:
            if len(path) < 2:
                output.append(-1)
            else:
                p = parent[y]
                g[y].remove(p)
                g[p].remove(y)
        elif not path:
            output.append(-1)
        elif kind == 3:
            for u in path:
                v[u] += op[1]
        else:
            output.append(max(v[u] for u in path))
    return '\n'.join(lines) + '\n', ''.join(str(x) + '\n' for x in output) + '\n'


def main():
    if not __debug__:
        raise RuntimeError('Oracle requires assertions')
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='dynamic-path-max-' + mode + '-', dir=ROOT / 'build'))
    flags = ['-std=c++20'] + (['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    sha = lambda b: hashlib.sha256(b).hexdigest()
    report = dict(mode=mode, source_before_sha256=before, programs=[], mutants=[],
                  stack_bytes=256 << 20, scope='Local source-model/API checks; official statement/resources and online AC remain unverified.')
    cases = [dataset(3, [(1, 2), (2, 3)], [100, -20, 1],
             [(4, 1, 3), (3, 7, 1, 3), (4, 1, 1), (4, 3, 3), (2, 1, 3),
              (4, 1, 2), (4, 2, 3), (2, 1, 1), (1, 2, 3), (4, 1, 3)]),
             dataset(1, [], [-100], [(4, 1, 1), (3, -5, 1, 1), (4, 1, 1),
                                   (1, 1, 1), (2, 1, 1), (4, 1, 1)])]
    rng = random.Random(40102026)
    for _ in range(200):
        n = rng.randrange(2, 51)
        edges = [(i, rng.randrange(1, i)) for i in range(2, n + 1)]
        values = [rng.randrange(-1000, 1001) for _ in range(n)]
        ops = []
        for _ in range(400):
            kind = rng.randrange(1, 5)
            x, y = rng.randrange(1, n + 1), rng.randrange(1, n + 1)
            ops.append((kind, rng.randrange(-100, 101), x, y) if kind == 3 else (kind, x, y))
        cases.append(dataset(n, edges, values, ops))
    data = ''.join(x for x, _ in cases)
    want = ''.join(y for _, y in cases)
    report.update(datasets=len(cases), input_sha256=sha(data.encode()), expected_output_sha256=sha(want.encode()))
    header = (ROOT / 'src/compact/dynamic_path_max.hpp').read_text()
    component = header[header.index('struct DynamicPathMax'):]
    core = (ROOT / 'tests/dynamic_path_max.cpp').read_text()
    copied_core = '#include <bits/stdc++.h>\nusing namespace std;\n' + component + '\n' + '\n'.join(core.splitlines()[1:])
    driver = (ROOT / 'verify/api/dynamic_path_max.compact.cpp').read_text()
    row = next(r for r in records() if r['id'] == 'example-328')
    minimal = '#include <algorithm>\n#include <optional>\n#include <vector>\n#include <utility>\n#include <iostream>\nusing namespace std;\n' + component + '\n' + row['snippet']

    def compile(name, text, ndebug=False):
        cpp, obj, exe = out / (name + '.cpp'), out / (name + '.o'), out / name
        cpp.write_text(text)
        command = [CXX, *flags, *(['-DNDEBUG'] if ndebug else []), '-Dmain=cpc_entry', '-c', str(cpp), '-o', str(obj)]
        p = subprocess.run(command, capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        link = [CXX, *flags, '-pthread', str(ROOT / 'tests/driver_stack.cpp'), str(obj), '-o', str(exe)]
        q = subprocess.run(link, capture_output=True, text=True)
        assert q.returncode == 0, q.stderr
        return exe, dict(name=name, command=command, link_command=link, compiler_stderr=p.stderr + q.stderr,
                         source_sha256=sha(text.encode()), binary_sha256=sha(exe.read_bytes()))

    def run(exe, input_data):
        p = subprocess.run([str(exe)], input=input_data, text=True, capture_output=True, env=env, timeout=180)
        assert p.returncode == 0 and not p.stderr, (exe.name, p.returncode, p.stderr)
        return p.stdout

    for name, text, ndebug in [('header', '#include "' + str(ROOT / 'tests/dynamic_path_max.cpp') + '"\n', False),
                                ('copied-core', copied_core, False), ('ndebug-core', copied_core, True)]:
        exe, entry = compile(name, text, ndebug)
        got = run(exe, '')
        fields = got.split()
        assert len(fields) == 6 and fields[-1] == 'PASS' and fields[-3:-1] == ['30000', '100000']
        entry['core_counts'] = list(map(int, fields[:-1]))
        report['programs'].append(entry)
        print(name, got.strip(), flush=True)
    source = '#include <bits/stdc++.h>\nusing namespace std;\n' + (ROOT / 'tests/fixtures/dynamic_path_max_sources/kuangbin.inc').read_text()
    forms = [('driver', '#include "' + str(ROOT / 'verify/api/dynamic_path_max.compact.cpp') + '"\n', False),
             ('expanded', row['program'], False), ('minimal', minimal, False), ('ndebug-driver', minimal, True),
             ('original-source', source, False)]
    for name, text, ndebug in forms:
        exe, entry = compile(name, text, ndebug)
        got = run(exe, data)
        assert got == want, (name, 'protocol mismatch')
        entry.update(datasets=len(cases), output_sha256=sha(got.encode()))
        report['programs'].append(entry)
        print(name, len(cases), 'PASS', flush=True)
    mutations = [('direct-edge-instead-of-parent', 't.cut_parent(x, y)', 't.cut(x, y)'),
                 ('endpoint-instead-of-max', 'return a[y].mx;', 'return a[y].val;'),
                 ('omit-left-lazy', 'apply(a[x].ch[0], a[x].add);', '')]
    for name, anchor, replacement in mutations:
        assert minimal.count(anchor) == 1
        exe, entry = compile(name, minimal.replace(anchor, replacement))
        got = run(exe, cases[0][0])
        assert got != cases[0][1], name
        entry['rejected_by'] = 'independent BFS oracle answer mismatch'
        report['mutants'].append(entry)
    after = snapshot(ROOT)
    assert before == after
    report.update(source_after_sha256=after, passed=True)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out / 'report.json', flush=True)


if __name__ == '__main__':
    main()
