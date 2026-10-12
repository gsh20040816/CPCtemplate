"""Enable exactly the optional Scaling edits printed alongside ordinary Dinic."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]


def core():
    source = (ROOT / 'src/compact/flow.hpp').read_text()
    return 'struct Dinic' + source.split('struct Dinic', 1)[1].split('\n};', 1)[0] + '\n};\n'


def enabled(source):
    edits = [
        ('bool bfs(int s, int t)', 'bool bfs(int s, int t, ll lim = 1)'),
        ('if (e[id].cap &&', 'if (e[id].cap >= lim &&'),
        ('ll dfs(int u, int t, ll f)', 'll dfs(int u, int t, ll f, ll lim = 1)'),
        ('if (!e[id].cap ||', 'if (e[id].cap < lim ||'),
        ('dfs(v, t, min(f, e[id].cap))', 'dfs(v, t, min(f, e[id].cap), lim)'),
        ('bfs(s, t))', 'bfs(s, t, lim))'),
        ('dfs(s, t, limit - ans)', 'dfs(s, t, limit - ans, lim)'),
    ]
    for old, new in edits:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    start = source.index('        while (ans < limit && bfs')
    end = source.index('        return ans;', start)
    loop = source[start:end]
    setup = '''        ll mx = 0;
        for (const auto &a : e)
            mx = max(mx, a.cap);
        if (mx == 0)
            return 0;
        ll lim = 1;
        while (lim <= mx / 2)
            lim <<= 1;
        for (; lim; lim >>= 1)
        {
'''
    source = source[:start] + setup + ''.join('    ' + line + '\n' for line in loop.splitlines()) + '        }\n' + source[end:]
    return source


def main():
    out = ROOT / 'build/dinic-scaling'
    out.mkdir(parents=True, exist_ok=True)
    prelude = '#include <cassert>\n#include <bits/stdc++.h>\nusing namespace std;\n'
    base = core()
    scaled = enabled(base)
    (out / 'enabled.hpp').write_text(prelude + scaled)
    probe = (ROOT / 'tests/dinic_scaling.cpp').read_text()
    source = prelude + base + scaled.replace('Dinic', 'ScalingDinic') + probe
    cpp = out / 'probe.cpp'
    cpp.write_text(source)
    report = {'scope': 'Local exhaustive-cut, feasible-flow and residual certificates. No online verdict.', 'runs': []}
    for mode in ['normal', 'sanitizer']:
        flags = ['-std=c++20', '-Wall', '-Wextra']
        flags += ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        if platform.system() == 'Darwin':
            flags += ['-Wl,-stack_size,0x20000000']
        exe = out / mode
        command = [CXX, *flags, str(cpp), '-o', str(exe)]
        subprocess.run(command, check=True)
        env = os.environ.copy()
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
        result = subprocess.run([str(exe)], capture_output=True, text=True, env=env, timeout=180)
        assert result.returncode == 0 and not result.stderr, result.stderr
        print(mode, result.stdout.strip(), flush=True)
        report['runs'].append({'mode': mode, 'command': command, 'result': result.stdout.strip()})
    report['files'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in ['src/compact/flow.hpp', 'tests/dinic_scaling.cpp', 'tests/dinic_scaling.py']}
    report['enabled_source_sha256'] = hashlib.sha256((prelude + scaled).encode()).hexdigest()
    (ROOT / 'verification/dinic-scaling.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
