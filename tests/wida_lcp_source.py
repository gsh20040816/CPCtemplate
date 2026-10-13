"""Audit the truncated WIDA LCP example. The fixture prints nothing."""
import hashlib, os, random, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
fixture = root / 'tests/fixtures/wida_lcp/main.cpp'
blob = fixture.read_bytes()
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == 'b36bd5568fc01ca8f1641100df0d5a74634ba274'
text = blob.decode()
normalized = text.replace('\r\n', '\n')
assert '#include' not in normalized and 'cout' not in normalized and 'printf' not in normalized
loop = '''        int p = 1;
        for (auto c : S[i]) {
            p = extend(p, c - 'a');
            if (f[p] != -1) {
                if (f[p] == 0) {
                    f[p] = i + 1;
                } else if (f[p] != i + 1) {
                    f[p] = -1;
                }
            }
        }'''
assert loop in normalized
assert 'adj[lnk[i]].push_back(i);' in normalized
assert normalized.rstrip().endswith('}')

def simulate(strings):
    length = [0, 0]
    link = [0, 0]
    nxt = [[0] * 26, [0] * 26]
    owner = [0, 0]
    children = [[], []]
    tot = 1
    nxt[0] = [1] * 26
    length[0] = -1

    def ensure(n):
        while len(length) <= n:
            length.append(0)
            link.append(0)
            nxt.append([0] * 26)
            owner.append(0)
            children.append([])

    def extend(p, c):
        nonlocal tot
        if nxt[p][c]:
            q = nxt[p][c]
            if length[q] == length[p] + 1:
                return q
            tot += 1
            r = tot
            ensure(r)
            length[r] = length[p] + 1
            link[r] = link[q]
            nxt[r] = nxt[q][:]
            link[q] = r
            while nxt[p][c] == q:
                nxt[p][c] = r
                p = link[p]
            return r
        tot += 1
        cur = tot
        ensure(cur)
        length[cur] = length[p] + 1
        while not nxt[p][c]:
            nxt[p][c] = cur
            p = link[p]
        link[cur] = extend(p, c)
        return cur

    for i, s in enumerate(strings):
        p = 1
        for ch in s:
            p = extend(p, ord(ch) - 97)
            if owner[p] != -1:
                if owner[p] == 0:
                    owner[p] = i + 1
                elif owner[p] != i + 1:
                    owner[p] = -1
    ensure(tot)
    for i in range(1, tot + 1):
        children[link[i]].append(i)
    return tot, length, link, owner, nxt, children

def parse_dump(out, tot_expected):
    lines = out.splitlines()
    assert int(lines[0]) == tot_expected
    rows = []
    for line in lines[1:]:
        parts = list(map(int, line.split()))
        length, link, owner, *rest = parts
        trans = rest[:26]
        count = rest[26]
        kids = rest[27:]
        assert count == len(kids)
        rows.append((length, link, owner, trans, kids))
    assert len(rows) == tot_expected + 1
    return rows

rng = random.Random(8)
groups = [[], ['a'], ['ab', 'a'], ['ab', 'ba', 'a'], ['aaa', 'aa', 'a'], ['abc', 'ab', 'bc', 'b']]
for _ in range(40):
    group = []
    for _k in range(rng.randrange(1, 8)):
        group.append(''.join(rng.choice('abcd') for _ in range(rng.randrange(1, 12))))
    groups.append(group)
groups.append(['a' * 300, 'a' * 299 + 'b', 'b' * 40])

out = root / 'build/wida-lcp'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_lcp_source.cpp'
report = []
builds = [
    ('state-o2', ['-O2', '-DNDEBUG'], 'state'),
    ('main-o0', ['-O0', '-fno-unreachable-traps'], 'main'),
    ('sanitizer', ['-O1', '-g', '-fno-unreachable-traps', '-fsanitize=address,undefined', '-fno-sanitize=return'], 'both'),
]
for mode, flags, kind in builds:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    checks = 0
    for group in groups:
        payload = str(len(group)) + '\n' + '\n'.join(group) + '\n'
        if kind in ('state', 'both'):
            state = subprocess.run([str(exe), 'state'], input=payload, text=True, capture_output=True, env=env, timeout=30, check=True)
            assert state.stderr == ''
            tot, length, link, owner, nxt, children = simulate(group)
            rows = parse_dump(state.stdout, tot)
            for i, (ln, lk, ow, trans, kids) in enumerate(rows):
                assert ln == length[i] and lk == link[i] and ow == owner[i]
                assert trans == nxt[i] and kids == children[i]
                checks += 29 + len(kids)
        if kind in ('main', 'both'):
            raw = subprocess.run([str(exe), 'main'], input=payload, text=True, capture_output=True, env=env, timeout=30, check=True)
            assert raw.stdout == '' and raw.stderr == '' and raw.returncode == 0
            checks += 1
    report.append(dict(mode=mode, groups=len(groups), checks=checks))
    print(mode, checks, 'checks PASS', flush=True)

o2main = out / 'main-o2'
subprocess.run([CXX, '-std=c++20', '-O2', '-DNDEBUG', '-fno-unreachable-traps', str(src), '-o', str(o2main)], check=True)
o2 = subprocess.run([str(o2main), 'main'], input='0\n', text=True, capture_output=True, env=env, timeout=30)
report.append(dict(mode='main-o2-empty', returncode=o2.returncode, stderr=o2.stderr.strip(), stdout=o2.stdout))
print('main-o2', o2.returncode, o2.stderr.strip(), flush=True)

import json
(root / 'verification/wida-lcp-example.json').write_text(json.dumps(dict(
    scope='Exact truncated generalized-SAM fragment. Python mirrors extend, unique-string marks and the unused link tree. Original main prints nothing at -O0/-O1. No problem identity and no answer function. -O2 main is recorded separately.',
    blob='b36bd5568fc01ca8f1641100df0d5a74634ba274',
    runs=report), indent=2) + '\n')
