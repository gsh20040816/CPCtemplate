#!/usr/bin/env python3
"""Exact examples for knowledge-probability-games.tex, no third-party modules."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import permutations, product


def mex(values):
    values = set(values)
    answer = 0
    while answer in values:
        answer += 1
    return answer


def main():
    for n in range(1, 8):
        outcomes = list(permutations(range(n)))
        assert F(sum(sum(i == p[i] for i in range(n)) for p in outcomes),
                 len(outcomes)) == 1
    dice = list(product(range(1, 7), repeat=2))
    direct = F(sum(max(a, b) for a, b in dice), len(dice))
    tail = sum(1 - F((k - 1) ** 2, 36) for k in range(1, 7))
    assert direct == tail == F(161, 36)
    # Solve HH waiting time by exact elimination; then independently recover
    # partial tail sums by enumerating the two surviving suffix states.
    e0, e1 = F(6), F(4)
    assert e0 == 1 + e0 / 2 + e1 / 2
    assert e1 == 1 + e0 / 2
    mass0, mass1, partial = F(1), F(0), F(0)
    for _ in range(80):
        partial += mass0 + mass1
        mass0, mass1 = (mass0 + mass1) / 2, mass0 / 2
    assert partial < e0 and e0 - partial == mass0 * e0 + mass1 * e1
    assert e0 - partial < F(1, 10**6)
    # Infinite-support counterexample: telescoping mass and exact tail.
    for n in range(1, 100):
        assert sum((F(1, k * (k + 1)) for k in range(1, n + 1)), F(0)) == 1 - F(1, n + 1)
    for p in (2, 3, 5, 7, 101):
        success, failure = F(p, p + 1), F(1, p + 1)
        expected = 1 / success
        assert success.denominator % p and failure.denominator % p
        assert expected.denominator % p == 0
        assert (1 - failure.numerator * pow(failure.denominator, -1, p)) % p == 0

    moves = (1, 3, 4)
    sg = [0]
    for n in range(1, 1001):
        sg.append(mex(sg[n - s] for s in moves if s <= n))
    assert sg[:14] == [0, 1, 0, 1, 2, 3, 2] * 2
    assert all(sg[n] == sg[n % 7] for n in range(1001))

    @lru_cache(None)
    def winning(heaps):
        return any(not winning(heaps[:i] + (h - s,) + heaps[i + 1:])
                   for i, h in enumerate(heaps) for s in moves if s <= h)

    count = 0
    for arity, bound in ((1, 20), (2, 20), (3, 10)):
        for heaps in product(range(bound + 1), repeat=arity):
            xor = 0
            for h in heaps:
                xor ^= sg[h]
            assert winning(heaps) == bool(xor)
            count += 1
    assert winning((4, 5)) and not winning((4, 4))
    assert not winning((1, 1))
    print(f"PASS: exact probability examples; {count} brute-force game positions; SG through 1000")


if __name__ == "__main__":
    main()
