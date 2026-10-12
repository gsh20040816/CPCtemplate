"""Compile only the displayed prerequisite slices and usage bodies."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
out = root / 'build/matrix-apps'
number = (root / 'src/compact/number_theory.hpp').read_text()
modint = number[number.index('template <int mod> struct ModInt'):number.index('template <int mod> struct Binomial')]
det = (root / 'src/compact/det_prime.hpp').read_text().split('// BEGIN det_prime\n')[1].split('// END det_prime')[0]
tree = (root / 'src/compact/matrix_tree.hpp').read_text().split('template <int mod> struct MatrixTree')[1]
tree = 'template <int mod> struct MatrixTree' + tree
cases = {
    '427': [('3\n2\n1 2\n2 3\n2\n1 2\n2 3\n', '2'), ('2\n0\n', '0'), ('2\n1\n1 2\n', '1')],
    '428': [('3 2\n2 1\n3 2\n', '1'), ('3 2\n1 2\n2 3\n', '0'), ('1 0\n', '1'), ('2 3\n2 1\n2 1\n2 2\n', '1')]
}
results = {}
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for ident, data in cases.items():
    code = '#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'
    code += modint + det + (tree if ident == '428' else '')
    code += (root / f'docs/usage/example-{ident}.cpp').read_text()
    src = out / f'copied-{ident}.cpp'
    src.write_text(code)
    for mode in ['normal', 'sanitizer']:
        flags = ['-O2'] if mode == 'normal' else ['-O1', '-fsanitize=address,undefined']
        exe = out / f'copied-{ident}-{mode}'
        subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
        for text, expected in data:
            r = subprocess.run([str(exe)], input=text, text=True, capture_output=True, check=True, env=env)
            assert not r.stderr and r.stdout.split() == [expected], r
    results[ident] = {'modes': ['normal', 'sanitizer'], 'cases_per_mode': len(data),
                      'copied_program_sha256': hashlib.sha256(code.encode()).hexdigest()}
(root / 'verification/matrix-apps-copy.json').write_text(json.dumps(results, indent=2) + '\n')
print('Minimal printed dependencies and usages: PASS')
