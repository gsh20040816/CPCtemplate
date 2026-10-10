import hashlib
import json
import platform
import random
import statistics
import subprocess
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
source = root / 'examples/infra'
work = root / 'build/infra-performance'
work.mkdir(parents=True, exist_ok=True)
flags = ['-std=c++23', '-O2', '-Wall', '-Wextra']
commands = []
for name in ['performance', 'performance_io', 'performance_reuse', 'pragma_scope']:
    cmd = [CXX, *flags, str(source / (name + '.cpp')), '-o', str(work / name)]
    subprocess.run(cmd, check=True, timeout=120)
    commands.append(cmd)
assert subprocess.check_output([str(work / 'pragma_scope')], text=True) == '6\n'

n = 2048 ** 2
q, r = divmod(n, 1009)
expected = q * 1008 * 1009 // 2 + r * (r - 1) // 2
modes = ['grow', 'reserve', 'copy', 'reference', 'move', 'row', 'column']
samples = {m: [] for m in modes}
rng = random.Random(17)
order = []
for repeat in range(9):
    trial = modes.copy()
    rng.shuffle(trial)
    order.append(trial)
    for mode in trial:
        p = subprocess.run([str(work / 'performance'), mode, str(n)], capture_output=True,
                           text=True, check=True, timeout=30)
        checksum, ms = p.stdout.split()
        assert int(checksum) == expected
        samples[mode].append(float(ms))
    print('performance repetition', repeat + 1, flush=True)

io_path = work / 'input.txt'
io_count = 1000000
io_path.write_text(''.join(str(i % 1009) + '\n' for i in range(io_count)))
q, r = divmod(io_count, 1009)
io_expected = q * 1008 * 1009 // 2 + r * (r - 1) // 2
for mode in ['default', 'fast']:
    samples['io_' + mode] = []
for repeat in range(9):
    for mode in (['default', 'fast'] if repeat % 2 == 0 else ['fast', 'default']):
        with io_path.open() as data:
            p = subprocess.run([str(work / 'performance_io'), mode], stdin=data,
                               capture_output=True, text=True, check=True, timeout=30)
        checksum, ms = p.stdout.split()
        assert int(checksum) == io_expected
        samples['io_' + mode].append(float(ms))

for mode in ['fresh', 'reuse']:
    samples['allocation_' + mode] = []
for repeat in range(9):
    for mode in (['fresh', 'reuse'] if repeat % 2 == 0 else ['reuse', 'fresh']):
        p = subprocess.run([str(work / 'performance_reuse'), mode], capture_output=True,
                           text=True, check=True, timeout=30)
        checksum, ms = p.stdout.split()
        assert int(checksum) == 2048 * 4095 * 4096 // 2
        samples['allocation_' + mode].append(float(ms))

math_results = {}
for opt in ['-O2', '-O3', '-Ofast']:
    exe = work / ('fast_math_' + opt[1:])
    cmd = [CXX, '-std=c++23', opt, str(source / 'fast_math.cpp'), '-o', str(exe)]
    subprocess.run(cmd, check=True, timeout=120)
    commands.append(cmd)
    p = subprocess.run([str(exe)], input='10000000000000000 1\n', text=True,
                       capture_output=True, check=True, timeout=10)
    math_results[opt] = p.stdout.strip()
assert math_results['-O2'] == '0' and math_results['-Ofast'] == '1', math_results
option_samples = {}
for label, option in [('O2', ['-O2']), ('O3', ['-O3']), ('O2_unroll', ['-O2', '-funroll-loops'])]:
    exe = work / ('performance_' + label)
    cmd = [CXX, '-std=c++23', *option, str(source / 'performance.cpp'), '-o', str(exe)]
    subprocess.run(cmd, check=True, timeout=120)
    commands.append(cmd)
    option_samples[label] = []
# Interleave option runs to avoid running all samples of one option first.
for repeat in range(9):
    labels = list(option_samples)
    rng.shuffle(labels)
    for label in labels:
        p = subprocess.run([str(work / ('performance_' + label)), 'row', str(n)],
                           capture_output=True, text=True, check=True, timeout=30)
        checksum, ms = p.stdout.split()
        assert int(checksum) == expected
        option_samples[label].append(float(ms))
pragma_results = {}
for before in [False, True]:
    exe = work / ('include_before' if before else 'include_after')
    cmd = [CXX, '-std=c++23', '-O2', *(['-DBEFORE_HEADER'] if before else []),
           str(source / 'pragma_include.cpp'), '-o', str(exe)]
    subprocess.run(cmd, check=True, timeout=120)
    commands.append(cmd)
    p = subprocess.run([str(exe)], input='10000000000000000 1\n', text=True,
                       capture_output=True, check=True, timeout=10)
    assert p.stdout == ('1 1 0\n' if before else '0 1 0\n'), p.stdout
    pragma_results['before' if before else 'after'] = p.stdout.strip()
cpu = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string'], text=True).strip()
files = [source / (n + '.cpp') for n in ['performance', 'performance_io', 'performance_reuse', 'pragma_scope', 'fast_math']]
files += [Path(__file__), source / 'pragma_header.hpp', source / 'pragma_include.cpp']
report = dict(status='pass', compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0],
              cpu=cpu, platform=platform.platform(), commands=commands, flags=flags,
              elements=n, grid_side=2048, checksum=expected, io_tokens=io_count,
              io_input_sha256=hashlib.sha256(io_path.read_bytes()).hexdigest(),
              order=order, samples_ms=samples, median_ms={k:statistics.median(v) for k,v in samples.items()},
              fast_math_results=math_results, pragma_results=pragma_results,
              option_samples_ms=option_samples, option_median_ms={k:statistics.median(v) for k,v in option_samples.items()},
              source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
              scope='Single-host microbenchmarks, 9 fresh processes per variant, O2 baseline; setup outside measured time where documented, checksums validated. Not an OJ runtime or universal speed claim.')
(root / 'verification/infra-performance.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report['median_ms'], indent=2))
print('floating point:', math_results)
print('option median:', report['option_median_ms'])
print('pragma:', pragma_results)
