#!/usr/bin/env python3
"""Exact cover: subset oracle, restoration and independent semantic output checks."""
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
    out = Path(tempfile.mkdtemp(prefix='exact-cover-' + mode + '-', dir=ROOT / 'build'))
    before = snapshot(ROOT)
    probe = (ROOT / 'tests/exact_cover_probe.cpp').read_text()
    core = next(x['code'] for x in extract_components(json.loads((ROOT / 'docs/catalog.json').read_text())) if x['symbol'] == 'ExactCover')
    headers = ['algorithm', 'cassert', 'climits', 'cstddef', 'iostream', 'optional', 'random', 'stdexcept', 'vector']
    prelude = ''.join('#include <' + x + '>\n' for x in headers) + 'using namespace std;\n'
    copied = prelude + core + '\n' + probe.replace('#include "../src/compact/exact_cover.hpp"', '')
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
    for form, source in [('header', '#include "' + str(ROOT / 'tests/exact_cover_probe.cpp') + '"\n'), ('copied', copied)]:
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
        ('lose-column-restore', 'uncover(c);\n                return true;', 'return true;'),
        ('lose-count-restore', 's[a[j].c]++;', '/* no count restore */'),
        ('retain-failed-row', 'ans.pop_back();', '/* keep failed row */'),
        ('reject-empty', 'if (!c) return true;', 'if (!c) return false;'),
        ('shift-row-id', 'ans.push_back(a[i].row);', 'ans.push_back(a[i].row + 1);'),
    ]
    for name, old, new in mutations:
        assert copied.count(old) == 1, name
        exe, entry = compile(name, copied.replace(old, new), ['-DNDEBUG'])
        p = subprocess.run([str(exe)], capture_output=True, env=env, timeout=180)
        assert p.returncode == 0 and not p.stderr and p.stdout == b'ORACLE_REJECT\n', (name, p.returncode, p.stdout, p.stderr[-1000:])
        (out / (name + '.out')).write_bytes(p.stdout)
        entry.update(output_sha256=sha(p.stdout), independent_oracle_rejected=True)
        report['mutants'].append(entry)
    rng = random.Random(4929)
    def possible(m, rows):
        masks = [sum(1 << c for c in row) for row in rows]
        reachable = {0}
        for mask in masks:
            reachable |= {a | mask for a in tuple(reachable) if not (a & mask)}
        return (1 << m) - 1 in reachable

    def valid(m, rows, output, want):
        if output.strip() == b'No Solution!':
            return not want
        try:
            ids = [int(x) - 1 for x in output.split()]
        except ValueError:
            return False
        if not want or len(set(ids)) != len(ids) or any(i < 0 or i >= len(rows) for i in ids):
            return False
        count = [0] * m
        for i in ids:
            for c in rows[i]:
                count[c] += 1
        return all(x == 1 for x in count)

    negatives = [(2, [[0], [1]], b'1', True), (2, [[0], [1]], b'1 1 2', True),
                 (2, [[0], [1]], b'0 2', True), (2, [[0], [1]], b'1 3', True),
                 (2, [[0], [1]], b'No Solution!', True),
                 (2, [[0, 1], [0]], b'1 2', True)]
    assert all(not valid(*case) for case in negatives)
    datasets = []
    for i in range(160):
        m, n = rng.randrange(1, 11), rng.randrange(1, 13)
        rows = [[c for c in range(m) if rng.randrange(3) == 0] for _ in range(n)]
        datasets.append((f'small-{i}', m, rows, possible(m, rows)))
    datasets += [('knuth', 7, [[2,4,5],[0,3,6],[1,2,5],[0,3],[1,6],[3,4,6]], True),
                 ('odd-cycle', 3, [[0,1],[1,2],[0,2]], False),
                 ('empty-rows', 2, [[],[1],[],[0],[1]], True),
                 ('maximum-identity', 500, [[i] for i in range(500)], True),
                 ('maximum-blocks', 500, [list(range(i//10*10, i//10*10+10)) for i in range(500)], True),
                 ('maximum-unsat', 500, [[i] for i in range(497)]+[[497,498],[498,499],[497,499]], False),
                 ('maximum-zero', 500, [[] for _ in range(500)], False)]
    # 4x4 Sudoku: independently decode selected assignments as a second model.
    for clues in [{}, {(0,0):0, (1,2):1}, {(0,0):0, (0,1):0}]:
        rows, assignments = [], []
        for r in range(4):
            for c in range(4):
                for v in range(4):
                    if (r,c) not in clues or clues[r,c] == v:
                        rows.append([4*r+c,16+4*r+v,32+4*c+v,48+4*(2*(r//2)+c//2)+v])
                        assignments.append((r,c,v))
        datasets.append(('sudoku-'+str(len(datasets)),64,rows,len(clues)<2 or (0,1) not in clues))
    row = next(r for r in records() if r['id'] == 'example-243')
    for name, text in [('driver', '#include "' + str(ROOT / row['driver']) + '"\n'), ('bundle', row['program']), ('minimal-copy', prelude + core + '\n' + row['snippet'])]:
        exe, entry = compile(name, text)
        entry['runs'] = []
        for label, m, rows, want in datasets:
            inp = (str(len(rows))+' '+str(m)+'\n'+'\n'.join(' '.join('1' if c in r else '0' for c in range(m)) for r in rows)+'\n').encode()
            p = subprocess.run([str(exe)], input=inp, capture_output=True, env=env, timeout=180)
            assert p.returncode == 0 and not p.stderr, (name, label, p.returncode, p.stderr[-1000:])
            assert valid(m, rows, p.stdout, want), (name, label, p.stdout)
            if label.startswith('sudoku-') and want:
                # Recover each assignment from its cell and row/value constraint.
                grid = [[-1]*4 for _ in range(4)]
                for token in p.stdout.split():
                    selected = rows[int(token)-1]
                    cell, value = selected[0], (selected[1]-16)%4
                    grid[cell//4][cell%4] = value
                assert all(set(r)==set(range(4)) for r in grid)
                assert all({grid[r][c] for r in range(4)}==set(range(4)) for c in range(4))
                assert all({grid[r+i][c+j] for i in range(2) for j in range(2)}==set(range(4)) for r in [0,2] for c in [0,2])
            (out / (label + '.in')).write_bytes(inp)
            (out / (name + '-' + label + '.out')).write_bytes(p.stdout)
            entry['runs'].append(dict(case=label, input_sha256=sha(inp), satisfiable=want, output_sha256=sha(p.stdout), passed=True))
        report['applications'].append(entry)
    report.update(source_after_sha256=snapshot(ROOT), passed=True, application_case_count=len(datasets), checker_negative_controls=len(negatives), scope='Independent subset exact-cover oracle, full link/count restoration, header/copied assert/NDEBUG and three formal driver forms. Local checks, not online AC, full suite or LeakSanitizer.')
    assert before == report['source_after_sha256']
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('ExactCover', mode, 'PASS:', out / 'report.json')


if __name__ == '__main__':
    main()
