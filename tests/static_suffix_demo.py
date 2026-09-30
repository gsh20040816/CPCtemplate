"""Synthetic static-suffix API programs versus direct string oracles; no OJ claim."""
from compiler_config import CXX
from pathlib import Path
from collections import Counter
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
import itertools
import json
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import usage_examples
from template_dependencies import code_tokens


def oracle(s, query):
    op, *args = query
    if op == 0:
        x, y = args
        answer = 0
        while x + answer < len(s) and y + answer < len(s) and s[x + answer] == s[y + answer]:
            answer += 1
        return answer
    if op == 1:
        l1, r1, l2, r2 = args
        a, b = s[l1:r1], s[l2:r2]
        return (a > b) - (a < b)
    assert op == 2
    x, y = args
    answer = 0
    while answer < min(x, y) and s[x - answer - 1] == s[y - answer - 1]:
        answer += 1
    return answer


def all_queries(n):
    intervals = [(l, r) for l in range(n + 1) for r in range(l, n + 1)]
    return ([(op, x, y) for op in (0, 2) for x in range(n + 1) for y in range(n + 1)] +
            [(1, l1, r1, l2, r2) for l1, r1 in intervals for l2, r2 in intervals])


def random_queries(n, count, rng):
    queries = []
    for i in range(count):
        op = i % 3
        if op == 1:
            l1, r1 = sorted([rng.randrange(n + 1), rng.randrange(n + 1)])
            l2, r2 = sorted([rng.randrange(n + 1), rng.randrange(n + 1)])
            queries.append((op, l1, r1, l2, r2))
        else:
            queries.append((op, rng.randrange(n + 1), rng.randrange(n + 1)))
    return queries


def check_schema(work):
    """Run the real generator against isolated fixtures, never repository outputs."""
    original_root, original_records = usage_examples.ROOT, usage_examples.records
    checks = 0
    try:
        with tempfile.TemporaryDirectory(prefix='schema-', dir=work) as temp:
            base = Path(temp)
            (base / 'docs').mkdir()
            (base / 'verification').mkdir()
            (base / 'docs/catalog.json').write_text(json.dumps([['test', 'Test', 'Test', '']]))
            usage_examples.ROOT = base
            for mask in range(8):
                rows = []
                for i, kind in enumerate(('template', 'application', 'api')):
                    if mask >> i & 1:
                        row = dict(id=kind, symbol='Test', requires=['Test'], snippet='int main() {}\n',
                                   snippet_file='docs/usage/' + kind + '.cpp', program_sha256=kind)
                        if kind != 'template':  # Omission must retain the legacy default.
                            row['kind'] = kind
                        rows.append(row)
                usage_examples.records = lambda: rows
                proof = {r['id']: dict(program_sha256=r['program_sha256'], modes=['normal', 'sanitizer'])
                         for r in rows}
                for evidence in ('current', 'missing_mode', 'stale_hash'):
                    if rows and evidence == 'missing_mode':
                        proof[rows[-1]['id']]['modes'] = ['normal']
                    if rows and evidence == 'stale_hash':
                        proof[rows[-1]['id']]['modes'] = ['normal', 'sanitizer']
                        proof[rows[-1]['id']]['program_sha256'] = 'stale'
                    (base / 'verification/usage-examples.json').write_text(json.dumps(proof))
                    with redirect_stdout(io.StringIO()):
                        usage_examples.generate()
                    actual = json.loads((base / 'docs/usage-coverage.json').read_text())[0]['status']
                    expected = ('locally_checked_example' if mask & 1 else
                                'locally_checked_application' if mask & 2 else 'locally_checked_api')
                    if not rows:
                        expected = 'pending_example'
                    elif evidence != 'current':
                        expected = 'generated_unverified'
                    assert actual == expected, (mask, evidence, actual, expected)
                    if mask & 4:
                        assert '[api（接口演示）]' in (base / 'docs/USAGE-COVERAGE.md').read_text()
                    checks += 1
            usage_examples.records = original_records
            (base / 'docs/usage-examples.json').write_text(json.dumps([dict(id='bad-kind', kind='API')]))
            try:
                usage_examples.records()
            except AssertionError as error:
                assert 'Unknown usage kind' in str(error)
            else:
                raise AssertionError('An unknown usage kind was accepted')
            checks += 1
    finally:
        usage_examples.ROOT, usage_examples.records = original_root, original_records
    return checks


def named_program(row):
    """Copy just the declared definitions in order, without their inclusive headers."""
    catalog = json.loads((ROOT / 'docs/catalog.json').read_text())
    files = {symbol: file for file, symbol, _, _ in catalog}
    assert row['requires'] == ['SuffixArray', 'SuffixLCP', 'prefix_lcs']
    copied, known = [], set()
    for symbol in row['requires']:
        text = (ROOT / 'src/compact' / (files[symbol] + '.hpp')).read_text()
        marker = '// BEGIN ' + symbol + '\n'
        if marker in text:
            code = text.split(marker, 1)[1].split('// END ' + symbol, 1)[0]
        else:
            match = re.search(r'^struct ' + re.escape(symbol) + r'\n\{.*?^\};', text, re.M | re.S)
            assert match, symbol
            code = match[0] + '\n'
        assert (code_tokens(code) & set(files)) - {symbol} <= known, ('Missing earlier dependency', symbol)
        copied.append(code)
        known.add(symbol)
    return '#include <bits/stdc++.h>\nusing namespace std;\n' + '\n'.join(copied) + row['snippet']


def main():
    assert __debug__, 'Assertions must remain enabled'
    mode = 'sanitizer' if os.getenv('CPC_SANITIZE') == '1' else 'normal'
    work = ROOT / 'build' / ('static-suffix-demo-' + mode)
    work.mkdir(parents=True, exist_ok=True)
    paths = ['docs/usage-examples.json', 'docs/catalog.json', 'docs/usage-drivers/static-suffix-demo.cpp',
             'src/compact/string.hpp', 'src/compact/suffix_lcp.hpp', 'tests/static_suffix_demo.py',
             'tests/usage_examples.py', 'tests/compiler_config.py', 'tools/usage_examples.py',
             'tools/template_dependencies.py', 'tools/book.py']

    def hashes():
        return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}

    source_hashes = hashes()
    schema_checks = check_schema(work)
    row = next(r for r in usage_examples.records() if r['id'] == 'example-205')
    assert row['kind'] == 'api' and row['also_covers'] == ['prefix_lcs']
    assert not Path(row['driver']).is_relative_to('verify')
    programs = {'registered': row['program'], 'named_dependencies': named_program(row)}
    compiler = Path(shutil.which(CXX)).resolve()
    flags = ['-std=c++20', '-Wall', '-Wextra', '-O2']
    if mode == 'sanitizer':
        flags += ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    env = os.environ.copy()
    env['ASAN_OPTIONS'] = env.get('ASAN_OPTIONS', '') + ':detect_leaks=0:halt_on_error=1'
    env['UBSAN_OPTIONS'] = env.get('UBSAN_OPTIONS', '') + ':halt_on_error=1'
    commands = {}
    for name, program in programs.items():
        source = work / (name + '.cpp')
        source.write_text(program)
        commands[name] = [str(compiler), *flags, str(source), '-o', str(work / name)]
        subprocess.run(commands[name], check=True, cwd=ROOT)
    groups, queries_by_group = Counter(), Counter()
    inputs, outputs = hashlib.sha256(), hashlib.sha256()
    maximum_n = maximum_q = 0

    def run(s, queries, group):
        nonlocal maximum_n, maximum_q
        assert len(s) <= 200000 and len(queries) <= 200000
        data = f'{len(s)} {len(queries)}\n{s}\n' + ''.join(' '.join(map(str, q)) + '\n' for q in queries)
        # A repeated maximum-scale query is still independently scanned once;
        # caching oracle answers avoids O(n*q) Python work on periodic strings.
        answers = {query: oracle(s, query) for query in set(queries)}
        expected = ''.join(str(answers[q]) + '\n' for q in queries)
        for name in programs:
            p = subprocess.run([str(work / name)], input=data, text=True, capture_output=True,
                               env=env, check=True, timeout=120)
            assert not p.stderr, p.stderr
            assert p.stdout == expected, (name, group, s[:100], p.stdout[:300], expected[:300])
        inputs.update(data.encode())
        outputs.update(expected.encode())
        groups[group] += 1
        queries_by_group[group] += len(queries)
        maximum_n, maximum_q = max(maximum_n, len(s)), max(maximum_q, len(queries))

    for n in range(6):
        queries = all_queries(n)
        for chars in itertools.product('ab', repeat=n):
            run(''.join(chars), queries, 'exhaustive_binary_length_0_to_5_all_queries')
    for s in ['', 'a', 'ababb', 'banana', 'abcdefghijklmnopqrstuvwxyz']:
        run(s, [], 'zero_queries')
        if len(s) <= 6:
            run(s, all_queries(len(s)), 'explicit_boundary_and_reversal')
    assert oracle('ababb', (2, 2, 5)) == 1
    rng = random.Random(20260930)
    for _ in range(200):
        s = ''.join(rng.choice('abcdez') for _ in range(rng.randrange(81)))
        run(s, random_queries(len(s), 150, rng), 'seeded_random_length_0_to_80')
    for power in range(1, 11):
        for n in [2**power - 1, 2**power, 2**power + 1]:
            s = ('abac' * ((n + 3) // 4))[:n]
            run(s, random_queries(n, 100, rng), 'power_of_two_boundaries')
    n = 200000
    points = [0, 1, 2, 3, n // 2, n - 3, n - 2, n - 1, n]
    pool = [(op, x, y) for op in (0, 2) for x in points for y in points]
    intervals = [(0, 0), (n, n), (0, n), (1, n), (0, n - 1), (0, 1), (n - 1, n),
                 (n // 2, n // 2), (0, n // 2), (n // 2, n)]
    pool += [(1, l1, r1, l2, r2) for l1, r1 in intervals for l2, r2 in intervals]
    queries = [pool[i % len(pool)] for i in range(n)]
    run('a' * n, queries, 'maximum_equal_repeated_boundary_pool')
    run('ab' * (n // 2), queries, 'maximum_periodic_repeated_boundary_pool')
    s = ''.join(rng.choice('abcdez') for _ in range(n))
    run(s, random_queries(n, n, rng), 'maximum_seeded_random')
    assert hashes() == source_hashes, 'Test inputs changed during execution; discard this run'
    report = dict(
        checked_at=datetime.now(timezone.utc).isoformat(), mode=mode, kind='api', example=row['id'],
        driver=row['driver'], program_sha256=row['program_sha256'],
        named_dependencies_sha256=hashlib.sha256(programs['named_dependencies'].encode()).hexdigest(),
        source_sha256=source_hashes, input_sha256=inputs.hexdigest(), output_sha256=outputs.hexdigest(),
        compiler=str(compiler), compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),
        compiler_version=subprocess.check_output([str(compiler), '--version'], text=True).splitlines()[0],
        platform=platform.platform(), compile_commands=commands, groups=dict(groups),
        queries_by_group=dict(queries_by_group), cases_per_program=sum(groups.values()),
        queries_per_program=sum(queries_by_group.values()), maximum_n=maximum_n, maximum_q=maximum_q,
        schema_checks=schema_checks, asan_options=env['ASAN_OPTIONS'], ubsan_options=env['UBSAN_OPTIONS'],
        oracle='Direct character scans for LCP/LCS and Python substring lexicographic comparison; '
               'memoize duplicate queries in each dataset',
        scope='Exact registered program and declared dependency-only copy, local API demonstration only; '
              'chosen maximum-scale cases, not official full data, online AC, or performance ranking; '
              'LeakSanitizer disabled')
    (work / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"Static suffix demo {mode}: {report['cases_per_program']} datasets / "
          f"{report['queries_per_program']} queries per program, two program forms, "
          f"{schema_checks} schema checks PASS; report: {work.relative_to(ROOT) / 'report.json'}")


if __name__ == '__main__':
    main()
