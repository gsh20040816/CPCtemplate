#!/usr/bin/env python3
"""Audit complete kuangbin section 2.7; no copied source is installed in headers."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
build = root / 'build/phi-source-audit'
build.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pdf = root / 'build/source-audit/kuangbin.pdf'
assert sha(pdf) == 'f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad'
text = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], text=True)
start = text.index('     2.7   欧拉函数')
end = text.index('     2.8   高斯消元', start)
blocks = []
for part in re.split(r'2\.7\.[1-4][^\n]*\n', text[start:end])[1:]:
    lines = []
    for line in part.splitlines():
        match = re.match(r'\s*(\d+)\s+(.*)', line)
        if match:
            assert int(match[1]) == len(lines) + 1
            lines.append(match[2].replace('−', '-'))
    blocks.append('\n'.join(lines) + '\n')
assert [len(b.splitlines()) for b in blocks] == [5, 12, 12, 27]
for i, block in enumerate(blocks, 1):
    (build / f'original-{i}.cpp').write_text(block)
# The five-line fragment needs a factor supplier. This harness supplies exact
# trial factors; it does NOT pretend to test section 2.2's separate getFactors.
factor_prelude = r'''
long long factor[64][2];
int fatCnt;
void getFactors(long long n)
{
    fatCnt = 0;
    for (long long p = 2; p <= n / p; p++)
    {
        if (n % p) continue;
        factor[fatCnt][0] = p;
        factor[fatCnt][1] = 0;
        while (n % p == 0)
        {
            n /= p;
            factor[fatCnt][1]++;
        }
        fatCnt++;
    }
    if (n > 1)
    {
        factor[fatCnt][0] = n;
        factor[fatCnt][1] = 1;
        fatCnt++;
    }
}
long long run(long long n)
{
'''
originals = 'namespace source_factor {\n' + factor_prelude + blocks[0] + 'return ret;\n}\n}\n'
for name, block in zip(('sieve', 'single', 'linear'), blocks[1:]):
    originals += f'namespace source_{name} {{\n{block}}}\n'
sys.path.insert(0, str(root / 'tools'))
from audit_copy_context import extract_components
catalog = json.loads((root / 'docs/catalog.json').read_text())
order = ['Mod64', 'Prime64', 'PollardRho', 'LinearSieve', 'euler_phi']
# Catalog extraction returns each exact contest-copy component independently.
by_name = {r[1]: extract_components([r])[0]['code'] for r in catalog if r[1] in order}
copied = '\n'.join(by_name[n] for n in order)
prelude = '#include <bits/stdc++.h>\n#include <cassert>\nusing namespace std;\n'
harness = (root / 'tests/phi_source_audit.cpp').read_text()
report = {'source_pdf_sha256': sha(pdf), 'printed_pages': [32, 33],
          'physical_pages_visually_inspected': [34, 35], 'source_line_counts': [5, 12, 12, 27],
          'source_sha256': [sha(build / f'original-{i}.cpp') for i in range(1, 5)],
          'factor_dependency': 'Exact trial factor adapter; not upstream section 2.2 getFactors',
          'linear_table_entries': 10000000, 'divisor_identity_entries': 10000000,
          'eratosthenes_table_entries': 3000000, 'scalar_values': 20000,
          'gcd_count_values': 500, 'runs': []}
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for mode in ('normal', 'sanitizer'):
    flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=all']
    for form in ('header', 'ndebug', 'copied'):
        current = copied if form == 'copied' else f'#include "{root}/src/compact/euler_phi.hpp"\n'
        program = build / f'{mode}-{form}.cpp'
        program.write_text(prelude + current + originals + harness)
        exe = program.with_suffix('')
        command = [CXX, '-std=c++20', *flags]
        if form == 'ndebug':
            command.append('-DNDEBUG')
        subprocess.run(command + [str(program), '-o', str(exe)], check=True, capture_output=True, text=True)
        result = subprocess.run([str(exe)], capture_output=True, text=True, env=env, timeout=180)
        assert result.returncode == 0 and not result.stderr, result.stderr
        assert result.stdout.startswith('PASS:')
        report['runs'].append({'mode': mode, 'form': form, 'result': result.stdout.strip()})
        print(mode, form, 'PASS', flush=True)
probe = build / 'source-overflow.cpp'
probe.write_text(prelude + blocks[2] + '\nint main() { cout << eular(2147483647LL); }\n')
exe = probe.with_suffix('')
subprocess.run([CXX, '-std=c++20', '-O1', '-fsanitize=undefined', '-fno-sanitize-recover=all', str(probe), '-o', str(exe)], check=True)
result = subprocess.run([str(exe)], capture_output=True, text=True, env=env, timeout=10)
assert result.returncode != 0 and 'signed integer overflow' in result.stderr and '46341' in result.stderr, result.stderr
report['upstream_square_overflow'] = {'n': 2147483647, 'stderr': result.stderr, 'returncode': result.returncode}
report['upstream_narrow_accumulator'] = {'caller_n': 4294967296, 'observed_result': 0, 'correct_result': 2147483648,
    'scope': 'Outside int accumulator domain; observed compiler conversion, not claimed signed-overflow diagnostic'}
paths = ['tests/phi_source_audit.py', 'tests/phi_source_audit.cpp', 'src/compact/euler_phi.hpp',
         'src/compact/number_theory.hpp', 'src/compact/prime64.hpp', 'src/compact/mod64.hpp']
report['current_sha256'] = {p: sha(root / p) for p in paths}
(root / 'verification/phi-source-audit.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
print('source overflow detected; all comparisons PASS', flush=True)
