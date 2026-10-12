from pathlib import Path
import hashlib
import json
import os
import random
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
out = root / 'build/wida-balanced'
out.mkdir(exist_ok=True)
rng = random.Random(38102026)
cases = [([1, 2], [0, 1], [2, 1]),
         ([1, 2, 3], [3, 3, 3], [3, 2, 1]),
         ([2, 1, 4, 3, 5], [3, 4, 3, 1, 2], [3, 1, 5, 4, 2])]
for _ in range(180):
    n = rng.randint(1, 180)
    a = list(range(1, n + 1))
    rng.shuffle(a)
    limits = [rng.randint(0, n) for _ in a]
    expected = []
    for i in range(n):
        expected.append(i + 1)
        j = i
        for _ in range(limits[i]):
            if j == 0 or a[expected[j - 1] - 1] > a[i]:
                break
            expected[j], expected[j - 1] = expected[j - 1], expected[j]
            j -= 1
    cases.append((a, limits, expected))
n = 100000
ascending = list(range(1, n + 1))
descending = ascending[::-1]
cases += [(ascending, [n] * n, descending),
          (ascending, [0] * n, ascending),
          (descending, [n] * n, ascending)]
results = {}
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    probe = out / ('sequence-source-' + mode)
    subprocess.run([CXX, *flags, str(root / 'tests/sequence_max_source.cpp'), '-o', str(probe)], check=True)
    p = subprocess.run([str(probe)], capture_output=True, text=True, env=env, timeout=180)
    assert p.returncode == 0 and not p.stderr, p.stderr
    exe = out / ('queue-' + mode)
    subprocess.run([CXX, *flags, str(root / 'verify/codeforces/CF38G.compact.cpp'), '-o', str(exe)], check=True)
    for a, limits, expected in cases:
        data = str(len(a)) + '\n' + ''.join(f'{x} {c}\n' for x, c in zip(a, limits))
        run = subprocess.run([str(exe)], input=data, capture_output=True, text=True, env=env, timeout=20)
        assert run.returncode == 0 and not run.stderr, run.stderr
        assert list(map(int, run.stdout.split())) == expected
    results[mode] = {'source': p.stdout.strip(), 'protocol_cases': len(cases), 'max_n': n}
    print(mode, results[mode], flush=True)
files = ['src/compact/sequence_max_treap.hpp', 'verify/codeforces/CF38G.compact.cpp',
         'tests/sequence_max_source.cpp', 'tests/sequence_max_application.py',
         'tests/fixtures/wida_sequence_max/08C.cpp']
(root / 'verification/sequence-max-application.json').write_text(json.dumps({
    'runs': results, 'online_verdict': None,
    'files': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in files}
}, indent=2) + '\n')
