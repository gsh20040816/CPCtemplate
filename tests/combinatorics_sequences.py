#!/usr/bin/env python3
"""Check every identity in docs/knowledge-sequences.tex by enumeration or exact fractions."""
from fractions import Fraction
from itertools import permutations
from math import comb, factorial, e
import subprocess
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
checks = 0


def ok(c, *w):
    global checks
    assert c, w
    checks += 1


# derangements
D = [1, 0]
for n in range(2, 30):
    D.append((n - 1) * (D[n - 1] + D[n - 2]))
for n in range(0, 9):
    perms = list(permutations(range(n)))
    fixed = [sum(p[i] == i for i in range(n)) for p in perms]
    ok(fixed.count(0) == D[n], 'derangement', n)
    for k in range(n + 1):
        ok(fixed.count(k) == comb(n, k) * D[n - k], 'k fixed', n, k)
for n in range(1, 30):
    ok(D[n] == n * D[n - 1] + (-1) ** n, 'D alt')
    ok(D[n] == sum(Fraction(factorial(n) * (-1) ** k, factorial(k)) for k in range(n + 1)), 'D sum')
for n in range(1, 18):
    ok(D[n] == round(factorial(n) / e), 'nearest', n)


# Bell numbers by set-partition enumeration
def partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in partitions(rest):
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]
        yield [[first]] + p


B = [1]
for n in range(0, 25):
    B.append(sum(comb(n, k) * B[k] for k in range(n + 1)))
for n in range(0, 9):
    ok(sum(1 for _ in partitions(list(range(n)))) == B[n], 'bell enum', n)


def stirling2(n, k):
    return sum((-1) ** i * comb(k, i) * (k - i) ** n for i in range(k + 1)) // factorial(k)


for n in range(0, 20):
    ok(B[n] == sum(stirling2(n, k) for k in range(n + 1)), 'bell stirling', n)
tri = [[1]]
for n in range(1, 20):
    row = [tri[-1][-1]]
    for k in range(1, n + 1):
        row.append(row[k - 1] + tri[-1][k - 1])
    tri.append(row)
for n in range(20):
    ok(tri[n][0] == B[n], 'bell triangle', n)
# EGF exp(e^x - 1): series exp(g) via f' = g' f with exact fractions
N = 16
g = [Fraction(0)] + [Fraction(1, factorial(k)) for k in range(1, N)]
f = [Fraction(1)] + [Fraction(0)] * (N - 1)
for k in range(1, N):
    f[k] = sum(j * g[j] * f[k - j] for j in range(1, k + 1)) / k
for n in range(N):
    ok(f[n] * factorial(n) == B[n], 'bell egf', n)
for p in (2, 3, 5, 7, 11):
    for n in range(0, 10):
        ok((B[n + p] - B[n] - B[n + 1]) % p == 0, 'touchard', p, n)

# Bernoulli numbers (B1 = -1/2) and power sums
Bern = [Fraction(1)]
for m in range(1, 40):
    Bern.append(-sum(comb(m + 1, j) * Bern[j] for j in range(m)) / (m + 1))
ok(Bern[1] == Fraction(-1, 2) and Bern[2] == Fraction(1, 6) and Bern[4] == Fraction(-1, 30))
for k in range(3, 40, 2):
    ok(Bern[k] == 0, 'odd bernoulli', k)
for k in range(0, 15):
    for n in range(0, 30):
        lhs = sum(i ** k for i in range(n))
        rhs = sum(comb(k + 1, j) * Bern[j] * n ** (k + 1 - j) for j in range(k + 1)) / (k + 1)
        ok(lhs == rhs, 'power sum', k, n)
P = 998244353
exe = root / 'build/bernoulli_driver'
subprocess.run([CXX, '-std=c++20', '-O2', str(root / 'tests/bernoulli_driver.cpp'), '-o', str(exe)], check=True)
got = list(map(int, subprocess.run([str(exe)], input='39\n', capture_output=True, text=True, check=True).stdout.split()))
for k in range(40):
    ok(got[k] == Bern[k].numerator % P * pow(Bern[k].denominator, P - 2, P) % P, 'bernoulli mod', k)
big = list(map(int, subprocess.run([str(exe)], input='3000\n', capture_output=True, text=True, check=True).stdout.split()))
ok(len(big) == 3001 and big[:40] == got)
for m in range(1, 3000, 97):  # defining recurrence modulo P on the long table
    ok(sum(comb(m + 1, j) % P * big[j] for j in range(m + 1)) % P == 0, 'bernoulli recurrence', m)


# Eulerian numbers
def descents(p):
    return sum(p[i] > p[i + 1] for i in range(len(p) - 1))


A = {(0, 0): 1}
for n in range(1, 12):
    for k in range(n):
        A[n, k] = (k + 1) * A.get((n - 1, k), 0) + (n - k) * A.get((n - 1, k - 1), 0)
for n in range(1, 9):
    cnt = [0] * n
    for p in permutations(range(n)):
        cnt[descents(p)] += 1
    for k in range(n):
        ok(cnt[k] == A[n, k], 'eulerian enum', n, k)
for n in range(1, 12):
    for k in range(n):
        ok(A[n, k] == sum((-1) ** i * comb(n + 1, i) * (k + 1 - i) ** n for i in range(k + 1)), 'eulerian sum')
        ok(A[n, k] == A[n, n - 1 - k], 'symmetry')
    ok(sum(A[n, k] for k in range(n)) == factorial(n))
    for x in range(0, 12):
        ok(x ** n == sum(A[n, k] * comb(x + k, n) for k in range(n)), 'worpitzky', n, x)

# Vandermonde and variants
for n in range(0, 15):
    for m in range(0, 15):
        for k in range(0, n + m + 2):
            ok(sum(comb(n, i) * comb(m, k - i) for i in range(0, k + 1)) == comb(n + m, k), 'vandermonde')
        ok(sum(comb(n, i) * comb(m, i) for i in range(n + 1)) == comb(n + m, n))
    ok(sum(comb(n, i) ** 2 for i in range(n + 1)) == comb(2 * n, n))
    for a in range(0, 6):
        for b in range(0, 6):
            ok(sum(comb(i, a) * comb(n - i, b) for i in range(n + 1)) == comb(n + 1, a + b + 1), 'upper', n, a, b)
print(f'Counting sequences: derangements, Bell, Bernoulli (exact and mod 998244353), Eulerian and Vandermonde PASS ({checks} checks)')
