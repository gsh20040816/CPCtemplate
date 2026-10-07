"""Audit upstream capacity matching and compile the exact documented reduction."""
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from compiler_config import CXX
from run_provenance import snapshot


def main():
    sanitize = os.environ.get('CPC_SANITIZE') == '1'
    mode = 'sanitizer' if sanitize else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='capacity-source-' + mode + '-', dir=ROOT / 'build'))
    flags = ['-std=c++20', '-Wall', '-Wextra']
    flags += ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if sanitize else ['-O2']
    if platform.system() == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    else:
        _, hard = resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK, (min(512 << 20, hard) if hard != -1 else 512 << 20, hard))
    env = os.environ.copy()
    if sanitize:
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    sha = lambda b: hashlib.sha256(b).hexdigest()
    doc = (ROOT / 'docs/CAPACITATED-MATCHING-SOURCE-AUDIT.md').read_text()
    example = doc.split('```cpp\n', 1)[1].split('```', 1)[0]
    flow = (ROOT / 'src/compact/flow.hpp').read_text()
    core = 'struct Dinic' + flow.split('struct Dinic', 1)[1].split('\n};', 1)[0] + '\n};\n'
    probe = (ROOT / 'tests/capacitated_matching_source_audit.cpp').read_text()
    probe = probe.replace('"fixtures/matching_sources/', '"' + str(ROOT / 'tests/fixtures/matching_sources') + '/')
    prelude = '#include <cassert>\n#include <bits/stdc++.h>\nusing namespace std;\n'
    report = dict(mode=mode, source_before_sha256=before, programs=[], mutants=[], stack_mib=512,
                  example_sha256=sha(example.encode()), scope='Local source mapping and Markdown recipe, not an OJ driver, online AC, rank or new public component.')

    def compile(name, source, extra=()):
        cpp, exe = out / (name + '.cpp'), out / name
        cpp.write_text(source)
        cmd = [CXX, *flags, *extra, str(cpp), '-o', str(exe)]
        p = subprocess.run(cmd, capture_output=True)
        if p.returncode:
            raise RuntimeError(p.stderr.decode())
        return exe, dict(name=name, command=cmd, source_sha256=sha(source.encode()), binary_sha256=sha(exe.read_bytes()))

    def run(exe, args=()):
        p = subprocess.run([str(exe), *args], capture_output=True, timeout=300, env=env)
        if p.returncode or p.stderr:
            raise RuntimeError((exe, p.returncode, p.stderr.decode()[-2000:]))
        return p.stdout.decode().strip()

    full = prelude + core + example + probe
    for form, start in [('header', '#include "' + str(ROOT / 'src/compact/flow.hpp') + '"\n'), ('copied', prelude + core)]:
        for release in [False, True]:
            exe, entry = compile(form + ('-ndebug' if release else '-assert'), start + example + probe, ['-DNDEBUG'] if release else [])
            result = run(exe)
            if not result.startswith('PASS '):
                raise RuntimeError(result)
            entry['result'] = result
            report['programs'].append(entry)
            print(entry['name'], result, flush=True)
    for name, old, new in [
        ('right-capacity-one', 't, cap[v]);', 't, 1);'),
        ('left-capacity-two', 'g.add(s, u + 1, 1);', 'g.add(s, u + 1, 2);'),
        ('wrong-scheme', 'if (g.used(id[i]))', 'if (!g.used(id[i]))')
    ]:
        if old not in example:
            raise RuntimeError(name)
        exe, entry = compile(name, prelude + core + example.replace(old, new) + probe, ['-DNDEBUG'])
        result = run(exe, ['small-only'])
        if result != 'ORACLE_REJECT':
            raise RuntimeError((name, result))
        entry['independent_oracle_rejected'] = True
        report['mutants'].append(entry)
        print(name, result, flush=True)
    if sanitize:
        exe, entry = compile('source-boundary', full, ['-DNDEBUG'])
        p = subprocess.run([str(exe), 'source-overflow'], capture_output=True, timeout=30, env=env)
        diag = p.stderr.decode()
        if p.returncode == 0 or 'index 1010 out of bounds' not in diag:
            raise RuntimeError(('expected source boundary failure', p.returncode, diag))
        entry.update(expected_failure=True, returncode=p.returncode, diagnostic=diag)
        report['upstream_boundary_reproducer'] = entry
        print('upstream 1010-slot boundary reproduced', flush=True)
    after = snapshot(ROOT)
    if before != after:
        raise RuntimeError('source changed during run')
    report.update(source_after_sha256=after, passed=True)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS', out / 'report.json', flush=True)


if __name__ == '__main__':
    main()
