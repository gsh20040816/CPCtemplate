#!/usr/bin/env python3
"""Exact small partition bijections and current limited API; no online claim."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import os
import subprocess
from compiler_config import CXX


@lru_cache(None)
def partitions(n, maximum):
    if n == 0:
        return ((),)
    return tuple((first,) + tail for first in range(min(n, maximum), 0, -1)
                 for tail in partitions(n - first, first))


def conjugate(p):
    return tuple(sum(x >= i for x in p) for i in range(1, (p[0] if p else 0) + 1))


def allowed(n, values):
    if n < 0:
        return 0
    dp = [1] + [0] * n
    for part in values:
        for s in range(part, n + 1):
            dp[s] += dp[s - part]
    return dp[n]


def A(n, k):
    return allowed(n, range(1, min(n, k) + 1))


def main():
    if not __debug__ or os.environ.get('PYTHONOPTIMIZE') not in (None, '', '0'):
        raise SystemExit('Validation requires assertions')
    root = Path(__file__).resolve().parents[1]
    fixture = root / 'tests/fixtures/partition-knowledge'
    manifest = json.loads((fixture / 'manifest.json').read_text())
    original = (fixture / 'original.tex').read_text()
    assert hashlib.sha256(original.encode()).hexdigest() == manifest['original_sha256']
    lines = original.splitlines(keepends=True)
    for patch in reversed(manifest['amendments']):
        a, b = patch['start'], patch['end']
        assert ''.join(lines[a:b]) == patch['old']
        lines[a:b] = patch['new'].splitlines(keepends=True)
    text = (root / 'docs/knowledge-partitions.tex').read_text()
    assert text == ''.join(lines), 'unlisted migration amendment'
    for target in ['compact-Partitions', 'usage-example-158', 'usage-example-159']:
        assert r'\ref{' + target + '}' in text and r'\pageref{' + target + '}' in text
    mapping = json.loads((root / 'docs/knowledge-taxonomy.json').read_text())
    rows = [r for r in mapping['entries'] if r['label'] == 'knowledge-partitions']
    assert len(rows) == 1 and rows[0]['path'] == 'math/combinatorics/partition.md'
    queries = []
    partition_count = constraint_count = 0
    mods = [1, 2, 6, 8, 97, 998244353, 1000000007, (1 << 31) - 1]
    for n in range(31):
        ps = partitions(n, n)
        partition_count += len(ps)
        for p in ps:
            c = conjugate(p)
            assert sum(c) == n and conjugate(c) == p
        for k in range(33):
            at_most = {p for p in ps if len(p) <= k}
            small_parts = {p for p in ps if not p or p[0] <= k}
            assert {conjugate(p) for p in at_most} == small_parts
            assert len(small_parts) == A(n, k)
            exact = {p for p in ps if len(p) == k}
            shifted = {tuple(x - 1 for x in p if x > 1) for p in exact}
            target = {p for p in partitions(n - k, max(0, n - k)) if len(p) <= k} if n >= k else set()
            assert shifted == target and len(exact) == len(shifted) == A(n - k, k)
            distinct = {p for p in exact if len(set(p)) == k}
            staircase = {tuple(x - (k - i) for i, x in enumerate(p) if x > k - i) for p in distinct}
            s = n - k * (k + 1) // 2
            target = {p for p in partitions(s, s) if len(p) <= k} if s >= 0 else set()
            assert staircase == target and len(distinct) == len(staircase) == A(s, k)
            limited = sum(max(Counter(p).values(), default=0) <= k for p in ps)
            assert limited == allowed(n, (v for v in range(1, n + 1) if v % (k + 1)))
            for mod in mods:
                queries.append((mod, n, k, limited % mod))
            constraint_count += 1
        for mod in mods:
            queries.append((mod, n, (1 << 31) - 1, len(ps) % mod))
    assert A(5, 2) == 3 and A(3, 2) == 2
    assert sum(max(Counter(p).values(), default=0) <= 2 for p in partitions(5, 5)) == 5
    assert A(4, 2) == 3 and A(3, 2) == 2
    build = root / 'build'
    build.mkdir(exist_ok=True)
    source = build / 'partition-knowledge-api.cpp'
    source.write_text('''#include "../src/compact/partitions.hpp"
#include <iostream>
int main() {
    int q; std::cin >> q;
    while (q--) {
        int mod, n, k; std::cin >> mod >> n >> k;
        Partitions a(30, mod);
        std::cout << a.limited(n, k) << '\\n';
    }
}
''')
    exe = build / 'partition-knowledge-api'
    san = os.environ.get('CPC_SANITIZE', os.environ.get('SANITIZE', '0')) == '1'
    flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if san else ['-O2']
    subprocess.run([CXX, '-std=c++20', *flags, str(source), '-o', str(exe)], check=True)
    data = str(len(queries)) + '\n' + ''.join(f'{mod} {n} {k}\n' for mod, n, k, _ in queries)
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=120)
    assert not result.stderr, result.stderr
    assert list(map(int, result.stdout.split())) == [q[3] for q in queries]
    print(f'Partition knowledge: {partition_count} exact partitions/conjugations; {constraint_count} constraint rows; {len(queries)} current limited API answers across {len(mods)} moduli PASS')


if __name__ == '__main__':
    main()
