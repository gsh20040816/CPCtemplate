"""Independent oracles for exact registered graph usage programs, not online AC."""
from compiler_config import CXX
from pathlib import Path
import hashlib
import itertools
import json
import os
import platform
import random
import resource
import shutil
import subprocess
import sys
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import records

assert __debug__, 'Assertions must remain enabled'
mode = 'sanitizer' if os.getenv('CPC_SANITIZE') == '1' else 'normal'
work = root / 'build' / ('graph-printed-usages-' + mode)
work.mkdir(parents=True, exist_ok=True)
flags = ['-std=c++20', '-O2', '-Wall', '-Wextra']
if mode == 'sanitizer':
    flags += ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
if platform.system() == 'Darwin':
    flags += ['-Wl,-stack_size,0x20000000']
env = os.environ.copy()
env['ASAN_OPTIONS'] = env.get('ASAN_OPTIONS', '') + ':detect_leaks=0'
env['UBSAN_OPTIONS'] = env.get('UBSAN_OPTIONS', '') + ':halt_on_error=1'
stack_before = resource.getrlimit(resource.RLIMIT_STACK)
if platform.system() == 'Linux':
    soft, hard = stack_before
    target = 512 << 20
    if hard != resource.RLIM_INFINITY:
        target = min(target, hard)
    resource.setrlimit(resource.RLIMIT_STACK, (target, hard))
stack_actual = resource.getrlimit(resource.RLIMIT_STACK)

selected = {r['id']: r for r in records() if r['id'] in ('example-203', 'example-204')}
assert set(selected) == {'example-203', 'example-204'}
assert all(r['kind'] == 'application' for r in selected.values())
paths = [
    'docs/usage-examples.json', 'tests/graph_printed_usages.py',
    'tests/usage_examples.py', 'tests/usage_checkers.py', 'tests/compiler_config.py',
    'tools/usage_examples.py', 'verify/hdu/1814.compact.cpp',
    'verify/poj/2942.compact.cpp', 'src/compact/lex_two_sat.hpp',
    'src/compact/odd_cycle_vertices.hpp', 'src/compact/block_cut_forest.hpp',
    'src/compact/biconnected_core.hpp'
]


def hashes():
    return {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths}


source_hashes = hashes()
compiler = Path(shutil.which(CXX)).resolve()
compiler_hash = hashlib.sha256(compiler.read_bytes()).hexdigest()
commands = {}
programs = {}
for name, row in selected.items():
    source = work / (name + '.cpp')
    source.write_text(row['program'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['program_sha256']
    commands[name] = [str(compiler), *flags, str(source), '-o', str(work / name)]
    subprocess.run(commands[name], cwd=root, check=True)
    programs[name] = dict(driver=row['driver'], program_sha256=row['program_sha256'],
                          snippet_sha256=hashlib.sha256(row['snippet'].encode()).hexdigest(),
                          kind=row['kind'], invocations=0, batches=[])


def exact(actual, expected):
    assert actual == expected, (actual[:200], expected[:200])


def run(name, data, expected, cases, scope):
    process = subprocess.run([str(work / name)], input=data, text=True,
                             capture_output=True, env=env, timeout=120, check=True)
    assert not process.stderr, process.stderr
    exact(process.stdout, expected)
    report = programs[name]
    report['invocations'] += 1
    report['batches'].append(dict(cases=cases, scope=scope,
                                 input_sha256=hashlib.sha256(data.encode()).hexdigest(),
                                 output_sha256=hashlib.sha256(process.stdout.encode()).hexdigest()))


def encode(n, pairs):
    return f'{n} {len(pairs)}\n' + ''.join(f'{u} {v}\n' for u, v in pairs)


def representatives(n, conflicts):
    # Enumerate actual candidate choices in sequence order, not implications/SCCs.
    for values in itertools.product((0, 1), repeat=n):
        chosen = [2 * x + 1 + v for x, v in enumerate(values)]
        selected_people = set(chosen)
        if all(u not in selected_people or v not in selected_people for u, v in conflicts):
            return ''.join(f'{u}\n' for u in chosen)
    return 'NIE\n'


def expelled(n, hate):
    # Enumerate circular seating arrangements directly from the hate relation.
    # Fix the smallest member first to discard rotations; never use point blocks.
    forbidden = {tuple(sorted(pair)) for pair in hate}
    eligible = set()
    for size in range(3, n + 1, 2):
        for members in itertools.combinations(range(1, n + 1), size):
            for tail in itertools.permutations(members[1:]):
                order = (members[0], *tail)
                if all(tuple(sorted((order[i], order[(i + 1) % size]))) not in forbidden
                       for i in range(size)):
                    eligible.update(members)
                    break
    return n - len(eligible)


sat = []
for n in range(1, 3):
    # Self-conflicts are robustness cases; HDU's original bounds were not re-read.
    possible = list(itertools.combinations_with_replacement(range(1, 2 * n + 1), 2))
    for mask in range(1 << len(possible)):
        conflicts = [pair for i, pair in enumerate(possible) if mask >> i & 1]
        sat.append((n, conflicts, representatives(n, conflicts)))
sat_exhaustive = len(sat)
rng = random.Random(18142942)
for _ in range(200):
    n = rng.randrange(1, 10)
    conflicts = [tuple(rng.sample(range(1, 2 * n + 1), 2)) for _ in range(rng.randrange(40))]
    sat.append((n, conflicts, representatives(n, conflicts)))
# Successful rollback, a contradictory group and a free group in the same stream.
n = 10000
chain = [(2 * x - 1, 2 * x + 2) for x in range(1, n)]
chain += [(2 * x, 2 * x + 1) for x in range(1, n)]
chain += [(1, 3), (1, 4)]
sat += [(n, chain, ''.join(f'{2 * x}\n' for x in range(1, n + 1))),
        (2, [(1, 3), (1, 4), (2, 3), (2, 4)], 'NIE\n'),
        (2, [], '1\n3\n')]
run('example-203', ''.join(encode(n, pairs) for n, pairs, _ in sat),
    ''.join(answer for _, _, answer in sat), len(sat),
    'All conflict subsets up to two variables, 200 seeded assignment oracles, '
    '10000-variable rollback chain, contradiction then clean reconstruction; EOF termination')
run('example-203', '', '', 0, 'Immediate EOF')

odd = []
for n in range(1, 6):
    possible = list(itertools.combinations(range(1, n + 1), 2))
    for mask in range(1 << len(possible)):
        hate = [pair for i, pair in enumerate(possible) if mask >> i & 1]
        odd.append((n, hate, expelled(n, hate)))
odd_exhaustive = len(odd)
for _ in range(120):
    n = rng.randrange(6, 9)
    hate = [pair for pair in itertools.combinations(range(1, n + 1), 2) if rng.randrange(2)]
    odd.append((n, hate, expelled(n, hate)))
# UVA 1364 official sample, plus duplicate/reversed/self-hate normalization.
sample = [(1, 4), (1, 5), (2, 5), (3, 4), (4, 5)]
assert expelled(5, sample) == 2
odd.append((5, sample, 2))
normalization = [(1, 4), (4, 1), (1, 4), (1, 1), (4, 4)]
odd.append((4, normalization, expelled(4, normalization)))
# A triangle joined at vertex 3 to a square: odd-cycle membership must not leak
# across an articulation point. A path joined there also stays unmarked.
for n, allowed in [
    (6, {(1, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (3, 6)}),
    (7, {(1, 2), (1, 3), (2, 3), (3, 4), (4, 5), (6, 7)})
]:
    hate = [pair for pair in itertools.combinations(range(1, n + 1), 2) if pair not in allowed]
    assert expelled(n, hate) == n - 3
    odd.append((n, hate, n - 3))
run('example-204', ''.join(encode(n, pairs) for n, pairs, _ in odd) + '0 0\n',
    ''.join(f'{answer}\n' for _, _, answer in odd), len(odd),
    'All simple hate graphs up to five vertices, 120 seeded circular-seating oracles, '
    'UVA official sample, normalization and articulation separation')

n = 1000
large = [(n, [], 0),
         (n, list(itertools.combinations(range(1, n + 1), 2)), n),
         (n, [(u, v) for u, v in itertools.combinations(range(1, n + 1), 2)
              if (u <= n // 2) == (v <= n // 2)], n)]
allowed = {(1, 2), (1, 3), (2, 3)} | {(u - 1, u) for u in range(4, n + 1)}
large.append((n, [pair for pair in itertools.combinations(range(1, n + 1), 2)
                  if pair not in allowed], n - 3))
large.append((n, [(1, 2)] * 1000000, 0))
large.append((1, [], 1))  # Dense/large input must not contaminate the next group.
run('example-204', ''.join(encode(n, pairs) for n, pairs, _ in large) + '0 0\n',
    ''.join(f'{answer}\n' for _, _, answer in large), len(large),
    'Closed-form n=1000 complete/empty/bipartite/triangle-chain complement graphs; '
    '1000000 repeated hate records; singleton reset (zero hate is a local extension)')
run('example-204', '0 0\n3 0\n', '', 0, 'Sentinel must stop before trailing test data')
run('example-204', '', '', 0, 'Immediate EOF')
run('example-204', '3 0\n', '0\n', 1, 'EOF without sentinel is a driver extension')

# Negative controls target the exact serializer, including minimum selection and
# line boundaries; they never execute intentionally broken algorithm code.
negative = 0
for actual, expected in [
    ('2\n3\n', representatives(2, [(1, 3)])),
    ('1 4\n', representatives(2, [(1, 3)])),
    ('1\n3\n', representatives(2, [(1, 3)])),
    ('NIE\n', representatives(1, [])),
    ('NO\n', representatives(2, [(1, 3), (1, 4), (2, 3), (2, 4)])),
    ('3\n', f'{expelled(5, sample)}\n'),
    ('2\n\n', f'{expelled(5, sample)}\n'),
    ('0\n', '')
]:
    try:
        exact(actual, expected)
    except AssertionError:
        negative += 1
    else:
        raise AssertionError('Negative output accepted')

assert hashes() == source_hashes, 'Source input changed during focused run'
assert hashlib.sha256(compiler.read_bytes()).hexdigest() == compiler_hash
report = dict(
    status='PASS', mode=mode, completed_utc=datetime.now(timezone.utc).isoformat(),
    command=f'CPC_SANITIZE={int(mode == "sanitizer")} python3 tests/graph_printed_usages.py',
    compiler=dict(path=str(compiler), sha256=compiler_hash,
                  version=subprocess.check_output([str(compiler), '--version'], text=True).splitlines()[0],
                  target=subprocess.check_output([str(compiler), '-dumpmachine'], text=True).strip()),
    platform=platform.platform(), python=sys.version, compile_commands=commands,
    sanitizer_options={k: env[k] for k in ('ASAN_OPTIONS', 'UBSAN_OPTIONS')},
    stack_bytes=dict(before=stack_before, actual=stack_actual),
    exhaustive_conflict_sets=sat_exhaustive, exhaustive_simple_hate_graphs=odd_exhaustive,
    negative_output_controls=negative, programs=programs, sha256=source_hashes,
    scope='Exact registered printed programs, independent assignment/circular-seating oracles '
          'and closed-form scale cases. No algorithm or driver edits. ASan/UBSan only; '
          'LeakSanitizer disabled. Not a full-suite run, official-template classification, '
          'online AC, ranking or official HDU/POJ maximum-constraint claim.'
)
report_path = root / 'build' / f'graph-printed-usages-{mode}.json'
report_path.write_text(json.dumps(report, indent=2) + '\n')
print(f'Graph printed usages {mode}: PASS; SAT {len(sat)} datasets; '
      f'round-table {len(odd) + len(large) + 1} datasets; '
      f'{negative} negative controls; {report_path.relative_to(root)}')
