"""Check Fenwick::kth and the exact P3369 printed driver in both local modes.

This writes only fenwick-selection-prefixed build artifacts. It does not register
usage examples or create online-judge evidence. The integration JSON contains the
proposed example-210 record and canonical cases for the shared usage runner.
"""
from compiler_config import CXX
from pathlib import Path
import bisect
import datetime
import hashlib
import json
import os
import platform
import random
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import expand

DRIVER = 'verify/luogu/P3369.fenwick-selection.compact.cpp'
CORE = 'src/compact/data_structure.hpp'
BUILD = ROOT / 'build'
BUILD.mkdir(exist_ok=True)
entry = {
    'id': 'example-210',
    'symbol': 'Fenwick',
    'kind': 'template',
    'problem': 'Luogu P3369',
    'url': 'https://www.luogu.com.cn/problem/P3369',
    'summary': '维护可重集合的插入、删除一个、排名、第 k 小和严格前驱/后继。'
               '预读全部操作并离散化非第 k 小查询的值域；频数下标为 1-based，'
               'kth 的返回值减 1 后映射回原值。排名查询允许 x 不在集合中；'
               '第 k 小与前驱/后继按题目保证存在。n≤100000，|x|≤10000000；'
               '总复杂度 O(n log n)，空间 O(n)。',
    'driver': DRIVER,
    'requires': ['Fenwick'],
}

canonical = [
    ('12\n1 5\n1 2\n1 5\n3 5\n4 3\n5 5\n6 2\n2 5\n3 6\n4 2\n2 2\n4 1\n',
     {'exact_text': '2\n5\n2\n5\n3\n5\n5\n'}),
    ('13\n1 -10000000\n1 0\n1 10000000\n3 -10000000\n3 10000000\n4 1\n4 3\n5 1\n6 -1\n2 0\n5 1\n6 -1\n3 0\n',
     {'exact_text': '1\n3\n-10000000\n10000000\n0\n0\n-10000000\n10000000\n2\n'}),
    ('9\n1 7\n1 7\n2 7\n4 1\n2 7\n3 7\n1 -3\n3 7\n4 1\n',
     {'exact_text': '7\n1\n2\n-3\n'}),
    ('3\n3 -10000000\n3 0\n3 10000000\n', {'exact_text': '1\n1\n1\n'}),
    ('1\n1 10000000\n', {'exact_text': ''}),
    ('6\n1 -9\n1 9\n5 0\n6 0\n3 0\n3 10\n', {'exact_text': '-9\n9\n2\n3\n'}),
]


def encode(ops):
    return str(len(ops)) + '\n' + ''.join(f'{op} {x}\n' for op, x in ops)


def oracle(ops, allow_missing_erase=False):
    """A sorted Python list, independent of coordinate compression and Fenwick."""
    values, output = [], []
    for op, x in ops:
        if op == 1:
            bisect.insort(values, x)
        elif op == 2:
            p = bisect.bisect_left(values, x)
            if p < len(values) and values[p] == x:
                values.pop(p)
            else:
                assert allow_missing_erase
        elif op == 3:
            output.append(bisect.bisect_left(values, x) + 1)
        elif op == 4:
            assert 1 <= x <= len(values)
            output.append(values[x - 1])
        elif op == 5:
            p = bisect.bisect_left(values, x)
            assert p > 0
            output.append(values[p - 1])
        elif op == 6:
            p = bisect.bisect_right(values, x)
            assert p < len(values)
            output.append(values[p])
        else:
            raise AssertionError(op)
    return ''.join(f'{x}\n' for x in output)


programs = []
for i, (data, expected) in enumerate(canonical):
    tokens = list(map(int, data.split()))
    ops = list(zip(tokens[1::2], tokens[2::2]))
    assert len(ops) == tokens[0]
    assert oracle(ops) == expected['exact_text']
    programs.append((f'canonical-{i}', data, expected['exact_text']))

rng = random.Random(3369210)
for case in range(200):
    values, ops = [], []
    for step in range(500):
        op = rng.randrange(1, 7) if values else rng.choice([1, 3])
        x = rng.randrange(-100, 101)
        if op == 1:
            bisect.insort(values, x)
        elif op == 2:
            x = rng.choice(values)
            values.pop(bisect.bisect_left(values, x))
        elif op == 4:
            x = rng.choice([1, len(values), rng.randrange(1, len(values) + 1)])
        elif op == 5:
            x = max(x, values[0] + 1)
        elif op == 6:
            x = min(x, values[-1] - 1)
        ops.append((op, x))
    programs.append((f'random-{case}', encode(ops), oracle(ops)))

# Maximum operation count, maximum distinct compression domain, and both extremes.
ops = [(1, -10000000)] + [(1, x) for x in range(99995)] + [(1, 10000000)]
ops += [(4, 1), (4, 99997), (3, 10000000)]
assert len(ops) == 100000
programs.append(('scale-distinct', encode(ops), oracle(ops)))
ops = [(1, x) for x in range(100000)]
programs.append(('scale-domain', encode(ops), oracle(ops)))

# Delete exactly one occurrence, create zero-frequency holes, then query them.
ops = [(1, 2 * i - 50000) for i in range(50000)]
ops += [(2, 2 * i - 50000) for i in range(0, 50000, 2)]
queries = [(3, 10000000), (4, 1), (4, 25000), (5, 0), (6, 0)]
ops += queries * 5000
assert len(ops) == 100000
programs.append(('scale-deletions', encode(ops), oracle(ops)))

# Large multiplicity retains one boundary element on either side of zero.
ops = [(1, -10000000), (1, 10000000)] + [(1, 0)] * 39998
ops += [(2, 0)] * 20000
queries = [(4, 1), (4, 20000), (3, 0), (5, 0), (6, 0), (4, 2), (4, 19999), (3, 1)]
ops += queries * 5000
assert len(ops) == 100000
programs.append(('scale-duplicates', encode(ops), oracle(ops)))

# Conservative driver extension: ignore absent erases; not an OJ guarantee.
extension = [(2, 9), (3, 9), (1, 9), (2, 9), (2, 9), (3, 10), (1, -4), (4, 1)]
programs.append(('extension-absent-erase', encode(extension), oracle(extension, True)))

text = (ROOT / DRIVER).read_text()
start = re.search(r'(?m)^int main\(\)', text).start()
prefix, snippet = text[:start], text[start:]
program = '#include <bits/stdc++.h>\nusing namespace std;\n' + expand(prefix, (ROOT / DRIVER).parent, set()) + snippet
source = BUILD / 'fenwick-selection-printed.cpp'
source.write_text(program)
(BUILD / 'fenwick-selection-integration.json').write_text(
    json.dumps({'entry': entry, 'cases': canonical}, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


inputs = [DRIVER, CORE, 'tests/fenwick-selection.cpp', 'tests/fenwick-selection.py', 'tools/usage_examples.py']
hashes = {name: sha(ROOT / name) for name in inputs}
report = {
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Local independent kth checks and exact printed P3369 usage; no online AC',
    'official_statement': 'https://www.luogu.com.cn/problem/P3369',
    'source_sha256': hashes,
    'program_sha256': hashlib.sha256(program.encode()).hexdigest(),
    'compiler': subprocess.check_output([CXX, '--version'], text=True).splitlines()[0],
    'platform': platform.platform(),
    'driver_cases_per_mode': len(programs),
    'legal_driver_cases_per_mode': len(programs) - 1,
    'canonical_cases_per_mode': len(canonical),
    'maximum_input_operations': 100000,
    'random_seed': 3369210,
    'modes': {},
}
environment = dict(os.environ)
# Leak detection is explicitly outside this check; ASan/UBSan remain active.
environment['ASAN_OPTIONS'] = 'detect_leaks=0:halt_on_error=1'
environment['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
report['sanitizer_environment'] = {key: environment[key] for key in ('ASAN_OPTIONS', 'UBSAN_OPTIONS')}
for mode in ['normal', 'sanitizer']:
    flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    checked = []
    for label, file in [('core', ROOT / 'tests/fenwick-selection.cpp'), ('printed', source)]:
        exe = BUILD / f'fenwick-selection-{label}-{mode}'
        command = [CXX, '-std=c++20', *flags, str(file), '-o', str(exe)]
        subprocess.run(command, check=True)
        if label == 'core':
            run = subprocess.run([str(exe)], text=True, capture_output=True, check=True, env=environment, timeout=120)
            assert not run.stderr, run.stderr
            checked.append({'target': label, 'command': command, 'stdout': run.stdout})
            print(f'{mode}: {run.stdout.strip()}', flush=True)
        else:
            timings = []
            for name, data, expected in programs:
                before = time.monotonic()
                run = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, env=environment, timeout=120)
                assert not run.stderr, (mode, name, run.stderr)
                assert run.stdout == expected, (mode, name, run.stdout[:200], expected[:200])
                timings.append({'name': name, 'seconds': round(time.monotonic() - before, 6),
                                'input_sha256': hashlib.sha256(data.encode()).hexdigest(),
                                'output_sha256': hashlib.sha256(expected.encode()).hexdigest()})
            checked.append({'target': label, 'command': command, 'cases': timings})
            print(f'{mode}: {len(programs)} exact printed driver programs PASS', flush=True)
    report['modes'][mode] = checked
assert hashes == {name: sha(ROOT / name) for name in inputs}, 'Sources changed while testing'
(BUILD / 'fenwick-selection-report.json').write_text(json.dumps(report, indent=2) + '\n')
print('Fenwick selection normal and ASan/UBSan verification PASS', flush=True)
