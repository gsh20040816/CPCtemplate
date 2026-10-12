"""Keep recursive DFS and give it an explicit 512 MiB macOS stack for stress."""
from pathlib import Path
import hashlib
import json
import os
import resource
import subprocess
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
out = root / 'build/graph-source'
n = 1000000
sat = f'{n} {n}\n1 1 1 1\n' + ''.join(f'{i} 0 {i + 1} 1\n' for i in range(1, n))
sat_expected = ['POSSIBLE'] + ['1'] * n
n = 200000
m = 300000
dom = f'{n} {m}\n' + ''.join(f'{i} {i + 1}\n' for i in range(1, n)) + '1 1\n' * (m - n + 1)
dom_expected = list(map(str, range(n, 0, -1)))
results = {}
for mode in ['normal', 'sanitizer']:
    flags = ['-std=c++20', '-O2']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    if os.uname().sysname == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    else:
        soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK, (hard, hard))
    for name, problem, data, expected in [('sat', 'P4782', sat, sat_expected), ('dom', 'P5180', dom, dom_expected)]:
        for form in ['source', 'current']:
            src = out / (name + '-original.cpp') if form == 'source' else root / 'verify/luogu' / (problem + '.compact.cpp')
            exe = out / ('stress-' + name + '-' + form + '-' + mode)
            subprocess.run([CXX, *flags, str(src), '-o', str(exe)], check=True)
            p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'), timeout=120)
            assert p.returncode == 0 and not p.stderr, (name, form, mode, p.stderr[:2000])
            assert p.stdout.split() == expected
            results[name + '-' + form + '-' + mode] = len(expected)
            print(name, form, mode, 'PASS', flush=True)
report = {'runs': results, 'scope': 'SAT million variables forced-true recursive implication chain; LT 200000 vertices, 300000 edges, recursive chain plus root self-loops; all output entries checked against closed forms', 'macos_stack_bytes': 536870912, 'no_explicit_dfs_stack': True, 'files': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [out / 'sat-original.cpp', out / 'dom-original.cpp', root / 'tests/graph_source_stress.py']}, 'online': 'No new submission'}
(root / 'verification/graph-source-stress.json').write_text(json.dumps(report, indent=2) + '\n')
