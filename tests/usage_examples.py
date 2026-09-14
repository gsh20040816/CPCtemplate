"""Compile the exact printed usage listings with their declared template context."""
from compiler_config import CXX
from pathlib import Path
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import records

cases = {
    'example-1': [('4 5 1 4\n1 2 3\n1 3 2\n2 3 1\n2 4 2\n3 4 4\n', '5'), ('2 3 1 2\n1 2 0\n1 2 7\n2 1 10\n', '7')],
    'example-2': [('3 3\n0 1\n1 2\n2 1\n', '2 1 0 2 1 2'), ('1 0\n', '1 1 0')],
    'example-3': [('p cnf 2 2\n1 1 0\n-2 -2 0\n', 's SATISFIABLE v 1 -2 0'), ('p cnf 1 2\n1 1 0\n-1 -1 0\n', 's UNSATISFIABLE')],
    'example-4': [('5 4\n1 2\n2 3\n3 1\n3 4\n', [(1, 2, 3), (3, 4), (5,)]), ('2 2\n1 2\n2 1\n', [(1, 2)])],
    'example-5': [('5 4\n1 2\n2 3\n3 1\n3 4\n', [(1, 2, 3), (4,), (5,)]), ('2 2\n1 2\n2 1\n', [(1, 2)])],
    'example-6': [('4 5\n1 2 3 4\n0 2\n2 3\n0 3\n1 2\n1 3\n', '36'), ('3 3\n998244352 998244352 998244352\n0 1\n1 2\n2 0\n', '998244352')],
    'example-7': [('5 7\n2 1 2\n1 1 2\n2 1 2\n1 3 4\n2 1 4\n1 2 3\n2 1 4\n', 'N Y N Y'), ('1 1\n2 1 1\n', 'Y')]
}
rows = records()
assert {r['id'] for r in rows} == set(cases), 'Every registered example needs execution cases'
proof = {}
for row in rows:
    assert (root / row['snippet_file']).read_text() == row['snippet'], 'Regenerate printed usage first'
    source = root / ('build/usage-' + row['id'] + '.cpp')
    source.write_text(row['program'])
    for mode in ['normal', 'sanitizer']:
        flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined']
        exe = root / ('build/usage-' + row['id'] + '-' + mode)
        subprocess.run([CXX, '-std=c++20', *flags, str(source), '-o', str(exe)], check=True)
        for data, expected in cases[row['id']]:
            run = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
            assert not run.stderr, run.stderr
            if isinstance(expected, str):
                assert run.stdout.split() == expected.split(), (row['id'], mode, run.stdout, expected)
            else:
                lines = run.stdout.splitlines()
                assert int(lines[0]) == len(lines) - 1
                actual = []
                for line in lines[1:]:
                    nums = list(map(int, line.split()))
                    assert nums[0] == len(nums) - 1
                    actual.append(tuple(sorted(nums[1:])))
                assert sorted(actual) == sorted(expected), (row['id'], mode, actual)
    proof[row['id']] = dict(program_sha256=row['program_sha256'], modes=['normal', 'sanitizer'],
                           cases_per_mode=len(cases[row['id']]), driver=row['driver'],
                           scope='Printed usage execution only; no new online AC or comprehensive algorithm proof')
(root / 'verification/usage-examples.json').write_text(json.dumps(proof, indent=2) + '\n')
print('Usage examples: seven exact printed main programs, fourteen input/output certificates in normal and ASan/UBSan modes PASS')
