#!/usr/bin/env python3
"""Minimum repeated cover: subset optimum, admissible bound and link restoration."""
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
    out = Path(tempfile.mkdtemp(prefix='minimum-cover-' + mode + '-', dir=ROOT / 'build'))
    before = snapshot(ROOT)
    probe = (ROOT / 'tests/minimum_cover_probe.cpp').read_text()
    core = next(x['code'] for x in extract_components(json.loads((ROOT / 'docs/catalog.json').read_text())) if x['symbol'] == 'MinimumCover')
    headers = ['algorithm', 'cassert', 'climits', 'cstddef', 'iostream', 'optional', 'random', 'stdexcept', 'numeric', 'vector']
    prelude = ''.join('#include <' + x + '>\n' for x in headers) + 'using namespace std;\n'
    copied = prelude + core + '\n' + probe.replace('#include "../src/compact/minimum_cover.hpp"', '')
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
    for form, source in [('header', '#include "' + str(ROOT / 'tests/minimum_cover_probe.cpp') + '"\n'), ('copied', copied)]:
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
        ('lose-restore', 'restore(i);', '/* no restore */'),
        ('retain-row', 'path.pop_back();', '/* keep failed row */'),
        ('shift-row-id', 'path.push_back(a[i].row);', 'path.push_back(a[i].row + 1);'),
        ('overestimate', 'return bound;', 'return bound + 1;'),
        ('first-solution', 'if (lower_bound() >= best - depth) return;', 'if (best <= m || lower_bound() >= best - depth) return;'),
    ]
    for name, old, new in mutations:
        assert copied.count(old) == 1, name
        exe, entry = compile(name, copied.replace(old, new), ['-DNDEBUG'])
        p = subprocess.run([str(exe)], capture_output=True, env=env, timeout=180)
        assert p.returncode == 0 and not p.stderr and p.stdout == b'ORACLE_REJECT\n', (name, p.returncode, p.stdout, p.stderr[-1000:])
        (out / (name + '.out')).write_bytes(p.stdout)
        entry.update(output_sha256=sha(p.stdout), independent_oracle_rejected=True)
        report['mutants'].append(entry)
    rng = random.Random(5122026)
    def optimum(m, rows):
        costs = {0: 0}
        for row in rows:
            mask = sum(1 << c for c in row)
            for covered, cost in tuple(costs.items()):
                union = covered | mask
                costs[union] = min(costs.get(union, len(rows) + 1), cost + 1)
        return costs.get((1 << m) - 1, -1)

    def valid(m, rows, output, want):
        try:
            tokens = [int(x) for x in output.split()]
        except ValueError:
            return False
        if want < 0:
            return tokens == [-1]
        if not tokens or tokens[0] != want or len(tokens) != want + 1:
            return False
        ids = tokens[1:]
        return (len(set(ids)) == len(ids) and all(0 <= i < len(rows) for i in ids)
                and {c for i in ids for c in rows[i]} == set(range(m)))

    negatives = [(2, [[0], [1]], b'1 0', 2), (2, [[0], [1]], b'2 0 0', 2),
                 (2, [[0], [1]], b'2 0 2', 2), (2, [[0,1]], b'-1', 1),
                 (2, [[0,1],[0]], b'2 0 1', 1), (2, [[0]], b'1 0', -1)]
    assert all(not valid(*case) for case in negatives)
    datasets = []
    for i in range(200):
        m, n = rng.randrange(11), rng.randrange(13)
        rows = [[c for c in range(m) if rng.randrange(3) == 0] for _ in range(n)]
        datasets.append((f'small-{i}', m, rows, optimum(m, rows)))
    datasets += [('overlap-required', 3, [[0,1],[1,2],[0,2]], 2),
                 ('greedy-trap', 6, [[0,1,2,3],[0,1,4],[2,3,5]], 2),
                 ('empty-rows', 2, [[],[1],[],[0],[1]], 2),
                 ('empty-universe', 0, [[],[]], 0),
                 ('deep-identity', 500, [[i] for i in range(500)], 500),
                 ('blocks-5000', 500, [list(range(i//10*10, i//10*10+10)) for i in range(500)], 50),
                 ('uncovered-column', 500, [[i] for i in range(499)], -1),
                 ('all-overlap', 500, [list(range(500)) for _ in range(500)], 1)]
    row = next(r for r in records() if r['id'] == 'example-244')
    for name, text in [('driver', '#include "' + str(ROOT / row['driver']) + '"\n'), ('bundle', row['program']), ('minimal-copy', prelude + core + '\n' + row['snippet'])]:
        exe, entry = compile(name, text)
        entry['runs'] = []
        for label, m, rows, want in datasets:
            inp = (str(len(rows))+' '+str(m)+'\n'+'\n'.join(str(len(r))+' '+ ' '.join(map(str,r)) for r in rows)+'\n').encode()
            p = subprocess.run([str(exe)], input=inp, capture_output=True, env=env, timeout=180)
            assert p.returncode == 0 and not p.stderr, (name, label, p.returncode, p.stderr[-1000:])
            assert valid(m, rows, p.stdout, want), (name, label, p.stdout)
            (out / (label + '.in')).write_bytes(inp)
            (out / (name + '-' + label + '.out')).write_bytes(p.stdout)
            entry['runs'].append(dict(case=label, input_sha256=sha(inp), minimum_rows=want, output_sha256=sha(p.stdout), passed=True))
        report['applications'].append(entry)
    report.update(source_after_sha256=snapshot(ROOT), passed=True, application_case_count=len(datasets), checker_negative_controls=len(negatives), scope='Independent subset optimum oracle, initial/residual admissible bound, full link/count restoration, header/copied assert/NDEBUG and three API demonstration forms. Local checks, not online AC, full suite or LeakSanitizer.')
    assert before == report['source_after_sha256']
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('MinimumCover', mode, 'PASS:', out / 'report.json')


if __name__ == '__main__':
    main()
