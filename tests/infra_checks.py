import hashlib
import json
import os
import platform
import random
import subprocess
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
work = root / 'build/infra-checks'
work.mkdir(parents=True, exist_ok=True)
source = root / 'examples/infra'
records = []
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1')

def compile_file(name, flags, ok=True):
    exe = work / name
    cmd = [CXX, '-Wall', '-Wextra', *flags, str(source / (name + '.cpp')), '-o', str(exe)]
    p = subprocess.run(cmd, text=True, capture_output=True, timeout=120)
    assert (p.returncode == 0) == ok, (cmd, p.stderr)
    records.append(dict(command=cmd, returncode=p.returncode, stderr=p.stderr))
    return exe, p.stderr

def run(exe, args=(), data='', expected=None, error=None):
    p = subprocess.run([str(exe), *args], input=data, text=True,
                       capture_output=True, env=env, timeout=20)
    records.append(dict(command=[str(exe), *args], returncode=p.returncode,
                        stdout=p.stdout[:2000], stderr=p.stderr[:6000]))
    if error:
        assert p.returncode != 0 and error in p.stderr, p
    else:
        assert p.returncode == 0, p.stderr
        if expected is not None:
            assert p.stdout == expected, (p.stdout[:200], expected[:200])
    return p

rng = random.Random(17)
values = [0, 1, -1, -(1 << 127), (1 << 127) - 1]
values += [rng.randrange(-(1 << 127), 1 << 127) for _ in range(3000)]
tokens = list(map(str, values)) + ['+0', '-0000', '+0012', '-0012', '+', '-', '12x',
                                  str(1 << 127), str(-(1 << 127) - 1), '9' * 500]
answers = list(map(str, values)) + ['0', '0', '12', '-12'] + ['invalid'] * 6
input_data = '\n'.join(tokens) + '\n'
expected = '\n'.join(answers) + '\n'
for standard in ['c++20', 'gnu++20']:
    for opts in [['-O2'], ['-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=all']]:
        exe, _ = compile_file('int128_io', ['-std=' + standard, *opts])
        run(exe, data=input_data, expected=expected)
    exe, _ = compile_file('type_probe', ['-std=' + standard, '-O2'])
    result = run(exe)
    assert result.stdout.splitlines() == ['202002', '1' if standard == 'c++20' else '0', '16', '1', '127']
    exe, _ = compile_file('gnu_bits', ['-std=' + standard, '-O2'])
    run(exe, expected='0\n64\n129\n')
compile_file('int128_io', ['-std=c++20', '-pedantic-errors', '-O2'], ok=False)

parse_driver = work / 'parse_contract.cpp'
parse_driver.write_text((source / 'int128_io.cpp').read_text().split('int main()')[0] +
    '#include <cassert>\nint main() {\n    i128 x = 23;\n' +
    '    for (string s : {"", "+", "-", "a", "12x", "170141183460469231731687303715884105728"}) {\n' +
    '        assert(!parse128(s, x));\n        assert(x == 23);\n    }\n}\n')
parse_exe = work / 'parse_contract'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=address,undefined',
                '-fno-sanitize-recover=all', str(parse_driver), '-o', str(parse_exe)], check=True, timeout=120)
run(parse_exe)


# Exhaustive small masks and each 64-bit position against a shift-loop oracle.
driver = work / 'bits_check.cpp'
driver.write_text('#define main printed_main\n#include "' + str(source / 'gnu_bits.cpp') +
'''"
#undef main
int main() {
    for (uint64_t x = 0; x < 65536; x++) {
        vector<int> expected;
        for (int k = 0; k < 64; k++) {
            if ((x >> k) & 1) {
                expected.push_back(k);
            }
        }
        assert(positions(x) == expected);
    }
    for (int k = 0; k < 64; k++) {
        assert(positions(1ULL << k) == vector<int>{k});
    }
    bitset<130> b;
    for (size_t k = 0; k < b.size(); k++) {
        b.reset();
        b.set(k);
        assert(b._Find_first() == k);
        assert(b._Find_next(k) == b.size());
    }
}
''')
exe = work / 'bits_check'
cmd = [CXX, '-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', str(driver), '-o', str(exe)]
subprocess.run(cmd, check=True, timeout=120)
run(exe)

for mode, flags, signature in [
    ('1', ['-fsanitize=undefined', '-fno-sanitize-recover=all'], 'signed integer overflow'),
    ('2', ['-fsanitize=address'], 'heap-buffer-overflow'),
    ('3', ['-D_GLIBCXX_ASSERTIONS'], '__n < this->size()'),
    ('4', ['-D_GLIBCXX_DEBUG'], 'singular iterator'),
]:
    exe, _ = compile_file('diagnostics', ['-std=c++23', '-O1', '-g', *flags])
    run(exe, args=[mode], error=signature)
_, warnings = compile_file('warnings', ['-std=c++23', '-O2', '-Wshadow', '-Wconversion'])
for flag in ['-Wshadow', '-Wfloat-conversion', '-Wformat=', '-Wunused-variable']:
    assert flag in warnings, warnings
files = [source / (x + '.cpp') for x in ['int128_io', 'type_probe', 'gnu_bits', 'diagnostics', 'warnings']]
files += [Path(__file__), driver, parse_driver]
report = dict(status='pass', platform=platform.platform(),
              compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0],
              integer_tokens=len(tokens), integer_input_sha256=hashlib.sha256(input_data.encode()).hexdigest(),
              records=records, source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
              scope='GNU GCC host behavior in strict and GNU C++20; printed warning fixture compile-only; four intentionally faulty cases run only under matching checkers. Not a full-library correctness claim.')
(root / 'verification/infra-checks.json').write_text(json.dumps(report, indent=2) + '\n')
print('PASS int128 boundaries/3000 random tokens, GNU bits, mode probes, four diagnostics and warnings')
