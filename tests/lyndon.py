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
work = root / 'build/lyndon' / mode
work.mkdir(parents=True, exist_ok=True)
flags = ['-std=c++20', '-O1' if san else '-O2']
if san:
    flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
rows = [r for r in records() if r['id'] in ['example-372', 'example-373']]
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

prefix = candidate(rows[0], ['lyndon'], components)['program'].split('int main()')[0]
core_source = (root / 'tests/lyndon.cpp').read_text().replace('#include "../src/compact/lyndon.hpp"', prefix)
core = {}
for form in ['header', 'ndebug', 'copied']:
    src = root / 'tests/lyndon.cpp'
    exe = work / ('core-' + form)
    if form == 'copied':
        src = exe.with_suffix('.cpp')
        src.write_text(core_source)
    compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
    core[form] = run(exe).strip()
    print(mode, form, core[form], flush=True)

def brute(s):
    # Enumerate all cuts; definition-only suffix comparisons, no Duval recurrence.
    solutions = []
    def dfs(l, prev, ends):
        if l == len(s):
            solutions.append(ends)
            return
        for r in range(l + 1, len(s) + 1):
            word = s[l:r]
            if prev is not None and prev < word:
                continue
            if all(word < word[k:] for k in range(1, len(word))):
                dfs(r, word, ends + [r])
    dfs(0, None, [])
    assert len(solutions) == 1
    return solutions[0]

def xor(a):
    ans = 0
    for x in a:
        ans ^= x
    return ans

rng = random.Random(6114)
strings = ['ababa', 'bbababaabaaabaaaab']
strings += [''.join(chr(97 + rng.randrange(4)) for _ in range(rng.randrange(1, 15))) for _ in range(100)]
cases = {'example-372': [(s + '\n', [xor(brute(s))]) for s in strings], 'example-373': []}
n = 5000001
cases['example-372'] += [('a' * n + '\n', [1]), ('a' * (n - 1) + 'b\n', [n]), ('ab' * (n // 2) + 'a\n', [xor(range(2, n, 2)) ^ n])]
for trial in range(101):
    s = bytes(rng.randrange(256) for _ in range(trial % 15))
    ends = brute(s)
    data = str(len(s)) + '\n' + ' '.join(map(str, s)) + '\n'
    cases['example-373'].append((data, [len(ends), *ends]))
usage = {}
for row in rows:
    forms = {}
    for form in ['header', 'ndebug', 'expanded', 'copied']:
        src = root / row['driver']
        exe = work / (row['id'] + '-' + form)
        if form in ['expanded', 'copied']:
            src = exe.with_suffix('.cpp')
            src.write_text(row['program'] if form == 'expanded' else candidate(row, ['lyndon'], components)['program'])
        compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
        for data, want in cases[row['id']]:
            got = list(map(int, run(exe, data).split()))
            assert got == want, (row['id'], form, data[:100], got[:50], want[:50])
        forms[form] = len(cases[row['id']])
        print(mode, row['id'], form, 'PASS', flush=True)
    usage[row['id']] = dict(program_sha256=row['program_sha256'], forms=forms)
mutants = {}
if not san:
    for name, old, new in [('equality', 's[k] <= (unsigned char)s[j]', 's[k] < (unsigned char)s[j]'), ('signed-byte', '(unsigned char)s[k] <= (unsigned char)s[j]', 's[k] <= s[j]'), ('endpoint', 'ends.push_back(i);', 'ends.push_back(i - 1);')]:
        assert old in core_source
        src = work / ('mutant-' + name + '.cpp')
        exe = src.with_suffix('')
        src.write_text(core_source.replace(old, new))
        # Force signed char so this regression does not depend on target defaults.
        compile(src, exe, ['-fsigned-char'])
        p = subprocess.run([str(exe)], capture_output=True, timeout=90)
        assert p.returncode != 0, name
        mutants[name] = 'detected'
files = ['src/compact/lyndon.hpp', 'tests/lyndon.cpp', 'tests/lyndon.py'] + [r['driver'] for r in rows]
report = dict(status='pass', mode=mode, compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0], commands=commands, core=core, usage=usage, mutants=mutants, source_sha256={p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in files}, scope='Full factor endpoints compared with unique definition-only partition enumeration; maximum-length pressure. Online and runtime ranking tracked separately.')
(root / f'verification/lyndon-{mode}.json').write_text(json.dumps(report, indent=2) + '\n')
