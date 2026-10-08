#!/usr/bin/env python3
"""Independent BFS oracles for lifetime intervals and full operation streams."""
import argparse, collections, hashlib, json, os, random, subprocess, sys
from pathlib import Path
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records
from audit_copy_context import candidate, extract_components


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sanitize', action='store_true')
    args = ap.parse_args()
    mode = 'sanitizer' if args.sanitize else 'normal'
    out = ROOT / 'build/time-connectivity' / mode
    out.mkdir(parents=True, exist_ok=True)
    flags = ['-std=c++20', '-O1' if args.sanitize else '-O2']
    if args.sanitize:
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    sha = lambda b: hashlib.sha256(b).hexdigest()
    rows = [r for r in records() if r['symbol'] == 'TimeConnectivity']
    paths = ['src/compact/time_connectivity.hpp', 'src/compact/data_structure.hpp', 'tests/time_connectivity.cpp', 'tests/time_connectivity.py', 'docs/catalog.json', 'docs/usage-examples.json'] + [r['driver'] for r in rows]
    hashes = {p: sha((ROOT / p).read_bytes()) for p in paths}
    components = {r['symbol']: r for r in extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))}
    def compile(src, exe, extra=()):
        subprocess.run([CXX, *flags, *extra, str(src), '-o', str(exe)], check=True, capture_output=True)
    def run(exe, data=''):
        r = subprocess.run([str(exe)], input=data, text=True, capture_output=True, env=env, timeout=120)
        assert r.returncode == 0, r.stderr
        return r.stdout
    copied = candidate(rows[0], rows[0]['requires'], components)['program'].split('int main()')[0]
    core = {}
    for form in ['header', 'ndebug', 'copied']:
        src = ROOT / 'tests/time_connectivity.cpp'
        exe = out / ('core-' + form)
        if form == 'copied':
            src = exe.with_suffix('.cpp')
            src.write_text((ROOT / 'tests/time_connectivity.cpp').read_text().replace('#include "../src/compact/time_connectivity.hpp"', copied))
        compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
        core[form] = run(exe).strip()
        print(mode, form, core[form], flush=True)
    rng = random.Random(2147353)
    def component(n, edges, u):
        seen = {u}
        todo = collections.deque([u])
        while todo:
            x = todo.popleft()
            for (a, b), count in edges.items():
                if count and (a == x or b == x):
                    v = b if a == x else a
                    if v not in seen:
                        seen.add(v)
                        todo.append(v)
        return seen
    api_data, api_answer = [], []
    for case in range(320):
        n = rng.randrange(1, 15)
        initial = [(rng.randint(1, n), rng.randint(1, n)) for _ in range(rng.randrange(25))]
        edges = collections.Counter(tuple(sorted(e)) for e in initial)
        ops, answers = [], []
        for _ in range(rng.randrange(0, 180)):
            u, v = rng.randint(1, n), rng.randint(1, n)
            e = tuple(sorted((u, v)))
            op = rng.choice(['+', '-', '?', '?'])
            if op == '-':
                alive = [e for e, c in edges.items() if c]
                if not alive:
                    op = '+'
                else:
                    u, v = rng.choice(alive)
                    e = (u, v)
            if op == '+':
                edges[e] += 1
            elif op == '-':
                edges[e] -= 1
            else:
                seen = component(n, edges, u)
                answers.append(f'{int(v in seen)} {len(seen)}')
            if op != '?' and rng.randrange(2):
                u, v = v, u
            ops.append(f'{op} {u} {v}')
        api_data.append(f'{n} {len(initial)} {len(ops)}\n' + ''.join(f'{u} {v}\n' for u, v in initial) + '\n'.join(ops) + '\n')
        api_answer += answers
    # Exact multiplicity and lifetime boundary witness; q=0 and no queries.
    api_data += ['3 2 7\n1 2\n2 1\n? 1 2\n- 1 2\n? 2 1\n- 2 1\n? 1 2\n+ 2 3\n? 1 3\n', '1 1 0\n1 1\n']
    api_answer += ['1 2', '1 2', '0 1', '0 1']
    forests = []
    for case in range(64):
        n = rng.randrange(1, 25)
        edges = collections.Counter()
        ops, answers = [], []
        for _ in range(150):
            u, v = rng.randint(1, n), rng.randint(1, n)
            seen = component(n, edges, u)
            op = rng.choice(['Connect', 'Destroy', 'Query'])
            alive = [e for e, c in edges.items() if c]
            if op == 'Connect' and v not in seen:
                edges[tuple(sorted((u, v)))] = 1
            elif op == 'Destroy' and alive:
                u, v = rng.choice(alive)
                edges[(u, v)] = 0
            else:
                op = 'Query'
                answers.append('Yes' if v in seen else 'No')
            if rng.randrange(2):
                u, v = v, u
            ops.append(f'{op} {u} {v}')
        forests.append((f'{n} {len(ops)}\n' + '\n'.join(ops) + '\n', answers))
    # Maximum official n and q: repeated fresh lifetime, then destroy, then query.
    ops, ans = [], []
    for i in range(50000):
        v = 2 + i % 9999
        ops += [f'Connect 1 {v}', f'Query 1 {v}', f'Destroy {v} 1', f'Query 1 {v}']
        ans += ['Yes', 'No']
    forests.append(('10000 200000\n' + '\n'.join(ops) + '\n', ans))
    usage = {}
    for row in rows:
        cp = candidate(row, row['requires'], components)
        for form in ['header', 'ndebug', 'expanded', 'copied']:
            src = ROOT / row['driver']
            exe = out / (row['id'] + '-' + form)
            if form in ['expanded', 'copied']:
                src = exe.with_suffix('.cpp')
                src.write_text(row['program'] if form == 'expanded' else cp['program'])
            compile(src, exe, ['-DNDEBUG'] if form == 'ndebug' else [])
            if row['id'] == 'example-352':
                for data, answer in forests:
                    assert run(exe, data).splitlines() == answer
            else:
                assert run(exe, ''.join(api_data)).splitlines() == api_answer
        usage[row['id']] = dict(program_sha256=row['program_sha256'], copied_program_sha256=cp['program_sha256'], forms=['header', 'ndebug', 'expanded', 'copied'], cases=len(forests) if row['id']=='example-352' else len(api_data))
        print(mode, row['id'], 'PASS', flush=True)
    # Semantically wrong variants must produce wrong answers or need(false).
    mutants = {}
    probe = (ROOT / 'tests/time_connectivity.cpp').read_text().replace('#include "../src/compact/time_connectivity.hpp"', copied)
    changes = {'no_rollback': ('d.rollback(saved);', '(void)saved;'), 'short_interval': ('insert(1, 0, q, l, r, {u, v});', 'if (l + 1 < r) insert(1, 0, q, l, r - 1, {u, v});')}
    for name, (a, b) in changes.items():
        assert a in probe
        src, exe = out / (name + '.cpp'), out / name
        src.write_text(probe.replace(a, b))
        compile(src, exe)
        r = subprocess.run([str(exe)], text=True, capture_output=True, env=env, timeout=30)
        assert r.returncode == 1 and not r.stderr, (name, r.returncode, r.stderr)
        mutants[name] = 'need(false) detected'
    cp = candidate(rows[1], rows[1]['requires'], components)['program']
    assert 'if (state.first == 0)\n                    graph.add' in cp
    src, exe = out / 'multiplicity.cpp', out / 'multiplicity'
    src.write_text(cp.replace('if (state.first == 0)\n                    graph.add', 'if (state.first == 1)\n                    graph.add'))
    compile(src, exe)
    assert run(exe, ''.join(api_data)).splitlines() != api_answer
    mutants['close_at_one_copy'] = 'output mismatch detected'
    assert hashes == {p: sha((ROOT / p).read_bytes()) for p in paths}
    report = dict(mode=mode, compiler=CXX, flags=flags, source_sha256=hashes, core=core, usages=usage, mutants=mutants, passed=True, scope='Independent BFS tests; P2147 forest domain, multigraph API and raw lifetimes separately checked. No online AC inferred.')
    (ROOT / f'verification/time-connectivity-{mode}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(mode, 'ALL PASS', flush=True)

if __name__ == '__main__':
    main()
