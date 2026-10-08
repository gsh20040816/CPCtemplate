#!/usr/bin/env python3
"""Audit the complete DA source program and copied SA/LCP composition."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records
from audit_copy_context import candidate, extract_components


def oracle(s):
    best = b''
    start = len(s)
    for center in range(2 * len(s) - 1):
        l = center // 2
        r = (center + 1) // 2
        while l >= 0 and r < len(s) and s[l] == s[r]:
            if r - l + 1 > len(best) or (r - l + 1 == len(best) and l < start):
                best = s[l:r + 1]
                start = l
            l -= 1
            r += 1
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sanitize', action='store_true')
    args = ap.parse_args()
    mode = 'sanitizer' if args.sanitize else 'normal'
    out = ROOT / 'build/da-palindrome' / mode
    out.mkdir(parents=True, exist_ok=True)
    row = next(r for r in records() if r['id'] == 'example-343')
    sha = lambda data: hashlib.sha256(data).hexdigest()
    paths = ['src/compact/string.hpp', 'src/compact/suffix_lcp.hpp', row['driver'],
             'tests/da_palindrome_source.py', 'tests/fixtures/da_palindrome_sources/kuangbin.cpp',
             'docs/catalog.json', 'docs/usage-examples.json', 'tools/usage_examples.py',
             'tools/audit_copy_context.py']
    snapshot = {p: sha((ROOT / p).read_bytes()) for p in paths}
    cases = []
    for alphabet, maximum in [(b'ab', 12), (b'abc', 7)]:
        for n in range(1, maximum + 1):
            cases += [bytes(v) for v in itertools.product(alphabet, repeat=n)]
    rng = random.Random(20261008)
    cases += [bytes(rng.randrange(33, 127) for _ in range(rng.randrange(1, 301))) for _ in range(500)]
    cases += [b'babad', b'cbbd', b'abc', b'abacdfgdcaba', b'abbaXYbaab', b'a', b'aa']
    source_cases = [(s, oracle(s)) for s in cases]
    for n in (10002, 10003, 10004):
        source_cases.append((b'a' * n, b'a' * n))
        s = (b'ab' * n)[:n]
        source_cases.append((s, s if n % 2 else s[:-1]))
        s = bytes(rng.randrange(33, 127) for _ in range(n))
        source_cases.append((s, oracle(s)))
    # Put tiny tokens after maximum sizes to detect stale global state in the original.
    source_cases += [(b'z', b'z'), (b'ab', b'a'), (b'aba', b'aba')]
    alphabet = bytes(i for i in range(256) if i not in b' \t\r\n\v\f')
    extension = [(s, oracle(s)) for s in [b'\0', b'\1\0\1', b'\xff\0\xff', b'\x80\x01\x80']]
    for _ in range(300):
        s = bytes(rng.choice(alphabet) for _ in range(rng.randrange(1, 151)))
        extension.append((s, oracle(s)))
    for n in (500000, 500001):
        extension.append((b'a' * n, b'a' * n))
        s = (b'ab' * n)[:n]
        extension.append((s, s if n % 2 else s[:-1]))
    flags = ['-std=c++20', '-O1' if args.sanitize else '-O2']
    if args.sanitize:
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
    env = {**os.environ, 'ASAN_OPTIONS': 'detect_leaks=0:halt_on_error=1', 'UBSAN_OPTIONS': 'halt_on_error=1'}
    def compile(src, exe, extra=()):
        p = subprocess.run([CXX, *flags, *extra, str(src), '-o', str(exe)], capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
    def check(exe, batch):
        data = b' \n\t' + b'\n\t'.join(s for s, _ in batch)
        want = b''.join(v + b'\n' for _, v in batch)
        p = subprocess.run([str(exe)], input=data, capture_output=True, timeout=180, env=env)
        assert p.returncode == 0, p.stderr.decode(errors='replace')
        assert p.stdout == want, (str(exe), len(p.stdout), len(want), p.stdout[:100], want[:100])
    components = {r['symbol']: r for r in extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))}
    programs = []
    for form in ('source', 'header', 'ndebug', 'expanded', 'copied'):
        exe = out / form
        src = ROOT / row['driver']
        if form == 'source':
            src = exe.with_suffix('.cpp')
            fixture = ROOT / 'tests/fixtures/da_palindrome_sources/kuangbin.cpp'
            src.write_text('#include <bits/stdc++.h>\nusing namespace std;\nnamespace original {\n#include "' + str(fixture) + '"\n}\nint main()\n{\n    return original::main();\n}\n')
        elif form in ('expanded', 'copied'):
            src = exe.with_suffix('.cpp')
            src.write_text(row['program'] if form == 'expanded' else candidate(row, row['requires'], components)['program'])
        compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
        check(exe, [])
        check(exe, source_cases)
        if form != 'source':
            check(exe, extension)
        programs.append(dict(form=form, source_cases=len(source_cases), extension_cases=0 if form=='source' else len(extension), source_sha256=sha(src.read_bytes())))
        print(mode, form, 'PASS', flush=True)
    mutants = []
    if not args.sanitize:
        base = row['program']
        replacements = [
            ('rightmost-tie', '> best', '>= best'),
            ('odd-center-offset', 'lcp.query(i, n - i - 1)', 'lcp.query(i, n - i)'),
            ('even-empty-suffix', 'lcp.query(i, n - i)', 'lcp.query(i, n - i - 1)'),
            ('separator-collision', 'a[len] = 1;', 'a[len] = a[0];')]
        for name, old, new in replacements:
            assert old in base
            src = out / (name + '.cpp')
            src.write_text(base.replace(old, new))
            exe = out / name
            compile(src, exe)
            try:
                check(exe, source_cases[:8190])
            except AssertionError:
                mutants.append(dict(name=name, detected=True))
            else:
                raise AssertionError('surviving mutant ' + name)
    assert all(sha((ROOT / p).read_bytes()) == v for p, v in snapshot.items())
    report = dict(mode=mode, source_lines=121, source_cases=len(source_cases), extension_cases=len(extension),
                  programs=programs, mutants=mutants, snapshot=snapshot, usage=row['id'],
                  program_sha256=row['program_sha256'], scope='Complete original EOF token protocol and exact leftmost output; original domain printable ASCII length1..10004. New non-whitespace byte extension and500001 length tested separately. No online AC.',
                  source_adaptations='Minus glyphs normalized and PDF wrapped lines joined; full fragment included inside namespace with standard headers, original main called by wrapper. No algorithm edits.')
    (ROOT / f'verification/da-palindrome-{mode}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(mode, len(source_cases), len(extension), 'PASS', flush=True)


if __name__ == '__main__':
    main()
