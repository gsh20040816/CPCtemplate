import hashlib
import json
import os
import random
import subprocess
import sys
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import records
from audit_copy_context import candidate, extract_components

san = '--sanitize' in sys.argv
mode = 'sanitizer' if san else 'normal'
work = root / 'build/min-mean-cycle' / mode
work.mkdir(parents=True, exist_ok=True)
flags = ['-std=c++20', '-O1' if san else '-O2']
if san:
    flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
rows = [r for r in records() if r['id'] in ['example-380', 'example-381']]
components = {r['symbol']: r for r in extract_components(json.loads((root / 'docs/catalog.json').read_text()))}
commands = []

def compile(src, exe, extra=()):
    cmd = [CXX, *flags, *extra, str(src), '-o', str(exe)]
    commands.append(cmd)
    subprocess.run(cmd, check=True, capture_output=True, text=True)

def run(exe, data=''):
    p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env=env, timeout=90)
    assert p.returncode == 0, p.stderr
    return p.stdout

prefix = candidate(rows[0], ['minimum_mean_cycle'], components)['program'].split('int main()')[0]
core_source = (root / 'tests/minimum_mean_cycle.cpp').read_text().replace('#include "../src/compact/minimum_mean_cycle.hpp"', prefix)
core = {}
for form in ['header', 'ndebug', 'copied']:
    src = root / 'tests/minimum_mean_cycle.cpp'
    exe = work / ('core-' + form)
    if form == 'copied':
        src = exe.with_suffix('.cpp')
        src.write_text(core_source)
    compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
    core[form] = run(exe).strip()
    print(mode, form, core[form], flush=True)

from fractions import Fraction

def brute(n, edges):
    g = [[] for _ in range(n)]
    for u, v, w in edges:
        g[u].append((v, w))
    best = None
    def dfs(start, u, seen, total, length):
        nonlocal best
        for v, w in g[u]:
            if v == start:
                r = Fraction(total + w, length + 1)
                if best is None or r < best:
                    best = r
            elif v > start and v not in seen:
                dfs(start, v, seen | {v}, total + w, length + 1)
    for start in range(n):
        dfs(start, start, {start}, 0, 0)
    return best

rng = random.Random(3199)
cases = {'example-380': [], 'example-381': []}
for trial in range(151):
    n = rng.randrange(1, 8)
    edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(-10000000, 10000001)) for _ in range(rng.randrange(20))]
    want = brute(n, edges)
    data = f'{n} {len(edges)}\n' + ''.join(f'{u} {v} {w}\n' for u,v,w in edges)
    cases['example-381'].append((data, want))
    if want is not None:
        data = f'{n} {len(edges)}\n' + ''.join(f'{u+1} {v+1} {w / 10000:.4f}\n' for u,v,w in edges)
        cases['example-380'].append((data, want / 10000))
cases['example-381'] += [('0 0\n', None), ('2 2\n0 1 -9223372036854775808\n1 0 9223372036854775807\n', Fraction(-1, 2))]
cases['example-380'] += [('4 5\n1 2 5\n2 3 5\n3 1 5\n2 4 3\n4 1 3\n', Fraction(11,3)), ('2 2\n1 2 -2.9\n2 1 -3.1\n', Fraction(-3))]
# Large cancelling terms, mean close to a decimal rounding boundary.
for n in [2, 31, 3000]:
    weights = [9999999 if i % 2 == 0 else -9999999 for i in range(n)]
    tail = Fraction('0.000000123456789123456789')
    want = (sum(weights) + tail) / n
    lines = [f'{n} {n}']
    for i,w in enumerate(weights):
        value = str(w) if i else '9999999.000000123456789123456789'
        lines.append(f'{i+1} {(i+1)%n+1} {value}')
    cases['example-380'].append(('\n'.join(lines)+'\n', want))
usage = {}
for row in rows:
    forms = {}
    for form in ['header', 'ndebug', 'expanded', 'copied']:
        src = root / row['driver']
        exe = work / (row['id'] + '-' + form)
        if form in ['expanded', 'copied']:
            src = exe.with_suffix('.cpp')
            src.write_text(row['program'] if form == 'expanded' else candidate(row, ['minimum_mean_cycle'], components)['program'])
        compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
        for data, want in cases[row['id']]:
            output = run(exe, data).strip()
            if row['id'] == 'example-381':
                if want is None:
                    assert output == 'NONE'
                else:
                    a, b = map(int, output.split())
                    assert b > 0 and Fraction(a, b) == want, (data, output, want)
            else:
                assert abs(Fraction(output) - want) <= Fraction(51, 10**10), (output, want)
        forms[form] = len(cases[row['id']])
        print(mode, row['id'], form, 'PASS', flush=True)
    usage[row['id']] = dict(program_sha256=row['program_sha256'], forms=forms)
mutants = {}
if not san:
    for name, old, new in [('minmax', 'less(best[v], now)', 'less(now, best[v])'), ('exact-length', 'fill(next.begin(), next.end(), inf);', 'next = d;'), ('fraction-order', 'a.first * b.second < b.first * a.second', 'a.first < b.first')]:
        assert old in core_source
        src = work / ('mutant-' + name + '.cpp')
        exe = src.with_suffix('')
        src.write_text(core_source.replace(old, new))
        # Bounds checks make wrong-index mutants fail deterministically.
        compile(src, exe, ['-D_GLIBCXX_ASSERTIONS'])
        p = subprocess.run([str(exe)], capture_output=True, timeout=90)
        assert p.returncode != 0, name
        mutants[name] = 'detected'
files = ['src/compact/minimum_mean_cycle.hpp', 'tests/minimum_mean_cycle.cpp', 'tests/minimum_mean_cycle.py'] + [r['driver'] for r in rows]
report = dict(status='pass', mode=mode, compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0], commands=commands, core=core, usage=usage, mutants=mutants, source_sha256={p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in files}, scope='Definition-only simple-cycle enumeration; exact rational integer answers, Fraction reference for decimal weights and cancellation/rounding tests; two-pass Karp tested in four driver forms. OJ evidence separate.')
(root / f'verification/min-mean-cycle-{mode}.json').write_text(json.dumps(report, indent=2) + '\n')
