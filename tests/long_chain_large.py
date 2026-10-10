"""Native Linux recursive-depth and maximum-query stress; no stack simulation."""
import hashlib
import json
import os
import platform
import resource
import subprocess
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
assert platform.system() == 'Linux', 'Run native Linux with its stack limit expanded.'
soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
resource.setrlimit(resource.RLIMIT_STACK, (512 * 1024 * 1024, hard))
work = root / 'build/long-chain/large'
work.mkdir(parents=True, exist_ok=True)
(root / 'verification').mkdir(exist_ok=True)
commands, evidence = [], {}
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
for san in [False, True]:
    mode = 'sanitizer' if san else 'normal'
    flags = ['-std=c++20', '-O1' if san else '-O2']
    if san:
        flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-no-pie']
    for kind, source in [('core', 'tests/long_chain.cpp'), ('driver', 'verify/luogu/P5903.compact.cpp')]:
        exe = work / f'{kind}-{mode}'
        cmd = [CXX, *flags, str(root / source), '-o', str(exe)]
        commands.append(cmd)
        subprocess.run(cmd, check=True)
    p = subprocess.run([str(work / f'core-{mode}'), '--large'], capture_output=True, text=True, env=env, timeout=180)
    assert p.returncode == 0, p.stderr
    evidence[mode] = dict(core=p.stdout.strip(), cases=[])
    print(mode, p.stdout.strip(), flush=True)
n, q = 500000, 5000000
for shape in ['chain', 'star', 'heap']:
    parent = [0] + [u - 1 if shape == 'chain' else 1 if shape == 'star' else u // 2 for u in range(2, n + 1)]
    seed = 4294967295
    data = f'{n} {q} {seed}\n' + ' '.join(map(str, parent)) + '\n'
    source = work / f'{shape}.in'
    source.write_text(data)
    s, last, ans = seed, 0, 0
    def get():
        global s
        s ^= (s << 13) & 0xffffffff
        s ^= s >> 17
        s ^= (s << 5) & 0xffffffff
        return s
    for i in range(1, q + 1):
        u = (get() ^ last) % n + 1
        dep = u if shape == 'chain' else (1 if u == 1 else 2) if shape == 'star' else u.bit_length()
        k = (get() ^ last) % dep
        last = u - k if shape == 'chain' else (u if k == 0 else 1) if shape == 'star' else u >> k
        ans ^= i * last
    for mode in ['normal', 'sanitizer']:
        timer = work / f'{shape}-{mode}.time'
        cmd = ['/usr/bin/time', '-f', '%e %M', '-o', str(timer), str(work / f'driver-{mode}')]
        with source.open() as inp:
            p = subprocess.run(cmd, stdin=inp, capture_output=True, text=True, env=env, timeout=180)
        assert p.returncode == 0, p.stderr
        assert p.stdout.strip() == str(ans), (shape, mode, p.stdout, ans)
        elapsed, rss = timer.read_text().split()
        evidence[mode]['cases'].append(dict(shape=shape, n=n, q=q, seed=seed, expected=ans, elapsed_seconds=float(elapsed), peak_rss_kib=int(rss)))
        print(shape, mode, ans, elapsed, rss, flush=True)
files = ['src/compact/long_chain.hpp', 'tests/long_chain.cpp', 'tests/long_chain_large.py', 'verify/luogu/P5903.compact.cpp']
report = dict(status='pass', platform=platform.platform(), machine=platform.machine(), compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0], stack_bytes=resource.getrlimit(resource.RLIMIT_STACK)[0], original_stack_bytes=soft, commands=commands, results=evidence, source_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files}, scope='Local native Linux tests only; shape formulas are independent of long-chain tables. Recursive source unchanged; no OJ/runtime-rank claim.')
(root / 'verification/long-chain-linux-large.json').write_text(json.dumps(report, indent=2)+'\n')
