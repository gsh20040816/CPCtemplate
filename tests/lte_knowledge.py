#!/usr/bin/env python3
"""Exact-integer checks of the stated LTE identities; finite evidence, not a proof."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'docs/mathematics.tex').exists())


def valuation(x, p):
    if x == 0:
        raise ValueError('v_p(0) is not a finite integer')
    x = abs(x)
    result = 0
    while x % p == 0:
        x //= p
        result += 1
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--report', type=Path, default=ROOT / 'build/lte-knowledge.json')
    args = ap.parse_args()
    counts = Counter()
    primes = [p for p in range(2, 44) if all(p % d for d in range(2, p))]
    # Direct large integer powers and repeated division are the reference.
    for a in range(1, 25):
        for b in range(1, 25):
            for n in range(1, 19):
                difference, total = a**n - b**n, a**n + b**n
                for p in primes:
                    if p > 2 and a % p and b % p:
                        if a != b and (a-b) % p == 0:
                            assert valuation(difference, p) == valuation(a-b, p) + valuation(n, p)
                            counts['odd_prime_difference'] += 1
                        if n % 2 and (a+b) % p == 0:
                            assert valuation(total, p) == valuation(a+b, p) + valuation(n, p)
                            counts['odd_prime_odd_sum'] += 1
                    if a != b:
                        r, s = valuation(a, p), valuation(b, p)
                        if r != s:
                            assert valuation(difference, p) == n * min(r, s)
                            assert valuation(total, p) == n * min(r, s)
                            counts['unequal_common_factor_difference_and_sum'] += 1
                        else:
                            x, y = a // p**r, b // p**s
                            assert valuation(difference, p) == n*r + valuation(x**n-y**n, p)
                            assert valuation(total, p) == n*r + valuation(x**n+y**n, p)
                            counts['equal_common_factor_difference_and_sum'] += 1
                if a % 2 and b % 2:
                    if a != b:
                        wanted = valuation(a-b, 2) if n % 2 else valuation(a-b, 2) + valuation(a+b, 2) + valuation(n, 2) - 1
                        assert valuation(difference, 2) == wanted
                        counts['two_adic_odd_difference' if n % 2 else 'two_adic_even_difference'] += 1
                    assert valuation(total, 2) == (valuation(a+b, 2) if n % 2 else 1)
                    counts['two_adic_odd_sum' if n % 2 else 'two_adic_even_sum'] += 1
    # Arithmetic laws, including cancellation: equal valuations need not give equality.
    for p in primes:
        for x in range(1, 65):
            for y in range(1, 65):
                vx, vy = valuation(x, p), valuation(y, p)
                assert valuation(x*y, p) == vx + vy
                assert valuation(x+y, p) >= min(vx, vy)
                if vx != vy:
                    assert valuation(x+y, p) == min(vx, vy)
                counts['valuation_arithmetic'] += 1
    negatives = []
    for title, actual, invalid_formula in [
        ('documented nonunit p=3,a=6,b=3,n=2', valuation(6**2-3**2,3),valuation(6-3,3)+valuation(2,3)),
        ('nonunit a,b: p=3,a=6,b=3,n=3', valuation(6**3-3**3,3),valuation(6-3,3)+valuation(3,3)),
        ('p does not divide difference: p=3,a=2,b=1,n=2',valuation(2**2-1,3),valuation(2-1,3)+valuation(2,3)),
        ('odd-prime formula used at2: a=3,b=1,n=2',valuation(3**2-1,2),valuation(3-1,2)+valuation(2,2)),
        ('even exponent used in odd-prime sum: p=3,a=2,b=1,n=2',valuation(2**2+1,3),valuation(2+1,3)+valuation(2,3)),
        ('composite base9: a=28,b=1,n=3',valuation(28**3-1,9),valuation(28-1,9)+valuation(3,9)),
    ]:
        assert actual != invalid_formula
        negatives.append(dict(reason=title,actual=actual,invalid_formula=invalid_formula))
    try:
        valuation(0, 3)
    except ValueError:
        counts['zero_rejected'] += 1
    else:
        raise AssertionError('Zero must not enter finite-valuation formulas')
    assert valuation(3+6,3) > min(valuation(3,3),valuation(6,3))
    # Closed-form divisibility examples, checked by literal powers; minimum n
    # established independently by testing every smaller positive exponent.
    for base, p, initial, maximum in [(10,3,2,6),(9,2,3,11)]:
        for k in range(1,maximum+1):
            wanted=p**max(0,k-initial)
            actual=next(n for n in range(1,wanted+1) if (base**n-1) % p**k == 0)
            assert actual==wanted
            counts['minimum_exponent_examples'] += 1
    for n in range(1,145):
        assert ((7**n-1) % (2**6*3**2) == 0) == (n % 24 == 0)
        counts['documented_seven_power_divisibility'] += 1
    report={'scope':'Finite exact-integer checks; mathematical proof and hypotheses are in the knowledge text. No C++ runtime, sanitizer or online AC claim.',
            'passed':True,'checked_at':datetime.now(timezone.utc).isoformat(),'domains':{'a_b':[1,24],'n':[1,18],'primes':primes,'arithmetic_x_y':[1,64]},'checks':dict(counts),'hypothesis_counterexamples':negatives,
            'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),ROOT/'docs/knowledge-lte.tex']}}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    print('LTE exact-integer identities and hypothesis counterexamples PASS:',dict(counts))


if __name__=='__main__':
    main()
