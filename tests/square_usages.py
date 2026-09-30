"""Exact printed P1117 driver against direct A/B length enumeration."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import random
import subprocess
import sys
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records


def brute(s):
    n = len(s)
    answer = 0
    for i in range(n):
        for a in range(1, (n - i) // 2):
            j = i + 2 * a
            if s[i:i + a] != s[i + a:j]:
                continue
            for b in range(1, (n - j) // 2 + 1):
                if s[j:j + b] == s[j + b:j + 2 * b]:
                    answer += 1
    return answer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sanitizer', action='store_true')
    args = ap.parse_args()
    mode = 'sanitizer' if args.sanitizer else 'normal'
    folder = ROOT / 'build' / ('square-' + mode)
    folder.mkdir(parents=True, exist_ok=True)
    row = next(r for r in records() if r['id'] == 'example-186')
    source = folder / 'P1117.cpp'
    source.write_text(row['program'])
    flags = ['-O1', '-g', '-fsanitize=address,undefined'] if args.sanitizer else ['-O2']
    exe = folder / 'P1117'
    subprocess.run([CXX, '-std=c++20', *flags, str(source), '-o', str(exe)], check=True)
    groups = {}
    invocations = 0
    inputs = hashlib.sha256()
    outputs = hashlib.sha256()

    def run(cases, group, answers=None):
        nonlocal invocations
        groups[group] = len(cases)
        if answers is None:
            answers = [brute(s) for s in cases]
        for begin in range(0, len(cases), 10):
            batch = cases[begin:begin + 10]
            data = str(len(batch)) + '\n' + '\n'.join(batch) + '\n'
            p = subprocess.run([str(exe)], input=data, text=True, capture_output=True,
                               check=True, timeout=60)
            assert not p.stderr, p.stderr
            want = answers[begin:begin + 10]
            assert p.stdout == ''.join(str(x) + '\n' for x in want), (group, batch, p.stdout, want)
            inputs.update(data.encode())
            outputs.update(p.stdout.encode())
            invocations += 1

    run([''.join(s) for n in range(1, 11) for s in itertools.product('ab', repeat=n)],
        'exhaustive_binary_length_1_to_10')
    run([''.join(s) for n in range(1, 8) for s in itertools.product('abc', repeat=n)],
        'exhaustive_ternary_length_1_to_7')
    rng = random.Random(20260930)
    run([''.join(rng.choice('abcd') for _ in range(rng.randrange(1, 65))) for _ in range(500)],
        'random_length_1_to_64')
    run([('abc' * 25)[:n] for n in range(1, 75)] + [('aab' * 25)[:n] for n in range(1, 75)],
        'periodic_boundaries')
    n = 30000
    maximum = []
    expected = []
    for period in [1, 2, 3, 4, 5, 6, 7, 8, 9, 26]:
        word = 'abcdefghijklmnopqrstuvwxyz'[:period]
        maximum.append((word * (n // period + 1))[:n])
        # All letters in a period are distinct, so a square half-length is
        # precisely a positive multiple of period. Sum A/B lengths directly.
        expected.append(sum((t - 1) * (n - 2 * period * t + 1)
                            for t in range(2, n // (2 * period) + 1)))
    run(maximum, 'maximum_10_cases_each_length_30000', expected)
    report = dict(mode=mode, program_sha256=row['program_sha256'], groups=groups,
                  strings=sum(groups.values()), invocations=invocations,
                  input_sha256=inputs.hexdigest(), output_sha256=outputs.hexdigest(),
                  oracle='Direct substring A/B length enumeration; distinct-letter periodic closed sum for maximum cases',
                  scope='Independent local tests; no official full data, checker, or new online AC')
    (ROOT / 'verification' / ('square-usages-' + mode + '.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
