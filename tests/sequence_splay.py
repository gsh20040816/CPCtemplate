"""Fixed-ID sequence splay: independent vector permutations and stable sorting."""
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import resource
import subprocess
import sys
import tempfile
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from compiler_config import CXX
from run_provenance import snapshot
from usage_examples import records


def reverse_cases():
    rng = random.Random(3391)
    out = []
    for test in range(80):
        n = 1 + test % 40
        a = list(range(n))
        ops = []
        for _ in range(200):
            l, r = sorted([rng.randrange(n), rng.randrange(n)])
            ops.append(f'{l+1} {r+1}')
            a[l:r+1] = a[l:r+1][::-1]
        out.append((f'random-{test}', f'{n} {len(ops)}\n'+'\n'.join(ops)+'\n', [x+1 for x in a]))
    n = 100000
    for name, ops, want in [
        ('full-even', [f'1 {n}'] * n, list(range(1, n+1))),
        ('rotate', [f'2 {n}', f'1 {n}'] * (n//2), list(range(n//2+1, n+1))+list(range(1, n//2+1))),
        ('nested', [f'{i+1} {n-i}' for i in range(n//2)]*2, list(range(1, n+1)))]:
        out.append((name, f'{n} {len(ops)}\n'+'\n'.join(ops)+'\n', want))
    return out


def robotic_cases():
    rng = random.Random(3165)
    out = []
    for test in range(100):
        n = 1 + test % 70
        values = [rng.randrange(1, 12) for _ in range(n)]
        ids = list(range(n))
        want = []
        for i, id in enumerate(sorted(ids, key=lambda x: (values[x], x))):
            p = ids.index(id)
            want.append(p+1)
            ids[i:p+1] = ids[i:p+1][::-1]
        assert [(values[x], x) for x in ids] == sorted((v, i) for i, v in enumerate(values))
        out.append((f'duplicates-{test}', f'{n}\n'+' '.join(map(str, values))+'\n', want))
    n = 100000
    for name, values, want in [
        ('sorted', list(range(1, n+1)), list(range(1, n+1))),
        ('descending', list(range(n, 0, -1)), [n]+list(range(2, n+1))),
        ('equal', [10000000]*n, list(range(1, n+1)))]:
        out.append((name, f'{n}\n'+' '.join(map(str, values))+'\n', want))
    return out


def api_cases():
    rng = random.Random(288)
    out = []
    for test in range(70):
        n = test % 31
        a = list(range(n))
        ops, want = [], []
        for step in range(300):
            op = rng.randrange(4) if n else rng.choice([0, 3])
            if op == 0:
                l, r = sorted([rng.randrange(n+1), rng.randrange(n+1)])
                ops.append(f'0 {l} {r}')
                a[l:r] = a[l:r][::-1]
            elif op == 1:
                id = rng.randrange(n)
                ops.append(f'1 {id}')
                want.append(a.index(id))
            elif op == 2:
                k = rng.randrange(n)
                ops.append(f'2 {k}')
                want.append(a[k])
            else:
                ops.append('3')
                want.extend(a)
        out.append((f'mixed-{test}', f'{n} {len(ops)}\n'+'\n'.join(ops)+'\n', want))
    return out


def main():
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    before = snapshot(ROOT)
    out = Path(tempfile.mkdtemp(prefix='sequence-splay-'+mode+'-', dir=ROOT/'build'))
    flags = ['-std=c++20', '-Wall', '-Wextra']
    flags += ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2']
    if platform.system() == 'Darwin':
        flags += ['-Wl,-stack_size,0x20000000']
    else:
        _, hard = resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK, (min(512<<20, hard) if hard != -1 else 512<<20, hard))
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    header = (ROOT/'src/compact/sequence_splay.hpp').read_text().replace('#pragma once\n', '')
    probe = (ROOT/'tests/sequence_splay_probe.cpp').read_text()
    copied = header+'\n'+'\n'.join(l for l in probe.splitlines() if not l.startswith('#include "'))
    sha = lambda data: hashlib.sha256(data).hexdigest()
    report = dict(mode=mode, source_before_sha256=before, programs=[], mutants=[], local_stack_mib=512,
                  scope='All permutations n<=7 and every reversal interval; independent vector ranks/IDs, stable robotic sort, deep copy, lazy tags, parent/size invariants and 100000-node recursion. Local evidence only.')
    def compile(name, source, extra=()):
        cpp, exe = out/(name+'.cpp'), out/name
        cpp.write_text(source)
        cmd = [CXX, *flags, *extra, str(cpp), '-o', str(exe)]
        p = subprocess.run(cmd, capture_output=True)
        assert p.returncode == 0, p.stderr.decode()
        return exe, dict(name=name, compile_command=cmd, source_sha256=sha(source.encode()), binary_sha256=sha(exe.read_bytes()), runs=[])
    for form, source in [('header', '#include "'+str(ROOT/'tests/sequence_splay_probe.cpp')+'"\n'), ('copied', copied)]:
        for release in [False, True]:
            name = form+('-ndebug' if release else '-assert')
            exe, entry = compile(name, source, ['-DNDEBUG'] if release else [])
            start = time.monotonic()
            p = subprocess.run([str(exe)], capture_output=True, env=env, timeout=600)
            assert p.returncode == 0 and not p.stderr and p.stdout.splitlines()[-1].startswith(b'PASS '), (name, p.returncode, p.stdout, p.stderr[-1000:])
            entry.update(result=p.stdout.decode().strip(), elapsed_seconds=time.monotonic()-start, output_sha256=sha(p.stdout))
            report['programs'].append(entry)
            print(name, entry['result'], flush=True)
    for name, old, new in [
        ('missing-ancestor-push', 'push_path(x);\n        while', 'push(x);\n        while'),
        ('no-reversal', 'flip(a[y].ch[0]);', '(void)y;'),
        ('missing-lazy-tag', 'a[x].rev = !a[x].rev;', 'a[x].rev = false;'),
        ('rank-sentinel-offset', 'return a[a[x].ch[0]].siz - 1;', 'return a[a[x].ch[0]].siz;'),
        ('id-sentinel-offset', 'return x - 2;', 'return x - 1;'),
        ('right-endpoint', 'int y = select(r + 1);', 'int y = select(r);')]:
        assert header.count(old) == 1, name
        exe, entry = compile(name, copied.replace(old, new), ['-DNDEBUG'])
        p = subprocess.run([str(exe), 'small-only'], capture_output=True, env=env, timeout=180)
        assert p.returncode == 0 and not p.stderr and p.stdout == b'ORACLE_REJECT\n', (name, p.returncode, p.stdout, p.stderr[-1000:])
        entry['independent_oracle_rejected'] = True
        report['mutants'].append(entry)
        print(name, 'ORACLE_REJECT', flush=True)
    for example, cs in [('example-286', reverse_cases()), ('example-287', robotic_cases()), ('example-288', api_cases())]:
        row = next(r for r in records() if r['id'] == example)
        for form, source in [('driver', '#include "'+str(ROOT/row['driver'])+'"\n'), ('expanded', row['program']), ('minimal-copy', '#include <iostream>\n#include <numeric>\n#include <utility>\n'+header+'\n'+row['snippet'])]:
            exe, entry = compile(example+'-'+form, source)
            for name, raw, want in cs:
                start = time.monotonic()
                p = subprocess.run([str(exe)], input=raw.encode(), capture_output=True, env=env, timeout=180)
                assert p.returncode == 0 and not p.stderr, (example, form, name, p.returncode, p.stderr[-1000:])
                assert list(map(int, p.stdout.split())) == want, (example, form, name, p.stdout[:300], want[:30])
                entry['runs'].append(dict(case=name, input_sha256=sha(raw.encode()), output_sha256=sha(p.stdout), elapsed_seconds=time.monotonic()-start, passed=True))
            report['programs'].append(entry)
            print(example, form, len(cs), 'PASS', flush=True)
    report.update(passed=True, source_after_sha256=snapshot(ROOT))
    assert before == report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS:', out/'report.json', flush=True)

if __name__ == '__main__':
    main()
