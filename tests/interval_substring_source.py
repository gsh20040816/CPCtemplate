"""Source audit: HDU4622 hash vs exact SAM, sets and suffix-sorting oracles."""
from pathlib import Path
import hashlib
import itertools
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


def sha(data):
    return hashlib.sha256(data).hexdigest()


def direct(s):
    return len({s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)})


def sorted_suffixes(s):
    a = sorted(s[i:] for i in range(len(s)))
    count = len(s) * (len(s) + 1) // 2
    for x, y in zip(a, a[1:]):
        k = 0
        while k < min(len(x), len(y)) and x[k] == y[k]:
            k += 1
        count -= k
    return count


def dataset(strings, full):
    rng = random.Random(4622)
    raw = str(len(strings)) + '\n'
    want = []
    for s in strings:
        n = len(s)
        if full:
            queries = [(l, r) for l in range(n) for r in range(l, n)]
        else:
            queries = [(0, n - 1), (0, 0), (n - 1, n - 1), (0, n // 2), (n // 2, n - 1)]
            for _ in range(15):
                l = rng.randrange(n)
                queries.append((l, rng.randrange(l, n)))
        rng.shuffle(queries)
        queries += queries[:3]
        raw += s + '\n' + str(len(queries)) + '\n'
        for l, r in queries:
            part = s[l:r + 1]
            expected = sorted_suffixes(part)
            if full:
                assert direct(part) == expected
            want.append(expected)
            raw += f'{l + 1} {r + 1}\n'
    return raw, want


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='interval-substring-' + mode + '-', dir=ROOT / 'build'))
    flags = ['-std=c++20', '-O2'] if mode == 'normal' else [
        '-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    report = dict(mode=mode, source_before_sha256=before, programs=[], mutants=[], expected_failures=[],
                  scope='Source-model API325; official statement and online verification remain pending.')

    def compile(name, text, extra=()):
        cpp = out / (name + '.cpp')
        exe = out / name
        cpp.write_text(text)
        command = [CXX, *flags, *extra, str(cpp), '-o', str(exe)]
        p = subprocess.run(command, capture_output=True, text=True)
        if p.returncode:
            raise RuntimeError(p.stderr)
        return exe, dict(name=name, command=command, source_sha256=sha(text.encode()),
                         binary_sha256=sha(exe.read_bytes()), compiler_stderr=p.stderr, runs=[])

    def run(exe, raw):
        return subprocess.run([str(exe)], input=raw, capture_output=True, text=True, timeout=240, env=env)

    rng = random.Random(46222026)
    strings = []
    for alphabet, limit in [('ab', 8), ('abc', 5)]:
        for n in range(1, limit + 1):
            strings += [''.join(x) for x in itertools.product(alphabet, repeat=n)]
    exhaustive = len(strings)
    strings += [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz'[:k]) for _ in range(rng.randrange(1, 31)))
                for k in [2, 3, 6, 26] for _ in range(25)]
    small = dataset(strings, True)
    stress_strings = ['a' * 2000, 'ab' * 1000, ''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(2000)),
                      'a' * 2008, 'a']
    stress = dataset(stress_strings, False)
    extended = dataset(['abcde' * 500, 'z'], False)
    inputs = [('small', small), ('source-boundaries', stress)]
    fixture = (ROOT / 'tests/fixtures/interval_substring_sources/kuangbin.inc').read_text()
    prelude = '#include <bits/stdc++.h>\nusing namespace std;\n'
    original, entry = compile('original', prelude + fixture)
    if mode == 'sanitizer':
        raw = '1\na\n1\n1 1\n'
        p = run(original, raw)
        if not p.returncode or 'index -1 out of bounds' not in p.stderr:
            raise RuntimeError(('missing original negative-column defect', p.returncode, p.stderr))
        entry.update(input=raw, returncode=p.returncode, diagnostic=p.stderr)
        report['expected_failures'].append(entry)
    else:
        # Undefined behavior is not used as correctness evidence, even if output looks right.
        report['original_compiled_only'] = entry
    anchor = 'for(int i = n;i >= 0;i--)'
    assert fixture.count(anchor) == 1
    repaired = fixture.replace(anchor, 'for(int i = n;i >= 1;i--)')
    exe, entry = compile('source-positive-rows', prelude + repaired)
    forms = [(exe, entry, inputs)]
    expanded_path = out / 'expanded.cpp'
    subprocess.run([sys.executable, str(ROOT / 'tools/bundle.py'), str(ROOT / 'tests/interval_substring_source_driver.cpp'), str(expanded_path)], check=True)
    expanded = expanded_path.read_text()
    for name, text in [('header', '#include "' + str(ROOT / 'tests/interval_substring_source_driver.cpp') + '"\n'), ('copied', expanded)]:
        for release in [False, True]:
            exe, entry = compile(name + ('-ndebug' if release else '-assert'), text, ['-DNDEBUG'] if release else [])
            forms.append((exe, entry, inputs + [('dynamic-size', extended)]))
    row = next(r for r in records() if r['id'] == 'example-325')
    sam = (ROOT / 'src/compact/string.hpp').read_text().split('struct SuffixAutomaton', 1)[1]
    minimal = prelude + '#include <cassert>\nstruct SuffixAutomaton' + sam + row['snippet']
    for name, text, extra in [('325-expanded', row['program'], []), ('325-minimal', minimal, []),
                              ('325-minimal-ndebug', minimal, ['-DNDEBUG'])]:
        exe, entry = compile(name, text, extra)
        forms.append((exe, entry, inputs + [('dynamic-size', extended)]))
    for exe, entry, selected in forms:
        for name, (raw, want) in selected:
            p = run(exe, raw)
            if p.returncode or p.stderr or list(map(int, p.stdout.split())) != want:
                raise RuntimeError((entry['name'], name, p.returncode, p.stderr[-1800:], p.stdout[:200]))
            entry['runs'].append(dict(name=name, input_sha256=sha(raw.encode()), output_sha256=sha(p.stdout.encode()), queries=len(want)))
        report['programs'].append(entry)
        print(entry['name'], 'PASS', flush=True)
    for name, old, new in [
        ('omit-link-length', 'sum += sam.a[u].len - sam.a[sam.a[u].link].len;', 'sum += sam.a[u].len;'),
        ('overwrite-total', 'sum += sam.a[u].len - sam.a[sam.a[u].link].len;', 'sum = sam.a[u].len - sam.a[sam.a[u].link].len;'),
        ('omit-left-reset', 'for (int l = 0; l < n; l++)\n        {\n            SuffixAutomaton sam;', 'SuffixAutomaton sam;\n        for (int l = 0; l < n; l++)\n        {')]:
        assert expanded.count(old) == 1
        exe, entry = compile(name, expanded.replace(old, new), ['-DNDEBUG'])
        p = run(exe, small[0])
        if p.returncode or p.stderr or list(map(int, p.stdout.split())) == small[1]:
            raise RuntimeError(('mutant not cleanly rejected', name, p.stderr))
        entry['oracle_rejected'] = True
        report['mutants'].append(entry)
        print(name, 'REJECT', flush=True)
    after = snapshot(ROOT)
    assert before == after, 'Source snapshot changed during runner'
    report.update(source_after_sha256=after, exhaustive_strings=exhaustive, random_strings=100,
                  small_queries=len(small[1]), source_stress_strings=len(stress_strings),
                  source_patch='Only i>=0 to i>=1 in final accumulation; original fixture unchanged.', passed=True)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out / 'report.json', flush=True)


if __name__ == '__main__':
    main()
