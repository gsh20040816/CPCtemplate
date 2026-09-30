#!/usr/bin/env python3
"""Independent finite enumeration for docs/knowledge-mobius.tex and current APIs.

Run with Python 3 and C++20. SANITIZE=1 enables ASan+UBSan.
Sanitized child processes default to ASAN_OPTIONS=detect_leaks=0 because
LeakSanitizer is incompatible with this ptrace-based executor; leaks are untested.
Caller-provided sanitizer options are preserved.
All compiler products are temporary. No network or OJ submission is involved.
"""
from collections import Counter
from itertools import combinations, product
from math import gcd, isqrt
from pathlib import Path
import os
import re
import subprocess
import tempfile

from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]


def mu_trial(n):
    """Independent prime factorization, with no linear-sieve recurrence."""
    result = 1
    for p in range(2, isqrt(n) + 1):
        if n % p == 0:
            n //= p
            if n % p == 0:
                return 0
            result = -result
    return -result if n > 1 else result


def phi_trial(n):
    result, remaining = n, n
    for p in range(2, isqrt(n) + 1):
        if remaining % p == 0:
            result = result // p * (p - 1)
            while remaining % p == 0:
                remaining //= p
    if remaining > 1:
        result = result // remaining * (remaining - 1)
    return result


def prefix(values):
    out = [0]
    for value in values:
        out.append(out[-1] + value)
    return out


def brute_pairs(a, b, c, d, k):
    return sum(gcd(x, y) == k for x in range(a, b + 1)
               for y in range(c, d + 1))


def quotient_blocks(a, b):
    left = 1
    while left <= min(a, b):
        x, y = a // left, b // left
        right = min(a // x, b // y)
        yield left, right, x, y
        left = right + 1


def main():
    stats = Counter()
    mu = [0] + [mu_trial(n) for n in range(1, 20001)]
    phi = [0] + [phi_trial(n) for n in range(1, 20001)]
    pmu, pphi = prefix(mu[1:]), prefix(phi[1:])
    for n in range(1, 121):
        assert phi[n] == sum(gcd(n, x) == 1 for x in range(1, n + 1))
        assert sum(mu[d] for d in range(1, n + 1) if n % d == 0) == (n == 1)
        stats['trial-factor base checks'] += 1

    # Neither divisor inversion nor finite-support multiple inversion needs
    # multiplicativity. Test explicitly nonmultiplicative signed sequences.
    values = [0] + [(n * n + 3 * n) % 13 - 6 for n in range(1, 121)]
    divisor = [0] + [sum(values[d] for d in range(1, n + 1) if n % d == 0)
                     for n in range(1, 121)]
    multiples = [0] + [sum(values[n::n]) for n in range(1, 121)]
    for n in range(1, 121):
        assert sum(mu[d] * divisor[n // d]
                   for d in range(1, n + 1) if n % d == 0) == values[n]
        assert sum(mu[t] * multiples[n * t]
                   for t in range(1, 120 // n + 1)) == values[n]
        stats['inversion sequences'] += 2

    for size in range(5):
        for a in product(range(1, 7), repeat=size):
            histogram = Counter(gcd(x, y) for x, y in combinations(a, 2))
            count = [0] + [sum(x % d == 0 for x in a) for d in range(1, 7)]
            whole = [c * (c - 1) // 2 for c in count]
            exact = whole.copy()
            for k in range(6, 0, -1):
                exact[k] -= sum(exact[2 * k::k])
                via_mu = sum(mu[t] * whole[k * t] for t in range(1, 6 // k + 1))
                assert via_mu == exact[k] == histogram[k], (a, k)
                stats['array gcd histogram coefficients'] += 1
    assert brute_pairs(1, 3, 1, 4, 1) == 9
    assert sum(gcd(x, y) for x in range(1, 4) for y in range(1, 5)) == 16
    assert sum(mu[d] * d * (3 // d) * (4 // d) for d in range(1, 4)) == 5
    assert sum(gcd(x, y) == 1 for x, y in combinations((2, 3, 4, 6), 2)) == 2
    assert sum(gcd(x, y) == 1 for x, y in combinations((1, 1, 2), 2)) == 3

    cases, expected = [], []

    def add(case, answer):
        cases.append(case)
        expected.append(answer)

    for a in range(41):
        for b in range(41):
            coprime = brute_pairs(1, a, 1, b, 1)
            weighted = sum(gcd(x, y) for x in range(1, a + 1)
                           for y in range(1, b + 1))
            add(f'C {a} {b}', coprime)
            add(f'W {a} {b}', weighted)
            for weight in (lambda n: n, lambda n: int(n == 1),
                           lambda n: n * n % 7 - 3):
                h = [0] + [sum(mu[d] * weight(n // d)
                               for d in range(1, n + 1) if n % d == 0)
                           for n in range(1, min(a, b) + 1)]
                reference = sum(weight(gcd(x, y)) for x in range(1, a + 1)
                                for y in range(1, b + 1))
                assert reference == sum(h[d] * (a // d) * (b // d)
                                        for d in range(1, min(a, b) + 1))
                stats['weighted gcd identities'] += 1
            ph = prefix(mu[1:min(a, b) + 1])
            grouped = 0
            last = 0
            for l, r, x, y in quotient_blocks(a, b):
                assert l == last + 1 and l <= r <= min(a, b)
                assert all((a // d, b // d) == (x, y) for d in range(l, r + 1))
                assert r == min(a, b) or (a // (r + 1), b // (r + 1)) != (x, y)
                grouped += (ph[r] - ph[l - 1]) * x * y
                last = r
            assert last == min(a, b) and grouped == coprime
            stats['quotient partitions'] += 1
    for m in range(1, 101):
        assert len(list(quotient_blocks(m, m * m))) == m
        stats['skewed-rectangle partitions'] += 1
    assert (3, 3, 3, 2) in list(quotient_blocks(10, 8))
    assert 8 // (8 // 3) == 4 and 10 // 3 != 10 // 4

    for a in range(1, 9):
        for b in range(a, 9):
            for c in range(1, 9):
                for d in range(c, 9):
                    for k in range(1, 11):
                        add(f'R {a} {b} {c} {d} {k}', brute_pairs(a, b, c, d, k))
    add('R 3 8 5 10 2', 6)
    assert [brute_pairs(1, a, 1, b, 1) for a, b in ((4, 5), (1, 5), (4, 2), (1, 2))] == [15, 5, 6, 2]
    assert [(x, y) for x in range(3, 9) for y in range(5, 11) if gcd(x, y) == 2] == [
        (4, 6), (4, 10), (6, 8), (6, 10), (8, 6), (8, 10)]

    for low in range(1, 9):
        for high in range(low, 9):
            for k in range(1, 11):
                total = brute_pairs(low, high, low, high, k)
                diagonal = int(low <= k <= high)
                strict = sum(gcd(x, y) == k for x in range(low, high + 1)
                             for y in range(x + 1, high + 1))
                assert (total - diagonal) // 2 == strict
                assert (total + diagonal) // 2 == strict + diagonal
                stats['ordered/unordered conversions'] += 1
    for a in range(10):
        for b in range(10):
            for k in range(1, 11):
                positive = brute_pairs(1, a, 1, b, k)
                assert brute_pairs(0, a, 0, b, k) == positive + int(k <= a) + int(k <= b)
                stats['zero-axis corrections'] += 1
    assert brute_pairs(1, 5, 1, 5, 1) == 19 and pphi[5] == 10
    assert brute_pairs(1, 2, 1, 3, 1) == 5

    for n in range(1, 501):
        assert pmu[n] == 1 - sum(pmu[n // i] for i in range(2, n + 1))
        assert pphi[n] == n * (n + 1) // 2 - sum(pphi[n // i] for i in range(2, n + 1))
        stats['DuJiao identities'] += 2
    for limit in (1, 7, 64, 1024):
        queries = list(range(1025)) + [20000, 10007, 9973, 20000, 0, 1, 1024, 1023]
        for n in queries:
            add(f'D {limit} {n}', f'{pmu[n]} {pphi[n]}')
    for n in range(101):
        add(f'S {n}', brute_pairs(1, n, 1, n, 1))
    for a, b in ((0, 2147483647), (2147483647, 0), (1, 2147483647), (2147483647, 1)):
        add(f'C {a} {b}', 0 if min(a, b) == 0 else max(a, b))
    add('E', 6)

    document = (ROOT / 'docs/knowledge-mobius.tex').read_text()
    example = re.search(r'% BEGIN mobius-rectangle-example\s*\\begin\{lstlisting\}\n(.*?)'
                        r'\\end\{lstlisting\}', document, re.S).group(1)
    source = r'''
#include "src/compact/coprime_pairs.hpp"
#include "src/compact/algebra.hpp"
using I = __int128_t;
void print(I x)
{
    if (x < 0) cout << '-', x = -x;
    if (x >= 10) print(x / 10);
    cout << char('0' + x % 10);
}
I weighted(int a, int b, const vector<long long> &prefix)
{
    I answer = 0;
    for (long long l = 1, r; l <= min(a, b); l = r + 1)
    {
        long long x = a / l, y = b / l;
        r = min(a / x, b / y);
        answer += I(prefix[r] - prefix[l - 1]) * x * y;
    }
    return answer;
}
int main()
{
    CoprimePairs pairs(40);
    LinearSieve sieve(40);
    vector<long long> prefix(41);
    for (int i = 1; i <= 40; i++) prefix[i] = prefix[i - 1] + sieve.phi[i];
    map<int, DuJiao> solvers;
    for (int limit : {1, 7, 64, 1024}) solvers.emplace(limit, DuJiao(limit));
    char op;
    while (cin >> op)
    {
        if (op == 'C' || op == 'W')
        {
            int a, b;
            cin >> a >> b;
            if (op == 'C') print(pairs.count(a, b));
            else print(weighted(a, b, prefix));
        }
        else if (op == 'R')
        {
            int a, b, c, d, k;
            cin >> a >> b >> c >> d >> k;
            print(pairs.rectangle(a, b, c, d, k));
        }
        else if (op == 'D')
        {
            int limit;
            long long n;
            cin >> limit >> n;
            auto &solver = solvers.at(limit);
            print(solver.mertens(n));
            cout << ' ';
            print(solver.totient_sum(n));
        }
        else if (op == 'S')
        {
            long long n;
            cin >> n;
            print(n == 0 ? 0 : 2 * solvers.at(7).totient_sum(n) - 1);
        }
        else if (op == 'E')
        {
            // This body is copied verbatim from the LaTeX listing at runtime.
            auto example = []()
            {
__EXAMPLE__
                return answer;
            };
            print(example());
        }
        cout << '\n';
    }
    for (auto &[limit, solver] : solvers)
    {
        assert(solver.mmu.count(20000) && solver.mphi.count(20000));
        auto m = solver.mertens(20000);
        auto p = solver.totient_sum(20000);
        solver.mmu.clear();
        solver.mphi.clear();
        assert(solver.mertens(20000) == m && solver.totient_sum(20000) == p);
    }
}
'''.replace('__EXAMPLE__', example)
    flags = ['-std=c++20', '-O2', '-Wall', '-Wextra']
    mode = 'normal'
    environment = os.environ.copy()
    if os.environ.get('SANITIZE') == '1':
        flags = ['-std=c++20', '-O1', '-g', '-Wall', '-Wextra',
                 '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie']
        mode = 'ASan/UBSan'
        environment.setdefault('ASAN_OPTIONS', 'detect_leaks=0')
        environment.setdefault('UBSAN_OPTIONS', 'halt_on_error=1')
    with tempfile.TemporaryDirectory(prefix='cpc-mobius-') as temporary:
        cpp, exe = Path(temporary) / 'check.cpp', Path(temporary) / 'check'
        cpp.write_text(source)
        subprocess.run([CXX, *flags, '-I', str(ROOT), str(cpp), '-o', str(exe)], check=True)
        result = subprocess.run([str(exe)], input='\n'.join(cases) + '\n', text=True,
                                capture_output=True, check=False, timeout=120, env=environment)
        assert result.returncode == 0, (result.returncode, result.stderr)
    assert not result.stderr, result.stderr
    actual = result.stdout.splitlines()
    assert len(actual) == len(expected), (len(actual), len(expected))
    for case, got, want in zip(cases, actual, expected):
        assert got == str(want), (case, got, want)
    print(f'PASS ({mode}): {len(cases)} current C++ API cases, including exact LaTeX listing')
    print(f'PASS: {sum(stats.values())} independent Python formula/model cases')
    for label, number in sorted(stats.items()):
        print(f'  {label}: {number}')
    print('Four DuJiao pre-sieve limits; repeated, zero and cache-cleared queries checked.')
    print('Local evidence only; no online AC, huge-N benchmark or new algorithm claim.')


if __name__ == '__main__':
    main()
