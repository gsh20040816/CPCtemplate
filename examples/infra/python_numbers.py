from math import comb, gcd, isqrt, lcm
from fractions import Fraction
from decimal import Decimal, localcontext

n = 10**100
assert isqrt(n - 1) == 10**50 - 1
assert comb(100, 50) == 100891344545564193334812497256
assert gcd(12, 18) == 6
assert lcm(12, 18) == 36
assert pow(3, 100, 7) == 4
assert pow(3, -1, 7) == 5
assert divmod(-7, 3) == (-3, 2)
assert (-7) // 3 == -3
assert -(7 // 3) == -2

a = Fraction(1, 3) + Fraction(1, 6)
assert (a.numerator, a.denominator) == (1, 2)
assert Fraction("0.1") == Fraction(1, 10)
assert Fraction(0.1) != Fraction(1, 10)
with localcontext() as ctx:
    ctx.prec = 60
    x = Decimal(2).sqrt()
    assert abs(x * x - 2) < Decimal("1e-58")
    assert Decimal("0.1") * 3 == Decimal("0.3")
print("numbers: pass")
