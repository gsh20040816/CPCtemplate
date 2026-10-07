#!/usr/bin/env python3
"""Nearest active point: independent original-tree distances and full QTREE5 inputs."""
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import resource
import shutil
import subprocess
import sys
import tempfile
from collections import deque
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from usage_examples import records
from compiler_config import CXX


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if not __debug__:
        raise RuntimeError('Python checks must stay enabled')
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='centroid-nearest-' + mode + '-', dir=ROOT / 'build'))
    before = snapshot(ROOT)
    probe = (ROOT / 'tests/centroid_nearest_probe.cpp').read_text()
    core = next(x['code'] for x in extract_components(json.loads((ROOT / 'docs/catalog.json').read_text())) if x['symbol'] == 'CentroidNearest')
    headers = ['algorithm', 'cassert', 'climits', 'iostream', 'optional', 'set', 'utility', 'vector']
    prelude = ''.join('#include <' + x + '>\n' for x in headers) + 'using namespace std;\n'
    copied = prelude + core + '\n' + probe.replace('#include "../src/compact/centroid_nearest.hpp"', '')
    flags = ['-std=c++20', '-Wall', '-Wextra', '-pthread'] + (['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if mode == 'sanitizer' else ['-O2'])
    env = os.environ.copy()
    if mode == 'sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    report = dict(mode=mode, source_before_sha256=before, compiler=str(compiler), compiler_sha256=sha(compiler.read_bytes()), flags=flags, programs=[], mutants=[], applications=[])
    def compile(name, source, extra=()):
        cpp, exe = out / (name + '.cpp'), out / name
        cpp.write_text(source)
        command = [CXX, *flags, *extra, str(cpp), '-o', str(exe)]
        subprocess.run(command, capture_output=True, check=True)
        return exe, dict(name=name, compile_command=command, source_sha256=sha(cpp.read_bytes()), binary_sha256=sha(exe.read_bytes()))
    reference = None
    for form, source in [('header', '#include "' + str(ROOT / 'tests/centroid_nearest_probe.cpp') + '"\n'), ('copied', copied)]:
        for nd in [False, True]:
            name = form + ('-ndebug' if nd else '-assert')
            exe, entry = compile(name, source, ['-DNDEBUG'] if nd else [])
            p = subprocess.run([str(exe)], capture_output=True, env=env, timeout=600)
            assert p.returncode == 0 and not p.stderr, (name, p.returncode, p.stderr[-1000:])
            assert p.stdout.startswith(b'PASS ') and p.stdout.endswith(b' checks\n'), p.stdout
            if reference is None:
                reference = p.stdout
            assert p.stdout == reference
            entry.update(output_sha256=sha(p.stdout), result=p.stdout.decode().strip())
            report['programs'].append(entry)
            print(name, entry['result'], flush=True)
    mutations = [
        ('equal-distance-erasure', 'bag[c].erase({d, u});', 'bag[c].erase(bag[c].lower_bound({d, 0}), bag[c].upper_bound({d, INT_MAX}));'),
        ('retain-inactive', 'else bag[c].erase({d, u});', 'else {}'),
        ('wrong-tie', 'now < *ans', '(now.first < ans->first || (now.first == ans->first && now.second > ans->second))'),
        ('retain-on-rebuild', 'bag[u].clear();', '/* retain stale points */'),
        ('max-is-sentinel', 'if (x > LLONG_MAX - d) continue;', 'if (x >= LLONG_MAX - d) continue;'),
    ]
    for name, old, new in mutations:
        assert copied.count(old) == 1, name
        exe, entry = compile(name, copied.replace(old, new), ['-DNDEBUG'])
        p = subprocess.run([str(exe)], capture_output=True, env=env, timeout=180)
        assert p.returncode == 0 and not p.stderr and p.stdout == b'ORACLE_REJECT\n', (name, p.returncode, p.stdout, p.stderr[-1000:])
        entry.update(output_sha256=sha(p.stdout), independent_oracle_rejected=True)
        report['mutants'].append(entry)
    # Removing the overflow guard must fail the oracle (normal) or UBSan (sanitizer).
    old = 'if (x > LLONG_MAX - d) continue;'
    exe, entry = compile('unchecked-detour', copied.replace(old, '/* unchecked sum */'), ['-DNDEBUG'])
    p = subprocess.run([str(exe)], capture_output=True, env=env, timeout=180)
    if mode == 'sanitizer':
        assert p.returncode != 0 and b'signed integer overflow' in p.stderr, p.stderr[-1000:]
        entry['rejected_by'] = 'UBSan signed integer overflow'
    else:
        assert p.returncode == 0 and p.stdout == b'ORACLE_REJECT\n' and not p.stderr
        entry['rejected_by'] = 'independent oracle'
    entry.update(stdout_sha256=sha(p.stdout), stderr_sha256=sha(p.stderr))
    report['mutants'].append(entry)
    rng = random.Random(29392026)
    datasets = [('official-sample', '10\n1 2\n1 3\n2 4\n1 5\n1 6\n4 7\n7 8\n5 9\n1 10\n10\n0 6\n0 6\n0 6\n1 3\n0 1\n0 1\n1 3\n1 10\n1 4\n1 6\n', [2,2,2,3,0])]
    def dataset(name, n, edges, ops, answers):
        inp = str(n)+'\n'+''.join(f'{u+1} {v+1}\n' for u,v in edges)
        inp += str(len(ops))+'\n'+''.join(f'{op} {u+1}\n' for op,u in ops)
        datasets.append((name, inp, answers))
    for case in range(180):
        n = rng.randrange(1, 61)
        edges = [(rng.randrange(v), v) for v in range(1,n)]
        g = [[] for _ in range(n)]
        for u,v in edges:
            g[u].append(v)
            g[v].append(u)
        d = []
        for s in range(n):
            row = [-1]*n
            row[s] = 0
            q = deque([s])
            while q:
                u = q.popleft()
                for v in g[u]:
                    if row[v] < 0:
                        row[v] = row[u]+1
                        q.append(v)
            d.append(row)
        on, ops, answers = set(), [], []
        for step in range(300):
            u = rng.randrange(n)
            op = rng.randrange(2)
            ops.append((op,u))
            if op == 0:
                on.symmetric_difference_update([u])
            else:
                answers.append(min((d[u][v] for v in on), default=-1))
        dataset(f'random-{case}',n,edges,ops,answers)
    n = 100000
    for shape in range(3):
        edges = [(v-1 if shape == 0 else 0 if shape == 1 else (v-1)//2,v) for v in range(1,n)]
        def distance(u,v):
            if shape == 0: return abs(u-v)
            if shape == 1: return 0 if u == v else 1 if u == 0 or v == 0 else 2
            a,b = [],[]
            while u:
                a.append(u)
                u=(u-1)//2
            while v:
                b.append(v)
                v=(v-1)//2
            while a and b and a[-1] == b[-1]:
                a.pop()
                b.pop()
            return len(a)+len(b)
        pool = [0, 1, n//2, n-2, n-1]
        on,ops,answers = set(),[],[]
        for step in range(n):
            if step % 3 == 0:
                u = rng.choice(pool)
                ops.append((0,u))
                on.symmetric_difference_update([u])
            else:
                u = rng.randrange(n)
                ops.append((1,u))
                answers.append(min((distance(u,v) for v in on), default=-1))
        dataset(f'max-shape-{shape}',n,edges,ops,answers)
    row = next(r for r in records() if r['id'] == 'example-245')
    stack_flags = ['-Wl,-stack_size,0x20000000'] if platform.system() == 'Darwin' else []
    if platform.system() != 'Darwin':
        soft,hard=resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK,(min(512<<20,hard) if hard != -1 else 512<<20,hard))
    for name, source in [('driver','#include "'+str(ROOT / row['driver'])+'"\n'),('bundle',row['program']),('minimal-copy',prelude+core+'\n'+row['snippet'])]:
        exe, entry=compile(name,source,stack_flags)
        entry['runs']=[]
        for label,inp,want in datasets:
            data=inp.encode()
            p=subprocess.run([str(exe)],input=data,capture_output=True,env=env,timeout=180)
            assert p.returncode == 0 and not p.stderr,(name,label,p.returncode,p.stderr[-1000:])
            assert p.stdout.split() == [str(x).encode() for x in want],(name,label,p.stdout[:300])
            entry['runs'].append(dict(case=label,input_sha256=sha(data),output_sha256=sha(p.stdout),passed=True))
        report['applications'].append(entry)
        print(name, len(datasets), 'inputs PASS',flush=True)
    report.update(source_after_sha256=snapshot(ROOT),passed=True,application_case_count=len(datasets),scope='Local BFS/scan oracle, all labelled trees n<=6 in unit/zero/mixed weights, all active subsets, random weighted updates, copies/rebuilds, long long boundary and 100000-vertex recursive topologies; header/copied assert/NDEBUG and three QTREE5 forms. Not online AC, full-suite regression, or LeakSanitizer.')
    assert before == report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('CentroidNearest',mode,'PASS:',out/'report.json')

if __name__ == '__main__':
    main()
