"""Current vector core regression, plus arbitrary precision geometric reference."""
from compiler_config import CXX
from pathlib import Path
import hashlib
import json
import random
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import expand

names = ['divisor_sum', 'carmichael', 'kth_residue', 'prime_power_roots',
         'composite_roots', 'root_factors']

def oracle(a, n, mod):
    def mul(x, y):
        return [[sum(x[i][k] * y[k][j] for k in range(2)) % mod
                 for j in range(2)] for i in range(2)]
    b = [[a % mod, 1 % mod], [0, 1 % mod]]
    r = [[1 % mod, 0], [0, 1 % mod]]
    while n:
        if n & 1:
            r = mul(r, b)
        b = mul(b, b)
        n //= 2
    return r[0]

rng = random.Random(15932026)
maximum = (1 << 64) - 1
cases = [(a, n, m) for a in [0, 1, maximum]
         for n in [0, 1, 2, 1 << 64, (1 << 128) - 1]
         for m in [1, 2, 6, 9901, maximum - 1, maximum]]
cases += [(rng.getrandbits(64), rng.getrandbits(128), rng.randrange(1, 1 << 64))
          for _ in range(2000)]
data = ''.join(f'{a} {n >> 64} {n & maximum} {m}\n' for a, n, m in cases)
expected = [oracle(*c) for c in cases]
report = {'scope': 'current vector cores; local independent oracles, no online AC',
          'compiler': CXX, 'core': [], 'geometric_cases': len(cases)}
for mode in ['normal', 'sanitizer']:
    flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    for name in names + ['power_sum_probe']:
        source = root / f'tests/{name}.cpp'
        program = expand(source.read_text(), source.parent, set())
        exe = root / f'build/math-current-{name}-{mode}'
        subprocess.run([CXX, '-std=c++20', *flags, str(source), '-o', str(exe)], check=True)
        start = time.monotonic()
        result = subprocess.run([str(exe)], input=data if name == 'power_sum_probe' else '',
                                text=True, capture_output=True, check=True, timeout=240)
        assert not result.stderr, result.stderr
        if name == 'power_sum_probe':
            assert [list(map(int, line.split())) for line in result.stdout.splitlines()] == expected
            message = f'{len(cases)} Python arbitrary-precision matrix cases PASS\n'
        else:
            assert 'PASS' in result.stdout
            message = result.stdout
        output = root / f'verification/math-current-{name}-{mode}.txt'
        output.write_text(message)
        report['core'].append({'name': name, 'mode': mode, 'flags': flags,
                              'expanded_source_sha256': hashlib.sha256(program.encode()).hexdigest(),
                              'report_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                              'seconds': round(time.monotonic() - start, 4)})
        print(mode, name, message.strip(), flush=True)
report['test_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(root / 'verification/math-current-core.json').write_text(json.dumps(report, indent=2) + '\n')
