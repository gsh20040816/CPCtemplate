#!/usr/bin/env python3
"""SA-IS: independent suffix enumeration and maximum-size closed forms."""
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from usage_examples import records
from compiler_config import CXX


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if not __debug__:
        raise RuntimeError('Python checks must stay enabled')
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='sais-' + mode + '-', dir=ROOT / 'build'))
    before = snapshot(ROOT)
    probe = (ROOT / 'tests/sais_probe.cpp').read_text()
    core = next(x['code'] for x in extract_components(json.loads((ROOT / 'docs/catalog.json').read_text())) if x['symbol'] == 'SAIS')
    headers = ['algorithm', 'cassert', 'climits', 'iostream', 'numeric', 'random', 'stdexcept', 'string', 'vector']
    prelude = ''.join('#include <' + x + '>\n' for x in headers) + 'using namespace std;\n'
    copied = prelude + core + '\n' + probe.replace('#include "../src/compact/sais.hpp"', '')
    flags = ['-std=c++20', '-Wall', '-Wextra'] + (['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    report = dict(mode=mode, source_before_sha256=before, compiler=str(compiler), compiler_sha256=sha(compiler.read_bytes()), flags=flags, programs=[], mutants=[], applications=[])

    def compile(name, source, extra=()):
        cpp, exe = out / (name + '.cpp'), out / name
        cpp.write_text(source)
        command = [CXX, *flags, *extra, str(cpp), '-o', str(exe)]
        subprocess.run(command, capture_output=True, check=True)
        return exe, dict(name=name, compile_command=command, source_sha256=sha(cpp.read_bytes()), binary_sha256=sha(exe.read_bytes()))

    reference = None
    for form, source in [('header', '#include "' + str(ROOT / 'tests/sais_probe.cpp') + '"\n'), ('copied', copied)]:
        for nd in [False, True]:
            name = form + ('-ndebug' if nd else '-assert')
            exe, entry = compile(name, source, ['-DNDEBUG'] if nd else [])
            p = subprocess.run([str(exe)], capture_output=True, env=env, timeout=600)
            assert p.returncode == 0 and not p.stderr, (name, p.returncode, p.stderr[-1000:])
            assert p.stdout.startswith(b'PASS ') and p.stdout.endswith(b' checks\n'), p.stdout
            if reference is None:
                reference = p.stdout
            assert p.stdout == reference
            (out / (name + '.out')).write_bytes(p.stdout)
            entry.update(output_sha256=sha(p.stdout), result=p.stdout.decode().strip())
            report['programs'].append(entry)
    mutations = [
        ('merge-lms-names', 'reduced[id[order[i]]] = names - 1;', 'reduced[id[order[i]]] = 0;'),
        ('reverse-result', 'sa = sort_suffixes(s, alphabet);', 'sa = sort_suffixes(s, alphabet); reverse(sa.begin(), sa.end());'),
        ('zero-lcp', 'lcp[rk[i]] = k;', 'lcp[rk[i]] = 0;'),
        ('shift-lcp', 'lcp[rk[i]] = k;', 'lcp[rk[i] - 1] = k;'),
        ('no-kasai-decrement', 'if (k) k--;', 'if (false) k--;'),
    ]
    for name, old, new in mutations:
        assert copied.count(old) == 1, name
        exe, entry = compile(name, copied.replace(old, new), ['-DNDEBUG'])
        p = subprocess.run([str(exe)], capture_output=True, env=env, timeout=180)
        assert p.returncode == 0 and not p.stderr and p.stdout == b'ORACLE_REJECT\n', (name, p.returncode, p.stdout, p.stderr[-1000:])
        (out / (name + '.out')).write_bytes(p.stdout)
        entry.update(output_sha256=sha(p.stdout), independent_oracle_rejected=True)
        report['mutants'].append(entry)
    rng = random.Random(2413809)
    cases = ['a', 'banana', 'mississippi', 'abababab', 'zzzz', 'zyxwvutsrqponmlkjihgfedcba']
    cases += [''.join(rng.choice('abcde') for _ in range(rng.randrange(1, 250))) for _ in range(100)]
    datasets = [(f'small-{i}', s, sorted(range(len(s)), key=lambda j: s[j:])) for i, s in enumerate(cases)]
    n = 500000
    datasets.append(('maximum-constant', 'a' * n, list(range(n - 1, -1, -1))))
    for pattern in ['ab', 'dacb']:
        s = (pattern * ((n + len(pattern) - 1) // len(pattern)))[:n]
        answer = []
        for phase in sorted(range(len(pattern)), key=lambda j: pattern[j]):
            last = n - 1 - (n - 1 - phase) % len(pattern)
            answer.extend(range(last, -1, -len(pattern)))
        datasets.append(('maximum-' + pattern, s, answer))
    row = next(r for r in records() if r['id'] == 'example-241')
    for name, text in [('driver', '#include "' + str(ROOT / row['driver']) + '"\n'), ('bundle', row['program']), ('minimal-copy', prelude + core + '\n' + row['snippet'])]:
        exe, entry = compile(name, text)
        entry['runs'] = []
        for label, s, expected in datasets:
            inp = (s + '\n').encode()
            p = subprocess.run([str(exe)], input=inp, capture_output=True, env=env, timeout=180)
            assert p.returncode == 0 and not p.stderr, (name, label, p.returncode, p.stderr[-1000:])
            assert list(map(int, p.stdout.split())) == expected, (name, label)
            data = (' '.join(map(str, expected)) + '\n').encode()
            (out / (label + '.in')).write_bytes(inp)
            (out / (label + '.expected')).write_bytes(data)
            (out / (name + '-' + label + '.out')).write_bytes(p.stdout)
            entry['runs'].append(dict(case=label, input_sha256=sha(inp), expected_sha256=sha(data), output_sha256=sha(p.stdout), passed=True))
        report['applications'].append(entry)
    report.update(source_after_sha256=snapshot(ROOT), passed=True, application_case_count=len(datasets), scope='Independent suffix/LCP oracles and large closed forms; header/copied assert/NDEBUG core and three formal driver forms. Local checks, not OJ AC, timing ranking, full suite or LeakSanitizer.')
    assert before == report['source_after_sha256']
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('SAIS', mode, 'PASS:', out / 'report.json')


if __name__ == '__main__':
    main()
