#!/usr/bin/env python3
"""Official-domain word-chain full-driver tests; separate from broader API tests.

Run normally, or with SANITIZE=1 / CPC_SANITIZE=1. The default registered
usage is example-217; its exact printed form is always included.
All products stay under build/word-chain-next unless --output is supplied.
"""
import argparse
import datetime
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'tools/usage_examples.py').is_file())
sys.dont_write_bytecode = True
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'tests')]
from compiler_config import CXX
from usage_examples import expand, records

SEED = 1044120261002
DRIVER = ROOT / 'verify/poj/2337.compact.cpp'
HEADERS = [ROOT / 'src/compact/directed_euler.hpp', ROOT / 'src/compact/word_chain.hpp']
sha = lambda data: hashlib.sha256(data).hexdigest()


def validate(words):
    assert 3 <= len(words) <= 1000
    assert len(set(words)) == len(words), 'Official domain requires distinct words'
    assert all(re.fullmatch('[a-z]{1,20}', word) for word in words)


def parse(data):
    tokens = iter(data.decode('ascii').split())
    cases = []
    for _ in range(int(next(tokens))):
        words = [next(tokens) for _ in range(int(next(tokens)))]
        validate(words)
        cases.append(words)
    assert next(tokens, None) is None
    return cases


def encode(cases):
    return (str(len(cases)) + '\n' + ''.join(str(len(w)) + '\n' + '\n'.join(w) + '\n' for w in cases)).encode('ascii')


def oracle(words):
    """Visit EVERY permutation; no graph, Euler, degree, or connectivity logic."""
    validate(words)
    assert len(words) <= 8
    best = None
    for perm in itertools.permutations(words):
        if all(left[-1] == right[0] for left, right in zip(perm, perm[1:])):
            dotted = '.'.join(perm)
            if best is None or dotted < best:
                best = dotted
    return best if best is not None else '***'


def small_cases():
    rng = random.Random(SEED)
    result = []
    # All subsets, including prefixes, disconnected endpoints, length 1 and 20.
    dictionary = ['a', 'aa', 'aaa', 'az', 'za', 'z', 'zz', 'zzz', 'a' * 20]
    for n in range(3, 9):
        for subset in itertools.combinations(dictionary, n):
            words = list(subset)
            rng.shuffle(words)
            result.append((f'subset-{n}-{len(result)}', words))
    regressions = [
        ['aab', 'aza', 'ba'], ['a', 'aa', 'aba'],
        ['ab', 'aca', 'ca'], ['aa', 'az', 'za', 'zz'],
        ['a' * 20, 'a' * 19 + 'z', 'z' * 19 + 'a', 'z' * 20],
    ]
    # The first two deliberately reuse existing regressions, not novel coverage.
    for i, words in enumerate(regressions):
        result.append((f'existing-style-regression-{i}', words))
    for n in range(3, 9):
        for trial in range(18):
            words = set()
            while len(words) < n:
                length = rng.choice([1, 2, 3, 5, 20])
                words.add(''.join(rng.choice('abcz') for _ in range(length)))
            result.append((f'arbitrary-{n}-{trial}', sorted(words)))
        for trial in range(12):
            # Construct a known chain, then shuffle. This generator is not the oracle.
            words = []
            endpoint = rng.choice('abcz')
            while len(words) < n:
                finish = rng.choice('abcz')
                length = rng.choice([2, 3, 5, 20])
                word = endpoint + ''.join(rng.choice('abcz') for _ in range(length - 2)) + finish
                if word in words:
                    continue
                words.append(word)
                endpoint = finish
            result.append((f'known-chain-{n}-{trial}', words))
    expanded = []
    for label, words in result:
        validate(words)
        answer = oracle(words)
        if label.startswith('known-chain'):
            assert answer != '***'
        expanded.append((label, words, answer))
        if not label.startswith('subset'):
            for i in range(2):
                shuffled = words[:]
                rng.shuffle(shuffled)
                # Explicitly recompute every permutation for each input ordering.
                assert oracle(shuffled) == answer
                expanded.append((f'{label}-shuffle-{i}', shuffled, answer))
    return expanded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', type=Path, default=ROOT / 'tests/fixtures/word-chain')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--usage', default='example-217', help='Require and also test this exact registered usage ID (default: example-217)')
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    assert args.usage, 'A registered usage ID is required'
    san = args.sanitize or os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1'
    mode = 'sanitizer' if san else 'normal'
    out = args.output or ROOT / 'build/word-chain-next' / mode
    out.mkdir(parents=True, exist_ok=True)
    tracked_sources = [DRIVER, *HEADERS, ROOT / 'tools/usage_examples.py', ROOT / 'tests/compiler_config.py']
    originals = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in tracked_sources}
    compiler_path = Path(shutil.which(CXX) or CXX).resolve()
    compiler_hash = sha(compiler_path.read_bytes())
    def registration_details(row):
        return {k: v for k, v in row.items() if k not in {'program', 'snippet'}}
    def registration_hash(details):
        return sha(json.dumps(details, sort_keys=True, separators=(',', ':')).encode())
    driver = DRIVER.read_text()
    exact_main = driver[driver.index('int main()'):]
    euler = HEADERS[0].read_text()
    euler = euler[euler.index('struct DirectedEuler'):].rstrip()
    chain = HEADERS[1].read_text().split('// BEGIN word_chain\n', 1)[1].split('// END word_chain', 1)[0].rstrip()
    programs = {
        'standalone': expand(driver, DRIVER.parent, set()),
        'minimal-copy': '#include <bits/stdc++.h>\nusing namespace std;\n\n' + euler + '\n\n' + chain + '\n\n' + exact_main,
    }
    usage_info = {'status': 'not_requested', 'note': 'Scratch minimal-copy is not claimed to be registered/printed example-217'}
    if args.usage:
        row = next(r for r in records() if r['id'] == args.usage)
        assert row['driver'] == str(DRIVER.relative_to(ROOT))
        assert row['snippet'] == exact_main
        programs['registered'] = row['program']
        details = registration_details(row)
        usage_info = {'status': 'requested', 'id': args.usage, 'program_sha256': row['program_sha256'],
                      'registration_details': details, 'registration_sha256': registration_hash(details)}
    fixture_paths = [args.fixtures / name for name in ['official-sample.in', 'official-sample.out', 'distinct-boundary.in', 'distinct-boundary.out', 'contract.json']]
    fixture_hashes = {p.name: sha(p.read_bytes()) for p in fixture_paths}
    script_hash = sha(Path(__file__).read_bytes())
    fixtures = []
    for name in ['official-sample', 'distinct-boundary']:
        data = (args.fixtures / (name + '.in')).read_bytes()
        expected = (args.fixtures / (name + '.out')).read_bytes()
        cases = parse(data)
        if name == 'official-sample':
            assert expected == ''.join(oracle(w) + '\n' for w in cases).encode('ascii')
        else:
            assert len(cases) == 3 and all(len(w) == 1000 for w in cases)
            a, b, c = cases
            assert all(len(w) == 20 and w[0] == w[-1] == 'a' for w in a)
            assert b.count('ab') == 1
            loops = [w for w in b if w != 'ab']
            assert all(len(w) == 20 and w[0] == w[-1] == 'a' for w in loops)
            assert 'ab' < min(loops)
            assert all(len(w) == 20 and w[0] == w[-1] and w[0] in 'az' for w in c)
            assert sum(w[0] == 'a' for w in c) == 500
            proof_expected = '.'.join(sorted(a)) + '\n' + '.'.join(sorted(loops) + ['ab']) + '\n***\n'
            assert expected == proof_expected.encode('ascii')
        fixtures.append((name, data, expected, len(cases)))
    small = small_cases()
    data = encode([w for _, w, _ in small])
    parse(data)
    expected = ''.join(answer + '\n' for _, _, answer in small).encode('ascii')
    fixtures.append(('distinct-full-permutations', data, expected, len(small)))
    (out / 'distinct-full-permutations.in').write_bytes(data)
    (out / 'distinct-full-permutations.out').write_bytes(expected)
    (out / 'case-labels.json').write_text(json.dumps([label for label, _, _ in small], indent=2) + '\n')
    flags = ['-std=c++20', '-O2'] if not san else ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    env = os.environ.copy()
    if san:
        existing = env.get('ASAN_OPTIONS', '').split(':')
        assert not any('quarantine' in option for option in existing), 'Default ASan quarantine required; no workaround'
        env['ASAN_OPTIONS'] = ':'.join([v for v in existing if v and not v.startswith(('detect_leaks=', 'halt_on_error='))] + ['detect_leaks=0', 'halt_on_error=1'])
        env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
    report = {
        'status': 'running', 'mode': mode, 'seed': SEED,
        'scope': 'Local official-domain full-driver evidence only; not online AC, speed ranking, broader API coverage, or leak detection',
        'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'script_sha256': script_hash, 'production_sources': originals, 'fixture_sources': fixture_hashes,
        'contract_sha256': fixture_hashes['contract.json'],
        'compiler': subprocess.check_output([CXX, '--version'], text=True),
        'compiler_executable': str(compiler_path), 'compiler_executable_sha256': compiler_hash, 'flags': flags,
        'fixture_process_invocations_per_form': len(fixtures), 'individual_cases_per_form': sum(f[3] for f in fixtures),
        'total_process_invocations': len(fixtures) * len(programs), 'total_case_executions': sum(f[3] for f in fixtures) * len(programs),
        'environment': {k: env.get(k) for k in ['ASAN_OPTIONS', 'UBSAN_OPTIONS']},
        'registered_form': usage_info, 'small_cases': len(small),
        'small_successes': sum(answer != '***' for _, _, answer in small),
        'small_failures': sum(answer == '***' for _, _, answer in small),
        'programs': {},
    }
    path = out / 'report.json'
    def save():
        path.write_text(json.dumps(report, indent=2) + '\n')
    save()
    try:
        for form, source in programs.items():
            cpp, exe = out / (form + '.cpp'), out / form
            cpp.write_text(source)
            subprocess.run([CXX, *flags, str(cpp), '-o', str(exe)], check=True)
            info = {'source_sha256': sha(cpp.read_bytes()), 'binary_sha256': sha(exe.read_bytes()), 'fixtures': []}
            report['programs'][form] = info
            for label, data, expected, count in fixtures:
                started = time.monotonic()
                result = subprocess.run([str(exe.resolve())], input=data, capture_output=True, env=env, timeout=60)
                (out / (form + '.' + label + '.actual')).write_bytes(result.stdout)
                item = {'label': label, 'cases': count, 'input_sha256': sha(data), 'expected_sha256': sha(expected),
                        'actual_sha256': sha(result.stdout), 'returncode': result.returncode,
                        'stderr': result.stderr.decode(errors='replace'), 'wall_seconds': round(time.monotonic() - started, 6)}
                info['fixtures'].append(item)
                save()
                assert result.returncode == 0 and not result.stderr and result.stdout == expected, (form, label, item)
        assert originals == {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in tracked_sources}
        assert sha(compiler_path.read_bytes()) == compiler_hash
        assert sha(Path(__file__).read_bytes()) == script_hash
        assert {p.name: sha(p.read_bytes()) for p in fixture_paths} == fixture_hashes
        if args.usage:
            current_row = next(r for r in records() if r['id'] == args.usage)
            assert current_row['program_sha256'] == usage_info['program_sha256']
            assert registration_hash(registration_details(current_row)) == usage_info['registration_sha256']
            usage_info['status'] = 'passed'
        report['status'] = 'passed'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = repr(error)
        raise
    finally:
        report['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save()
    print(f'Word chain {mode}: {len(small)} full-permutation distinct cases + 2 official sample + 3 distinct n=1000 per {list(programs)} (3 fixture processes and 1025 individual cases per form) PASS; {path}')


if __name__ == '__main__':
    main()
