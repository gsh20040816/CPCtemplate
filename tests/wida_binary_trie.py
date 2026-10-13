"""Audit WIDA 09B binary trie. The file has no root setup and f[0] stays 0."""
import hashlib, os, random, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = (root / 'tests/fixtures/wida_binary_trie/main.cpp').read_bytes()
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '47c6850d2a957c9e4e2cfbb52d168c57f7c14c9d'
text = blob.decode().replace('\r\n', '\n')
assert 'int main' not in text and 'f[0]' not in text
assert text.count('newNode();') == 1 and 'q = newNode();' in text

INF = 10**9

def run_model(inserts, queries, sentinel):
    trie = [[0, 0]]
    owner = [sentinel]
    tot = 0

    def new_node():
        nonlocal tot
        tot += 1
        trie.append([0, 0])
        owner.append(INF)
        return tot

    new_node()
    for x, i in inserts:
        p = 1
        for bit in range(29, -1, -1):
            d = (x >> bit) & 1
            if trie[p][d] == 0:
                trie[p][d] = new_node()
            p = trie[p][d]
            owner[p] = min(owner[p], i)
    out = []
    for a, b in queries:
        ans1 = ans2 = INF
        p = 1
        for bit in range(29, -1, -1):
            d = (a >> bit) & 1
            e = (b >> bit) & 1
            if e:
                ans1 = min(ans1, owner[trie[p][d]])
            else:
                ans2 = min(ans2, owner[trie[p][d ^ 1]])
            p = trie[p][e ^ d]
        ans1 = min(ans1, owner[p])
        ans2 = min(ans2, owner[p])
        out.append(-1 if ans1 == INF or ans2 == INF else max(1, ans1, ans2))
    return out

rng = random.Random(9)
cases = [([(0, 3)], [(0, 0), (0, 1)]), ([(1, 4), (2, 8), (1, 2)], [(1, 2), (3, 1), (0, 0)])]
for _ in range(30):
    inserts = [(rng.randrange(1 << 30), rng.randrange(1, 50)) for _ in range(rng.randrange(1, 8))]
    queries = [(rng.randrange(1 << 30), rng.randrange(1 << 30)) for _ in range(6)]
    cases.append((inserts, queries))
assert run_model([(0, 3)], [(0, 1)], 0) != run_model([(0, 3)], [(0, 1)], INF)

def payload(inserts, queries):
    lines = [str(len(inserts))]
    lines += [f'{x} {i}' for x, i in inserts]
    lines.append(str(len(queries)))
    lines += [f'{a} {b}' for a, b in queries]
    return '\n'.join(lines) + '\n'

out = root / 'build/wida-binary-trie'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_binary_trie.cpp'
report = []
for mode, flags in [('normal', ['-O2', '-DNDEBUG']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    raw = subprocess.run([str(exe), 'raw'], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert raw.stdout == '1 3 1\n' and raw.stderr == ''
    checks = 3
    for inserts, queries in cases:
        for sentinel, label in ((0, 'source'), (INF, 'sentinel')):
            got = subprocess.run([str(exe), label], input=payload(inserts, queries), text=True,
                                 capture_output=True, env=env, timeout=30, check=True)
            assert got.stderr == ''
            lines = list(map(int, got.stdout.split()))
            expect = run_model(inserts, queries, sentinel)
            assert lines[:-1] == expect
            assert lines[-1] == sentinel
            checks += len(expect) + 1
    report.append(dict(mode=mode, checks=checks, cases=len(cases)))
    print(mode, checks, 'checks PASS', flush=True)

import json
(root / 'verification/wida-binary-trie.json').write_text(json.dumps(dict(
    scope='Exact 09B functions. raw add(0,3) without newNode makes trie[1][0] point at the root. Source leaves f[0]=0; setting it to inf is a test-only mutation and changes results. No main, no problem statement, no persistent xor trie equivalence.',
    blob='47c6850d2a957c9e4e2cfbb52d168c57f7c14c9d', runs=report), indent=2) + '\n')
