#!/usr/bin/env python3
"""Independent small-object enumeration + real compact API integration.

Run from any directory with Python 3 and a C++20 compiler (CXX, default g++).
No third-party Python packages; generated C++ and binaries stay in a temp dir.
"""
from collections import Counter
from itertools import product
from math import comb
from pathlib import Path
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MOD = 998244353


def bounded_counts(caps):
    counts = Counter(map(sum, product(*(range(c + 1) for c in caps))))
    return [counts[n] for n in range(sum(caps) + 3)]


def words(total):
    if total == 0:
        return [()]
    return [(s,) + tail for s in (1, 2) if s <= total
            for tail in words(total - s)]


def partitions(n):
    """Canonical restricted-growth construction, not a counting recurrence."""
    out = []

    def visit(i, blocks):
        if i == n:
            out.append(tuple(tuple(b) for b in blocks))
            return
        for b in blocks:
            if len(b) < 2:
                b.append(i)
                visit(i + 1, blocks)
                b.pop()
        blocks.append([i])
        visit(i + 1, blocks)
        blocks.pop()

    visit(0, [])
    assert len(out) == len(set(out))
    return Counter(map(len, out))


def main():
    cases = []
    expected = []
    for k in range(4):
        for caps in product(range(4), repeat=k):
            want = bounded_counts(caps)
            for n, answer in enumerate(want):
                cases.append("B " + " ".join(map(str, (n, k, *caps))))
                expected.append(answer)
    for k in range(6):
        for cap in range(5):
            counts = bounded_counts([cap] * k)
            for n in range(min(sum([cap] * k) + 3, 16)):
                cases.append(f"P {n} {k} {cap}")
                expected.append(counts[n])
                if k:
                    ie = sum((-1) ** j * comb(k, j) * comb(n - j * (cap + 1) + k - 1, k - 1)
                             for j in range(min(k, n // (cap + 1)) + 1))
                    assert ie == counts[n]
    for n in range(13):
        cases.append(f"W {n}")
        expected.append(len(words(n)))
    for n in range(9):
        by_blocks = partitions(n)
        cases.append(f"E {n}")
        expected.append(sum(by_blocks.values()))
        for k in range(n + 2):
            cases.append(f"K {n} {k}")
            expected.append(by_blocks[k])
    for n in range(31):
        for k in range(n + 3):
            answer = comb(n, k) if k <= n else 0
            cases.append(f"C {n} {k}")
            expected.append(answer % MOD)
            for mod in (2, 3, 5, 7, 11):
                cases.append(f"L {n} {k} {mod}")
                expected.append(answer % mod)
            for mod in (1, 4, 6, 8, 9, 12, 25, 27, 32):
                cases.append(f"X {n} {k} {mod}")
                expected.append(answer % mod)
    source = r'''
#include "src/compact/fps_power.hpp"
#include "src/compact/lucas.hpp"
#include "src/compact/exlucas.hpp"
using F = FpsFunctions;
using Z = F::Z;
int main() {
    Binomial<998244353> comb(64);
    char op;
    while (std::cin >> op) {
        int n;
        std::cin >> n;
        Z answer;
        if (op == 'B' || op == 'P') {
            int k;
            std::cin >> k;
            F::Poly a{1};
            if (op == 'B') {
                for (int i = 0; i < k; ++i) {
                    int cap;
                    std::cin >> cap;
                    F::Poly b(std::min(cap, n) + 1, Z(1));
                    a = F::multiply(a, b);
                    if ((int)a.size() > n + 1) a.resize(n + 1);
                }
                a.resize(n + 1);
            } else {
                int cap;
                std::cin >> cap;
                F::Poly b(std::min(cap, n) + 1, Z(1));
                a = FpsPower::power(b, std::to_string(k), n + 1);
            }
            answer = a[n];
        } else if (op == 'W') {
            answer = F::inverse(F::Poly{1, -1, -1}, n + 1)[n];
        } else if (op == 'E' || op == 'K') {
            F::Poly b(n + 1);
            if (n >= 1) b[1] = 1;
            if (n >= 2) b[2] = Z(2).inv();
            if (op == 'E') {
                answer = F::exp(b, n + 1)[n] * comb.fac[n];
            } else {
                int k;
                std::cin >> k;
                auto f = FpsPower::power(b, std::to_string(k), n + 1);
                answer = f[n] * comb.fac[n] * comb.ifac[k];
            }
        } else {
            int k, mod;
            std::cin >> k;
            if (op == 'C') answer = comb.choose(n, k);
            if (op == 'L') {
                std::cin >> mod;
                answer = Lucas(mod).choose(n, k);
            }
            if (op == 'X') {
                std::cin >> mod;
                answer = ExLucas(mod).choose(n, k);
            }
        }
        std::cout << answer.v << '\n';
    }
}
'''
    with tempfile.TemporaryDirectory(prefix="cpc-combinatorics-") as temp:
        cpp, exe = Path(temp) / "check.cpp", Path(temp) / "check"
        cpp.write_text(source)
        subprocess.run([os.environ.get("CXX", "g++"), "-std=c++20", "-O2",
                        "-Wall", "-Wextra", "-I", str(ROOT), str(cpp), "-o", str(exe)], check=True)
        result = subprocess.run([str(exe)], input="\n".join(cases) + "\n", text=True,
                                capture_output=True, check=True)
    actual = list(map(int, result.stdout.split()))
    assert len(actual) == len(expected), (len(actual), len(expected))
    for case, got, want in zip(cases, actual, expected):
        assert got == want % MOD, (case, got, want)
    assert bounded_counts((2, 3, 1))[4] == 5
    assert len(words(3)) == 3 and len(words(5)) == 8
    assert sum(partitions(4).values()) == 10 and partitions(4)[2] == 3
    print(f"PASS: {len(cases)} current C++ API cases; independent object enumeration and exact binomials")


if __name__ == "__main__":
    main()
