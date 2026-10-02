#!/usr/bin/env python3
"""Small independent exact checks; no production imports or modular FPS calls."""
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import factorial
from pathlib import Path
import json
import argparse
import hashlib

ROOT = Path(__file__).resolve().parents[1]

MAX_N = 12


def mul(a, b, n):
    """Schoolbook multiplication modulo x^(n+1)."""
    out = [0] * (n + 1)
    for i, ai in enumerate(a[:n + 1]):
        for j, bj in enumerate(b[:n + 1 - i]):
            out[i + j] += ai * bj
    return out


def compose(h, t, n):
    out = [0] * (n + 1)
    power = [1] + [0] * n
    for c in h:
        for i in range(n + 1):
            out[i] += c * power[i]
        power = mul(power, t, n)
    return out


def fixed_point(phi, n):
    """Oracle A: x-adic iteration of T <- x Phi(T), no inversion formula."""
    if not phi or phi[0] == 0:
        raise ValueError('Phi(0)=0 is outside this checker contract')
    t = [0] * (n + 1)
    for _ in range(n):
        t = [0] + compose(phi, t, n)[:n]
    assert t == [0] + compose(phi, t, n)[:n]
    return t


def check_phi(phi):
    nmax = MAX_N
    t = fixed_point(phi, nmax)
    powers_t = [[1] + [0] * nmax]
    for k in range(1, nmax + 3):
        powers_t.append(mul(powers_t[-1], t, nmax))
    # Oracle B computes each Phi^n by another schoolbook multiplication.
    phi_power = [1] + [0] * nmax
    checks = divisibility = 0
    hs = ((7, -2, 3, 1), (-5, 0, -1, 2, 1), (2, 1, 0, -2, 0, 1))
    composed = [compose(h, t, nmax) for h in hs]
    for k in range(nmax + 3):
        assert powers_t[k][0] == (1 if k == 0 else 0)
        checks += 1
    for h, ht in zip(hs, composed):
        assert ht[0] == h[0]
        checks += 1
    for n in range(1, nmax + 1):
        phi_power = mul(phi_power, phi, nmax)
        for k in range(n + 3):
            actual = powers_t[k][n]
            if k == 0:
                expected = 0  # Positive-degree coefficient of T^0=1.
            elif k > n:
                expected = 0  # T has valuation one under this contract.
            else:
                numerator = k * phi_power[n - k]
                assert numerator % n == 0
                expected = numerator // n
                divisibility += 1
            assert actual == expected, (phi, n, k, actual, expected)
            checks += 1
        for h, ht in zip(hs, composed):
            derivative = [j * h[j] for j in range(1, len(h))]
            numerator = mul(derivative, phi_power, nmax)[n - 1]
            assert numerator % n == 0
            assert ht[n] == Fraction(numerator, n), (phi, h, n)
            checks += 1
            divisibility += 1
    return checks, divisibility


@lru_cache(None)
def shapes(d, internal):
    """Actual nested-tuple plane full d-ary shapes; () is a leaf."""
    if internal == 0:
        return frozenset({()})
    result = set()
    for allocation in product(range(internal), repeat=d):
        if sum(allocation) == internal - 1:
            for children in product(*(shapes(d, k) for k in allocation)):
                result.add(tuple(children))
    return frozenset(result)


def count_vertices(shape):
    return 1 + sum(map(count_vertices, shape))


def check_shapes():
    results = {}
    for d, limit in ((2, 7), (3, 5)):
        nmax = d * limit + 1
        phi = [1] + [0] * (d - 1) + [1]
        coefficients = fixed_point(phi, nmax)
        counts = []
        for internal in range(limit + 1):
            actual_shapes = shapes(d, internal)
            size = d * internal + 1
            assert all(count_vertices(s) == size for s in actual_shapes)
            assert coefficients[size] == len(actual_shapes)
            counts.append(len(actual_shapes))
        for size in range(nmax + 1):
            if size == 0 or (size - 1) % d:
                assert coefficients[size] == 0
        results[str(d)] = {'max_internal_nodes': limit, 'shape_counts': counts,
                           'ogf': 'T=x(1+T^d); x counts all vertices'}
    return results


def connected(n, edges):
    adjacency = [set() for _ in range(n)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    seen = {0}
    todo = [0]
    while todo:
        for v in adjacency[todo.pop()]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen) == n


def check_labelled_trees():
    # exp(t) truncated at 5 suffices for coefficients through x^5.
    coefficients = fixed_point([Fraction(1, factorial(j)) for j in range(6)], 5)
    counts = []
    for n in range(1, 6):
        possible_edges = list(combinations(range(n), 2))
        rooted_graphs = set()
        connected_graphs = 0
        candidates = 0
        for edges in combinations(possible_edges, n - 1):
            candidates += 1
            if connected(n, edges):
                connected_graphs += 1
                for root in range(n):
                    rooted_graphs.add((edges, root))
        count = len(rooted_graphs)
        assert coefficients[n] == Fraction(count, factorial(n))
        counts.append({'vertices': n, 'candidate_graphs': candidates,
                       'connected_graphs': connected_graphs,
                       'rooted_graphs': count, 'egf_coefficient': str(coefficients[n])})
    assert coefficients[0] == 0
    return counts


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: assertions are required')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=ROOT / 'build/lagrange-knowledge.json')
    args = parser.parse_args()
    paths = [Path(__file__).resolve(), ROOT / 'docs/knowledge-lagrange.tex']
    sources_before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    checks = divisibility = 0
    phis = set()
    for constant in (1, 2):
        for degree in range(4):
            for tail in product((-1, 0, 1, 2), repeat=degree):
                phi = (constant,) + tail
                # Canonicalize trailing zeroes; exhaustive degrees at most 3.
                while len(phi) > 1 and phi[-1] == 0:
                    phi = phi[:-1]
                phis.add(phi)
    for phi in sorted(phis):
        c, d = check_phi(phi)
        checks += c
        divisibility += d
    rejected = 0
    for phi in ([0], [0, 1], [0, -1, 2]):
        try:
            fixed_point(phi, MAX_N)
        except ValueError as error:
            assert 'outside this checker contract' in str(error)
            rejected += 1
        else:
            raise AssertionError('Expected contract rejection')
    # Catalan C=x(1+C)^2 has [x^3]C=5; the numerator is [t^2](1+t)^6=15.
    catalan = fixed_point([1, 2, 1], 3)[3]
    cubed = [1, 0, 0, 0]
    for _ in range(3):
        cubed = mul(cubed, [1, 2, 1], 3)
    numerator = cubed[2]
    assert (catalan, numerator) == (5, 15)
    assert not any((3 * candidate) % 3 == 1 for candidate in range(3))
    result = {
        'status': 'pass', 'max_n': MAX_N,
        'unique_integer_phi_cases': len(phis),
        'phi_scope': 'constant 1 or 2, degree <=3, remaining coefficients in {-1,0,1,2}',
        'identity_and_boundary_checks': checks,
        'exact_integer_divisibility_checks': divisibility,
        'nonmonomial_H': [[7, -2, 3, 1], [-5, 0, -1, 2, 1], [2, 1, 0, -2, 0, 1]],
        'phi_zero_contract_rejections': rejected,
        'ordered_full_d_ary_shapes': check_shapes(),
        'labelled_rooted_tree_enumeration': check_labelled_trees(),
        'modular_nonunit_example': {'modulus': 3, 'n': 3, 'true_coefficient': catalan,
            'true_residue': catalan % 3, 'integer_numerator': numerator,
            'numerator_residue': numerator % 3, 'inverse_n_exists': False,
            'interpretation': 'Integer division before reduction works; division by n inside this field is undefined.'},
        'scope': 'Exact characteristic-zero mathematical checks only; no C++ runtime, sanitizer, new algorithm or online-judge claim'
    }
    sources_after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert sources_before == sources_after, 'Sources changed during exact checks'
    result['sources_before'] = sources_before
    result['sources_after'] = sources_after
    target = args.report
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
